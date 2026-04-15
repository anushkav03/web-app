from pydantic import BaseModel, ConfigDict, Field, EmailStr
# our models will all inherit from BaseModel

from datetime import datetime

class UserBase(BaseModel):
    # fields should be what is shared between UserCreate and UserResponse
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120) #EmailStr automatically validates correctness

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True) # see comments in PostResponse
 
    id: int

    # why are we returning these?
    # probably when we call this (?) on main, we can pass this str info
    # into an html template
    image_file: str | None
    # note image_path is @property in the User model. model_config lets
    # pydantic read it as an attribute so we don't have to recompute file path 
    image_path: str


# our base model for posts
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    # comes from relationship now
    #author: str = Field(min_length=1, max_length=50)

class PostCreate(PostBase):
    user_id: int # temporary for testing
    # eventually (after adding authentication) user_id will be
    # automatically grabbed from session and passed in

# What our API returns
class PostResponse(PostBase):
    # by default Pydantic can read dictionaries
    # setting this to true will allow it to also
    # read attributes from objects (will be relevant 
    # when adding database)
    model_config = ConfigDict(from_attributes=True)

    id: int
    # why are we returning user_id? 
    user_id: int
    date_posted: datetime
    # api response will give nested JSON with full 
    # UserReponse details - email, username etc
    author: UserResponse