# internal imports
from cryptowatch.config import API_KEY

# imports
import pandas as pd
import requests


#################################################################################################
# Exchanges are where all the action happens! Each exchange in our system has a list of markets #
#################################################################################################

class Exchanges:

    def __init__(self):
        self.api_key = API_KEY

    #################################################################
    # This endpoint returns all exchanges in the Cryptowatch system #
    #################################################################

    # Returns a pandas dataframe
    # id         int64
    # symbol    object
    # name      object
    # route     object
    # active      bool

    def list(self):
        url = r"https://api.cryptowat.ch/exchanges"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"])
        return df

    ########################################################
    # This endpoint returns details for the given exchange #
    ########################################################

    # Returns a dictionary with the following keys
    # id
    # symbol
    # name
    # active
    # routes
    #     markets

    def details(self, market):
        url = fr"https://api.cryptowat.ch/exchanges/{market}"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        return result["result"]

    #####################################################################
    # This endpoint returns all markets available on the given exchange #
    #####################################################################

    # Returns a pandas dataframe
    # id           int64
    # exchange    object
    # pair        object
    # active        bool
    # route       object

    def markets(self, market):
        url = fr"https://api.cryptowat.ch/markets/{market}"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"])
        return df
