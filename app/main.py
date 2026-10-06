from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Job, Recipient
from .schemas import JobCreate
from .services.certificate_generator import generate_certificate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    version="1.0.0",
    description="Generate certificates in bulk and track generation progress."
)

def process_job(job_id: int):
    db: Session = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return
        job.status = "processing"
        db.commit()

        recipients = db.scalars(
            select(Recipient).where(Recipient.job_id == job_id)
        ).all()

        for recipient in recipients:
            try:
                recipient.status = "processing"
                db.commit()

                path = generate_certificate(
                    recipient.name,
                    recipient.email,
                    job.event_name,
                    job.certificate_title,
                    recipient.id,
                )
                recipient.status = "success"
                recipient.certificate_path = path
                recipient.error_message = None
            except Exception as exc:
                recipient.status = "failed"
                recipient.error_message = str(exc)
            finally:
                db.commit()

        failed = sum(1 for r in recipients if r.status == "failed")
        job.status = "completed_with_errors" if failed else "completed"
        db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Bulk Certificate Generator API", "docs": "/docs"}

@app.post("/jobs", status_code=202)
def create_job(payload: JobCreate, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        job = Job(
            event_name=payload.event_name,
            certificate_title=payload.certificate_title,
            status="queued",
            total=len(payload.recipients),
        )
        db.add(job)
        db.flush()

        for item in payload.recipients:
            db.add(Recipient(
                job_id=job.id,
                name=item.name,
                email=item.email,
                status="pending",
            ))

        db.commit()
        job_id = job.id
        background_tasks.add_task(process_job, job_id)

        return {
            "job_id": job_id,
            "status": "queued",
            "total": len(payload.recipients),
        }
    finally:
        db.close()

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        recipients = db.scalars(
            select(Recipient).where(Recipient.job_id == job_id)
        ).all()

        successful = sum(r.status == "success" for r in recipients)
        failed = sum(r.status == "failed" for r in recipients)
        processed = successful + failed
        progress = round((processed / job.total) * 100, 2) if job.total else 100

        return {
            "job_id": job.id,
            "status": job.status,
            "event_name": job.event_name,
            "certificate_title": job.certificate_title,
            "total": job.total,
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "progress_percent": progress,
            "recipients": [
                {
                    "recipient_id": r.id,
                    "name": r.name,
                    "email": r.email,
                    "status": r.status,
                    "certificate_url": (
                        f"/certificates/{r.id}" if r.status == "success" else None
                    ),
                    "error": r.error_message,
                }
                for r in recipients
            ],
        }
    finally:
        db.close()

@app.get("/certificates/{recipient_id}")
def get_certificate(recipient_id: int):
    db = SessionLocal()
    try:
        recipient = db.get(Recipient, recipient_id)
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        if recipient.status != "success" or not recipient.certificate_path:
            raise HTTPException(
                status_code=409,
                detail="Certificate is not available yet."
            )
        if not os.path.exists(recipient.certificate_path):
            raise HTTPException(status_code=404, detail="Certificate file not found")

        return FileResponse(
            recipient.certificate_path,
            media_type="application/pdf",
            filename=f"certificate_{recipient.id}.pdf",
        )
    finally:
        db.close()
