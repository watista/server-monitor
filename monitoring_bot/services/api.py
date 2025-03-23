#!/usr/bin/python3

import aiohttp
import json
import time
import traceback
from typing import Optional, Union, Dict, Any
from config import config
from services.logger import logger


class Api:
    """
    Class responsible for API requests.
    """

    def __init__(self, functions) -> None:
        """
        Initializes the API client.
        :param functions: An object containing helper functions.
        """
        self.function = functions
        self.token = 0
        self.token_timestamp = 0
        self.base_url = f"http://{config.api_address}:{str(config.api_port)}"

    async def token_check(self) -> Optional[bool]:
        """
        Checks if the current token is valid, otherwise fetches a new one.
        :return: True if the token is valid or successfully refreshed, None if an error occurs.
        """
        if not (self.token_timestamp + 1500) >= round(time.time()):

            # Get new token
            payload = f"username={config.api_user}&password={config.api_password}"

            try:
                # Make the request
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.base_url}/api/auth/token", data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}) as response:
                        if not response.ok:
                            logger.error(f"Error while fetching new API token. Error: {response.status} - {response.reason}")
                            return None

                        # Write token
                        token = await response.json()
                        self.token = token["access_token"]
                        self.token_timestamp = round(time.time())

            except Exception as e:
                logger.error(f"Error during get API token. Error: {str(e)}")
                logger.debug(f"Stack trace:\n{traceback.format_exc()}")
                return None

        # Return success
        return True

    async def get(self, path: str) -> Optional[Union[Dict[str, Any], list]]:
        """
        Performs a GET request to the specified API endpoint.
        :param path: The API path to request.
        :return: The JSON response as a dictionary or list, or None if an error occurs.
        """
        if not await self.token_check():
            logger.warning(
                "Token check failed, couldn't verify or refresh token")
            return None

        # Make the request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/status/{path}", headers={'Authorization': f'Bearer {self.token}'}) as response:
                    if not response.ok:
                        logger.error(f"Not OK response for API GET, path: /{path}. Error: {response.status} - {response.reason} - {response.text}")
                        return None

                    return await response.json()

        except Exception as e:
            logger.error(f"Failed to get info for path {path}. Error: {str(e)}")
            logger.debug(f"Stack trace:\n{traceback.format_exc()}")
            return None
