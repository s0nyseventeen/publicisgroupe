from typing import Annotated

import pandas as pd
from fastapi import Depends
from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel

from .models import UploadedData
from .models import UploadedFile

engine = create_engine(
    'sqlite:///publicisgroupe.db',
    connect_args={'check_same_thread': False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


def read_file(file: UploadFile) -> pd.DataFrame:
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file.file)
    elif file.filename.endswith('.xls') or file.filename.endswith('.xlsx'):
        df = pd.read_excel(file.file)
    else:
        raise HTTPException(status_code=400, detail='Unsupported file format')
    return df


def validate_dataframe(df: pd.DataFrame):
    required_columns = {
        'Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr'
    }
    if required_columns != set(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f'Missing required_columns. {required_columns=}'
        )


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.post("/upload")
async def upload(
    file: UploadFile = File(...), session: SessionDep = Depends(get_session)
):
    try:
        df = read_file(file)
        validate_dataframe(df)

        uploaded_file = UploadedFile(name=file.filename)
        session.add(uploaded_file)
        session.commit()
        session.refresh(uploaded_file)

        for _, row in df.iterrows():
            uploaded_data = UploadedData(
                file_id=uploaded_file.id,
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
        return {'message': 'File uploaded and data saved successfully'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error processing file: {e}')
