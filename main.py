from fastapi import FastAPI, HTTPException, Request, status
#from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# importing HTTPException twice because FastAPI exception is built ON TOP OF starlette and only handles a subset of all exception cases; starlette handles all cases
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates") # creates a Jinja2Templates object that knows to look in the templates directory

posts: list[dict] = [
    {
        "id": 1,
        "author": "Mishtu",
        "title": "hawa hawaii",
        "content": "oh oui oui oui oui",
        "date_posted": "March 25, 2026"
    },
    {
        "id": 2,
        "author": "Quirinus Quirrell",
        "title": "TROLLLLLL in the dungeon",
        "content": "thought you ought to know",
        "date_posted": "April 1, 2026"
    }
]

## HTML ROUTES ##
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



## API ROUTES ##
@app.get("/api/posts") # for api
def get_posts():
    return posts 

@app.get("/api/posts/{post_id}") 
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

## ERROR HANDLING ##
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