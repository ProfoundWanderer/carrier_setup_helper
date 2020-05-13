# local imports
import mcp_api as mcp

# standard library imports
from datetime import datetime
import json
import time


class Decorators:
    @staticmethod
    def refresh_token(decorated):
        mcp_api_class = mcp.MyCarrierPacketsApi()

        def wrapper(self, *args, **kwargs):
            try:
                # see if token data has been saved (i.e. the first time script
                # runs there won't be one)
                with open('token_data.json') as token_json_file:
                    # loads json file where we saved file
                    token_data = json.load(token_json_file)
                    # changes token_data from str to dict
                    token_dict = json.loads(token_data)

                    # format token date time so it can be used. This is the
                    # GMT timezone.
                    unformatted_token_exp_gmt_date = token_dict['.expires']
                    formatted_token_exp_gmt_date = datetime.strptime(
                        unformatted_token_exp_gmt_date,
                        '%a, %d %b %Y %H:%M:%S %Z',
                    )

                    # format current date time so it can be used. This is the
                    # GMT timezone.
                    unformatted_token_exp_gmt_date = time.strftime(
                        '%a, %d %b %Y %I:%M:%S %p', time.gmtime()
                    )
                    formatted_current_gmt_date = datetime.strptime(
                        unformatted_token_exp_gmt_date,
                        '%a, %d %b %Y %I:%M:%S %p',
                    )

                    # make sure token is not expired
                    if (
                        formatted_token_exp_gmt_date.date()
                        > formatted_current_gmt_date.date()
                    ):
                        # self._api_authorization = token_dict['access_token']
                        print('Token is good.')
                    else:
                        print('Token has expired. Getting new token data.')
                        mcp_api_class.get_bearer_access_token()
            except IOError:
                # this catches if token_data.json doesn't exists (usually just
                # for when script first runs) relay message
                print('File not accessible.')
                mcp_api_class.get_bearer_access_token()
            except Exception as e:
                # broad exception catch just to be safe.
                # relay message
                print(e)

            return decorated(self, *args, **kwargs)

        return wrapper


if __name__ == '__main__':
    pass
