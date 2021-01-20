import os
import numpy as np
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line, Scatter, Bar, Timeline, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.faker import Faker

data_name_list = ['example']


def draw_picture(df_all_list: list, data_name):
    # -------------------- 时间线轮播多图 --------------------
    # 实例化，并通过 opts.InitOpts 预设整幅图的尺寸
    tl = Timeline(init_opts=opts.InitOpts(width="1500px", height="750px"))
    # 坐标轴类型
    # label_opts=opts.LabelOpts(is_show=True, position="bottom") 表示在下方显示 label
    tl.add_schema(pos_bottom="bottom", is_auto_play=False, label_opts=opts.LabelOpts(is_show=True, position="bottom"))

    for i in range(len(df_all_list)):
        # -------------------- 数据预处理 --------------------
        df_all = df_all_list[i]
        df_all = df_all.set_index(pd.DatetimeIndex(pd.to_datetime(df_all.time)))
        df_all = df_all.fillna(np.nan)
        x_all = df_all['time'].tolist()
        y_all_list = {}
        y_all_list['data'] = df_all['data'].tolist()
        y_all_list['volume_diff'] = df_all['volume_diff'].tolist()
        y_all_list['buy'] = df_all["buy"].tolist()
        y_all_list['sell'] = df_all["sell"].tolist()

        if '价格' not in df_all.columns:
            y_all_list['价格'] = []
            y_all_list['数量'] = []
            y_all_list['操作'] = []
            for i in range(len(x_all)):
                y_all_list['价格'].append(np.nan)
                y_all_list['数量'].append(np.nan)
                y_all_list['操作'].append(np.nan)
        else:
            y_all_list['价格'] = df_all['价格'].tolist()
            y_all_list['数量'] = df_all['数量'].tolist()
            y_all_list['操作'] = df_all["操作"].tolist()

        y_buy = []
        for i in range(len(x_all)):
            if (y_all_list['操作'][i] == "买"):
                y_buy.append(y_all_list['价格'][i])
            else:
                y_buy.append(np.nan)
        y_sell = []
        for i in range(len(x_all)):
            if (y_all_list['操作'][i] == "卖"):
                y_sell.append(y_all_list['价格'][i])
            else:
                y_sell.append(np.nan)

        text1 = []
        for i in range(len(x_all)):
            if (y_all_list['操作'][i] == "买"):
                one_text = []
                one_text.append(x_all[i])
                one_text.append(y_all_list['价格'][i])
                one_text.append(y_all_list['数量'][i])
                one_text.append(y_all_list['操作'][i])
                text1.append(one_text)

        text2 = []
        for i in range(len(x_all)):
            if (y_all_list['操作'][i] == "卖"):
                one_text = []
                one_text.append(x_all[i])
                one_text.append(y_all_list['价格'][i])
                one_text.append(y_all_list['数量'][i])
                one_text.append(y_all_list['操作'][i])
                text2.append(one_text)

        # -------------------- 数据预处理结束 --------------------

        # 设置标记点
        mark_data_list1 = []
        for i in range(len(text1)):
            mark_data_list1.append(opts.MarkPointItem(name="操作", coord=[text1[i][0], text1[i][1]], value=text1[i][2]))
        mark_data_list2 = []
        for i in range(len(text2)):
            mark_data_list2.append(opts.MarkPointItem(name="操作", coord=[text2[i][0], text2[i][1]], value=text2[i][2]))

        title = " 数据 " + data_name
        time = x_all[0].split(' ')[0]

        # -------------------- 画图主体 --------------------
        # ---------- Line: 折线图 ----------
        # ----- 参数设置 - 第一部分 - 基础设置 - add_xaxis + add_yaxis
        # add_xaxis: 设置 x 轴，坐标值为 x_all
        # add_yaxis: 设置 y 轴，此图集成 3 条折线
        # 坐标值分别为 y_all_list["data"]，y_all_list["buy"]，y_all_list["sell"]
        # label_opts=opts.LabelOpts(is_show=False) 表示折线上不显示取值
        # itemstyle_opts=opts.ItemStyleOpts(color="#41ae3c") 设置折线颜色
        #
        #
        # ----- 参数设置 - 第二部分 - 全局属性 - set_global_opts
        #
        # 标题配置项: title_opts=opts.TitleOpts(title=title, pos_top="top", pos_left='center', pos_right='center'):
        # - 设置折线图的标题内容 title，位置属性 pos_top、pos_left、pos_right
        #
        # 坐标轴配置项: xaxis_opts=opts.AxisOpts(type_="category", name='时间', boundary_gap=False, axisline_opts=opts.AxisLineOpts(is_on_zero=True)),
        # - 设置 x 轴坐标轴属性，
        # - type_ 设置坐标轴类型，'category' 为类目轴，适用于离散的类目数据；
        # - name 设置坐标轴名称；
        # - boundary_gap 设置坐标轴两边留白策略；
        # - axisline_opts=opts.AxisLineOpts() 设置坐标轴刻度线配置项，is_on_zero=True 表示 X 轴或者 Y 轴的轴线在另一个轴的 0 刻度上；
        #
        # 坐标轴配置项：yaxis_opts=opts.AxisOpts(type_="value", is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)),
        # - 设置 y 轴坐标轴属性，
        # - type_ 设置坐标轴类型，'value'为数值轴，适用于连续数据；
        # - is_scale 只在数值轴中（type: 'value'）有效，表示是否是脱离 0 值比例，设置成 true 后坐标刻度不会强制包含零刻度；
        # - splitline_opts=opts.SplitLineOpts() 设置分割线配置项，is_show 表示是否显示分割线；
        #
        # 图例配置项：legend_opts=opts.LegendOpts(pos_left="right"),
        # - pos_left 设置图例组件离容器左侧的距离；
        #
        # 提示框配置项：tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        # - trigger 设置触发类型， 'axis'表示坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用；
        # - axis_pointer_type 设置指示器类型， 'cross'为十字准星指示器。其实是种简写，表示启用两个正交的轴的 axisPointer；
        #
        # 坐区域缩放配置项：
        # datazoom_opts=[
        #     opts.DataZoomOpts(is_realtime=True, type_="inside", xaxis_index=[0, 1], range_start=15, range_end=85),
        #     opts.DataZoomOpts(is_realtime=True, type_="slider", xaxis_index=[0, 1], range_start=15, range_end=85, pos_bottom='55px'),
        # ],
        # - is_realtime 设置拖动时，是否实时更新系列的视图；
        # - type_ 设置组件类型，"inside"表示可以在图内使用鼠标滚轮进行图的缩放，"slider"表示拖动滑动条进行缩放；
        # - xaxis_index 设置 dataZoom-inside 组件控制的 x 轴；
        # - range_start 设置数据窗口范围的起始百分比，范围是：0 ~ 100，表示 0% ~ 100%；
        # - range_end 设置数据窗口范围的结束百分比，范围是：0 ~ 100，表示 0% ~ 100%；
        # - pos_bottom 设置 dataZoom-slider 组件离容器下侧的距离；
        line = (
            Line()
                .add_xaxis(xaxis_data=x_all)
                .add_yaxis(
                series_name="data", y_axis=y_all_list["data"],
                linestyle_opts=opts.LineStyleOpts(),
                # itemstyle_opts=opts.ItemStyleOpts(color="#2F4554"),
                label_opts=opts.LabelOpts(is_show=False), )
                .add_yaxis(
                series_name="buy", y_axis=y_all_list["buy"],
                linestyle_opts=opts.LineStyleOpts(),
                # itemstyle_opts=opts.ItemStyleOpts(color="#a61b29"),
                label_opts=opts.LabelOpts(is_show=False), )
                .add_yaxis(
                series_name="sell", y_axis=y_all_list["sell"],
                linestyle_opts=opts.LineStyleOpts(),
                # itemstyle_opts=opts.ItemStyleOpts(color="#41ae3c"),
                label_opts=opts.LabelOpts(is_show=False), )
                .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_top="top", pos_left='center', pos_right='center'),
                xaxis_opts=opts.AxisOpts(type_="category", name='时间', boundary_gap=False,
                                         axisline_opts=opts.AxisLineOpts(is_on_zero=True)),
                yaxis_opts=opts.AxisOpts(type_="value", is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)),
                legend_opts=opts.LegendOpts(pos_left="right"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                datazoom_opts=[
                    opts.DataZoomOpts(is_realtime=True, type_="inside", xaxis_index=[0, 1], range_start=15,
                                      range_end=85),
                    opts.DataZoomOpts(is_realtime=True, type_="slider", xaxis_index=[0, 1], range_start=15,
                                      range_end=85, pos_bottom='55px'),
                ],
            )
        )

        # ---------- Scatter: 散点图 ----------
        # add_xaxis: 设置 x 轴，坐标值为 x_all，同上面的折线图横轴；
        # add_yaxis: 设置 y 轴；
        # label_opts=opts.LabelOpts(is_show=False) 表示点上不显示取值；
        # 标记点配置项：markpoint_opts=opts.MarkPointOpts(data=mark_data_list1, symbol_size=40, label_opts=opts.LabelOpts(position="inside", color="#fff", font_size=8),)
        # 设置散点上标记点；
        # - data 标记点数据，参考 `series_options.MarkPointItem`；
        # - symbol_size 设置标记的大小，可以设置成诸如 10 这样单一的数字，也可以用数组分开表示宽和高；
        # - label_opts=opts.LabelOpts() 设置标签配置项，参考 `series_options.LabelOpts`；
        scatter1 = (
            Scatter()
                .add_xaxis(xaxis_data=x_all)
                .add_yaxis(
                series_name="发生点-买", y_axis=y_buy,
                label_opts=opts.LabelOpts(is_show=False),
                # itemstyle_opts=opts.ItemStyleOpts(color="#621624"),
                markpoint_opts=opts.MarkPointOpts(symbol_size=40,
                                                  data=mark_data_list1,
                                                  label_opts=opts.LabelOpts(position="inside", color="#fff",
                                                                            font_size=8), )
            )
                .set_global_opts(
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
        )

        scatter2 = (
            Scatter()
                .add_xaxis(xaxis_data=x_all)
                .add_yaxis(
                series_name="发生点-卖", y_axis=y_sell,
                label_opts=opts.LabelOpts(is_show=False),
                # itemstyle_opts=opts.ItemStyleOpts(color="#223e36"),
                markpoint_opts=opts.MarkPointOpts(symbol_size=40,
                                                  data=mark_data_list2,
                                                  label_opts=opts.LabelOpts(position="inside", color="#fff",
                                                                            font_size=8), )
            )
                .set_global_opts(
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
        )

        # 将两个散点图叠加到折线图上
        line.overlap(scatter1)
        line.overlap(scatter2)

        # ---------- Bar: 柱状图 ----------
        # add_xaxis: 设置 x 轴，坐标值为 x_all，同上面的折线图、散点图横轴；
        # add_yaxis: 设置 y 轴；
        bar = (
            Bar()
                .add_xaxis(xaxis_data=x_all)
                .add_yaxis(
                series_name="volume_diff", y_axis=y_all_list['volume_diff'],
                itemstyle_opts=opts.ItemStyleOpts(color="#123456"),
                label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="category", name='时间',
                                         axisline_opts=opts.AxisLineOpts(is_on_zero=True)),
                yaxis_opts=opts.AxisOpts(type_="value", is_scale=True,
                                         splitline_opts=opts.SplitLineOpts(is_show=True),
                                         ),
                legend_opts=opts.LegendOpts(pos_left="left", is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                datazoom_opts=[
                    opts.DataZoomOpts(is_realtime=True, type_="inside", xaxis_index=[0, 1], range_start=15,
                                      range_end=85),
                    opts.DataZoomOpts(is_realtime=True, type_="slider", xaxis_index=[0, 1], range_start=15,
                                      range_end=85, pos_bottom='55px'),
                ],
            )
        )

        # ---------- Grid: 并行多图 ----------
        # 增加 折线图、柱状图 两个图表实例，上为折线图，下为柱状图
        grid = (
            Grid()
                .add(line, grid_opts=opts.GridOpts(pos_left=100, pos_right=100, height="35%"))
                .add(bar, grid_opts=opts.GridOpts(pos_left=100, pos_right=100, pos_top="50%", pos_bottom="15%",
                                                  height="35%"))
        )

        # 时间线轮播多图添加图表实例
        tl.add(grid, "{}".format(time))

    # render 会生成本地 HTML 文件，默认会在当前目录生成 .html 文件，使用浏览器打开即可
    tl.render("数据" + data_name + "_all.html")


if __name__ == "__main__":
    root_path_all = "./data/"
    all_file_list = os.listdir(root_path_all)

    for data_name in data_name_list:
        df_all_list = []

        for day_folder in all_file_list:
            root_path_all_day = os.path.join(root_path_all, day_folder)
            csvfiles = os.listdir(root_path_all_day)
            for file in csvfiles:
                if data_name in file:
                    all_file_path = os.path.join(root_path_all, day_folder, file)
                    df_all = pd.DataFrame(pd.read_csv(all_file_path, encoding='gbk'))
                    df_all_list.append(df_all)

        draw_picture(df_all_list, data_name)
