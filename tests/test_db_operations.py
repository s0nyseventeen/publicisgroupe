import pandas as pd
from pytest import fixture
from sqlmodel import Session

from .conftest import engine
from app.db_operations import create_uploaded_data
from app.db_operations import create_uploaded_file
from app.models import UploadedData


@fixture
def session(setup_test_db):
    with Session(engine) as session:
        yield session


def test_create_uploaded_file(session):
    uploaded_file = create_uploaded_file('test_file', session)
    session.add(uploaded_file)
    session.commit()
    assert uploaded_file.name == 'test_file'


def test_create_uploaded_data(session):
    uploaded_file = create_uploaded_file('test_file', session)
    uploaded_file_id = uploaded_file.id
    data = {
        'Advertiser': ['Test Advertiser1', 'Test Advertiser2'],
        'Brand': ['Test Brand1', 'Test Brand2'],
        'Start': ['2024-01-01', '2024-01-02'],
        'End': ['2024-01-31', '2024-02-01'],
        'Format': ['Video', 'Video'],
        'Platform': ['YouTube', 'Instagram'],
        'Impr': [100.0, 200.0]
    }
    df = pd.DataFrame(data)
    create_uploaded_data(df, uploaded_file_id, session)
    results = session.query(UploadedData).filter_by(
        uploaded_file_id=uploaded_file_id
    ).all()

    assert len(results) == len(df)
    for i, res in enumerate(results):
        assert res.advertiser == data['Advertiser'][i]
        assert res.brand == data['Brand'][i]
        assert res.start == data['Start'][i]
        assert res.end == data['End'][i]
        assert res.format == data['Format'][i]
        assert res.platform == data['Platform'][i]
        assert res.impr == data['Impr'][i]
