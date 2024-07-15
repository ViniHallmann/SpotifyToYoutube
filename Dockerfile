FROM n8nio/n8n:latest

USER root

RUN apk update && \
    apk add --no-cache python3 py3-pip

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install python-dotenv requests youtube-search-python google-api-python-client google-auth-oauthlib 

COPY main.py /usr/local/bin/main.py

ENV PATH="/opt/venv/bin:$PATH"

USER node
