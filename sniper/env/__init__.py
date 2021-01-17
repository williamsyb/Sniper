import pandas as pd
import os
from enum import Enum, unique

DATA_PATH = os.path.expanduser('~')

g_plt_figsize = (14, 7)

EMPRY_DF = pd.DataFrame()

DATE_FORMAT = '%Y-%m-%d'

CS_INDEX = 'http://www.csindex.com.cn/zh-CN/indices/index'

CS_INDEX_PAGE = 'http://www.csindex.com.cn/zh-CN/indices/index?page={page}&page_size=50&by=asc&order={order}&data_type=json'

PRODUCT_URL = 'http://www.csindex.com.cn/zh-CN/indices/index-detail/{code}'

PRODUCT_DETAIL_URL = 'http://www.csindex.com.cn/zh-CN/search/index-derivatives?index_name={}'

# type 1.静态市盈率  2.滚动市盈率   3. 市净率  4. 股息率
# http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?type=zjh1&date=2021-01-13
INDUSTRY_ZJH = 'http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?type=zjh{type_}&date={date}'

# http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?type=zz2&date=2021-01-13
INDUSTRY_ZZ = 'http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?type=zz{type_}&date={date}'

# http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?type=zy1&date=2021-01-13
INDUSTRY_ZY = 'http://www.csindex.com.cn/zh-CN/downloads/industry-price-earnings-ratio?type=zy{type_}&date={date}'


<<<<<<< HEAD
=======


@unique  # @unique装饰器可以帮助我们检查保证没有重复值
class RatioName(Enum):
    def __new__(cls, chinese, num):
        obj = object.__new__(cls)
        obj.chinese = chinese
        obj.num = num
        return obj

    STATIC_PE = '静态市盈率', 1
    TTM_PE = '滚动市盈率', 2
    PB = '市净率', 3
    DIVIDEND_YIELD = '股息率', 4
>>>>>>> f244fae5fdea0e99a9a177a8ab47f2868d80bacb
