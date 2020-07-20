
# internal imports
from cryptowatch.config import API_KEY

# imports
import pandas as pd
import requests


class Assets:
    def __init__(self):
        self.api_key = API_KEY

    def list(self):
        url = r"https://api.cryptowat.ch/assets"
        params = {
            "apikey": self.api_key
        }
        result = requests.get(url, params=params).json()
        df = pd.DataFrame(result["result"])
        return df
