import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path


app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    filenames = os.listdir("static/patterns")
    if "pattern" in filenames[0]:
        return

    for i, filename in enumerate(filenames):
        os.rename(f"static/patterns/{filename}", f"static/patterns/pattern_{str(i)}.png")

app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
FILE_COUNT = len(os.listdir("static/patterns"))
@app.get("/")
async def get_fake_pattern(request: Request, response_model=HTMLResponse) -> dict:
    img_path = f"../static/patterns/pattern_{random.randint(0, FILE_COUNT)}.png"
    print(f"Image Path {img_path}")
    return TEMPLATES.TemplateResponse("index.html", {"request": request, "img_path": img_path})
