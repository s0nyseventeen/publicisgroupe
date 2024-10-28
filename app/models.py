from datetime import date

from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel


class UploadedFile(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    uploaded_data: list['UploadedData'] = Relationship(
        back_populates='uploaded_file'
    )


class UploadedData(SQLModel, table=True):
    id: int = Field(primary_key=True)
    uploaded_file_id: int = Field(foreign_key='uploadedfile.id')
    advertiser: str = Field(nullable=False)
    brand: str = Field(nullable=False)
    start: date = Field(nullable=False)
    end: date = Field(nullable=False)
    format: str = Field(nullable=False)
    platform: str = Field(nullable=False)
    impr: float = Field(nullable=False)
    uploaded_file: UploadedFile = Relationship(back_populates='uploaded_data')
