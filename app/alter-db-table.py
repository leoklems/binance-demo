from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker

# Define the database URI
conn_str = "sqlite:///my.db"
engine = create_engine(conn_str, echo=True)

# Create a new metadata instance
metadata = MetaData()

# Define the old users table
old_users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True),
    Column('email', String, unique=True)
)

# Define the new users table with the password_hash field
new_users_table = Table('new_users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True),
    Column('email', String, unique=True),
    Column('password_hash', String)  # New field for storing hashed passwords
)

# Create the new users table
metadata.create_all(engine)

# Start a session
Session = sessionmaker(bind=engine)
session = Session()

# Copy data from the old users table to the new users table
with engine.connect() as connection:
    # Select all data from the old users table
    old_users = connection.execute(old_users_table.select()).fetchall()
    
    # Insert data into the new users table
    for user in old_users:
        connection.execute(new_users_table.insert().values(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=None  # Set to None or a default value
        ))

# Drop the old users table
old_users_table.drop(engine)

# Rename the new users table to the original name
connection.execute("ALTER TABLE new_users RENAME TO users;")

# Commit the session
session.commit()
session.close()

print("Password field added successfully.")