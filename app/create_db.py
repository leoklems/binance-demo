from databses import Base, engine
from models import User

Base.metadata.create_all(bind=encoding)

# To create the database, go to the console and type
# python create_db.py