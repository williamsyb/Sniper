import pandas as pd
import os

DATA_PATH = os.path.expanduser('~')

g_plt_figsize = (14, 7)

EMPRY_DF = pd.DataFrame()

DATE_FORMAT = '%Y-%m-%d'

CS_INDEX = 'http://www.csindex.com.cn/zh-CN/indices/index'

CS_INDEX_PAGE = 'http://www.csindex.com.cn/zh-CN/indices/index?page={page}&page_size=50&by=asc&order={order}&data_type=json'