from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def load_json_data(filename: str):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

@app.get("/test", response_class=JSONResponse)
def get_apis():
    data = load_json_data("apis.json")
    return JSONResponse(content=data)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("dummy.html", {"request": request})
