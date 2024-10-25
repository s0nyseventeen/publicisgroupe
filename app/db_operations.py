from sqlmodel import Session

from .models import UploadedFile


def create_uploaded_file(file_name: str, session: Session) -> UploadedFile:
    uploaded_file = UploadedFile(name=file_name)
    session.add(uploaded_file)
    session.commit()
    session.refresh(uploaded_file)
    return uploaded_file
