# -*- coding: utf-8 -*-
# @Time    : 2019/6/14 17:24
# @Author  : Yibin Sun
# @File    : metric_store.py
# @Software: PyCharm
import copy
import empyrical
import pandas as pd
from data_handler.data_handler import DataHanlder
from config import WORKING_DIR


class MetricStore:
    def get_annual_return(self, data):
        data = copy.deepcopy(data)
        annu_ret1 = empyrical.annual_return(data.rets.dropna(), period='weekly')
        return annu_ret1

    def get_sharpe_ratio(self, data):
        data = copy.deepcopy(data)
        sharpe_ratio = empyrical.sharpe_ratio(data.rets.dropna(),
                                              risk_free=self.rft_ret / self.q,
                                              period='weekly')
        return sharpe_ratio

    def get_sortino_ratio(self, data):
        data = copy.deepcopy(data)
        sortino_ratio = empyrical.sortino_ratio(data.rets.dropna(),
                                                required_return=self.rft_ret / self.q,
                                                period='weekly'
                                                )
        return sortino_ratio

    def get_max_drawdown(self, data):
        df = copy.deepcopy(data)
        max_drawdown = empyrical.max_drawdown(df.rets.dropna())
        return abs(max_drawdown)

    def get_calmar_ratio(self, data):
        data = copy.deepcopy(data)
        calmar_ratio = empyrical.calmar_ratio(data.rets.dropna(), period='weekly')
        return calmar_ratio

    def get_info_ratio(self, data, is_stock_type=True):
        from algorithm.metrics import Metrics
        from utils.data_util import DataUtil

        data = copy.deepcopy(data)
        if is_stock_type:
            # index_300 = self.index300[self.index300.index.isin(df.index)]
            index300_close = self.index300_close.loc[data.index[0]:data.index[-1]]
            # index = pd.concat([data.rets, index_300],how='inner',axis=1).index

            # index300_close = index300_close.reindex(index=data.index)
            bm_ret = index300_close.pct_change().dropna()
            bm_ret = bm_ret.resample('W').last()
            # print(data.rets.dropna())
            # print('bm_ret:',bm_ret)
            IR = Metrics.metrics_ir(data.rets.dropna(), bm_ret, freq='weekly')
        else:
            data['bm_ret'] = self.rft_ret / self.q
            IR = Metrics.metrics_ir(data.rets.dropna(), data.bm_ret, freq='weekly')
        return IR

    def get_annual_downside_risk(self, data):  # 2.15%
        data = copy.deepcopy(data)
        rh = self.rft_ret / self.q
        downside_risk = empyrical.downside_risk(data.rets.dropna(), required_return=rh, period='weekly')
        return downside_risk

    def get_alpha_p(self, data, is_stock_type=True):  # we need to discuss this part-- wgs

        from algorithm.metrics import Metrics
        # result = Metrics.attr_alpha_beta()
        data = copy.deepcopy(data)
        if is_stock_type:
            index_300 = DataHanlder.get_index300_close(WORKING_DIR)
            index_300 = index_300.resample('W').last()
            combine = pd.merge(data, index_300, left_index=True, right_index=True, how='inner')
            # print('combine:',combine)
            combine['bmk_rets'] = combine.data.pct_change()
            # combine_excess = combine - self.rft_ret / self.q
            alpha, beta, alpha_p, beta_p = Metrics.attr_alpha_beta(data.rets, combine.bmk_rets,
                                                                   self.rft_ret / self.q)
        else:
            combine = data
            # combine['bmk_rets'] = self.rft_ret / self.q
            alpha, alpha_p = Metrics.attr_alpha(data.rets, self.rft_ret / self.q)

        return alpha_p
