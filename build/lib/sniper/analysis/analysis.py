# -*- coding: utf-8 -*-
# @Time    : 2019/5/14 13:49
# @Author  : Yibin Sun
# @File    : analysis.py
# @Software: PyCharm
import traceback
from enum import Enum
import os
import pandas as pd
import warnings
from data_handler.data_handler import DataHanlder
from utils.log_handler import get_logger
from metrics_algo.metric_store import MetricStore
from config import WORKING_DIR
from env import Env

logger = get_logger('calc_error.log')
warnings.filterwarnings('ignore')
year_day = 250  # 252
q = 52


class Message(Enum):
    msg_missing = 'data missing'


class ValidateMixin:

    def check_fund(self):
        # print(self.data.shape)
        if len(self.data) < self.periods:
            return False
        else:
            return True
        # pass


class DataIndexBase(ValidateMixin, Env):
    def __init__(self, periods):
        self.year_day = 252
        self.q = 52
        self.rft_ret = 0.03
        self.daily_rft = 5 * self.rft_ret / self.year_day  # may be not need
        # self.stock_type = stock_type
        self.periods = periods

        self.annual_return = None
        self.annual_downside_risk = None
        self.sharpe_ratio = None
        self.sortino_ratio = None
        self.max_drawdown = None
        self.calmar_ratio = None
        self.information_ratio = None
        self.alpha_p = None

    def __call__(self, file_path_or_df, is_stock_type=True):
        self.file_path_or_df = file_path_or_df
        self.data = self.__treat_data()

        self.fit(is_stock_type)
        return self.out_put

    def __treat_data(self):
        if isinstance(self.file_path_or_df, str):
            df = pd.read_csv(self.file_path_or_df)

        elif isinstance(self.file_path_or_df, pd.DataFrame):
            df = self.file_path_or_df
        else:
            raise TypeError('file_path_or_df should be a file_path or DataFrame type.')
        # print(df.head())
        df['end_date'] = pd.to_datetime(df['end_date'])

        df.set_index('end_date', inplace=True)
        df.sort_index(inplace=True)
        df['rets'] = df['accum_nav'].pct_change()
        df = df[['accum_nav', 'rets']]

        # print(df.head())
        return df

    def fit(self, is_stock_type):
        if not self.check_fund():
            print(len(self.data))
            return ''
        print('>>> Start calculating...')
        self.index300 = DataHanlder.get_index300(WORKING_DIR)
        self.index300_close = DataHanlder.get_index300_close(WORKING_DIR)

        self.annual_return = self.get_annual_return(self.data)
        self.annual_downside_risk = self.get_annual_downside_risk(self.data)
        self.sharpe_ratio = self.get_sharpe_ratio(self.data)
        self.sortino_ratio = self.get_sortino_ratio(self.data)
        self.max_drawdown = self.get_max_drawdown(self.data)
        self.calmar_ratio = self.get_calmar_ratio(self.data)  # TODO  need to check
        self.information_ratio = self.get_info_ratio(self.data, is_stock_type)  # TODO  need to check
        self.alpha_p = self.get_alpha_p(self.data, is_stock_type)

    @property
    def out_put(self):
        out_put = {

            'annual_return': self.annual_return,
            'alpha_p': self.alpha_p,

            'annual_downside_risk': self.annual_downside_risk,
            'max_drawdown': self.max_drawdown,

            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'information_ratio': self.information_ratio,
        }
        return out_put

    def __repr__(self):
        text = '==================== Summary ====================\n'
        text += 'Annual_return:{annual_return}\n' \
                'Alpha p-value:{alpha_p}\n' \
                'Annual downside_risk:{annual_downside_risk}\n' \
                'Sharpe ratio:{sharpe_ratio}\n' \
                'Max drawdown:{max_drawdown}\n' \
                'Sortino ratio:{sortino_ratio}\n' \
                'Calmar ratio:{calmar_ratio}\n' \
                'Information ratio:{information_ratio}\n'.format(annual_return=self.annual_return,
                                                                 alpha_p=self.alpha_p,
                                                                 sharpe_ratio=self.sharpe_ratio,
                                                                 max_drawdown=self.max_drawdown,
                                                                 sortino_ratio=self.sortino_ratio,
                                                                 calmar_ratio=self.calmar_ratio,
                                                                 information_ratio=self.information_ratio,
                                                                 annual_downside_risk=self.annual_downside_risk
                                                                 )

        return text

    __str__ = __repr__


class DataIndex(DataIndexBase, MetricStore):
    def __init__(self, periods):
        super().__init__(periods)
        # self.validator = validator


class DataIndexObj(DataIndex):
    def check_fund(self):
        if len(self.data) < self.periods:
            return False
        else:
            return True



if __name__ == '__main__':
    # file = os.path.join(r'C:\DATA\FUND\stock', '40000012_week_stock_id_1_rows_62.csv')
    # file = os.path.join(r'D:\OSEC\data\stock', '40000012_week_stock_id_1_rows_62.csv')
    file = os.path.join(r'D:\William\data\wealth_manage\FUND\futures', '40000921_week_futures_id_18_rows_50.csv')
    periods = 52
    data_index: DataIndexObj = DataIndexObj(periods=periods)

    out_put = data_index(file)
    print(data_index.data)
    # print(data_index)
    # print(out_put)
    print(data_index)
