from datetime import datetime
from unittest import result

from select import select
from sqlalchemy import func, DateTime, String, Float
from fastapi import FastAPI,Query,Depends
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,async_session,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

app=FastAPI()

#创建异步引擎
ASYNC_DATABASE_URL="mysql+aiomysql://root:111111@localhost:3306/FastAPI_test?charset=utf8"
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
    , class_=async_session #指定会话类
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
    #查询
    result = await db.execute(select(Book))
    return result.scalars().all()


