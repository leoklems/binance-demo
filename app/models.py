from database import Base
from sqlalchemy import Column, String, Integer 

class User(Base):
	"""docstring for User"""
	__tablename__ = 'users'
	id = Column(Integer, primary_key = True)
	username = Column(String())
	email = Column(String)
	password = Column(String)

	def __init__(self, arg):
		super(User, self).__init__()
		self.arg = arg
