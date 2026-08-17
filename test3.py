from datetime import datetime
from sqlalchemy import func, DateTime, String, Float,select,funcfilter
from fastapi import FastAPI,Query,Depends,HTTPException
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,async_session,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from pydantic import BaseModel

app=FastAPI()

#创建异步引擎
ASYNC_DATABASE_URL="mysql+aiomysql://root:111111@localhost:3306/FastAPI_test?charset=utf8mb4"
async_engine=create_async_engine(
    ASYNC_DATABASE_URL
    ,echo=True #可选,输出数据库日志
    ,pool_size=10 #可选,连接池活跃大小
    ,max_overflow=20 #可选,连接池最大溢出数
)

#定义模型类，基类+表模型类
#基类：创建时间，更新时间 书籍表：id，书名，作者，价格，出版社
class Base(DeclarativeBase):
    create_time:Mapped[datetime]=mapped_column(DateTime, insert_default=func.now(), default=func.now(), comment="创建时间")
    update_time:Mapped[datetime]=mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(), default=func.now(), comment="更新时间")


class Book(Base):
    __tablename__ = "book"
    id :Mapped[int]=mapped_column(primary_key=True,comment="书籍id")
    name:Mapped[str]=mapped_column(String(255),comment="书名")
    author:Mapped[str]=mapped_column(String(255),comment="作者")
    price:Mapped[float]=mapped_column(Float,comment="书籍价格")
    publisher:Mapped[str]=mapped_column(String(255),comment="出版社")

#建表
async def create_table():
    #获取异步引擎
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_table()

#查询图书接口 依赖注入
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine #绑定数据库引擎
    , class_=AsyncSession #指定会话类
    , expire_on_commit=False #可选,提交后不过期
)
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session #返回数据库会话给路由处理函数
            await session.commit() #提交事务
        except Exception as e:
            await session.rollback() #回滚事务
            raise e
        finally:
            await session.close() #关闭会话

@app.get("/book/getbooks")
async def get_books_list(db: AsyncSession = Depends(get_session)):
    #查询所有
    result = await db.execute(select(Book)) #查询返回ORM对象
    book = result.scalars().all()    #获取所有
    book = result.scalars().first() #获取第一个数据
    return book
    # #查询单条
    # book = await db.get(Book,3)  #根据主键获取单条
    # return book  #返回
#条件查询
@app.get("/book/getbooks/{book_id}")
async def getbook(book_id: int,db:AsyncSession = Depends(get_session)):
    result=await db.execute(select(Book).where(Book.id==book_id))
    book = result.scalar_one_or_none()
    return book

@app.get("/book/getbook/money")
async def get_money(db:AsyncSession = Depends(get_session)):
    result=await db.execute(select(Book).where(Book.price>=50))
    book_money=result.scalars().all()
    return book_money

#模糊查询
@app.get("/book/getbook/name")
async def get_author(db:AsyncSession = Depends(get_session)):
    ##like模糊查询%匹配任意，_匹配一个  需求：查询作者为吴*的书籍，或者价格大于50的书籍
    # result=await db.execute(select(Book).where(Book.author.like("吴%")))
    ## &|，与或非条件，需求：查询作者为吴*的书籍，或者价格大于50的书籍
    # result=await db.execute(select(Book).where((Book.author.like("吴%"))|(Book.price>=50)))
    #in,包含需求：书籍id列表，在id列表里面，返回
    id_list=[1,2,5,7]
    result = await db.execute(select(Book).where(Book.id.in_(id_list) ))
    book_author=result.scalars().all()
    return book_author

#聚合查询   func.方法名(模型类.属性)  需求：查询书籍价格的总和sum，平均值avg，最大值max，最小值min,行数 count
@app.get("/book/getbookmoney")
async def get_bookmoney(db:AsyncSession = Depends(get_session)):
    # result=await db.execute(select(func.count(Book.price)))
    # result=await db.execute(select(func.max(Book.price)))
    # result=await db.execute(select(func.sum(Book.price)))
    result = await db.execute(select(func.avg(Book.price)))
    book_money=result.scalar()
    return book_money

#分页查询
@app.get("/book/pagebook")
async def get_pagebook(
        page:int = Query(1, title="页码"),
        size:int = Query(2, title="每页数量"),
        db:AsyncSession = Depends(get_session)
):
    offset=(page-1)*size
    #offset跳过的记录数 limit每页记录数
    result=await db.execute(select(Book).offset(offset).limit(size))
    book_page=result.scalars().all()
    return book_page


class BookBase(BaseModel):
    id: int
    name: str
    author: str
    price: float
    publisher: str

#新增数据
@app.post("/book/addbook")
async def addbook(book:BookBase,db:AsyncSession = Depends(get_session)):
    book_obj=Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book

class BookUpdate(BaseModel):
    name: str
    author: str
    price: float
    publisher: str

#更新数据/修改/先查再改
@app.put("/book/updatebook/{bookid}")
async def updatebook(
        bookid:int,
        data:BookUpdate,
        db:AsyncSession = Depends(get_session)
):
    db_book=await db.get(Book,bookid)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="概书籍未找到，请重试"
        )
    db_book.name=data.name
    db_book.author=data.author
    db_book.price=data.price
    db_book.publisher=data.publisher
    await db.commit()
    return db_book

#删除图书
@app.delete("/book/deletebook/{bookid}")
async def deletebook(bookid:int,db:AsyncSession = Depends(get_session)):
    db_book=await db.get(Book,bookid)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="概书籍未找到，请重试"
        )
    await db.delete(db_book)
    await db.commit()
    return {"message":"删除成功"}
