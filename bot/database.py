from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import requests

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)


class ProductQuery(Base):
    __tablename__ = 'product_queries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_code = Column(String)
    query_time = Column(DateTime)

    user = relationship('User')


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    product_code = Column(String, unique=True)
    name = Column(String)
    price = Column(Float)
    rating = Column(Float)
    quantity = Column(Integer)

    queries = relationship('ProductQuery', back_populates='product')


# Замените 'postgresql://user:password@localhost/dbname' на ваши реальные данные для подключения к базе данных
engine = create_engine('postgresql://user:password@localhost/dbname')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def save_product_query(user_id, product_code):
    session = Session()
    query = ProductQuery(
        user_id=user_id, product_code=product_code, query_time=datetime.now())
    session.add(query)
    session.commit()
    session.close()


def get_product_info(product_code):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={
        product_code}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        product_info = f"Название: {data['name']}\nАртикул: {data['code']}\nЦена: {
            data['price']}\nРейтинг: {data['rating']}\nКоличество на складах: {data['quantity']}"
        return product_info
    else:
        return "Товар не найден."
