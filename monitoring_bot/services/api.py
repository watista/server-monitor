#!/usr/bin/python3

import requests
import json
import time
import traceback
from config import config
from services.logger import logger

class Api:

    def __init__(self, functions):

        # Set default values
        self.function = functions
        self.token = 0
        self.token_timestamp = 0
        self.base_url = f"http://{config.api_address}:{str(config.api_port)}"


    def token_check(self):

        # Check if token is valid
        if not (self.token_timestamp + 3500) >= round(time.time()):

            # Get new token
            # payload = json.dumps({"username": config.api_user,"password": config.api_password})
            payload = f"username={config.api_user}&password={config.api_password}"

            try:
                # Make the request
                response = requests.request("POST", f"{self.base_url}/api/auth/token", headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=payload)
                if not response.ok:
                    logger.error(f"Error while fetching new API token. Error: {response.status_code} - {response.reason}")
                    return None

            except Exception as e:
                logger.error(f"Error during get API token. Error: {str(e)}")
                logger.debug(f"Stack trace:\n{traceback.format_exc()}")
                return None

            # Write token
            token = json.loads(response.text)
            self.token = token["access_token"]
            self.token_timestamp = round(time.time())

        # Return success
        return True


    def get(self, path: str):

        # Check if token is valid, otherwise renew
        if not self.token_check():
            logger.warning("Token check failed, couldn't verify or refresh token")
            return None

        # Make the request
        try:
            response = requests.request("GET", f"{self.base_url}/api/status/{path}", headers={'Authorization': f'Bearer {self.token}'}, data={})

            if not response.ok:
                logger.error(f"Not OK response for Api GET, path {path}. Error: {response.status_code} - {response.reason} - {response.text}")
                return None

            return response

        except Exception as e:
            logger.error(f"Failed to get info for path {path}. Error: {str(e)}")
            logger.debug(f"Stack trace:\n{traceback.format_exc()}")
            return None
