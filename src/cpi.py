import qstock as qs
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr

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
    
    # 绘制CPI走势图
    # 假设 '全国当月' 列是CPI值
    plt.figure(figsize=(10, 6))
    plt.plot(cpi_data['月份'], cpi_data['全国当月'], marker='o', linestyle='-', color='b')
    plt.title('China CPI from 1980 to 2025')
    plt.xlabel('Month')
    plt.ylabel('CPI')
    plt.grid(True)
    # plt.show()
    # 保存图片
    plt.savefig('../date/qstock_china_CPI_同比增速趋势图.png', dpi=300, bbox_inches='tight')
    
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
    
    # 前向填充缺失值（适用于连续少量缺失）
    cpi_fred = cpi_fred.ffill()
    
    # 或线性插值（适用于趋势平稳数据）
    cpi_fred = cpi_fred.interpolate(method='linear')
    
    # 保存为 Excel（需安装 openpyxl）
    cpi_fred.to_excel('../date/fred_china_cpi.xlsx', sheet_name='CPI')
    
    plt.figure(figsize=(14, 6))
    # plt.plot(cpi_fred.index, cpi_fred['DDOE01CNM086NWDB'], color='#2C73D2', linewidth=2)
    plt.plot(cpi_fred.index, cpi_fred.iloc[:, 0], color='#2C73D2', linewidth=2)  # 使用索引避免硬编码列名
    plt.title('China CPI Index (1980-2025)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('../date/fred_china_cpi_trend.png', dpi=300)
    # plt.show()
    

if __name__ == '__main__':
    get_cpi()
# breakpoint()