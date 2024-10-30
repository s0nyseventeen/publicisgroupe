from typing import Annotated

import pandas as pd
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import UploadFile
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel

from .db_operations import create_uploaded_data
from .db_operations import create_uploaded_file

engine = create_engine(
    'sqlite:///publicisgroupe.db',
    connect_args={'check_same_thread': False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


def read_file(file: UploadFile) -> pd.DataFrame:
    file_name = file.filename
    if not file_name.endswith(('.csv', '.xls', '.xlsx')):
        raise ValueError('Unsupported file format')
    if file_name.endswith('.csv'):
        return pd.read_csv(file.file)
    return pd.read_excel(file.file)


def validate_dataframe(df: pd.DataFrame):
    required_columns = {
        'Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr'
    }
    if required_columns != set(df.columns):
        raise ValueError(f'Missing required_columns. {required_columns=}')


def calculate_sum_by_year(df: pd.DataFrame) -> list[dict[str, int]]:
    df['Start'] = pd.to_datetime(df['Start'])
    df['Year'] = df['Start'].dt.year
    sum_by_year = df.groupby('Year')['Impr'].sum().reset_index()
    return sum_by_year.to_dict(orient='records')


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.post("/upload")
async def upload(
    session: Annotated[Session, Depends(get_session)], file: UploadFile
):
    try:
        df = read_file(file)
        validate_dataframe(df)
        uploaded_file = create_uploaded_file(file.filename, session)
        create_uploaded_data(df, uploaded_file.id, session)
        return {'message': calculate_sum_by_year(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error processing file: {e}')
