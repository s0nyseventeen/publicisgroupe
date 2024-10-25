import pandas as pd
from fastapi import FastAPI
from fastapi import UploadFile

app = FastAPI()


def read_file(file: UploadFile) -> pd.DataFrame:
    if file.filename.endswith('.csv'):
        return pd.read_csv(file.file)
    elif file.filename.endswith('.xls') or file.filename.endswith('.xlsx'):
        return pd.read_excel(file.file)
    raise ValueError('Unsupported file format')


def validate_dataframe(df: pd.DataFrame):
    required_columns = {
        'Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr'
    }
    if required_columns != set(df.columns):
        raise ValueError(f'Missing required_columns. {required_columns=}')


@app.post("/upload")
async def upload():
    return {'message': 'success'}
