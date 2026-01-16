from pydantic import BaseModel

class login(BaseModel):
    email :str
    
class otp_verify(BaseModel):
    email :str
    otp :str

class google_login(BaseModel):
    credential: str