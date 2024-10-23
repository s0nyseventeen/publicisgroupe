import os
from io import BytesIO

import pandas as pd
from fastapi import UploadFile
from fastapi.testclient import TestClient
from pytest import fixture
from pytest import raises
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.main import get_session
from app.main import read_file
from app.main import validate_dataframe
from app.models import UploadedFile

FILE_COLUMNS = ['Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr']
VALID_DATA = {
    'Advertiser': ['TestBrand'],
    'Brand': ['TestProduct'],
    'Start': ['2022'],
    'End': ['2023'],
    'Format': ['Video'],
    'Platform': ['YouTube'],
    'Impr': [1000.0]
}

TEST_DB_URL = "sqlite:///test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session():
    with Session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@fixture()
def setup_test_db():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)
    engine.dispose()
    os.remove('test.db')


@fixture
def client():
    return TestClient(app)


@fixture
def mock_csv_file():
    csv_content = b'Advertiser,Brand,Start,End,Format,Platform,Impr\nTestBrand,TestProduct,2022,2023,Video,YouTube,1000\n'
    return UploadFile(filename='test.csv', file=BytesIO(csv_content))


@fixture
def mock_excel_file():
    excel_content = BytesIO()
    df = pd.DataFrame(VALID_DATA)
    df.to_excel(excel_content, index=False)
    excel_content.seek(0)
    return UploadFile(filename='test.xlsx', file=excel_content)


@fixture
def mock_unsupported_file():
    file_content = b'Some unsupported data'
    return UploadFile(filename='test.txt', file=BytesIO(file_content))


def test_read_file_csv_success(mock_csv_file):
    df = read_file(mock_csv_file)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.columns.tolist() == FILE_COLUMNS


def test_read_file_xlsx_success(mock_excel_file):
    df = read_file(mock_excel_file)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.columns.tolist() == FILE_COLUMNS


def test_read_file_exception(mock_unsupported_file):
    with raises(ValueError, match='Unsupported file format'):
        read_file(mock_unsupported_file)


def test_validate_dataframe_empty_dataframe_exception():
    with raises(ValueError, match='Missing required_columns'):
        validate_dataframe(pd.DataFrame(columns=[]))


def test_validate_dataframe_extra_columns_exception():
    invalid_data = {**VALID_DATA, 'extra_column': ['extra_value']}
    with raises(ValueError, match='Missing required_columns'):
        validate_dataframe(pd.DataFrame(invalid_data))


def test_validate_dataframe_missing_required_columns():
    invalid_data = {**VALID_DATA}
    del invalid_data['Impr']

    with raises(ValueError, match='Missing required_columns'):
        validate_dataframe(pd.DataFrame(invalid_data))


def test_validate_dataframe_success():
    validate_dataframe(pd.DataFrame(VALID_DATA))


# TODO ?remove httpx
def test_upload_csv_success(tmp_path, setup_test_db, client):
    df = pd.DataFrame(VALID_DATA)
    test_file_csv = tmp_path / 'test_file.csv'
    df.to_csv(test_file_csv, index=False)

    with open(test_file_csv, 'rb') as f:
        resp = client.post(
            '/upload', files={'file': (test_file_csv.name, f, 'text/csv')}
        )

    assert resp.status_code == 200
    assert resp.json()['message'] == 'File uploaded and data saved successfully'

    with Session() as session:
        uploaded_file = session.query(UploadedFile).first()
        assert uploaded_file is not None
