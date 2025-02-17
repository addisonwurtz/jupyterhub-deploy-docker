import os
import requests


#TODO rename config vars for clarity
HUB_APP_NAME = os.getenv("APP_NAME")
HUB_PORT = os.getenv("HUB_PORT")
PROXY_APP_NAME = os.getenv("PROXY_NAME")
PROXY_PORT = os.getenv("PORT")
HEROKU_AUTH_TOKEN = os.getenv("HEROKU_AUTH_TOKEN")
PROXY_AUTH_TOKEN = os.getenv("PROXY_AUTH_TOKEN")
#PROXY_BLOB = os.getenv("PROXY_BLOB")
#TEAM_NAME = os.getenv("TEAM_NAME")

heroku_url = "https://api.heroku.com/apps"
#heroku_team_url = "https://api.heroku.com/teams/apps"

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
    payload = {"name": app_name, "region": region, "stack": "container"} if app_name else {"region": region}

    # TODO remove team name logic
    if TEAM_NAME is None or TEAM_NAME == "":
        print("No team name.")
        request_url = heroku_url
    else:
        print(f"Team name is {TEAM_NAME}")
        request_url = heroku_team_url
        payload["team"] = TEAM_NAME

    response = requests.post(request_url, headers=headers, json=payload)
    
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

    # Set PROXY_PORT config var in hub app
    print("Setting PROXY_PORT config variable in jupyterhub app...")
    set_config_vars(app_name=HUB_APP_NAME, config_vars={"PROXY_PORT": PROXY_PORT})