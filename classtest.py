# 載入必要模組
import os
import numpy as np
import indicator_f_Lo2_short
import datetime
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as stc 
import indicator_forKBar_short
import plotly.graph_objs as go

###### (1) 開始設定 ######
html_temp = """
		<div style="background-color:#3872fb;padding:10px;border-radius:10px">
		<h1 style="color:white;text-align:center;">雙邦金融資料視覺化呈現 (金融看板) </h1>
		<h2 style="color:white;text-align:center;">Financial Dashboard </h2>
		</div>
		"""
stc.html(html_temp)

# ## 讀取 excel 檔
df_original = pd.read_excel("6560.xlsx")

# ## 保存为Pickle文件:
df_original.to_pickle('kbars_6560.pkl')

## 读取Pickle文件
@st.cache_data(ttl=3600,show_spinner="正在加載資料...")
def load_data(url):
	df=pd.read_pickle(url)
	return df
df_original = load_data('kbars_6560.pkl')
df_original = pd.read_pickle('kbars_6560.pkl')

#df.columns  ## Index(['Unnamed: 0', 'data', 'open', 'high', 'low', 'close', 'change','transaction'], dtype='object')
# 檢查列名
print(df_original.columns)

##### 選擇資料區間
start_date = st.text_input('選擇開始日期 (日期格式: 2019-01-02)', '2019-01-02')
end_date = st.text_input('選擇結束日期 (日期格式: 2024-05-21)', '2024-05-21')
start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')

# 使用条件筛选选择时间区间的数据
df = df_original[(df_original['date'] >= start_date) & (df_original['date'] <= end_date)]

###### (2) 轉化為字典 ######:
KBar_dic = df.to_dict()

KBar_open_list = list(KBar_dic['open'].values())
KBar_dic['open']=np.array(KBar_open_list)

KBar_dic['product'] = np.repeat('tsmc', KBar_dic['open'].size)

KBar_time_list = list(KBar_dic['date'].values())
KBar_time_list = [i.to_pydatetime() for i in KBar_time_list] ## Timestamp to datetime
KBar_dic['date']=np.array(KBar_time_list)

KBar_low_list = list(KBar_dic['low'].values())
KBar_dic['low']=np.array(KBar_low_list)

KBar_high_list = list(KBar_dic['high'].values())
KBar_dic['high']=np.array(KBar_high_list)

KBar_close_list = list(KBar_dic['close'].values())
KBar_dic['close']=np.array(KBar_close_list)

KBar_volume_list = list(KBar_dic['change'].values())
KBar_dic['change']=np.array(KBar_volume_list)

KBar_amount_list = list(KBar_dic['capacity'].values())
KBar_dic['capacity']=np.array(KBar_amount_list)

KBar_capacity_list = list(KBar_dic['transaction'].values())
KBar_dic['transaction']=np.array(KBar_capacity_list)

######  (3) 改變 KBar 時間長度 (以下)  ########

Date = start_date.strftime("%Y-%m-%d")

cycle_duration_value = st.number_input('輸入一根 K 棒的時間數值(一天86400秒、1440分鐘)', value=24, key="KBar_duration_value")
cycle_duration_unit = st.selectbox('選擇一根 K 棒的時間單位', options=['小時', '分鐘','秒'], key="KBar_duration_unit")

if cycle_duration_unit == '小時':
    cycle_duration = cycle_duration_value * 60 *60 #小時轉秒
else:
    cycle_duration = cycle_duration_value *60      #分鐘轉秒

# 使用選擇的時間長度來計算 KBar
KBar = indicator_forKBar_short.KBar(Date, cycle_duration)  ## 設定cycle_duration可以改成你想要的 KBar 週期

amount = None  # 在迴圈外部初始化 amount 變數

for i in range(KBar_dic['date'].size):
    time = KBar_dic['date'][i]
    open_price = KBar_dic['open'][i]
    close_price = KBar_dic['close'][i]
    low_price = KBar_dic['low'][i]
    high_price = KBar_dic['high'][i]
    qty = KBar_dic['transaction'][i]
    length_of_capacity = len(KBar_dic['capacity'])    
    
    if i < length_of_capacity:
        amount = KBar_dic['capacity'][i]  # 在這裡為 amount 變數賦值

KBar_dic = {}

 ## 形成 KBar 字典 (新週期的):
KBar_dic['time'] =  KBar.TAKBar['time']   
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['time'].size)
KBar_dic['open'] = KBar.TAKBar['open']
KBar_dic['high'] =  KBar.TAKBar['high']
KBar_dic['low'] =  KBar.TAKBar['low']
KBar_dic['close'] =  KBar.TAKBar['close']
KBar_dic['volume'] = KBar.TAKBar['volume']

##### (4) 計算各種技術指標 ######
##### 將K線 Dictionary 轉換成 Dataframe
KBar_df = pd.DataFrame(KBar_dic)

#####  (i) 移動平均線策略   #####
LongMAPeriod=st.slider('選擇一個整數', 0, 100, 10)
ShortMAPeriod=st.slider('選擇一個整數', 0, 100, 2)

#### 計算長短移動平均線
KBar_df['MA_long'] = KBar_df['close'].rolling(window=LongMAPeriod).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ShortMAPeriod).mean()

#####  (ii) RSI 策略   #####
LongRSIPeriod=st.slider('選擇一個整數', 0, 1000, 10)
ShortRSIPeriod=st.slider('選擇一個整數', 0, 1000, 2)

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

KBar_df['RSI_long'] = calculate_rsi(KBar_df, LongRSIPeriod)
KBar_df['RSI_short'] = calculate_rsi(KBar_df, ShortRSIPeriod)
KBar_df['RSI_Middle']=np.array([50]*len(KBar_dic['time']))

##### (5) 將 Dataframe 欄位名稱轉換  ###### 
KBar_df.columns = [ i[0].upper()+i[1:] for i in KBar_df.columns ]

##### (6) 畫圖 ######
import plotly.graph_objects as go

# 绘制K线图和移动平均线（MA）
fig = go.Figure()

# 添加K线
fig.add_trace(go.Candlestick(x=KBar_df['TIME'],
                open=KBar_df['OPEN'],
                high=KBar_df['HIGH'],
                low=KBar_df['LOW'],
                close=KBar_df['CLOSE'], name='K线'))

# 添加长期移动平均线
fig.add_trace(go.Scatter(x=KBar_df['TIME'], y=KBar_df['MA_LONG'], mode='lines', name='长期移动平均线'))

# 添加短期移动平均线
fig.add_trace(go.Scatter(x=KBar_df['TIME'], y=KBar_df['MA_SHORT'], mode='lines', name='短期移动平均线'))

# 更新图表布局
fig.update_layout(title='K线图和移动平均线',
                   xaxis_title='时间',
                   yaxis_title='价格',
                   template='plotly_dark')

# 显示图表
st.plotly_chart(fig)

# 绘制RSI图表
fig_rsi = go.Figure()

# 添加RSI
fig_rsi.add_trace(go.Scatter(x=KBar_df['TIME'], y=KBar_df['RSI_LONG'], mode='lines', name='长期RSI'))
fig_rsi.add_trace(go.Scatter(x=KBar_df['TIME'], y=KBar_df['RSI_SHORT'], mode='lines', name='短期RSI'))
fig_rsi.add_trace(go.Scatter(x=KBar_df['TIME'], y=KBar_df['RSI_MIDDLE'], mode='lines', name='RSI中间值'))

# 更新图表布局
fig_rsi.update_layout(title='RSI指标',
                      xaxis_title='时间',
                      yaxis_title='RSI值',
                      template='plotly_dark')

# 显示RSI图表
st.plotly_chart(fig_rsi)

