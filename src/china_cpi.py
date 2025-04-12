import qstock as qs
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from pyecharts.charts import Grid, Line
from pyecharts import options as opts
import numpy as np
import plotly.express as px

def get_cpi():
    # 获取CPI数据
    cpi_data = qs.cpi()
    # 检查数据框的列名
    print("CPI数据的列名：", cpi_data.columns)
    
    # 确保数据框中包含 '月份' 列
    if '月份' in cpi_data.columns:
        # 指定日期格式并转换 '月份' 列
        cpi_data['月份'] = pd.to_datetime(cpi_data['月份'], format='%Y年%m月份')
        # 提取年份
        cpi_data['year'] = cpi_data['月份'].dt.year
        # 筛选1980年至今的数据
        cpi_data = cpi_data[cpi_data['year'] >= 1980]
    else:
        print("数据框中没有 '月份' 列，请检查数据结构并调整代码。")
    
    # 保存为Excel文件
    cpi_data.to_excel('../date/qstock_china_cpi_1980_2025.xlsx', index=False)
    
    # 前向填充缺失值
    cpi_data = cpi_data.ffill()
    # 转换为 Pandas 时间序列
    cpi_data.index = pd.to_datetime(cpi_data.index)
    
    # 生成格式化日期列表（用于 pyecharts）
    date_list = cpi_data['月份'].apply(lambda x: f"{x.year}-{x.month:02d}").tolist()
    values = cpi_data['全国当月'].round(2).tolist()
    # 计算动态范围
    y_min = np.floor(min(values) / 5) * 5
    y_max = np.ceil(max(values) / 5) * 5
    line = (
        Line(init_opts=opts.InitOpts(theme="chalk", width="1200px", height="600px"))
        .add_xaxis(date_list)
        .add_yaxis(
            series_name="CPI同比增速(%)",
            y_axis=values,
            is_smooth=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(width=3),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="中国CPI同比增速趋势（1980-2025）", subtitle="数据来源：qstock宏观经济数据库 CPI（居民消费价格指数）"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
            xaxis_opts=opts.AxisOpts(name="年份", axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(name="同比增速(%)", min_=y_min, max_=y_max),
        )
    )
    # 生成交互式 HTML
    line.render("../date/qstock_cpi_trend_pyecharts.html")
        
    # FRED 中中国 CPI 的代码为 CHNCPIALLMINMEI（1960年起，月度数据）
    cpi_fred = pdr.DataReader(
        'CHNCPIALLMINMEI',  # 经济指标代码
        'fred',             # 数据源标识（FRED）
        start='1960-01',    # 起始时间（支持年、年月、年月日格式）
        end='2025-03'       # 结束时间（默认到最新数据）
    )
    
    # 重命名列名并清理索引
    cpi_fred.columns = ['CPI']
    cpi_fred.index.name = 'Date'
    # 计算同比增速： (当前月CPI / 上年同月CPI - 1) * 100
    cpi_fred['CPI同比'] = cpi_fred['CPI'].pct_change(periods=12) * 100  # 网页2[2](@ref)
    cpi_fred = cpi_fred.dropna(subset=['CPI同比'])  # 删除前12个月无同比数据的行
    
    # 处理缺失值（线性插值，针对后续月份可能的数据缺失）
    cpi_fred['CPI同比'] = cpi_fred['CPI同比'].interpolate(method='time')  # 网页2[2](@ref)
    # 前向填充缺失值（适用于连续少量缺失）
    # cpi_fred = cpi_fred.ffill()
    # 或线性插值（适用于趋势平稳数据）
    # cpi_fred = cpi_fred.interpolate(method='linear')
    
    # 保存为 Excel（需安装 openpyxl）
    cpi_fred.to_excel('../date/fred_china_cpi.xlsx', sheet_name='CPI')
    
    # 生成格式化日期列表（用于 pyecharts）
    date_list = cpi_fred.index.strftime("%Y-%m").tolist()
    values = cpi_fred['CPI同比'].round(2).tolist()
    # 计算动态范围
    y_min = np.floor(min(values) / 5) * 5
    y_max = np.ceil(max(values) / 5) * 5
    line = (
        Line(init_opts=opts.InitOpts(theme="chalk", width="1200px", height="600px"))
        .add_xaxis(date_list)
        .add_yaxis(
            series_name="CPI同比增速(%)",
            y_axis=values,
            is_smooth=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(width=3),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="中国CPI同比增速趋势（1980-2025）", subtitle="数据来源：fred数据库"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
            xaxis_opts=opts.AxisOpts(name="年份", axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(name="同比增速(%)", min_=y_min, max_=y_max),
        )
    )
    # 生成交互式 HTML
    line.render("../date/fred_cpi_trend_pyecharts.html")
        

if __name__ == '__main__':
    get_cpi()

