# local imports
import all_decorators as decs
from safer_api import SaferWatch as sw

# standard library imports
import json
import requests


class EscalatedInvites:
    decorators = decs.Decorators()

    @decorators.refresh_token
    def escalated_invite(self, dot_number):
        print(f'Attempting to invite DOT number: {dot_number}.')

        url = f'https://api.mycarrierpackets.com/api/v1/carrier/getcustomerpacketwithsw?DOTNumber={dot_number}'

        with open('token_data.json') as token_json_file:
            # loads json file where we saved file
            token_data = json.load(token_json_file)
            # changes token_data from str to dict
            token_data_dict = json.loads(token_data)
            _api_authorization = token_data_dict['access_token']

        bearer_authorization = f'bearer {_api_authorization}'

        headers = {'Authorization': bearer_authorization}
        payload = {}
        files = {}

        response = requests.request(
            'POST', url, headers=headers, data=payload, files=files
        )

        try:
            ei_resp = json.loads(response.text)
            ei_resp_msg = ei_resp['Message']
            print(f'{ei_resp_msg} Checking to see if carrier satisfies necessary requirements to be invited and used.')
            results = sw().check_requirements(dot_number)
            print(results)
        except KeyError:
            # expected if carrier_setup already filled out packet
            print('Carrier has already filled out the packet.')
            exit()
        except Exception as e:
            # just a broad exception to be safe
            print(e)
            exit()

        return True


if __name__ == '__main__':
    """
        DOT STATUS  | STATUS    | Packet?   | 6 months old?
        -------------------------------------------------------------------------
       ~764564      | ACTIVE    | No        | Yes
       ~282176      | INACTIVE  | No        | Not active
       ~2344552     | Active    | Yes       | Yes   | Invited/Accepted/In Sys
       ~3360987     | ACTIVE    | No        | No
       ~3382665     | ACTIVE    | No        | No for auth or ops
       ~3077170     | Everything good not invited
       !3077157     | not enough insurance
       ~753733     | Safety
       ~3382665     | auth and dot no good
       ~3046325     | auth less than 6 months old but DOT is older than a year so its ok

        ~ Scenario handled/accounted for

    """
    EscalatedInvites().escalated_invite(2321331)
