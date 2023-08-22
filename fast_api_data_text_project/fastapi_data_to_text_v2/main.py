
import os 
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, status ,HTTPException, Response, UploadFile
from fastapi.security import OAuth2PasswordBearer
import jwt
import model
import UserRequest

try:
    secret_key = os.environ["SECRET_KEY_JWT"] 
except KeyError:
    raise Exception("Requested Environmental Variable does not exist.")

algorithm = "HS256"
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

def create_access_token(data: dict, time_to_expire: timedelta):
    unencoded_data = data.copy()
    expiration_time = datetime.utcnow() + time_to_expire
    unencoded_data["exp"] = expiration_time
    encoded_JWT = jwt.encode(unencoded_data, secret_key,algorithm)
    return encoded_JWT

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, key = secret_key, algorithms = [algorithm])
        user_name = payload.get("sub")
        if user_name == None:
             raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid authentication credentials",
                headers = {"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Expired Token",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Token",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    return {"user_name": user_name}


@app.post("/token")
async def login(auth_request: UserRequest.AuthRequest, response: Response):
    authentication = model.verify_user(auth_request.user_name, auth_request.password)
    if authentication:
        access_token_expires = timedelta(minutes = 60)
        access_token = create_access_token(data = {"sub": auth_request.user_name}, time_to_expire = access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code = 401, detail = "Either the password or the user name is incorrect.")

@app.post("/")
async def process_text_input(text_input_request: UserRequest.TextInputRequest, current_user: dict = Depends(get_current_user) ) -> list[model.Entity.Entity] :
    output = model.process_data(text_input_request.input, text_input_request.language)
    return output

@app.post("/file")
async def process_file(file: UploadFile, input_language: UserRequest.InputLanguage = UserRequest.InputLanguage() , current_user: dict = Depends(get_current_user)) -> list[model.Entity.Entity]:
    file_content = await file.read()
    file_type_data = model.find_file_type(file_content)
    data = await model.get_data_from_file(file_content, file_type_data)
    return model.process_data(data, input_language.language)

@app.post("/post_processed_file")
async def post_process_file(file: UploadFile, input_language: UserRequest.InputLanguage = UserRequest.InputLanguage() , current_user: dict = Depends(get_current_user)) -> list[model.Entity.EntityPostProcessed]:
    file_content = await file.read()
    file_type_data = model.find_file_type(file_content)
    data = await model.get_data_from_file(file_content, file_type_data)
    output = model.process_data(data, input_language.language)
    post_processed_output = model.ner_post_processing(output)
    return post_processed_output
@app.post("/ner_alternative")
async def ner_alternative(file: UploadFile, input_language: UserRequest.InputLanguage = UserRequest.InputLanguage() , current_user: dict = Depends(get_current_user)) -> list[model.Entity.EntityAlternative]:
    file_content = await file.read()
    file_type_data = model.find_file_type(file_content)
    data = await model.get_data_from_file(file_content, file_type_data)
    print(data)
    return model.ner_alternative(data, input_language.language)