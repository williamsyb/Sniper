# -*- coding: utf-8 -*-
# @Time     : 2019/5/22 17:28
# Author    ： Wang Guosong
# @File     : test_pf_cup.py
# @Software : PyCharm
import traceback

import numpy as np
import pandas as pd
import statsmodels.api as sm
import scipy.stats as ss
import empyrical
from utils.data_util import DataUtil
import sqlalchemy
import os

annual_factor = {"weekly": 52}


class Base:
    pass


class Metrics(Base):

    @staticmethod
    def attr_alpha_beta(ra, rb, rf=0.03 / 52, freq='weekly'):
        ret = pd.concat([ra, rb], axis=1, join='inner').dropna()
        ret.columns = ['ra', 'rb']
        # print('ra:',ra)
        # print('rb:',rb)
        ret = ret - rf

        x = sm.add_constant(ret['rb'])
        y = ret['ra']
        try:
            model = sm.OLS(y, x)
            results = model.fit()
            alpha = results.params['const'] * annual_factor[freq]
            beta = results.params['rb']
            # alpha_p = results.pvalues['const']
            alpha_p = ss.t.sf(results.tvalues[0], results.df_resid)
            beta_p = results.pvalues['rb']
            return alpha, beta, alpha_p, beta_p
        except ValueError:
            traceback.print_exc()
            return None, None, None, None

    @staticmethod
    def attr_alpha(ra, rf=0, freq='weekly'):
        rb = pd.Series(1, index=ra.index)
        ret = pd.concat([ra, rb], axis=1, join='inner').dropna()
        ret.columns = ['ra', 'rb']
        ret = ret - rf
        # ret['rb'] = 1

        x = sm.add_constant(ret['rb'])
        y = ret['ra']
        try:
            model = sm.OLS(y, x)
            results = model.fit()
            # alpha = results.params['const'] * annual_factor[freq]
            alpha = results.params['rb'] * annual_factor[freq]
            # alpha_p = results.pvalues['const']
            alpha_p = ss.t.sf(results.tvalues[0], results.df_resid)
            # alpha_p = ss.t.sf(results.tvalues[0], results.df_resid)
            # beta_p = results.pvalues['rb']
            return alpha, alpha_p
        except ValueError:
            traceback.print_exc()
            return None, None

    @staticmethod
    def alpha_ttest(ra, rf=0, freq='weekly'):
        from scipy import stats

        rb = pd.Series(rf, index=ra.index)
        rb = pd.Series(0.03 / 52, index=ra.index)

        ret = pd.concat([ra, rb], axis=1, join='inner').dropna()
        ret.columns = ['ra', 'rb']

        results = stats.ttest_rel(ret['ra'], ret['rb'])
        alpha = (ret['ra'] - ret['rb']).mean() * annual_factor[freq]
        alpha_p = results.pvalue / 2

        return alpha, alpha_p

    @staticmethod
    def active_premium(ra, rb, freq='weekly'):

        active_premium = empyrical.annual_return(ra, period=freq) - \
                         empyrical.annual_return(rb, period=freq)

        return active_premium

    @staticmethod
    def metrics_ir(ra, rb, freq='weekly'):
        ret = pd.concat([ra, rb], axis=1, join='inner').dropna()
        ret.columns = ['ra', 'rb']

        # print('ra:', ra)
        # print('rb:', rb)
        track_error_annual = np.nan_to_num(np.nanstd(ret['ra'] - ret['rb'], ddof=1, axis=0)) \
                             * np.sqrt(annual_factor[freq])
        # print('track_error_annual:', track_error_annual)
        _active_premium = Metrics.active_premium(ret['ra'], ret['rb'], freq='weekly')
        metrics_ir = _active_premium / track_error_annual

        return metrics_ir


class Returns(Base):
    pass


if __name__ == '__main__':

    # engine_dys = sqlalchemy.create_engine('oracle+cx_oracle://cfgl_cfyj:cfgl_cfyj123@10.45.5.21:1521/sjcj')
    # con_dys = engine_dys.connect()

    # sql = "SELECT SECURITY_ID, END_DATE, ACCUM_NAV FROM TLSJ.PFUND_NAV WHERE SECURITY_ID = 40000012" \
    #       "AND END_DATE >  TO_DATE('2018-04-26', 'YYYY-MM-DD')";
    temp=os.path.join(r'D:\OSEC\data\stock', '40000012_week_stock_id_1_rows_62.csv')
    file = os.path.join(r'C:\DATA\FUND\stock', '40181371_week_stock_id_1_rows_90.csv')
    fund_nav = pd.read_csv(file)

    # fund_nav = pd.read_sql(sql, con_dys)
    # fund_nav.set_index(fund_nav['end_date'], inplace=True)
    # fund_nav['trade_dt'] = pd.to_datetime(bm_nav['trade_dt'], format='%Y%m%d')
    fund_nav_xts = DataUtil.df_to_series(fund_nav[['end_date', 'accum_nav']])

    engine_wind = sqlalchemy.create_engine('oracle+cx_oracle://xiakun:Xiakun*123456@172.17.21.3:1521/wdzx')
    con_wind = engine_wind.connect()

    sql = "SELECT TRADE_DT, S_DQ_CLOSE FROM WIND_FILESYNC.AINDEXEODPRICES WHERE S_INFO_WINDCODE = 'h00300.CSI'"\
        "AND TRADE_DT > '2018-04-26'"


    bm_nav = pd.read_sql(sql, con_wind)
    bm_nav['trade_dt'] = pd.to_datetime(bm_nav['trade_dt'], format='%Y%m%d')
    bm_nav_xts = DataUtil.df_to_series(bm_nav).reindex(fund_nav_xts.index)

    ra = empyrical.simple_returns(fund_nav_xts)
    rb = empyrical.simple_returns(bm_nav_xts)
    ret_annual = empyrical.annual_return(ra, "weekly")
    # Metrics.active_premium(ra,rb)
    # metric = Metrics()
    print("RA:", ra)
    print("Rb:", rb)
    ir = Metrics.metrics_ir(ra, rb)
    print(ret_annual, ir)
