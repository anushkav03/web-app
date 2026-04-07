from pydantic import BaseModel, ConfigDict, Field
# our models will all inherit from BaseModel

# our base model for posts
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

class PostCreate(PostBase):
    pass

# What our API returns
class PostResponse(PostBase):
    # by default Pydantic can read dictionaries
    # setting this to true will allow it to also
    # read attributes from objects (will be relevant 
    # when adding database)
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str