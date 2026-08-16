from sys import path

from click import Path
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse,FileResponse
app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

#注册 用户姓名和密码
class User(BaseModel):
    username: str = Field(default="张三"  , min_length=2, max_length=5, description="用户名")
    password: str = Field("123456", min_length=8, max_length=50, description="密码")
@app.post("/register")
async def register(user: User):
    return {"username": user.username, "password": user.password}


#图书管理
class Book(BaseModel):
    bookname:str = Field(...,min_length=2,max_length=20)
    bookauthor:str = Field(min_length=2,max_length=10)
    bookfrom:str = Field(default="中国出版社")
    bookprice:float = Field(...,ge=0)

@app.post("/bookmessage")
async def bookst(book:Book):
    return {"bookname": book.bookname, "bookauthor": book.bookauthor, "bookfrom": book.bookfrom, "bookprice": book.bookprice}

@app.get("/html", response_class=HTMLResponse)
async def read_html():
    return "<h1>一个HTML返回值</h1>"

@app.get("/files")
async def read_files():
    path="./files/d6fd091b2c6aef1544466bfada79cbd2_20669_518_477.jpg"
    return FileResponse(path)

#定义一个新闻接口，包含ia，tile，content
class News(BaseModel):
    id:int
    title:str
    content:str

@app.get("/news/{id}",response_model=News)
async def get_news(id:int):
    id_list=[1,2,3,4,5,6]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="出现异常，News not found")
    return {"id": id, "title": "新闻标题", "content": "新闻内容"}

