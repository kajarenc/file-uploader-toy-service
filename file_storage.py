import os
import pickle
import pydantic
import shutil


class StoredFile(pydantic.BaseModel):
    filename: str
    content_type: str
    content: bytes


def store_file(session_id: str, file_id: str, file: StoredFile) -> None:
    file_path = _make_file_path(session_id, file_id)
    with open(file_path, "wb") as buf:
        pickle.dump(file, buf)


def retrieve_file(session_id: str, file_id: str) -> StoredFile:
    file_path = _get_file_path(session_id, file_id)
    with open(file_path, "rb") as buf:
        return pickle.load(buf)


def remove_file(session_id: str, file_id: str) -> None:
    file_path = _get_file_path(session_id, file_id)
    if os.path.exists(file_path):
        os.remove(file_path)


def remove_all_session_files(session_id: str) -> None:
    dir_path = _get_file_path(session_id)
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


def _get_file_path(session_id: str, file_id: str = "") -> str:
    return os.path.join("media", session_id, file_id)


def _make_file_path(session_id: str, file_id: str = "") -> str:
    expected_path = _get_file_path(session_id, file_id)
    if not os.path.exists(os.path.split(expected_path)[0]):
        os.makedirs(os.path.split(expected_path)[0])
    return expected_path
