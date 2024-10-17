import encodings
from database import Base, engine
from models import User

try:
    Base.metadata.create_all(engine)
    print("table created successfully")
except Exception as e:
    print(f"Error creating table: {e}")

# To create the database, go to the console and type
# python create_db.py