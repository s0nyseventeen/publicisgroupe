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


def validate_date(value, idx, column: str) -> pd.DataFrame:
    if isinstance(value, int):
        message = f'Invalid date format at index {idx=}, {column=}, {value=}'
        raise ValueError(message)
    return pd.to_datetime(value, format='mixed', dayfirst=True).date()


def create_uploaded_data(
    df: pd.DataFrame, uploaded_file_id: int, session: Session
):
    for idx, row in df.iterrows():
        try:
            uploaded_data = UploadedData(
                uploaded_file_id=uploaded_file_id,
                advertiser=row['Advertiser'],
                brand=row['Brand'],
                start=validate_date(row['Start'], idx, 'Start'),
                end=validate_date(row['End'], idx, 'End'),
                format=row['Format'],
                platform=row['Platform'],
                impr=row['Impr']
            )
            session.add(uploaded_data)
        except ValueError as e:
            message = f'Error processing row {idx} with data {row.to_dict()}: {e}'
            raise ValueError(message)
    session.commit()
