from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_name: Mapped[str] = mapped_column(String(200))
    certificate_title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    total: Mapped[int] = mapped_column(default=0)

    recipients = relationship(
        "Recipient",
        back_populates="job",
        cascade="all, delete-orphan",
    )

class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320))
    status: Mapped[str] = mapped_column(String(40), default="pending")
    certificate_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    job = relationship("Job", back_populates="recipients")
