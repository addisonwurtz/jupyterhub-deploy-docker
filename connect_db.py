import os
import psycopg2
from heroku_tools import set_config_vars


DATABASE_URL = os.environ['DATABASE_URL']
HUB_APP_NAME = os.environ['APP_NAME']

db_connection = psycopg2.connect(DATABASE_URL, sslmode='require')

# Create a cursor object
cursor = db_connection.cursor()

# Query the 'app_config' table for the entry with the key 'PROXY_PORT'
query = "SELECT value FROM app_config WHERE key = %s;"
cursor.execute(query, ('PROXY_PORT',))

# Fetch the result
result = cursor.fetchone()

# Check if a value was found
if result:
    proxy_port = result[0]
    print(f"PROXY_PORT: {proxy_port}")
    set_config_vars(app_name=HUB_APP_NAME, config_vars={"PROXY_PORT": proxy_port})

else:
    print("PROXY_PORT not found in app_config table.")

# Close the cursor and connection
cursor.close()
db_connection.close()