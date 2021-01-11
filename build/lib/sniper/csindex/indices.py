import requests
from pprint import pprint
import akshare as ak
import json
import os
from datetime import datetime as dt
from urllib import parse
from sniper.env import CS_INDEX_PAGE, EMPRY_DF, DATE_FORMAT
from sniper.protocol.io import FileSystem
import pandas as pd
import time
from loguru import logger


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
        if os.path.exists(self.__category_local_path) and not self.__to_update:
            self.__category = self.__io.read_csv(self.__category_local_path)
            return
        while self.__total_page ==0 or self.__cur_page<=self.__total_page:
            self.sleep()
            self.download_index_category()
            self.__cur_page +=1
        self.__cur_page = self.__init_page
        self.__io.to_csv(self.__category, self.__category_local_path)

    def download_index_category(self):
        url = CS_INDEX_PAGE.format(page=self.__cur_page,order=parse.quote(self.__order))
        res = requests.get(url).content
        res = json.loads(res)
        if self.__total_page ==0:
            self.__total_page = res['total_page']
        df = pd.DataFrame(res['list'])
        try:
            df.drop('index_id', axis=1, inplace=True)
            # print(df)
            logger.info(f'中证所有指数 第{self.__cur_page}/{self.__total_page} 页  {df.shape}下载成功')
            self.__category = self.__category.append(df)
        except:
            return

    def download_detail(self):
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
        pass


if __name__ == '__main__':
    cs_index = CSIndex(interval=1)
    cs_index.start()
    print(cs_index.category_df)
    # pprint(cs_index.download_index_category())
