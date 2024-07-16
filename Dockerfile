FROM n8nio/n8n:latest

USER root

RUN apk update && \
    apk add --no-cache python3 py3-pip

RUN python3 -m venv /opt/venv

RUN mkdir -p /usr/local/scripts
COPY main.py /usr/local/scripts/main.py

RUN chmod +x /usr/local/scripts/main.py

RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install python-dotenv requests youtube-search-python google-api-python-client google-auth-oauthlib 

ENV PATH="/opt/venv/bin:$PATH"

USER node
