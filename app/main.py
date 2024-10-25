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


@app.post("/upload")
async def upload():
    return {'message': 'success'}
