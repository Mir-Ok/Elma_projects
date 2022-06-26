from environs import Env
from loguru import logger
from os import environ

logger = logger

env = Env()
env.read_env()

# environment
SECRET = environ.get('MONGO_URL')
SECRET2 = environ.get('PSQL_URL')

# SECRET = "mongodb://root:hXbRKJE0LCi1JVs9@192.168.32.101:27017/?authSource=admin&readPreference=primary&directConnection=true&ssl=false"
# SECRET2 = "postgresql://postgres:aus5TyxKZDO80NP8@192.168.32.101:5432/elma365?sslmode=disable"