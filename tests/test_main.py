from io import BytesIO

import pandas as pd
from fastapi import UploadFile
from fastapi.testclient import TestClient
from pytest import fixture
from pytest import raises
from sqlmodel import Session

from .conftest import engine
from app.main import app
from app.main import calculate_sum_by_year
from app.main import get_session
from app.main import read_file
from app.main import validate_dataframe

FILE_COLUMNS = ['Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr']
VALID_DATA = {
    'Advertiser': ['TestBrand'],
    'Brand': ['TestProduct'],
    'Start': ['2024-01-31'],
    'End': ['2024-02-01'],
    'Format': ['Video'],
    'Platform': ['YouTube'],
    'Impr': [1000.0]
}


def upload_file(client, file_path, file_type):
    with open(file_path, 'rb') as f:
        resp = client.post(
            '/upload', files={'file': (file_path.name, f, file_type)}
        )
    return resp


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


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


@fixture
def make_data_invalid():
    invalid_data = {**VALID_DATA}
    del invalid_data['Impr']
    return invalid_data


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


def test_validate_dataframe_missing_required_columns(make_data_invalid):
    with raises(ValueError, match='Missing required_columns'):
        validate_dataframe(pd.DataFrame(make_data_invalid))


def test_validate_dataframe_success():
    validate_dataframe(pd.DataFrame(VALID_DATA))


def test_calculate_sum_by_year():
    data = {
        'Start': ['2024-01-01', '2024-02-01', '2025-03-01'],
        'Impr': [100, 200, 150]
    }
    result = calculate_sum_by_year(pd.DataFrame(data))
    expected = [{'Year': 2024, 'Impr': 300}, {'Year': 2025, 'Impr': 150}]
    assert result == expected


def test_upload_csv_success(tmp_path, setup_test_db, client):
    df = pd.DataFrame(VALID_DATA)
    test_file_csv = tmp_path / 'test_file.csv'
    df.to_csv(test_file_csv, index=False)

    resp = upload_file(client, test_file_csv, 'text/csv')
    assert resp.status_code == 200
    assert resp.json()['message'] == [{'Impr': 1000.0, 'Year': 2024}]


def test_upload_invalid_file_format_exception(tmp_path, setup_test_db, client):
    test_file_txt = tmp_path / 'test_file.txt'
    test_file_txt.write_text('Invalid file format')

    resp = upload_file(client, test_file_txt, 'text/plain')
    assert resp.status_code == 400
    assert 'Error processing file: Unsupported file format' in resp.json()['detail']


def test_upload_invalid_data_format_exception(
    tmp_path, setup_test_db, client, make_data_invalid
):
    df = pd.DataFrame(make_data_invalid)
    test_file_csv = tmp_path / 'test_file.csv'
    df.to_csv(test_file_csv, index=False)

    resp = upload_file(client, test_file_csv, 'text/csv')
    assert resp.status_code == 400
    assert 'Error processing file: Missing required_columns' in resp.json()['detail']
