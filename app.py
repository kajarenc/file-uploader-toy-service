import uuid

import pydantic
from fastapi import FastAPI, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import UploadFile as StarletteUploadFile

import file_storage as storage


class PresignedUrlsRequest(pydantic.BaseModel):
    number_of_files: int = pydantic.Field(alias="numberOfFiles")
    session_id: str = pydantic.Field(alias="sessionId")


class PresignedUrl(pydantic.BaseModel):
    file_id: uuid.UUID
    presigned_url: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_urls")
def make_upload_urls(
    request: Request, data: PresignedUrlsRequest
) -> list[PresignedUrl]:
    generated_urls = []

    for _ in range(data.number_of_files):
        file_id = uuid.uuid4()
        upload_to = request.url_for(
            "store_uploaded_file", session_id=data.session_id, file_id=file_id
        )
        generated_urls.append(
            PresignedUrl(file_id=file_id, presigned_url=str(upload_to))
        )

    return generated_urls


@app.get("/upload_fileZZ/{session_id}/{file_id}", status_code=200)
def retrieve_uploaded_file(session_id: str, file_id: str):
    try:
        file = storage.retrieve_file(session_id, file_id)
        return Response(
            file.content,
            media_type=file.content_type,
            headers={"Content-Disposition": f'attachment; filename="{file.filename}"'},
        )
    except OSError:
        return Response(status_code=404)


@app.put("/upload_fileZZ/{session_id}/{file_id}", status_code=201)
@app.post("/upload_fileZZ/{session_id}/{file_id}", status_code=201)
async def store_uploaded_file(request: Request, session_id: str, file_id: str):
    form_data = await request.form()
    for key, value in form_data.items():
        if isinstance(value, StarletteUploadFile):
            file = value
            break
    else:
        print("NO FILE IN PAYLOAD!!!")

    file_content = await file.read()
    stored_file = storage.StoredFile(
        filename=(file.filename or file_id),
        content_type=(file.content_type or "text/plain"),
        content=file_content,
    )
    storage.store_file(session_id, file_id, stored_file)


@app.delete("/upload_fileZZ/{session_id}/{file_id}")
def delete_uploaded_file(session_id: str, file_id: str) -> None:
    storage.remove_file(session_id, file_id)


@app.delete("/upload_fileZZ/{session_id}", status_code=204)
def remove_session_files(session_id: str):
    storage.remove_all_session_files(session_id)
