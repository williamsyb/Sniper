import traceback
from functools import lru_cache
import time
import akshare as ak
from datetime import datetime as dt
import pandas as pd
import os
import sqlite3 as sql
from loguru import logger
from sniper.utils.expt import ModuleExt
from sniper.utils import LazyFunc
from sniper.env import DATE_FORMAT

EMPTY_DF = pd.DataFrame()
DB_NAME = 'calender'


class Utils:

    @staticmethod
    def is_empty(li: list):
        return len(li) == 0


class FileSystem:
    def __init__(self, base_path, dir_name):
        self.__base_path = base_path

        self.__dir_name = os.path.join(base_path, dir_name)
        if not os.path.exists(self.__dir_name):
            os.mkdir(self.__dir_name)

    def to_csv(self, df, file_name, mode='w'):
        if not file_name.endswith('.csv'):
            file_name = file_name + '.csv'
        abs_path = os.path.join(self.__dir_name, file_name)
        logger.info(f'下载 {abs_path} ...')
        # print(df)
        header = True
        if mode == 'a':
            header = False
        df.to_csv(abs_path, index=False, mode=mode, header=header)

    def read_csv(self, file_name_or_code):
        file_name_or_code = str(file_name_or_code)
        files = os.listdir(self.__dir_name)
        files = [file for file in files if file.find(file_name_or_code) >= 0]
        if not Utils.is_empty(files):

            abs_path = os.path.join(self.__dir_name, files[0])

            return pd.read_csv(abs_path)
        else:
            raise ModuleExt(f'没有找到{file_name_or_code}')


class DbSystem:
    def __init__(self, base_path, name):
        self.base_path = base_path
        self.name = name
        self.engine = self.__make_engine()

    @lru_cache()
    def __make_engine(self):
        abs_path = os.path.join(self.base_path, f'{self.name}.db')

        # TODO 需要扩展 支持更多数据库
        engine = sql.connect(abs_path)
        return engine

    def to_sql(self, df: pd.DataFrame, table, mode='append'):
        logger.info(f'{df.shape}存储到数据库 "{table}" ...')
        df.to_sql(table, self.engine, index=False, if_exists=mode)

    def read_sql(self, sql_str):
        return pd.read_sql(sql_str, self.engine)


class Calender:
    today = dt.now().strftime(DATE_FORMAT)

    def __init__(self, base, name):
        self.sw_dates = self.__get_dates()
        self.__db = DbSystem(base, name)

    @lru_cache()
    def __get_dates(self):
        dates = ak.tool_trade_date_hist_sina()
        dates.trade_date = pd.to_datetime(dates.trade_date)
        return dates

    def get_missing(self, start):
        """
        检查从start至今的缺失日期
        """
        local_df = self.__db.read_sql(f'select * from {DB_NAME}')
        local_df.trade_date = pd.to_datetime(local_df.trade_date)
        sw_dates = self.get_periods(start, self.today).trade_date.tolist()
        local_dates = local_df.trade_date.tolist()
        diff = set(sw_dates).difference(set(local_dates))
        return list(diff)

    def make_up(self, dates: list):
        if not Utils.is_empty(dates):
            dates = [date.strftime(DATE_FORMAT) for date in dates]
        df = pd.DataFrame()
        df['trade_date'] = dates
        self.__db.to_sql(df, DB_NAME)

    def get_periods(self, start, end):
        df = self.sw_dates[(self.sw_dates.trade_date >= start) & (self.sw_dates.trade_date <= end)]
        return df


class SWManager:
    file_name = '{code}_{name}.csv'
    today = dt.now().strftime(DATE_FORMAT)

    def __init__(self, start, end, work_path=r'D:\William\notebooks\sniper\data'):
        self.start = start  # 2010-01-01
        self.end = end  # 2020-12-31
        self.folder = work_path
        self.__io = FileSystem(self.folder, 'sw')
        self.sw_index_spot_df = EMPTY_DF
        self.__missing_dates = []
        self.calender = Calender(self.folder, DB_NAME)

    @LazyFunc
    def category(self):
        codes = self.sw_index_spot_df.code.tolist()
        names = self.sw_index_spot_df.name.tolist()
        return {k: v for k, v in zip(codes, names)}

    def initialize(self):
        self.__spot()

    def read_data(self, code):
        return self.__io.read_csv(code)

    def download_history(self):
        for _, row in self.sw_index_spot_df.iterrows():
            time.sleep(1)
            code = row['code']
            name = row['name']
            file_name = self.file_name.format(code=code, name=name)
            df = ak.sw_index_daily(index_code=code, start_date=self.start, end_date=self.end)
            self.__io.to_csv(df, file_name)

    def download_daily(self):
        for _, row in self.sw_index_spot_df.iterrows():
            # time.sleep(1)
            code = row['code']
            name = row['name']
            file_name = self.file_name.format(code=code, name=name)
            if self.__has_cache(self.start):
                logger.info(f'已经存在{code}-{name}')
                continue
            else:
                for date in self.__missing_dates:
                    logger.warning(f"缺失 {date}, 补充下载...")
                    df = ak.sw_index_daily(index_code=code, start_date=date, end_date=date)
                    self.__io.to_csv(df, file_name, mode='a')
        self.calender.make_up(self.__missing_dates)
        self.__missing_dates = []

    def __has_cache(self, start):

        missing_dates = self.calender.get_missing(start)
        if len(missing_dates) == 0:
            return True
        else:
            logger.warning(f'缺失日期:{missing_dates}')
            self.__missing_dates = missing_dates
            return False

    def query_name(self, code):
        try:
            return self.sw_index_spot_df.set_index('code').loc[code, 'name']
        except:
            traceback.print_exc()
            raise Exception(f'未找到 {code}!')

    def __spot(self):
        df = self.__remote_spot()
        df.rename(columns={'指数代码': 'code', '指数名称': 'name'}, inplace=True)
        df.code = df.code.astype(str)
        self.sw_index_spot_df = df

    @lru_cache()
    def __remote_spot(self):
        return ak.sw_index_spot()


if __name__ == '__main__':
    sw_manager = SWManager('2010-01-01', SWManager.today)
    # sw_manager = SWManager('2010-01-01', '2020-12-31')
    sw_manager.initialize()
    # sw_manager.download_history()
    sw_manager.download_daily()
    print(sw_manager.read_data('801020'))
