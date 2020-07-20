# internal imports
from cryptowatch.config import API_KEY

# imports
import pandas as pd
import requests


######################################################################################
# A pair consists of a base and quote, and is traded on an exchange. Example: btceur #
######################################################################################

class Pairs:

    def __init__(self):
        self.api_key = API_KEY

    #############################################################
    # This endpoint returns all pairs in the Cryptowatch system #
    #############################################################

    # The method returns a pandas dataframe ###
    # id                        int64
    # symbol                   object all the available pairs are here
    # base                     object dictionary
    # quote                    object dictionary
    # route                    object url for information about the pair
    # futuresContractPeriod    object

    def list(self):
        url = r"https://api.cryptowat.ch/pairs"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"])
        return df

    ####################################################################################################################
    # Gets the id, symbol, base, quote, and markets for the given currency pair. base and quote are both asset details #
    ####################################################################################################################

    # The method returns a pandas dataframe ###
    # id           int64
    # exchange    object markets
    # pair        object
    # active        bool
    # route       object This url will return all the urls for the given pair and market: price, summary, orderbook, trades and ohlc

    def details(self, pair):
        url = fr"https://api.cryptowat.ch/pairs/{pair}"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"]["markets"])
        return df
