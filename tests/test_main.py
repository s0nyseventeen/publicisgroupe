from io import BytesIO

import pandas as pd
from fastapi import UploadFile
from pytest import fixture
from pytest import raises

from app.main import read_file

FILE_COLUMNS = ['Advertiser', 'Brand', 'Start', 'End', 'Format', 'Platform', 'Impr']


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
