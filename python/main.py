import os
import json
import requests
import hashlib
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def get_items():
    with open("items.json", "r") as f:
        items = json.load(f)
    return items

@app.get("/items/{item_id}")
def get_item_by_id(item_id: int):
    with open("items.json", "r") as f:
        items = json.load(f)
    item_list = items["items"]
    return item_list[item_id]

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    logger.info(f"Receive item: {name}, {category}, {image}")

    # 画像ファイルの読み込み
    with open(image, "rb") as f:
        image_data = f.read()
    # sha256ハッシュ値の計算
    hash_object = hashlib.sha256()
    hash_object.update(image_data)
    hex_dig = hash_object.hexdigest()

    # ファイルの保存
    with open(f"images/{hex_dig}.jpg", "wb") as f:
        f.write(image_data)

    item = {"name": name, "category": category, "image_filename": f"{hex_dig}.jpg"}
    with open("items.json", "r") as f:
        items = json.load(f)
    items["items"].append(item)
    with open("./items.json", "w") as f:
        json.dump(items, f)

    return {"message": f"item received: {name}"}

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)