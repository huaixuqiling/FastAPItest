from fastapi import FastAPI,Path,Query

#创建Fastapi实例
app = FastAPI()

#uvicorn main:app --reload
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


#访问/helllo 返回结果msg:"你好，Fastapi"
@app.get("/hello")
async def hello():
    return {"message":"你好，FastApi"}

@app.get("/user/hello")
async def user_hello():
    return {"message":"我正在学习FastApi......"}

@app.get("/book/{id}")
async def get_book(id:int = Path(...,gt=0,lt=101,description="这是对书本数的描述1~100")):
    return {"id":id,"message":f"这是拿到的第{id}本书"}

@app.get("/user/{id}")
async def getid(id:str = Path(...,min_length=3,max_length=5,description="这是对用户id的描述")):
    return {"id":id,"用户名称":f"普通用户 {id}"}

@app.get("/book/writer/{writer}")
async def get_writer(writer: str = Path(...,min_length=3,max_length=5,description="这是对作者名称的描述")):
    return {"writer":writer,"message":f"这是拿到的作者是{writer}"}

@app.get("/newsid/{id}")
async def get_id(id:int = Path(...,ge=1,le=100,description="新闻id，在1~100之间")):
    return {"id":id}
@app.get("/newstype/{type}")
async def get_type(type:str = Path(...,max_length=10,min_length=2,description="新闻的类型，在2~10之间")):
    return {f"新闻的类型为:{type}"}

#查询新闻 skip：分页，跳过的记录数 limit：返回的记录数
@app.get("/news/news_list")
async def get_news(
        skip:int =Query(...,ge=0,le=100,description="这是对跳过记录数的描述")
        ,limit:int = Query(10,ge=1,le=100,description="这是对返回记录数的描述")
):
    return {"skip":skip,"limit":limit}

#练习 图书查询
@app.get("/books/find_book")
async def findbook(booktype : str = Query("Python开发",min_length=5,max_length=255,description="图书分类的默认值")
                   ,bookprice :int = Query(...,gt=50,le=100,description="图书价格的默认值")
                    ):
    return {"图书分类":booktype,"图书价格":bookprice}