from langchain_community.utilities import SQLDatabase
import urllib



def get_db():
    password = "your password"
    encoded_password = urllib.parse.quote(password)
    mysql_uri = f'mysql+mysqlconnector://root:{encoded_password}@localhost:3306/cricket'
    db = SQLDatabase.from_uri(mysql_uri)
    return db

# for i in get_db().get_table_names():
#     print(i)