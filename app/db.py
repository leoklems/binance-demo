from databases import Session, engine
from models import User

local_session = Session(bind=engine)

def get_all_users():
	return local_session.query(User).all()

def create_user(user_data):

	new_user = User(**user_data)

	try:
		local_session.add(new_user)
		local_session.commit()
	except:
		local_session.rollback()
	finally:
		local_session.close()