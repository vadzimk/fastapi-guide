from typing import Optional, List

from fastapi import FastAPI, Form, File, UploadFile
from starlette.responses import HTMLResponse

form_data_app = FastAPI()


# form data is normally encoded using the 'media type' application/x-www-form-urlencoded
# but when the form includes files it is encoded as multipart/form-data
# when you need to receive form fields instead of json, you can use Form
# to use forms first install python-multipart
@form_data_app.post('/login')
async def login(
        # form parameters are defined the same as Body or Query
        username: str = Form(...),
        password: str = Form(...)):
    return {'username': username}


# to receive files first install python-multipart
# because uploaded files are sent as form data
@form_data_app.post('/files')
async def create_file(
        # declaring type as bytes will store content in memory and read the file (good for small files)
        file: bytes = File(...),  # File is a class that inherits from Form, it returns this class
        # file: Optional[bytes] = File(None) # you can make file optional
        files: List[bytes] = File(...)  # multiple files associated with the same form field
):
    return {'file_size': len(file)}


@form_data_app.post('/uploadfile')
async def create_upload_file(
        file: UploadFile,  # will store file on disk, good for large files
        # file: Optional[UploadFile] = None # you can make file optional
        files: List[UploadFile],  # multiple files associated with the same form field
        description='A file read as UploadFile',  # additional metadata for docs
):
    contents = await file.read()
    return {'filenames': [file.filename for file in files]}


@form_data_app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
