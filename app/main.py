import pandas as pd
from fastapi import FastAPI
from fastapi import UploadFile
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel

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


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.post("/upload")
async def upload():
    return {'message': 'success'}
