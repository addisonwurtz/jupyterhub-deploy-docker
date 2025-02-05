# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG JUPYTERHUB_ADMIN
ARG DOCKER_NETWORK_NAME
ARG DOCKER_NOTEBOOK_IMAGE
ARG DOCKER_NOTEBOOK_DIR

FROM quay.io/jupyterhub/jupyterhub

COPY start_hub jupyterhub_config.py create_proxy.py /srv/jupyterhub/
# COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

# Create non-root user
# RUN useradd -m myuser
# USER myuser

# Add non-root user's directories to PATH
# ENV PATH="$PATH:/home/myuser/.local/bin:/home/myuser/.local/lib/python3.10"

# Install dockerspawner, nativeauthenticator
RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir dockerspawner jupyterhub-nativeauthenticator
# RUN python3 -m pip install --no-cache-dir sudospawner jupyterhub-nativeauthenticator

# TODO: update CMD to reflect heroku.yml file
CMD ["sh", "-c", "jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py", "--port=${PORT}"]
