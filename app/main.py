import pandas as pd
from fastapi import FastAPI
from fastapi import UploadFile

app = FastAPI()


def read_file(file: UploadFile) -> pd.DataFrame:
    file_name = file.filename
    if not file_name.endswith(('.csv', '.xls', '.xlsx')):
        raise ValueError('Unsupported file format')
    if file_name.endswith('.csv'):
        return pd.read_csv(file.file)
    return pd.read_excel(file.file)


@app.post("/upload")
async def upload():
    return {'message': 'success'}
