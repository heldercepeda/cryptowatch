# internal imports
from cryptowatch.config import API_KEY

# imports
import pandas as pd
import requests



###############################################################################################
# A market is a pair listed on an exchange. For example, btceur on exchange kraken is a market#
###############################################################################################

class Markets:

    def __init__(self):
        self.api_key = API_KEY

    #####################################################################################################
    # This endpoint returns all markets in the Cryptowatch system, each entry containing market details #
    #####################################################################################################

    # Returns a pandas dataframe ###
    # id           int64
    # exchange    object
    # pair        object
    # active        bool
    # route       object

    def list(self):
        url = r"https://api.cryptowat.ch/markets"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"])
        return df

    ####################################################################################
    # Gets the id, exchange, pair, active status, and api routes for the given market. #
    # If active is false, the market is not currently supported                        #
    ####################################################################################

    # Returns a list where the elements are:
    # 1st: market
    # 2nd: pair
    # 3rd: active
    # 4th: dictionary with the urls for price, summary, orderbook, trades and ohlc

    def details(self, market, pair):
        url = fr"https://api.cryptowat.ch/markets/{market}/{pair}"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        return [market, pair, result["result"]["active"], result["result"]["routes"]]

    #############################################################################################################
    # Returns the price for every market on the platform. This is cached and will be a few seconds out of date, #
    # but it's an efficient way to fetch a lot of prices                                                        #
    #############################################################################################################

    # Returns a dictionary. The keys can be indexes or markets
    # index example: "index:kraken-futures:cf-in-bchusd": 210.75
    # market example: "market:binance-us:adausd": 0.0364

    def all_market_prices(self):
        url = fr"https://api.cryptowat.ch/markets/prices"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        dict_ = result["result"]
        return dict_

    ##################################################################################################
    # Gets the most recent trades for the given market. The most recent 50 are returned by default,  #
    # but you can get up to 1000 with the limit parameter.                                           #
    # You can also filter the response for trades after a certain timestamp with the since parameter #
    ##################################################################################################

    # Returns a pandas dataframe
    # ID             int64
    # Timestamp      int64
    # Price        float64
    # Amount       float64

    # The request can take two optional parameters: since and limit
    # "since" is not in use at the moment

    def trades(self, market, pair, limit=None):
        url = fr"https://api.cryptowat.ch/markets/{market}/{pair}/trades"
        params = {
            "apikey": self.api_key,
            "limit": limit  # number of trades in the response. max: 1000 | default: 50
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"], columns=["ID", "Timestamp", "Price", "Amount"])
        df = df.sort_values("Timestamp", ascending=False).reset_index(drop=True)
        df.Timestamp = pd.to_datetime(df.Timestamp, unit="s")
        return df

    ##########################################################################################
    # Returns a market's last price as well as other stats based on a 24-hour sliding window #
    # High price, Low price, % change, Absolute change, Volume, Quote volume                 #
    ##########################################################################################

    # Returns a dictionary with the following keys and subkeys
    # price
    #     last
    #     high
    #     low
    #     change
    #         percentage
    #         absolute
    # volume
    # volumeQuote
    # pair

    def summary_24h(self, market, pair):
        url = fr"https://api.cryptowat.ch/markets/{market}/{pair}/summary"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        dict_ = result["result"]
        dict_.update({"pair": pair})
        return dict_

    ################################################################
    # Returns the 24-hour summary for every market on the platform #
    ################################################################

    # Returns a pandas dataframe with the following columns
    # Market          object
    # Pair            object
    # Open           float64
    # High           float64
    # Low            float64
    # Close          float64
    # volume          object
    # volumeQuote     object

    def summary_24h_all(self):
        url = r"https://api.cryptowat.ch/markets/summaries"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"])
        df = df.T
        df["delete"] = df.index
        df["Market"] = df.delete.apply(lambda x: x.split(":")[0])
        df["Pair"] = df.delete.apply(lambda x: x.split(":")[1])
        df["Close"] = df["price"].apply(lambda x: x["last"])
        df["High"] = df["price"].apply(lambda x: x["high"])
        df["Low"] = df["price"].apply(lambda x: x["low"])
        df["Change_%"] = df["price"].apply(lambda x: x["change"]["percentage"])
        df["Change_abs"] = df["price"].apply(lambda x: x["change"]["absolute"])
        df["Open"] = df["Close"] - df["Change_abs"]
        df = df[["Market", "Pair", "Open", "High", "Low", "Close", "volume", "volumeQuote"]]
        df = df.reset_index(drop=True)
        return df

    #################################################################################
    # Gets the order book for a given market. An order book consists of two arrays, #
    # bids and asks. Each order is a 2-element array [Price, Amount]                #
    #################################################################################

    #####################################################################################
    # Each response includes a seqNum which is intended for use with the WebSocket API; #
    # you can use this to resynchronize your order book and replay deltas received over #
    # the live feed which have a higher seqNum                                          #
    #####################################################################################

    # Returns a dictionary with the following keys:
    # asks
    # The value of "asks" is an array of 2-elements array [[price 1, amount 1],[price 2, amount 2],...]
    # bids
    # The value of "bids" is an array of 2-elements array [[price 1, amount 1],[price 2, amount 2],...]
    # seqNum
    # The value of "seqNum" is an integer

    def order_book(self, market, pair, depth=None, span=None, limit=None):
        url = fr"https://api.cryptowat.ch/markets/{market}/{pair}/orderbook"
        params = {
            "apikey": self.api_key,
            "depth": depth,
            # Only return orders cumulating up to this size (example: depth=100 means the sum of the amounts is 100)
            "span": span,  # Only return orders within this percentage of the midpoint. Example: 0.5 (meaning 0.5%)
            "limit": limit  # Limits the number of orders on each side of the book
        }
        result = requests.get(url, params=params).json()
        return result["result"]

    ###########################################################################
    # Provides liquidity sums at several basis point levels in the order book #
    ###########################################################################

    # Returns a dictionary with the following keys
    # bid
    #     base
    #     quote
    # ask
    #     base
    #     quote
    # Each "base" and "quote" has "25","50","75","100","150","200","250","300","400","500" as keys

    def oder_book_liquidity(self, market, pair):
        url = fr"https://api.cryptowat.ch/markets/{market}/{pair}/orderbook/liquidity"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        return result["result"]

    ###################################################################################################################
    # Returns a market's OHLC candlestick data. A series of candlesticks is represented as a list of lists of numbers #
    ###################################################################################################################

    ########################################################################################################
    # Limit must be in { 60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200, 604800 } #
    ########################################################################################################

    # Returns a pandas dataframe
    # CloseTime        int64
    # OpenPrice      float64
    # HighPrice      float64
    # LowPrice       float64
    # ClosePrice     float64
    # Volume         float64
    # QuoteVolume    float64
    # Period           int64
    # Label           object

    def ohlc(self, market, pair, before=None, after=None, periods=None):
        url = fr"https://api.cryptowat.ch/markets/{market}/{pair}/ohlc"
        if periods:
            periods = ",".join(periods)
        params = {
            "apikey": self.api_key,
            "before": before,  # Unix timestamp. Only return candles opening before this time. Example: 1481663244
            "after": after,  # Unix timestamp. Only return candles opening after this time. Example 1481663244
            "periods": periods  # comma separated integers. Only return these time periods.
        }
        result = requests.get(url, params=params).json()
        list_ = []
        values = [60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200, 604800]
        labels = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "3d", "1w"]
        for key in result["result"].keys():
            df = pd.DataFrame(result["result"][key],
                              columns=["CloseTime", "OpenPrice", "HighPrice", "LowPrice", "ClosePrice", "Volume",
                                       "QuoteVolume"])
            df["Period"] = [int(key) for _ in df.index]
            ii = values.index(int(key))
            df["Label"] = [labels[ii] for _ in df.index]
            list_.append(df)
        final_df = pd.concat(list_)
        final_df = final_df.sort_values(["Period", "CloseTime"])
        return final_df
