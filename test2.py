#中间件
from fastapi import FastAPI,Query,Depends
from sqlalchemy.ext.asyncio import create_async_engine
app=FastAPI()

@app.middleware("http")
async def middleware(request, call_next):
    print("中间件开始处理")
    response = await call_next(request)
    print("中间件结束处理")
    return response

@app.middleware("http")
async def middleware(request, call_next):
    print("中间件2开始处理")
    response = await call_next(request)
    print("中间件2结束处理")
    return response

@app.get("/")
async def root():
    return {"你好"}


#分页逻辑公用
async def common_parameters(
        skip:int = Query(0,ge=0)
        ,limit:int = Query(10,le=60)
):
    return {"skip":skip,"limit":limit}

@app.get("/new/newparameters")
async def new_parameters(commons = Depends(common_parameters)):
    return commons

@app.get("/user/userparameters")
async def user_parameters(commons = Depends(common_parameters)):
    return commons

