from pydantic import BaseModel, EmailStr, Field, field_validator

class RecipientInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value

class JobCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    certificate_title: str = Field(
        default="Certificate of Completion",
        min_length=2,
        max_length=200,
    )
    recipients: list[RecipientInput] = Field(min_length=1, max_length=1000)
