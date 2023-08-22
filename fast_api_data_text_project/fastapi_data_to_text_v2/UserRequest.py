from pydantic import BaseModel

class AuthRequest(BaseModel):
    user_name: str
    password: str

class TextInputRequest(BaseModel):
    input: str
    language: str = "not-provided"

class InputLanguage(BaseModel):
    language: str = "not-provided"