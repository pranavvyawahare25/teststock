#!/usr/bin/env bash
# This script installs Chrome and chromedriver for use with Selenium in the Render environment

# Exit on error
set -e

# Install Chrome
apt-get update
apt-get install -y wget gnupg2
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver (compatible with the Chrome version)
CHROME_VERSION=$(google-chrome --version | grep -oP '(?<=Google Chrome )[^\s]+')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Install Python requirements
pip install --upgrade pip
pip install -r requirements.txt

echo "Chrome and ChromeDriver setup complete" 