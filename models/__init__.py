from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from settings import DB_URI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.dialects.mysql.pymysql import MySQLDialect_pymysql


# 1. 自定义方言，修复 ping 方法参数
class CustomMySQLAsyncDialect(MySQLDialect_pymysql):
    def do_ping(self, dbapi_connection):
        try:
            # 补充 aiomysql 强制要求的 reconnect 参数
            dbapi_connection.ping(reconnect=True)
            return True
        except Exception:
            return False

# 数据库连接引擎
engine = create_async_engine(
    DB_URI,
    # 将输出所有执行SQL的日志
    echo=True,
    # 连接池大小
    pool_size=10,
    # 允许连接池最大的连接数
    max_overflow=20,
    # 获得连接超时时间
    pool_timeout=10,
    # 回收连接时间
    pool_recycle=3600,
    # 连接前是否预检查
    pool_pre_ping=True,
    dialect=CustomMySQLAsyncDialect(),  # 启用自定义方言


)

# 会话工厂
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    #是否在查找之前执行flush操作
    autoflush=True,
    # 是否在执行commit操作后Session就过期
    expire_on_commit=False,

)



class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        # ix : index, 索引
        "ix": 'ix_%(column_0_label)s',
        # uq : unique,唯一约束
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        # ck : Check, 检查约束
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        # fk ： Foreign Key,外键约束
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        # pk : Primary Key， 主键约束
        "pk": "pk_%(table_name)s"
    })

# 把定义好的user进行导入
from . import user