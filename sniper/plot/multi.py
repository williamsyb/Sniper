from sniper.plot.interface import Plot
from typing import Dict
import pandas as pd
import numpy as np
from datetime import datetime as dt
from sniper.env import g_plt_figsize
from copy import deepcopy
from zhdate import ZhDate
import math
from sniper.utils.expt import ModuleExt
from matplotlib import pyplot as plt

plt.style.use('ggplot')


class M(Plot):
    def __init__(self, data: Dict[str, pd.DataFrame], **kwargs):
        self.__data = data
        self.__size = len(data)
        self.__cur_col = 'close'
        self.__col_num = kwargs.pop('grid', 4)  # 默认使用3列
        self.__row_num = math.ceil(self.__size / self.__col_num)
        self.__storage = {}
        self.__special_dates = []
        self.__special_dates_chinese = []
        self.__start = None
        self.__sharex = True
        self.__end = dt.now().strftime("%Y%m%d")
        self.__favorite = []
        self.__initialize()

    @property
    def special_dates(self):
        return self.__special_dates

    def set_special_dates(self, dates):
        self.__special_dates_chinese = [str(date) for date in dates] if len(dates) > 0 else dates
        dates = [date.to_datetime() for date in dates] if len(dates) > 0 else dates
        self.__special_dates = dates

    @property
    def special_dates_chinese(self):
        return self.__special_dates_chinese

    @property
    def favorite(self):
        return self.__favorite

    def set_favorite(self, li: list):
        self.__favorite = li
        if len(li) == 0:
            self.__size = len(self.__data)
            self.__row_num = math.ceil(self.__size / self.__col_num)
        else:
            self.__size = len(li)
            self.__row_num = math.ceil(self.__size / self.__col_num)

    def __initialize(self):
        self.__store_data()

    def set_col_num(self, n):
        if n < 1 or not isinstance(n, int):
            raise ModuleExt('不能设置列数小于1或者非自然数')
        self.__col_num = n
        self.__row_num = math.ceil(self.__size / self.__col_num)

    def set_col(self, col: str):
        self.__cur_col = col
        self.__store_data()

    def set_periods(self, start, end):
        self.__start = start
        self.__end = end

        self.__store_data()

    def __store_data(self):
        for data_name in self.data_names:
            kline_data = self.__data[data_name][:]
            # print('kline_data:', kline_data)
            kline_data.date = pd.to_datetime(kline_data.date)
            kline_data.set_index('date', inplace=True)
            kline_data.sort_index(inplace=True)
            kline_data = kline_data.loc[self.__start: self.__end,
                         :] if self.__start is not None and self.__end is not None else kline_data

            price = kline_data[self.__cur_col]
            price = pd.DataFrame(price)
            # price['returns'] = np.log(price / price.shift(1))
            price.dropna(inplace=True)
            self.__storage[data_name] = price

    @property
    def data_names(self):
        return list(self.__data.keys())

    def set_sharex(self, flag: bool):
        self.__sharex = flag

    def plot(self):
        # plt.subplots(figsize=ABuEnv.g_plt_figsize)
        # # tl装载技术线本体
        # plt.plot(self.tl)
        # plt.axhline(self.high, color='c')
        # plt.axhline(self.mean, color='r')
        # plt.axhline(self.low, color='g')
        # _ = plt.setp(plt.gca().get_xticklabels(), rotation=30)
        # plt.legend(['TLine', 'high', 'mean', 'low'],
        #            bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        # plt.title(self.line_name)
        # plt.show()
        fig, ax = plt.subplots(self.__row_num, self.__col_num,
                               sharex=self.__sharex,
                               # sharey=True,
                               figsize=(20, 4 * self.__row_num),
                               facecolor='#ccddef'
                               )
        count = 0
        data_names = self.data_names if len(self.__favorite) == 0 else self.__favorite
        for ix, data_name in enumerate(data_names):
            if len(self.__favorite) > 0 and data_name in self.__favorite:

                cur_row = count // self.__col_num
                cur_col = count % self.__col_num
                price = self.__storage[data_name]
                ax[cur_row, cur_col].plot(price[self.__cur_col], label=f'{data_name} {self.__cur_col}', ms=3)
                ax[cur_row, cur_col].set(title=f'{data_name} {self.__cur_col} Price', ylabel='Price')

                # 标记重要节日
                if len(self.__special_dates) > 0:
                    for jx, special_date in enumerate(self.__special_dates):
                        x = price.loc[:special_date].index[-1]  #  由于节假日不是交易，在画图时需要得到最后一个交易日
                        y = price.loc[x, self.__cur_col]

                        text = self.__special_dates_chinese[jx]
                        ax[cur_row, cur_col].annotate(text, xy=(x, y), xytext=(x, y * 1.05),
                                                      # xycoords='data',
                                                      arrowprops=dict(facecolor='black', shrink=0.05)
                                                      )

                ax[cur_row, cur_col].grid(True)
                ax[cur_row, cur_col].legend()
                count += 1
            if len(self.__favorite) == 0:
                cur_row = count // self.__col_num
                cur_col = count % self.__col_num
                price = self.__storage[data_name]
                ax[cur_row, cur_col].plot(price[self.__cur_col], label=f'{data_name} {self.__cur_col}', ms=3)
                ax[cur_row, cur_col].set(title=f'{data_name} {self.__cur_col} Price', ylabel='Price')
                # 标记重要节日
                if len(self.__special_dates) > 0:
                    for jx, special_date in enumerate(self.__special_dates):
                        x = special_date
                        y = price.loc[x, self.__cur_col]
                        text = self.__special_dates_chinese[jx]
                        ax[cur_row, cur_col].annotate(text, xy=(x, y), xytext=(x, y * 1.05),
                                                      # xycoords='data',
                                                      arrowprops=dict(facecolor='black', shrink=0.05)
                                                      )
                ax[cur_row, cur_col].grid(True)
                ax[cur_row, cur_col].legend()
                count += 1
        fig.autofmt_xdate(rotation=45)
        fig.subplots_adjust(left=0.2, bottom=0.1, right=0.8, top=0.8, hspace=0.5)
