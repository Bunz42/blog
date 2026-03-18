from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI() # initialize fastapi server
templates = Jinja2Templates(directory="templates") # tell fastapi where to find HTML files (in templates dir)

app.mount("/static", StaticFiles(directory="static"), name="static") # serve the css file

@app.get("/")
async def root():
    return RedirectResponse(url="/home")

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    articles_list = []

    # check if data folder exists to prevent crashes
    if os.path.exists("data"):

        # iterate through files in data directory (representing each article)
        for filename in os.listdir("data"):
            
            # only process files that end with .json (articles)
            if filename.endswith(".json"):

                # extract id from filename
                article_id = filename.replace(".json", "")

                # open file, load data, create id attribute once file has been parsed to a dict, then append the data to a list of articles
                with open(f'data/{filename}', 'r') as file:
                    article_data = json.load(file)

                    article_data["id"] = article_id

                    articles_list.append(article_data)

    articles_list.sort(key=lambda x: int(x["id"]), reverse=True) # sort articles in reverse order by id so that most recent articles are at the top

    # send the list of articles to the home.html template
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "articles": articles_list,
            "is_admin": False
        }
    )

# listen for traffic at routes /article/1, /article/2, etc.
@app.get("/article/{article_id}", response_class=HTMLResponse)
async def read_article(request: Request, article_id: int):
    
    # construct the file path based on the URL
    file_path = f"data/{article_id}.json"
    
    # try to open the JSON file
    try:
        with open(file_path, "r") as file:
            article_data = json.load(file)
            
    except FileNotFoundError:
        # if the file doesn't exist, send a basic 404 error page
        return HTMLResponse(content="<h1>Article not found</h1>", status_code=404)

    # merge the data with the HTML template and send it to the browser
    return templates.TemplateResponse(
        request=request, 
        name="article.html", 
        context={"article": article_data} # 'article' is the variable name used in the HTML
    )

@app.get("/new", response_class=HTMLResponse)
async def show_new_article_form(request: Request, blog_session: Optional[str] = Cookie(None)):
    if blog_session != "authenticated_admin":
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(request=request, name="new.html", context={"is_edit": False})

@app.post("/new", response_class=RedirectResponse)
async def publish_article(
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    blog_session: Optional[str] = Cookie(None)
):
    if blog_session != "authenticated_admin":
        return RedirectResponse(url="/login", status_code=303)

    # figure out the next available id to use for the new article
    existing_ids = []
    if os.path.exists("data"):
        for filename in os.listdir("data"):
            if filename.endswith(".json"):
                existing_ids.append(int(filename.replace(".json", "")))
    
    # if there are articles already, add 1 to the max id. If empty, start at id 1
    new_id = max(existing_ids) + 1 if existing_ids else 1
    
    # package the article form data into a python dictionary so we can write it to a new JSON file
    new_article_data = {
        "title": title,
        "date": date,
        "content": content
    }

    with open(f"data/{new_id}.json", 'w') as file:
        # json.dump to convert the python dict into properly formatted JSON
        json.dump(new_article_data, file, indent=4)
    
    # redirect the admin back to the home page so they can view their new post
    # standard status code for a redirect after a POST form submission is 303
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request, 
    blog_session: Optional[str] = Cookie(None) # make fastapi look for the authorized cookie session
):
    if blog_session != "authenticated_admin":
        return RedirectResponse(url="/login", status_code=303)

    articles_list = []

    if os.path.exists("data"):
        for filename in os.listdir("data"):
            if filename.endswith(".json"):
                article_id = filename.replace(".json", "")

                with open(f'data/{filename}', 'r') as file:
                    article_data = json.load(file)
                    article_data["id"] = article_id
                    articles_list.append(article_data)
    
    articles_list.sort(key=lambda x: int(x["id"]), reverse=True)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "articles": articles_list,
            "is_admin": True
        }
    )

@app.post("/delete/{article_id}", response_class=RedirectResponse)
async def delete_article(article_id: int, blog_session: Optional[str] = Cookie(None)):
    if blog_session != "authenticated_admin":
        return RedirectResponse(url="/login", status_code=303)
    
    file_path = f"data/{article_id}.json"

    # check if the file actually exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # redirect admin to the admin page: form POST redirect standard code 303
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/edit/{article_id}", response_class=HTMLResponse)
async def show_article_edit_form(request: Request, article_id: int, blog_session: Optional[str] = Cookie(None)):
    if blog_session != "authenticated_admin":
        return RedirectResponse(url="/login", status_code=303)
    
    file_path = f"data/{article_id}.json"

    if not os.path.exists(file_path):
        return HTMLResponse(content="<h1>Article not found</h1>", status_code=404)
    
    with open(file_path, 'r') as file:
        article_data = json.load(file)
        article_data["id"] = article_id 

    return templates.TemplateResponse(
        request=request, 
        name="new.html", 
        context={
            "is_edit": True,
            "article": article_data
        }
    )

@app.post("/edit/{article_id}", response_class=RedirectResponse)
async def edit_article(
    article_id: int,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    blog_session: Optional[str] = Cookie(None)
):
    if blog_session != "authenticated_admin":
        return RedirectResponse(url="/login", status_code=303)

    file_path = f"data/{article_id}.json"

    if os.path.exists(file_path):
        updated_data = {
            "title": title,
            "date": date,
            "content": content
        }

    with open (file_path, "w") as file:
        json.dump(updated_data, file, indent=4)
    
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login", response_class=RedirectResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    correct_username = os.getenv("ADMIN_USERNAME")
    correct_password = os.getenv("ADMIN_PASSWORD")

    if username == correct_username and password == correct_password: # temporary hard coded passwords
        # redirect the admin if they get the right username and password
        response = RedirectResponse(url="/admin", status_code=303)

        # plant a cookie session in the user's browser
        response.set_cookie(key="blog_session", value="authenticated_admin")
        return response
    
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid username or password!"}
    )

@app.get("/logout", response_class=RedirectResponse)
async def logout():
    # redirect the admin to the guest page if they logout
    response = RedirectResponse(url="/home", status_code=303)
    # delete the admin cookie session
    response.delete_cookie("blog_session")

    return response