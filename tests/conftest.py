from pytest import fixture
from sqlmodel import create_engine
from sqlmodel import SQLModel
from sqlmodel import StaticPool


engine = create_engine(
    'sqlite:///:memory:',
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


@fixture()
def setup_test_db():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)
