# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 21:35:26 2025

@author: Administrator
"""

import pandas as pd
from pandas_datareader import data as pdr
from pyecharts import options as opts
from pyecharts.charts import Line


def get_ppi():
    # 设置时间范围（1980年至今）
    start_date = '1980-01-01'
    end_date = pd.to_datetime('today').strftime('%Y-%m-%d')
    
    # FRED数据代码：PPIACO（生产者价格指数，季调）
    ppi = pdr.DataReader('PPIACO', 'fred', start_date, end_date)
    
    # 转换为月度数据并计算同比变化率
    ppi_monthly = ppi.resample('M').last()
    ppi_monthly['YoY'] = ppi_monthly['PPIACO'].pct_change(12) * 100  # 年同比涨幅
    
    # 重置索引并格式化日期
    ppi_clean = ppi_monthly.reset_index()
    ppi_clean['Date'] = ppi_clean['DATE'].dt.strftime('%Y-%m')  # 转为YYYY-MM格式
    
    # 筛选1980年后的数据并处理缺失值
    ppi_final = ppi_clean[ppi_clean['DATE'] >= '1980-01-01'][['Date', 'YoY']].dropna()
    
    ppi_final['MA12'] = ppi_final['YoY'].rolling(window=12).mean()
    
    ppi_final.to_excel('../date/fred_us_ppi.xlsx', sheet_name='PPI')
    
    # 数据拆分
    x_data = ppi_final['Date'].tolist()
    y_data = ppi_final['YoY'].round(2).tolist()
    
    # 创建折线图
    line = (
        Line(init_opts=opts.InitOpts(width="1600px", height="800px", theme="essos"))
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="PPI同比涨幅(%)",
            y_axis=y_data,
            is_smooth=True,
            symbol_size=8,
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="峰值"),
                    opts.MarkPointItem(type_="min", name="谷值")
                ]
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="美国PPI走势（1980-2025）", subtitle="数据来源：FRED经济数据库"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
            yaxis_opts=opts.AxisOpts(
                name="同比涨幅(%)",
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value}%")
            )
        )
    )
    
    # 生成HTML文件
    line.render("../date/fred_us_ppi_trend_pyecharts.html")
    
if __name__ == '__main__':
    get_ppi()

