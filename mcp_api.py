# local imports
import config

# standard library imports
import json

# third party imports
import requests


class MyCarrierPacketsApi:
    """
    Class for using MyCarrierPackets API

    Class based on: https://medium.com/better-programming/how-to-refresh-an-
    access-token-using-decorators-981b1b12fcb9
    """

    def __init__(self):
        """
        Attributes:
            self._api_username (str): user name to log into api that is
                retrieved from config file
            self._api_password (str): password to log into api that is
                retrieved from config file
        """
        self._api_username = config.api_username
        self._api_password = config.api_password

    def get_bearer_access_token(self):
        """
        This function is to get a new mycarrierpackets access token

        :return: access_token
        """
        print('Attempting to get new token.')

        try:
            url = 'https://api.mycarrierpackets.com/token'
            payload = f'grant_type=password&username={self._api_username}&password={self._api_password}'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            response = requests.request('POST', url, headers=headers, data=payload)

            # optional: raise exception for status code
            response.raise_for_status()
        # catch any exception that may be caused such as unable to access api
        except Exception as e:
            print(e)
            exit()
            # return None so it can be handled.
            return None
        else:
            # gets the api response text then save to json file and returns
            # the variable data (which is just response.text)
            data = response.text
            with open('token_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data


if __name__ == '__main__':
    pass
