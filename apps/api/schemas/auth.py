from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthUser(BaseModel):
    id: str
    name: str
    primary_image_tag: str | None = None


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class AuthMeResponse(BaseModel):
    id: str
    name: str
    primary_image_tag: str | None = None
