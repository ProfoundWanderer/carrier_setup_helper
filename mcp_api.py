# local imports
import config

# standard library imports
import json
import time

# third party imports
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait


class MyCarrierPacketsApi:
    """
    Class for using MyCarrierPackets API

    Class based on: https://medium.com/better-programming/how-to-refresh-an-access-token-using-decorators-981b1b12fcb9
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
        self._web_email = config.web_email
        self._web_password = config.web_password

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

    def send_inv(self, dot_number, invite_address):
        geckodriver_path = './geckodriver-v0.26.0-win64/geckodriver.exe'
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(executable_path=geckodriver_path, firefox_options=options)

        try:
            driver.get('https://mycarrierpackets.com/RegisteredCustomer/SendCarrierPacket')

            driver.find_element_by_id('UserName').send_keys(self._web_email)
            driver.find_element_by_id('Password').send_keys(self._web_password)
            driver.find_element_by_css_selector('input.btn').click()

            driver.find_element_by_id('DotNumber').send_keys(dot_number)
            driver.find_element_by_id('btnSearchDotNumber').click()

            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-danger'))).click()

            driver.find_element_by_css_selector('button.btn-primary:nth-child(1)').click()
            driver.save_screenshot('C:/Users/derrick.freeman/Downloads/1.png')


            driver.find_element_by_link_text('EMAIL NOT LISTED HERE')



            driver.find_element_by_css_selector('#RecipientEmailInput').send_keys(invite_address)

            driver.save_screenshot('./2.png')
        except Exception as e:
            print(e)
        finally:
            driver.quit()


if __name__ == '__main__':
    MyCarrierPacketsApi().send_inv(00000000, 'email@email.email')
