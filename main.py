# Depends lets us inject database session into our routes
from fastapi import FastAPI, HTTPException, Request, status, Depends
#from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# importing HTTPException twice because FastAPI exception is built ON TOP OF starlette and only handles a subset of all exception cases; starlette handles all cases
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import PostCreate, PostResponse, UserCreate, UserResponse
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session, session

import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)
# idempotent (safe to run multiple times)
# actually creates database tables! references models.py
# runs every time you start app

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media") # directory for user uploaded media

templates = Jinja2Templates(directory="templates") # creates a Jinja2Templates object that knows to look in the templates directory

# posts: list[dict] = [
#     {
#         "id": 1,
#         "author": "Mishtu",
#         "title": "hawa hawaii",
#         "content": "oh oui oui oui oui",
#         "date_posted": "March 25, 2026"
#     },
#     {
#         "id": 2,
#         "author": "Quirinus Quirrell",
#         "title": "TROLLLLLL in the dungeon",
#         "content": "thought you ought to know",
#         "date_posted": "April 1, 2026"
#     },
#     {
#       "id": 3,
#       "author": "Squirrell",
#       "title": "squirrel in the dungeon",
#       "content": "nut",
#       "date_posted": "April 12, 2026"  
#     }
# ]

## --------------------- HTML ROUTES --------------------- ##
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts") # don't want duplicate routes in schema
def home(request: Request): # jinja2 needs request parameter, will use when calling template
    #return f"<h1>{posts[0]['title']}<h1>"
    return templates.TemplateResponse(request, "home_finished.html", {"posts": posts, "title": "Home"})

@app.get("/posts/{post_id}", include_in_schema=False) # wtv comes after /posts/ is variable post_id
def post_page(request: Request, post_id: int): # wtv you get as post_id - verify it's an int
    # WHERE IS REQUEST VARIABLE COMING FROM?? okay apparently you don't need to pass in a request
    for post in posts:
        if post["id"] == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                request, 
                "post_finished.html", 
                {"post": post, "title":title},
                )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # if an API client makes an incorrect request, we want to return JSON
    # but if a user makes an incorrect request, we want to return an HTML page
    # => raise HTTPException which gets routed to exception handler
    # which sees this is not an API request, and returns an HTML template



## --------------------- API ROUTES --------------------- ##
@app.post(
        "/api/users",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED
        )
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    # get id and make user object
    # how to get new id based on what's in database? 

    # similarly how check username, email unique
    result = db.execute(
        select(models.User)
        .where(models.User.username == user.username)
    )

    # (per my understadning) returns as regular value instead of database row object type thing 
    existing_username = result.scalars().first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken!"
        )
    
    result = db.execute(
        select(models.User)
        .where(models.User.email == user.email)
    )

    existing_email = result.scalars().first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists!"
        )

    # add to users db
    # treating model as a class in usage; 
    new_user = models.User(
        username=user.username,
        email=user.email
    )
    db.add(new_user) # stages new user
    db.commit() # executes 
    db.refresh(new_user) # "reloads new user from database"? ok among other things: reloads the new_user obj from the database to get certain db-generated fields, like user_id for example

    # pydantic automatically converts new_user return to PostResponse as specified in our route
    return new_user

@app.get("/api/posts", response_model=list[PostResponse]) # for api
def get_posts():
    return posts 

# expose endpoint
@app.post(
        "/api/posts",
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED # this is new info
        )
def create_post(post: PostCreate):
    # get id and make post object
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "Tue April 7, 2026"
        }
    
    # add to posts list
    posts.append(new_post)
    return new_post

@app.get(
        "/api/posts/{post_id}",
        response_model=PostResponse) 
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

## --------------------- ERROR HANDLING --------------------- ##
# catches some exception errors raised automatically by FastAPI (ex. 404)
# as well as any exceptions you manually raise - like in /posts/post_id
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    # desired message
    message = (
        exception.detail
        if exception.detail
        else "An error occurred but we don't know what it is"
        )
    # if api response, return JSONResponse
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )
    # else return HTML template
    else:
        # for TemplateResponse pass in: request, layout name, context dict
        return templates.TemplateResponse(
            request,
            "error.html",
            {"status_code": exception.status_code,
             "message": message,
             "title": exception.status_code},
             status_code=exception.status_code
        )
    
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    # if api response, return JSONResponse
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            # this exception object (requestvalidationerror object) doesn't have .status_code
            # they are always 422 errors
            content={"detail": exception.errors()}
        )
    # else return HTML template
    else:
        # for TemplateResponse pass in: request, layout name, context dict
        return templates.TemplateResponse(
            request,
            "error.html",
            {"status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
             "message": "Invalid request, please try again.",
             "title": status.HTTP_422_UNPROCESSABLE_CONTENT},
             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )