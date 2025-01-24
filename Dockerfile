# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG PORT
FROM quay.io/jupyterhub/jupyterhub

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
RUN useradd -m myuser
USER myuser
# Install dockerspawner, nativeauthenticator
# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    jupyterhub-nativeauthenticator

CMD ["sh", "-c", "jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py", "--port=${PORT}"]
