from fastapi import FastAPI, Form

form_data_app = FastAPI()
# form data is normally encoded using the 'media type' application/x-www-form-urlencoded
# but when the form includes files it is encoded as multipart/form-data
# when you need to receive form fields instead of json, you can use Form
# to use forms first install python-multipart
@form_data_app.post('/login')
async def login(
        # form parameters are defined the same as Body or Query
        username: str=Form(...),
        password: str=Form(...)):
    return {'username': username}

