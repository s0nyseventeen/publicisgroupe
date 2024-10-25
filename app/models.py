from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel


class UploadedFile(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    uploaded_data: list['UploadedData'] = Relationship(
        back_populates='uploaded_file'
    )
