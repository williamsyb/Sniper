import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from sniper.env import INDUSTRY_ZJH, INDUSTRY_ZZ, INDUSTRY_ZY, DATE_FORMAT, RatioName, ENGINE
from datetime import datetime as dt


class Ratio:
    today = dt.now().strftime(DATE_FORMAT)
    START_DATE = '2008-01-01'

    def __init__(self):
        pass

    def start(self):
        for section_url, section_name in ((INDUSTRY_ZJH, '证监会分类'), (INDUSTRY_ZZ, '中证分类'), (INDUSTRY_ZY, '主要板块')):
            for ratio in RatioName:
                date = '2021-01-13'
                url = section_url.format(type_=ratio.num, date=date)
                self.download(url, ratio.chinese, section_name, date)

    def download(self, url, col_name, section_name, date):
        res = requests.get(url).content.decode('utf-8', 'ignore')
        # print(res)
        soup = BeautifulSoup(res, 'lxml')
        all_tables = soup.find_all('table', class_='list-div-table')
        # print(res)
        data_list = []
        # df = pd.DataFrame()
        for table in all_tables:
            # print(table)

            for idx, tr in enumerate(table.find_all('tr')):
                tds = tr.find_all('td')
                # print(tds[0].text)
                data_list.append({
                    '行业代码': tds[0].text.strip(),
                    '行业名称': tds[1].text.strip(),
                    col_name: tds[2].text.strip(),
                    '股票家数': tds[3].text.strip(),
                    '亏损家数': tds[4].text.strip(),
                    '近一个月': tds[5].text.strip(),
                    '近三个月': tds[6].text.strip(),
                    '近六个月': tds[7].text.strip(),
                    '近一年': tds[8].text.strip(),
                })
        df = pd.DataFrame(data_list)
        df['section_name'] = section_name
        df['date'] = date
        # df.to_csv('pe.csv', index=False, encoding='gbk')
        print(df)
        return df
        # print(res)


if __name__ == '__main__':
    ratio = Ratio()
    ratio.start()
