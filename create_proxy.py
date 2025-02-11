import os
import requests


#TODO rename config vars for clarity
HUB_APP_NAME = os.getenv("APP_NAME")
HEROKU_AUTH_TOKEN = os.getenv("HEROKU_AUTH_TOKEN")
HUB_PORT = os.getenv("PORT")
PROXY_APP_NAME = os.getenv("PROXY_NAME")
PROXY_AUTH_TOKEN = os.getenv("PROXY_AUTH_TOKEN")
TEAM_NAME = os.getenv("TEAM_NAME")

heroku_url = "https://api.heroku.com/apps"
heroku_team_url = "https://api.heroku.com/teams/apps"

headers = {
    "Authorization": f"Bearer {HEROKU_AUTH_TOKEN}",
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
}

# Get app info using Heroku API
def get_app_info(app_name=None, region="us"):
    request_url = heroku_url + "/" + app_name

    print(f"Headers: {headers}")
    print(f"Request URL: {request_url}")
    
    response = requests.get(url=request_url, headers=headers) 
    
    if response.status_code == 200:
        return response.json() 
    else:
        print(f"Failed to get app info: {response.status_code}, {response.text}")
        return None


# Create a new Heroku app
def create_heroku_app(app_name=None, region="us"):
    payload = {"name": app_name, "region": region, "stack": "container"} if app_name else {"region": region}

    if TEAM_NAME is None:
        request_url = heroku_url
    else:
        request_url = heroku_team_url
        payload["team"] = TEAM_NAME

    response = requests.post(heroku_url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("App created successfully!")
        return response.json()  # Returns details of the new app
    elif response.status_code == 422 and response.json()["message"] == "Name jupyterhub-proxy-server is already taken":
        print("This app aready exists.")
        print("Getting app info...")
        return get_app_info(app_name=app_name)
    else:
        print(f"Failed to create app: {response.status_code}, {response.text}")
        return None

def set_config_vars(app_name, config_vars:dict):
    request_url = heroku_url + "/" + app_name + "/config-vars"
    response = requests.patch(url=request_url, headers=headers, json=config_vars)

    if response.status_code == 200:
        print("Config vars updated successfully")
        print(response.text)
    else:
        print(f"Failed to update config vars: {response.status_code}, {response.text}")
        return None

def get_permanent_token():
    token_request_url = "https://api.heroku.com/oauth/authorizations"
    token_request_headers = {
    "Authorization": f"Bearer {HEROKU_AUTH_TOKEN}",
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
    "description": "Permanent auth token for Heroku API",
    }
    response = requests.post(url=token_request_url, headers=token_request_headers)
    return response.json()
    
    if response.status_code == 200:
        print("Permantent authentication token successfully created")
        print(response.text)
    else:
        print(f"Failed to create auth token: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":

    # Check for permanent token and create if necessary
    #if HEROKU_PERMANENT_TOKEN is None:
    #token_info = get_permanent_token()
    #    print(token_info)
    #    print(token_info["token"])
    #    set_config_vars(app_name=HUB_APP_NAME, config_vars={"HEROKU_PERMANENT_TOKEN": token_info["token"]})

    # query for current app url
    print("Getting hub app info...")
    hub_info = get_app_info(app_name=HUB_APP_NAME)
    hub_url = hub_info["web_url"]
    print("Hub info: ")
    for item in hub_info:
        print(f"{item}: {hub_info[item]}")

    # create new app to run proxy 
    print("Getting proxy app info...")
    proxy_info = create_heroku_app(app_name=PROXY_APP_NAME)
    proxy_url = proxy_info["web_url"]
    print("Proxy info: ")
    for item in proxy_info:
        print(f"{item}: {proxy_info[item]}")

    # Set config variable for proxy_url in hub app
    set_config_vars(app_name=HUB_APP_NAME, config_vars={"PROXY_URL": proxy_url})

    # set config variables to hub address
    proxy_config_vars = {
                    "HUB_URL": hub_url, 
                    "HUB_PORT": HUB_PORT, 
                    "APP_NAME": PROXY_APP_NAME,
                    "PROXY_AUTH_TOKEN": PROXY_AUTH_TOKEN,
                    "HEROKU_AUTH_TOKEN": HEROKU_AUTH_TOKEN
                    } 
    set_config_vars(app_name=PROXY_APP_NAME, config_vars=proxy_config_vars)

    print("proxy git url: ")
    print(proxy_info["git_url"])
    # release proxy container

    # query for proxy uri and port

    # user proxy info to set config in hub

    # check that hub and proxy have connected

