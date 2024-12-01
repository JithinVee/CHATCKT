from langchain_community.utilities import SQLDatabase
import urllib

def get_db():
    password = "your password"
    encoded_password = urllib.parse.quote(password)
    # mysql_uri = f'mysql+mysqlconnector://root:{encoded_password}@/cloudsql/winged-yeti-443001-j1:us-central1:mysql-instance-shopalyst/crickshopalyst'
    mysql_uri = f"mysql+mysqlconnector://root:{encoded_password}@34.42.186.42:3306/crickshopalyst"
    db = SQLDatabase.from_uri(mysql_uri)
    return db

# for i in get_db().get_table_names():
#     print(i)