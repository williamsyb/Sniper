import requests
from pprint import pprint
import akshare as ak
import json
from sniper.env import CS_INDEX_PAGE
import pandas as pd


class CSIndex:
    def __init__(self):
        self.__total_page = 0

    def download(self):
        res = requests.get(CS_INDEX_PAGE).content
        res = json.loads(res)
        df = pd.DataFrame(res['list'])
        print(df)

        return res

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
    cs_index = CSIndex()
    pprint(cs_index.download())
