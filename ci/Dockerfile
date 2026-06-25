# Optional, hermetic Jenkins agent image: Python + Chrome + Firefox.
#
# Not wired into the Jenkinsfile by default (it assumes a static agent that
# already has Chrome and Firefox installed). To use this instead, swap the
# top-level `agent any` in the Jenkinsfile for:
#
#   agent {
#       dockerfile {
#           dir 'ci'
#           additionalBuildArgs '--pull'
#       }
#   }
#
# which requires the Docker Pipeline plugin and a Docker-capable Jenkins agent.

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget gnupg ca-certificates \
        fonts-liberation libnss3 libxss1 libasound2 \
        libatk-bridge2.0-0 libgtk-3-0 libgbm1 \
        firefox-esr \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
