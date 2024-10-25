import pandas as pd
from sqlmodel import Session

from .models import UploadedData
from .models import UploadedFile


def create_uploaded_file(file_name: str, session: Session) -> UploadedFile:
    uploaded_file = UploadedFile(name=file_name)
    session.add(uploaded_file)
    session.commit()
    session.refresh(uploaded_file)
    return uploaded_file


def create_uploaded_data(
    df: pd.DataFrame, uploaded_file_id: int, session: Session
):
    for _, row in df.iterrows():
        uploaded_data = UploadedData(
            uploaded_file_id=uploaded_file_id,
            advertiser=row['Advertiser'],
            brand=row['Brand'],
            start=row['Start'],
            end=row['End'],
            format=row['Format'],
            platform=row['Platform'],
            impr=row['Impr']
        )
        session.add(uploaded_data)
    session.commit()
