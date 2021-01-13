import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from sniper.env import INDUSTRY_ZJH, DATE_FORMAT
from datetime import datetime as dt


class Ratio:
    today = dt.now().strftime(DATE_FORMAT)

    def __init__(self):
        pass

    def download(self):
        url = INDUSTRY_ZJH.format(type_=1, date=self.today)
        res = requests.get(url).content.decode('utf-8', 'ignore')
        soup = BeautifulSoup(res, 'lxml')
        all_tables = soup.find_all('table', class_='list-div-table')
        # print(res)
        for table in all_tables:
            print(table)
        # print(res)


if __name__ == '__main__':
    ratio = Ratio()
    ratio.download()
