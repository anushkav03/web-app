from fastapi import FastAPI, Request
#from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates") # creates a Jinja2Templates object that knows to look in the templates directory

posts: list[dict] = [
    {
        "id": 1,
        "author": "Mishtu",
        "title": "I am cool and smart",
        "content": "And capable of learning new things, and I'm gonna do cool things in life",
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

@app.get("/", include_in_schema=False) # html for humans
@app.get("/posts", include_in_schema=False) # don't want duplicate routes in schema
def home(request: Request): # jinja2 needs request parameter, will use when calling template
    #return f"<h1>{posts[0]['title']}<h1>"
    return templates.TemplateResponse(request, "home_finished.html", {"posts": posts, "title": "Home"})


@app.get("/api/posts") # for api
def get_posts():
    return posts