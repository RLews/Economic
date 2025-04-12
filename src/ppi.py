import qstock as qs
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from pyecharts.charts import Grid, Line
from pyecharts import options as opts
import numpy as np
import plotly.express as px

def get_ppi():
    # 获取CPI数据
    ppi_data = qs.ppi()
    # 检查数据框的列名
    print("PPI数据的列名：", ppi_data.columns)
    
    # 确保数据框中包含 '月份' 列
    if '月份' in ppi_data.columns:
        # 指定日期格式并转换 '月份' 列
        ppi_data['月份'] = pd.to_datetime(ppi_data['月份'], format='%Y年%m月份')
        # 提取年份
        ppi_data['year'] = ppi_data['月份'].dt.year
        # 筛选1980年至今的数据
        ppi_data = ppi_data[ppi_data['year'] >= 1980]
    else:
        print("数据框中没有 '月份' 列，请检查数据结构并调整代码。")
    
    # 保存为Excel文件
    ppi_data.to_excel('../date/qstock_china_ppi_1980_2025.xlsx', index=False)
    
    # 前向填充缺失值
    ppi_data = ppi_data.ffill()
    # 转换为 Pandas 时间序列
    ppi_data.index = pd.to_datetime(ppi_data.index)
    
    # 生成格式化日期列表（用于 pyecharts）
    date_list = ppi_data['月份'].apply(lambda x: f"{x.year}-{x.month:02d}").tolist()[::-1]
    values = ppi_data['当月'].round(2).tolist()[::-1]
    # 计算动态范围
    y_min = np.floor(min(values) / 5) * 5
    y_max = np.ceil(max(values) / 5) * 5
    line = (
        Line(init_opts=opts.InitOpts(theme="chalk", width="1200px", height="600px"))
        .add_xaxis(date_list)
        .add_yaxis(
            series_name="PPI同比增速(%)",
            y_axis=values,
            is_smooth=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(width=3),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="中国PPI同比增速趋势（1980-2025）", subtitle="数据来源：qstock宏观经济数据库 CPI（居民消费价格指数）"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
            xaxis_opts=opts.AxisOpts(name="年份", axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(name="同比增速(%)", min_=y_min, max_=y_max),
        )
    )
    # 生成交互式 HTML
    line.render("../date/qstock_ppi_trend_pyecharts.html")


if __name__ == '__main__':
    get_ppi()

