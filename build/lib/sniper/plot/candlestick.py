from typing import List, Sequence, Union
from sniper.plot.interface import Plot
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid
from sniper.utils.expt import ModuleExt


# data = df[['date','open','close','low','high']]
# data=data.values.tolist()
# data=split_data(data)


class Candle(Plot):
    def __init__(self, data):
        self.__data = data
        self.kline = self.__gen_kline()

    def __gen_kline(self):
        if self.__data is None:
            raise ModuleExt(f'{self.__data}' is None)
        kline = Kline().add_xaxis(xaxis_data=[date.replace('-', '/') for date in self.__data["times"]]).add_yaxis(
            series_name="",
            y_axis=self.__data["datas"],
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
        ).set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True,
                                     #                                      boundary_gap=False,
                                     axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                                     splitline_opts=opts.SplitLineOpts(is_show=False),
                                     split_number=20,
                                     min_="dataMin",
                                     max_="dataMax",
                                     ),
            title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
                ),
            ],
        )
        return kline

    def plot(self):
        self.kline.render_notebook()
