# local imports
import config

# standard library imports
from datetime import date, datetime
import xml.etree.ElementTree as ElementTree

# third party imports
from dateutil.relativedelta import relativedelta
import requests


class SaferWatch:
    """
    Class for using SaferWatch API
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
            f'https://www.saferwatch.com/webservices/CarrierService32.php?Action=CarrierLookup&'
            f'ServiceKey={self._service_key}&CustomerKey={self._customer_key}&number={dot_number}'
        )

        response = requests.request('POST', url)
        response_xml = ElementTree.fromstring(response.content)

        carrier = response_xml.find('CarrierDetails').find('Identity').find('legalName')
        carrier_status = response_xml.find('CarrierDetails').find('Operation').find('operatingStatus')
        # for backup check of status
        backup_status = response_xml.find('CarrierDetails').find('dotNumber').get('status')
        str_dot_date = response_xml.find('CarrierDetails').find('Operation').find('dotAddDate')
        str_auth_date = response_xml.find('CarrierDetails').find('Authority').find('authGrantDate')
        carrier_type = response_xml.find('CarrierDetails').find('Operation').find('carrierOperation')
        safety_rating = response_xml.find('CarrierDetails').find('Safety').find('rating')

        date_dot_date = datetime.strptime(str_dot_date.text, '%Y-%m-%d')
        # get the date 6 months after the dot_date
        six_mon_past_dot_date = date_dot_date.date() + relativedelta(months=+6)

        """
        This handles unacceptable safety conditions
        """
        if not (safety_rating.text.upper() == 'NOT RATED' or safety_rating.text.upper() == 'SATISFACTORY'):
            email_resp = f'DOT {dot_number} has a safety rating of {safety_rating.text} so we are unable to use them.'
            return email_resp
        """
        This handles INACTIVE DOT cases
        """
        if (
                (carrier_status.text is None and backup_status.upper() == 'INACTIVE')
                or (carrier_status.text.upper() == 'INACTIVE' and backup_status is None)
                or (carrier_status.text.upper() == 'INACTIVE' or backup_status.upper() == 'INACTIVE')
        ):
            email_resp = f'DOT {dot_number} is inactive so we can not use them.'
            return email_resp
        """
        This handles DOT date not being 6 months old
        """
        if date.today() < six_mon_past_dot_date:
            until_valid = six_mon_past_dot_date - date.today()
            # send email
            email_resp = (f'Carrier DOT is not at least 6 months old so we can not use them for '
                          f'another {until_valid.days} days.'
                          )
            return email_resp

        """
        This handles cases that pass safety, inactive dot, and dot age check.
        """
        if (  # handles cases ACTIVE DOT AND INTRASTATE cases
                (carrier_status.text is None and backup_status.upper() == 'ACTIVE')
                or (carrier_status.text.upper() == 'ACTIVE' and backup_status is None)
                or (carrier_status.text.upper() == 'ACTIVE' or backup_status.upper() == 'ACTIVE')
                and (carrier_type.text.upper() == 'INTRASTATE')
        ):
            if date.today() > six_mon_past_dot_date:
                print('Looks good, send invite.')
                return None
        elif (  # handles cases ACTIVE DOT AND INTERSTATE cases
                (carrier_status.text is None and backup_status.upper() == 'ACTIVE')
                or (carrier_status.text.upper() == 'ACTIVE' and backup_status is None)
                or (carrier_status.text.upper() == 'ACTIVE' or backup_status.upper() == 'ACTIVE')
                and (carrier_type.text.upper() == 'INTERSTATE')
        ):
            date_auth_date = datetime.strptime(str_auth_date.text, '%Y-%m-%d')
            six_mon_past_auth_date = date_auth_date.date() + relativedelta(months=+6)

            date_dot_date = datetime.strptime(str_dot_date.text, '%Y-%m-%d')
            # get the date 12 months after the dot_date
            twelve_mon_past_dot_date = date_dot_date.date() + relativedelta(months=+12)

            until_auth_valid = six_mon_past_auth_date - date.today()
            until_dot_valid = six_mon_past_dot_date - date.today()

            # accounts for if authority and dot are less than 6 months old
            if (date.today() < six_mon_past_auth_date) and (date.today() < twelve_mon_past_dot_date):
                # send email
                email_resp = (f'dot and auth no go')
                return False
            # if dot and auth are good, it shouldn't ever happen since this script is for escalated invites
            elif (date.today() > six_mon_past_auth_date) and (date.today() > six_mon_past_dot_date):
                print('All good and shouldn\'t have been an escalated invite anyways but will account for it.')
                return None
            # this accounts for authority lapses but not foolproof since fmcsa authority api is still down
            elif (date.today() < six_mon_past_auth_date) and (date.today() > twelve_mon_past_dot_date):
                print('auth no go but dot good to go so can use but will keep turning false')
                return None

        else:
            print(carrier.text)
            print(carrier_status.text)
            print(backup_status)
            print(str_dot_date.text)
            print(carrier_type.text)

        return False


if __name__ == '__main__':
    pass
