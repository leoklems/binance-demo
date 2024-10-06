from database import database
from sqlalchemy import Column, String, Integer 






 class User(object):
 	"""docstring for User"""
 	__tablename__ = "users"
 	id = Column(Integer, primary_key = True)
 	username = Column(String())
 	def __init__(self, arg):
 		super(User, self).__init__()
 		self.arg = arg
