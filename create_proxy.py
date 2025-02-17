import os
import requests


#TODO rename config vars for clarity
HUB_APP_NAME = os.getenv("APP_NAME")
HEROKU_AUTH_TOKEN = os.getenv("HEROKU_AUTH_TOKEN")
HUB_PORT = os.getenv("PORT")
PROXY_APP_NAME = os.getenv("PROXY_NAME")
PROXY_AUTH_TOKEN = os.getenv("PROXY_AUTH_TOKEN")
PROXY_BLOB = os.getenv("PROXY_BLOB")
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

    response = requests.get(url=request_url, headers=headers) 
    
    if response.status_code == 200:
        return response.json() 
    else:
        print(f"Failed to get app info: {response.status_code}, {response.text}")
        return None


# Create a new Heroku app
def create_heroku_app(app_name=None, region="us"):
    payload = {"name": app_name, "region": region, "stack": "container"}
    # payload = {"name": app_name, "region": region, "stack": {"name": "container"}}if app_name else {"region": region}

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
        print(f"Config vars for {app_name} updated successfully")
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
    
    if response.status_code == 200:
        print("Permantent authentication token successfully created")
        print(response.text)
        return response.json()
    else:
        print(f"Failed to create auth token: {response.status_code}, {response.text}")
        return None


def create_blob_source(app_name, blob_path):
    blob_source_request_url = heroku_url + f"/{app_name}/sources"
    blob_put_headers = { 
                        "Accept": "application/vnd.heroku+json; version=3",
                        "Content-Type": ""
                        # "Content-Type": "--data-binary @source.tgz"
                        }
    response = requests.post(url=blob_source_request_url, headers=headers)

    if response.status_code == 201:
        print("Blob source url successfully created")
        source_url = response.json()["source_blob"] 

        print("Uploading source blob...")
        response = requests.put(url=source_url["put_url"], headers=blob_put_headers, data=open(blob_path, 'rb')) 

        if response.status_code == 200:
            print("Blob source successfully created")
            return source_url["get_url"] 
        else:
            print(f"Failed to create blob source: {response.status_code}, {response.text}")
            return None
    else:
        print(f"Failed to create blob source url: {response.status_code}, {response.text}")
        return None


def create_build(app_name, source_blob={"checksum": None, "url": None, "version": None, "version_description": None }):
    build_request_url = heroku_url + f"/{app_name}/builds"

    response = requests.post(url=build_request_url, headers=headers, json=source_blob)
    if response.status_code == 201:
        print(f"{app_name} build successfully created")
        print("Response: ") 
        print(response.text)
    else:
        print(f"Failed to create build for {app_name}: {response.status_code}, {response.text}")


if __name__ == "__main__":

    # TODO helpful error for expired tokens
    # Check for permanent token and create if necessary
    #if HEROKU_PERMANENT_TOKEN is None:
    #token_info = get_permanent_token()
    #    print(token_info)
    #    print(token_info["token"])
    #    set_config_vars(app_name=HUB_APP_NAME, config_vars={"HEROKU_PERMANENT_TOKEN": token_info["token"]})

    # query for current (hub) app url
    print("Getting hub app info...")
    hub_info = get_app_info(app_name=HUB_APP_NAME)
    print("Hub info: ")
    for item in hub_info:
        print(f"{item}: {hub_info[item]}")

    # create new app to run proxy 
    # Push proxy app blob to heroku source url
    print("Creating source for proxy app blob...")
    #blob_get_url = create_blob_source(app_name=PROXY_APP_NAME, blob_path=PROXY_BLOB)
    blob_get_url = create_blob_source(app_name=HUB_APP_NAME, blob_path=PROXY_BLOB)
    proxy_setup = requests.post(url="https://api.heroku.com/app-setups", headers=headers, json={"app": {"name": "jupyterhub-proxy-server", "stack": "container"}, "source_blob": {"url": blob_get_url}}).json()
    for each in proxy_setup:
        print(f"{each}: {proxy_setup[each]}")

    print("Getting proxy app info...")
    #proxy_info = create_heroku_app(app_name=PROXY_APP_NAME)

    proxy_info = get_app_info(app_name=PROXY_APP_NAME)
    print("Proxy info: ")
    for item in proxy_info:
        print(f"{item}: {proxy_info[item]}")

    print("Saving proxy info to hub...")
    # Set config variable for proxy_url in hub app
    # TODO may not need git url now that I am creating builds 
    set_config_vars(app_name=HUB_APP_NAME, config_vars={
        "PROXY_WEB_URL": proxy_info["web_url"],
        "PROXY_GIT_URL": proxy_info["git_url"]})

    # set config variables to hub address
    print("Saving app info to proxy app...")
    proxy_config_vars = {
                    "HUB_WEB_URL": hub_info["web_url"], 
                    "HUB_PORT": HUB_PORT, 
                    "APP_NAME": PROXY_APP_NAME,
                    "PROXY_WEB_URL": proxy_info["web_url"],
                    "PROXY_AUTH_TOKEN": PROXY_AUTH_TOKEN,
                    "HEROKU_AUTH_TOKEN": HEROKU_AUTH_TOKEN
                    } 
    set_config_vars(app_name=PROXY_APP_NAME, config_vars=proxy_config_vars)

    # Push proxy app blob to heroku source url
    #print("Creating source for proxy app blob...")
    #blob_get_url = create_blob_source(app_name=PROXY_APP_NAME, blob_path=PROXY_BLOB)
     
    # Create build for proxy server app
    #print("Attempting to create proxy server build...")
    #proxy_build = create_build(app_name=PROXY_APP_NAME, source_blob={"source_blob": {"url": blob_get_url}})
    
    # Make myself collaborator on app
    # TODO remove this when done with development
    response = requests.post(url=f"{heroku_url}/{PROXY_APP_NAME}/collaborators", headers=headers, json={"user": "awurtz@salesforce.com"})
    print("Add collaborator response: ")
    print(response.json())
    # Transfer proxy app to me
    # TODO remove this when done with development
    response = requests.post(url="https://api.heroku.com/account/app-transfers", headers=headers, json={"app": "jupyterhub-proxy-server", "recipient": "awurtz@salesforce.com", "silent": False})
    print("App transfer response:") 
    print(response.json())
    print("Proxy server is running...") 



