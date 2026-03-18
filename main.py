from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI() # initialize fastapi server
templates = Jinja2Templates(directory="templates") # tell fastapi where to find HTML files (in templates dir)

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
        context={"articles": articles_list}
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
async def show_new_article_form(request: Request):
    return templates.TemplateResponse(request=request, name="new.html")

@app.post("/new", response_class=RedirectResponse)
async def publish_article(
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...)
):
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
    return RedirectResponse("/home", status_code=303)