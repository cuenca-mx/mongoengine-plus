from mongoengine import connect

DATABASE_URI = 'mongomock://localhost:27017/db'
connect(host=DATABASE_URI)
