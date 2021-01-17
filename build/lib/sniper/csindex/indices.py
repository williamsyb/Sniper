import requests
from pprint import pprint
import akshare as ak
import json
import os
from datetime import datetime as dt
from urllib import parse
from sniper.env import CS_INDEX_PAGE, EMPRY_DF, DATE_FORMAT, PRODUCT_URL, PRODUCT_DETAIL_URL
from sniper.protocol.io import FileSystem
import pandas as pd
import time
from loguru import logger
from bs4 import BeautifulSoup
from urllib import parse


class CSIndex:
    today = dt.now().strftime(DATE_FORMAT)

    def __init__(self, interval=0.5, to_update=False, work_path=''):
        self.__total_page = 0
        self.__init_page = 1
        self.__cur_page = 1
        self.__order = '发布时间'
        self.__category = EMPRY_DF
        self.__interval = interval
        self.__to_update = to_update
        self.__io = FileSystem(work_path, 'csindex')
        self.__category_local_path = 'csindex_category.csv'

    def sleep(self):
        time.sleep(self.__interval)

    @property
    def category_df(self):
        return self.__category

    def start(self):
        if not self.__to_update:
            try:
                self.__category = self.__io.read_csv(self.__category_local_path)
                return
            except:
                pass
        while self.__total_page == 0 or self.__cur_page <= self.__total_page:
            self.sleep()
            self.download_index_category()
            self.__cur_page += 1
        self.__cur_page = self.__init_page
        self.__io.to_csv(self.__category, self.__category_local_path)

    def download_index_category(self):
        url = CS_INDEX_PAGE.format(page=self.__cur_page, order=parse.quote(self.__order))
        res = requests.get(url).content
        res = json.loads(res)
        if self.__total_page == 0:
            self.__total_page = res['total_page']
        df = pd.DataFrame(res['list'])
        try:
            df.drop('index_id', axis=1, inplace=True)
            # print(df)
            logger.info(f'中证所有指数 第{self.__cur_page}/{self.__total_page} 页  {df.shape}下载成功')
            self.__category = self.__category.append(df)
        except:
            return

    def download_detail(self, code):
        """
        举个例子：http://www.csindex.com.cn/zh-CN/indices/index-detail/000001
        都是以最后一个指数代码结尾
        详情中有
        1. 简介
        2. 表现
        3. 相关产品
        4. 十大持仓
        5. 行业权重分布
        :return: 
        """
        url = PRODUCT_URL.format(code=code)
        data = requests.get(url).content.decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'lxml')
        # 1. 获取指数简介
        all_a = soup.find('div', class_='js_txt_new')
        brief = all_a.text.replace('\n', '')

        # 2. 获取相关产品
        name = soup.find('h1', class_='d_title').text
        url_more = PRODUCT_DETAIL_URL.format(parse.quote(name))
        detail_data = requests.get(url_more).content.decode('utf-8', 'ignore')

        soup_more = BeautifulSoup(detail_data, 'lxml')
        data_list = []  # 结构: [dict1, dict2, ...], dict结构{'船名': ship_name, '航次': voyage, '提单号': bill_num, '作业码头': wharf}
        for idx, tr in enumerate(soup_more.find_all('tr')):
            if idx != 0:
                tds = tr.find_all('td')
                data_list.append({
                    '证券代码': tds[0].contents[0],
                    '基金名称': tds[1].contents[0],
                    '基金成立日': tds[2].contents[0],
                    '基金类型': tds[3].contents[0],
                    '产品类型': tds[4].contents[0],
                    '标的指数': tds[5].contents[0],
                    # '基金管理人': tds[7].contents[0],
                })
        df = pd.DataFrame(data_list)
        # print(df)
        return df

    def load_index_price(self, index_code):
        df = ak.stock_zh_index_hist_csindex(symbol=index_code)
        return df

    def load_fund_price(self, code):
        df = ak.stock_zh_index_daily_em(symbol="sz399812")
        return df


if __name__ == '__main__':
    cs_index = CSIndex(interval=1)
    cs_index.start()
    print(cs_index.category_df)
    # pprint(cs_index.download_index_category())
