import os
import requests
import json


# Heroku API key (use the config var if running on Heroku)
HEROKU_API_KEY = os.getenv("API_KEY")
APP_NAME = os.getenv("APP_NAME")

heroku_url = "https://api.heroku.com/apps"

headers = {
    "Authorization": f"Bearer {HEROKU_API_KEY}",
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
}


def get_app_info(app_name=None, region="us"):
    request_url = heroku_url + "/" + app_name
    response = requests.get(request_url, headers=headers) 
    
    if response.status_code == 200:
        return response.json() 
    else:
        print(f"Failed to get app info: {response.status_code}, {response.text}")
        return None


# Create a new Heroku app
def create_heroku_app(app_name=None, region="us"):
    payload = {"name": app_name, "region": region} if app_name else {"region": region}
    
    response = requests.post(heroku_url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("App created successfully!")
        return response.json()  # Returns details of the new app
    else:
        print(f"Failed to create app: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":

    # query for current app url
    hub_info = get_app_info(app_name=APP_NAME)
    hub_url = hub_info["web_url"]

    # create new app to run proxy 
    # TODO make proxy app name ENV var
    proxy_info = create_heroku_app(app_name="jupyterhub-proxy-server")

    # set config variables to hub address

    # release proxy container

    # query for proxy uri and port

    # user proxy info to set config in hub

    # check that hub and proxy have connected

