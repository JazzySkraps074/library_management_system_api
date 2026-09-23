from pydantic import BaseModel, ConfigDict, EmailStr, Field

model_config = ConfigDict(str_strip_whitespace=True)

class BookBase(BaseModel):
    title: str = Field(min_length=1,max_length=200)
    author: str = Field(min_length=1,max_length=120)
    isbn: str
    published_year: int = Field(ge=1450, le=2026)
    member_id: int

class BookResponse(BaseModel):
    id: int
    title: str = Field(min_length=1,max_length=200)
    author: str = Field(min_length=1,max_length=120)
    isbn: str
    published_year: int
    member_id: int

class MemberBase(BaseModel):
    name: str = Field(min_length=1,max_length=120)
    email: EmailStr
    membership_id: str
    phone: str

class MemberResponse(BaseModel):
    id: int
    name: str = Field(min_length=1,max_length=120)
    email: EmailStr
    membership_id: str
    phone: str