import pandas as pd
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt
import akshare as ak
import time
from typing import Union, List
from loguru import logger
from sniper.utils.expt import ModuleExt
import talib as ta
from sniper.utils import LazyFunc, sleep
from pyecharts import options as opts
from pyecharts.charts import Map, Bar, Grid, Page, Line
from pyecharts.globals import ChartType, ThemeType
import random
import talib as ta


class Fund:
    def __init__(self):
        self.__all_funds: pd.DataFrame = self.__get_all_funds()

    @LazyFunc
    def all_funds(self):
        return self.__all_funds

    def __get_all_funds(self) -> pd.DataFrame:
        logger.info("初始化全量基金")
        fund_cate = ak.fund_em_fund_name()
        fund_cate.rename(columns={'基金类型': 'fund_type', '基金简称': 'fund_name', '基金代码': 'fund_code'},
                         inplace=True)
        fund_cate = fund_cate[['fund_code', 'fund_name', 'fund_type']]
        return fund_cate

    def search(self, name: Union[str, List], type_list=[], default_type='C') -> pd.DataFrame:
        if isinstance(name, str):
            names = [name]
        elif isinstance(name, list):
            names = name
        else:
            raise ModuleExt("不支持参数类型")
        df_li = []
        for name_ in names:
            df = self.__all_funds[(self.__all_funds.fund_name.str.contains(name_)) & (
                self.__all_funds.fund_type.isin(type_list) if len(type_list) > 0 else True) & (
                                       self.__all_funds.fund_name.str.contains(
                                           default_type) if default_type != '' else True)]

            df_li.append(df)
        return pd.concat(df_li)

    def combine_data(self, start, end, mat: pd.DataFrame, batch=30):
        df_list = []
        for ix, row in list(mat.iterrows()):
            sleep(1)
            fund_code = row['fund_code']
            fund_name = row['fund_name']
            try:
                fund_em_info_df = ak.fund_em_open_fund_info(fund=fund_code)
            except:
                logger.warning(f'获取 {fund_code}-{fund_name} 失败')
                continue
            fund_em_info_df.rename(columns={'净值日期': 'Date', '单位净值': 'price', '日增长率': 'ret'}, inplace=True)
            fund_em_info_df.Date = pd.to_datetime(fund_em_info_df.Date)
            fund_em_info_df.price = fund_em_info_df.price.astype(float)
            fund_em_info_df.set_index('Date', inplace=True)

            fund_em_info_df.rename(columns={'price': fund_name}, inplace=True)
            df_list.append(fund_em_info_df[[fund_name]])
        total_df = pd.concat(df_list, axis=1)
        total_df = total_df.loc[start:end, :]
        return total_df

    def plot(self, total_df):
        page = Page(layout=Page.DraggablePageLayout)
        dates = [date.strftime('%Y-%m-%d') for date in total_df.index]
        for column in total_df.columns[:]:
            tmp = total_df[[column]]
            tmp.fillna(method='bfill', inplace=True)  # 应该用前一天，但是为了画图，这里用了后一天，对总体影响不大
            ma5 = tmp.rolling(5).mean()
            ma5.fillna(method='bfill', inplace=True)
            ma5 = round(ma5, 4)
            ma10 = tmp.rolling(10).mean()
            ma10.fillna(method='bfill', inplace=True)
            ma10 = round(ma10, 4)
            ma20 = tmp.rolling(20).mean()
            ma20.fillna(method='bfill', inplace=True)
            ma20 = round(ma20, 4)
            ma40 = tmp.rolling(40).mean()
            ma40.fillna(method='bfill', inplace=True)
            ma40 = round(ma40, 4)
            upper, middle, lower = ta.BBANDS(tmp[column].values, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            c = (
                Line(init_opts=opts.InitOpts(height="300px", width='100%', bg_color="white"))
                    .add_xaxis(dates)
                    .add_yaxis(
                    '',
                    tmp.values.tolist(),
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#FF0000", width=2),
                    markpoint_opts=opts.MarkPointOpts(
                        data=[opts.MarkPointItem(type_="min"), opts.MarkPointItem(type_="max")])
                )
                    .add_yaxis(
                    '',
                    upper,
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#404040", width=0.5)
                    #             markpoint_opts=opts.MarkPointOpts(),
                )
                    .add_yaxis(
                    '',
                    middle,
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#404040", width=0.5)
                    #             markpoint_opts=opts.MarkPointOpts(),
                )
                    .add_yaxis(
                    '',
                    lower,
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#404040", width=0.5)
                    #             markpoint_opts=opts.MarkPointOpts(),
                )
                    .add_yaxis(
                    "ma5",
                    ma5.values.tolist(),
                    symbol="emptyCircle",
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#0000FF", width=1)
                )
                    .add_yaxis(
                    "ma10",
                    ma10.values.tolist(),
                    symbol="emptyCircle",
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#000000", width=1)

                )
                    .add_yaxis(
                    "ma20",
                    ma20.values.tolist(),
                    symbol="emptyCircle",
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#006400", width=1)
                )
                    .add_yaxis(
                    "ma40",
                    ma40.values.tolist(),
                    symbol="emptyCircle",
                    is_symbol_show=False,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(color="#800080", width=1)
                )
                    .set_global_opts(title_opts=opts.TitleOpts(title=column),
                                     xaxis_opts=opts.AxisOpts(is_scale=True),
                                     yaxis_opts=opts.AxisOpts(is_scale=True,
                                                              axistick_opts=opts.AxisTickOpts(is_show=True),
                                                              splitline_opts=opts.SplitLineOpts(is_show=True), ),
                                     toolbox_opts=opts.ToolboxOpts(
                                        #  feature=opts.ToolBoxFeatureOpts(
                                        #                            save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                                        #                                 type_="png",
                                        #                                 background_color='white',
                                        #                                  pixel_ratio=15))
                                                                         ),
                                     tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                                     datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100),
                                                    opts.DataZoomOpts(type_="inside"), ]
                                     )
                    .set_series_opts(
                    label_opts=opts.LabelOpts(is_show=False),
                    #             markpoint_opts=opts.MarkPointOpts(
                    #                 data=[
                    #                     opts.MarkPointItem(type_="max", name="最大值"),
                    #                     opts.MarkPointItem(type_="min", name="最小值"),
                    #                     opts.MarkPointItem(type_="average", name="平均值"),
                    #                 ]
                    #             ),
                )
            )
            page.add(c)
        page.render_notebook()
        return page
