import os
import requests

# Connect to Heroku Platform API:

# Heroku API key (use the config var if running on Heroku)
HEROKU_API_KEY = os.getenv("HEROKU_API_KEY")

def get_hostname(app_name=None):
    pass

def get_port(app_name=None):
    pass

# Create a new Heroku app
def create_heroku_app(app_name=None, region="us"):
    url = "https://api.heroku.com/apps"
    headers = {
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3",
        "Content-Type": "application/json",
    }
    payload = {"name": app_name, "region": region} if app_name else {"region": region}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("App created successfully!")
        return response.json()  # Returns details of the new app
    else:
        print(f"Failed to create app: {response.status_code}, {response.text}")
        return None


# Example usage
new_app = create_heroku_app(app_name="my-new-app")
print(new_app)

if __name__ == "__main__":

    # connect to heroku api

    # query for current app uri and port

    # create new app to run proxy 

    # set config variables to hub address

    # release proxy container

    # query for proxy uri and port

    # user proxy info to set config in hub

    # check that hub and proxy have connected

    pass
