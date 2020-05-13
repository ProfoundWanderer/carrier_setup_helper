# local imports
import config

# standard library imports
from datetime import date, datetime
import json
import xml.etree.ElementTree as ElementTree

# third party imports
from dateutil.relativedelta import relativedelta
import requests


class SaferWatch:
    """
    Class for using SaferWatch API

    https://www.saferwatch.com/helpdocs/WebServices/CarrierLookup12032.php
    ?version=32

    https://www.saferwatch.com/webservices/CarrierService32.php
    ?Action=CarrierLookup
    &ServiceKey=YourServiceKey
    &CustomerKey=YourCustomerKey
    &number=MC, MX, FF or DOT Number (Numbers with no prefix are interpreted as DOT numbers)

    ex: https://www.saferwatch.com/webservices/CarrierService32.php?Action=CarrierLookup&ServiceKey=DemoServiceKey&CustomerKey=DemoCustomerKey&number=51442

    """

    def __init__(self):
        """
        Attributes:
            self._api_username (str): user name to log into api that is
                retrieved from config file
            self._api_password (str): password to log into api that is
                retrieved from config file
        """
        self._service_key = config.service_key
        self._customer_key = config.customer_key

    def check_requirements(self, dot_number):
        url = (
            f'https://www.saferwatch.com/webservices/CarrierService32.php'
            f'?Action=CarrierLookup&ServiceKey={self._service_key}'
            f'&CustomerKey={self._customer_key}&number={dot_number}'
        )

        # response.content is xml as a str
        response = requests.request('POST', url)
        # change response into ElementTree so it can be parsed later on
        response_xml = ElementTree.fromstring(response.content)

        # gather information
        carrier = (
            response_xml.find('CarrierDetails')
            .find('Identity')
            .find('legalName')
        )
        carrier_status = (
            response_xml.find('CarrierDetails')
            .find('Operation')
            .find('operatingStatus')
        )
        # double check status
        backup_status = (
            response_xml.find('CarrierDetails').find('dotNumber').get('status')
        )
        str_dot_date = (
            response_xml.find('CarrierDetails')
            .find('Operation')
            .find('dotAddDate')
        )
        str_auth_date = (
            response_xml.find('CarrierDetails')
            .find('Authority')
            .find('authGrantDate')
        )
        carrier_type = (
            response_xml.find('CarrierDetails')
            .find('Operation')
            .find('carrierOperation')
        )
        safety_rating = (
            response_xml.find('CarrierDetails')
            .find('Safety')
            .find('rating')
        )

        # change dot_date from string to a date object
        date_dot_date = datetime.strptime(str_dot_date.text, '%Y-%m-%d')
        # get the date 6 months after the dot_date
        six_mon_past_dot_date = date_dot_date.date() + relativedelta(months=+6)

        # this handles INACTIVE DOT cases
        if (
            (
                carrier_status.text is None
                and backup_status.upper() == 'INACTIVE'
            )
            or (
                carrier_status.text.upper() == 'INACTIVE'
                and backup_status is None
            )
            or (
                carrier_status.text.upper() == 'INACTIVE'
                or backup_status.upper() == 'INACTIVE'
            )
        ):
            # send email
            print('Carrier DOT status is inactive so we can not use them.')
            return False

        # this handles unacceptable safety conditions
        if not (safety_rating.text.upper() == 'NOT RATED' or safety_rating.text.upper() == 'SATISFACTORY'):
            print('bad')
            return False

        # handles cases ACTIVE DOT AND INTRASTATE cases
        if (
            (carrier_status.text is None and backup_status.upper() == 'ACTIVE')
            or (
                carrier_status.text.upper() == 'ACTIVE'
                and backup_status is None
            )
            or (
                carrier_status.text.upper() == 'ACTIVE'
                or backup_status.upper() == 'ACTIVE'
            )
            and (carrier_type.text.upper() == 'INTRASTATE')
        ):
            if date.today() > six_mon_past_dot_date:
                # send email
                print('we good, lets send one')
            else:
                until_valid = six_mon_past_dot_date - date.today()
                # send email
                print(
                    f'Carrier DOT is not at least 6 months old so we can not '
                    f'use them for another {until_valid.days} days.'
                )

        # handles cases ACTIVE DOT AND INTERSTATE cases
        if (
            (carrier_status.text is None and backup_status.upper() == 'ACTIVE')
            or (
                carrier_status.text.upper() == 'ACTIVE'
                and backup_status is None
            )
            or (
                carrier_status.text.upper() == 'ACTIVE'
                or backup_status.upper() == 'ACTIVE'
            )
            and (carrier_type.text.upper() == 'INTERSTATE')
        ):
            # change dot_date from string to a date object
            date_auth_date = datetime.strptime(str_auth_date.text, '%Y-%m-%d')
            # get the date 6 months after the dot_date
            six_mon_past_auth_date = date_auth_date.date() + relativedelta(months=+6)

            # these two need to account for lapses
            if (date.today() > six_mon_past_auth_date) and (date.today() > six_mon_past_dot_date):
                print('made it')
            if date.today() < six_mon_past_auth_date:
                until_auth_valid = six_mon_past_auth_date - date.today()
                # send email
                print(
                    f'Carrier authority is not at least 6 months old so we can '
                    f'not use them for another {until_auth_valid.days} days.'
                )
            if date.today() < six_mon_past_dot_date:
                until_dot_valid = six_mon_past_dot_date - date.today()
                # send email
                print(
                    f'Carrier DOT is not at least 6 months old so we can '
                    f'not use them for another {until_dot_valid.days} days.'
                )
        else:
            print(carrier.text)
            print(carrier_status.text)
            print(backup_status)
            print(str_dot_date.text)
            print(carrier_type.text)

        return False


if __name__ == '__main__':
    pass
