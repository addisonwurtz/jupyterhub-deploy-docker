# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG JUPYTERHUB_ADMIN
ARG DOCKER_NETWORK_NAME
ARG DOCKER_NOTEBOOK_IMAGE
ARG DOCKER_NOTEBOOK_DIR

FROM quay.io/jupyterhub/jupyterhub

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
RUN useradd -m myuser
USER myuser
ENV PATH="$PATH:/home/myuser/.local/bin"
ENV PATH="$PATH:/home/myuser/.local/lib"
# Install dockerspawner, nativeauthenticator
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install -r requirements.txt 
    #python3 -m pip install --no-cache-dir dockerspawner jupyterhub-nativeauthenticator


CMD ["sh", "-c", "jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py", "--port=${PORT}"]
