# internal imports
from cryptowatch.config import API_KEY

# imports
import pandas as pd
import requests


class Assets:
    def __init__(self):
        self.api_key = API_KEY

    #############################################################################################
    # Gets all assets in the Cryptowatch system. Each asset response includes the asset details #
    #############################################################################################

    # This method returns a pandas df ###
    # id         int64
    # symbol    object assets
    # name      object full name of the asset
    # fiat        bool
    # route     object
    def list(self):
        url = r"https://api.cryptowat.ch/assets"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        print(result)
        df = pd.DataFrame(result["result"])
        return df

    #############################################################################################################
    # Gets the id, symbol, name, and markets for the given asset. Markets are broken into base and quote,       #
    # whichever the asset represents in the pair. "fiat" is true when the asset is fiat currency (such as usd), #
    # and false when it is a cryptocurrency                                                                     #
    #############################################################################################################

    # This method returns two pandas dataframes ###
    # base dataframe
    # id           int64
    # exchange    object
    # pair        object
    # active        bool
    # route       object

    # quote dataframe
    # id           int64
    # exchange    object
    # pair        object
    # active        bool
    # route       object
    def details(self, asset):
        url = fr"https://api.cryptowat.ch/assets/{asset}"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df_base = pd.DataFrame(result["result"]["markets"]["base"])
        df_quote = pd.DataFrame(result["result"]["markets"]["quote"])
        return df_base, df_quote
