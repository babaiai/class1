# 載入必要模組
import os
# os.chdir(r'C:\Users\user\Dropbox\系務\專題實作\112\金融看板\for students')
#import haohaninfo
#from order_Lo8 import Record
import numpy as np
#from talib.abstract import SMA,EMA, WMA, RSI, BBANDS, MACD
#import sys
import indicator_f_Lo2_short,datetime, indicator_forKBar_short
import datetime
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as stc 


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
start_date = st.text_input('選擇開始日期 (日期格式: 2022-01-03)', '2022-01-03')
end_date = st.text_input('選擇結束日期 (日期格式: 2022-11-18)', '2022-11-18')
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

KBar_amount_list = list(KBar_dic['transaction'].values())
KBar_dic['transaction']=np.array(KBar_amount_list)

KBar_capacity_list = list(KBar_dic['capacity'].values())
KBar_dic['capacity']=np.array(KBar_capacity_list)


######  (3) 改變 KBar 時間長度 (以下)  ########


Date = start_date.strftime("%Y-%m-%d")

#st.subheader("設定一根 K 棒的時間長度(小時)")
#cycle_duration = st.number_input('輸入一根 K 棒的時間長度(單位:小時, 一日=24小時)',value=48,key="KBar_duration")

#cycle_duration_options = [720, 1440, 2880]  # 可供選擇的時間長度
#selected_cycle_duration = st.selectbox('選擇一根 K 棒的時間長度(單位:分鐘, 一日=1440分鐘)', options=cycle_duration_options, index=2, format_func=lambda x: f"{x} 分鐘", key="KBar_duration")


#cycle_duration = int(cycle_duration)
#cycle_duration = 1440   ## 可以改成你想要的 KBar 週期
#KBar = indicator_f_Lo2.KBar(Date,'time',2)
#KBar = indicator_forKBar_short.KBar(Date,cycle_duration)    ## 設定cycle_duration可以改成你想要的 KBar 週期

#下拉式選單(單一)
#cycle_duration_options = [24, 48, 72]  # 可供選擇的時間長度，單位為小時
#selected_cycle_duration = st.selectbox('選擇一根 K 棒的時間長度(單位:小時, 一日=24小時)', options=cycle_duration_options, index=1, format_func=lambda x: f"{x} 小時", key="KBar_duration")

# 將選擇的時間長度轉換為分鐘
#cycle_duration = selected_cycle_duration * 60

# 使用選擇的時間長度來計算 KBar
#KBar = indicator_forKBar_short.KBar(Date, cycle_duration)  ## 設定cycle_duration可以改成你想要的 KBar 週期


#下拉式選擇小時、分鐘
cycle_duration_value = st.number_input('輸入一根 K 棒的時間數值(一天86400秒、1440分鐘)', value=24, key="KBar_duration_value")
cycle_duration_unit = st.selectbox('選擇一根 K 棒的時間單位', options=['小時', '分鐘','秒'], key="KBar_duration_unit")
length_of_capacity = len(KBar_dic['capacity'])
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

    # 在這裡使用 amount 變數進行相應的操作

    # 確保 KBar 實例被正確初始化，並調用 AddPrice 方法
def AddPrice(self, time, open_price, close_price, low_price, high_price, qty):
    # 檢查 TAKBar 是否已經初始化
    if not hasattr(self, 'TAKBar'):
        print("TAKBar 尚未初始化")
        return
    # 在這裡可以加入其他操作代碼
    pass

    
    
    

    
    
        


KBar_dic = {}


 ## 形成 KBar 字典 (新週期的):
KBar_dic['time'] =  KBar.TAKBar['time']   
#KBar_dic['product'] =  KBar.TAKBar['product']
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['time'].size)
KBar_dic['open'] = KBar.TAKBar['open']
KBar_dic['high'] =  KBar.TAKBar['high']
KBar_dic['low'] =  KBar.TAKBar['low']
KBar_dic['close'] =  KBar.TAKBar['close']
KBar_dic['transaction'] = KBar.TAKBar.get('transaction', [])




###### (4) 計算各種技術指標 ######
##### 將K線 Dictionary 轉換成 Dataframe
KBar_df = pd.DataFrame(KBar_dic)


#####  (i) 移動平均線策略   #####
####  設定長短移動平均線的 K棒 長度:
st.subheader("設定計算長移動平均線(MA)的 K 棒數目(整數, 例如 10)")
#LongMAPeriod=st.number_input('輸入一個整數', key="Long_MA")
#LongMAPeriod=int(LongMAPeriod)
LongMAPeriod=st.slider('選擇一個整數', 0, 100, 10)
st.subheader("設定計算短移動平均線(MA)的 K 棒數目(整數, 例如 2)")
#ShortMAPeriod=st.number_input('輸入一個整數', key="Short_MA")
#ShortMAPeriod=int(ShortMAPeriod)
ShortMAPeriod=st.slider('選擇一個整數', 0, 100, 2)

#### 計算長短移動平均線
KBar_df['MA_long'] = KBar_df['close'].rolling(window=LongMAPeriod).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ShortMAPeriod).mean()

#### 尋找最後 NAN值的位置
last_nan_index_MA = KBar_df['MA_long'][::-1].index[KBar_df['MA_long'][::-1].apply(pd.isna)]
if not last_nan_index_MA.empty:
    last_nan_index_MA = last_nan_index_MA[0]
else:
    last_nan_index_MA = None




#####  (ii) RSI 策略   #####
#### 順勢策略
### 設定長短 RSI 的 K棒 長度:
st.subheader("設定計算長RSI的 K 棒數目(整數, 例如 10)")
LongRSIPeriod=st.slider('選擇一個整數', 0, 1000, 10)
st.subheader("設定計算短RSI的 K 棒數目(整數, 例如 2)")
ShortRSIPeriod=st.slider('選擇一個整數', 0, 1000, 2)

### 計算 RSI指標長短線, 以及定義中線
## 假设 df 是一个包含价格数据的Pandas DataFrame，其中 'close' 是KBar週期收盤價
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

### 尋找最後 NAN值的位置
last_nan_index_RSI = KBar_df['RSI_long'][::-1].index[KBar_df['RSI_long'][::-1].apply(pd.isna)]
if not last_nan_index_RSI.empty:
    last_nan_index_RSI = last_nan_index_RSI[0]
else:
    last_nan_index_RSI = None






###### (5) 將 Dataframe 欄位名稱轉換  ###### 
KBar_df.columns = [ i[0].upper()+i[1:] for i in KBar_df.columns ]


###### (6) 畫圖 ######
st.subheader("畫圖")
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
#from plotly.offline import plot
import plotly.offline as pyoff


##### K線圖, 移動平均線 MA
with st.expander("K線圖, 移動平均線"):
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    #### include candlestick with rangeselector
    fig1.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=True)   ## secondary_y=True 表示此圖形的y軸scale是在右邊而不是在左邊
    
    #### include a go.Bar trace for volumes
    fig1.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['transaction'], name='成交量', marker=dict(color='black')), secondary_y=False)

    fig1.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA+1:], y=KBar_df['MA_long'][last_nan_index_MA+1:], mode='lines',line=dict(color='orange', width=2), name=f'{LongMAPeriod}-根 K棒 移動平均線'), 
                  secondary_y=True)
    fig1.add_trace(go.Scatter(x=KBar_df['time'][last_nan_index_MA+1:], y=KBar_df['MA_short'][last_nan_index_MA+1:], mode='lines',line=dict(color='pink', width=2), name=f'{ShortMAPeriod}-根 K棒 移動平均線'), 
                  secondary_y=True)
    
    fig1.layout.yaxis2.showgrid=True
    st.plotly_chart(fig1, use_container_width=True)


##### K線圖, RSI
with st.expander("K線圖, 長短 RSI"):
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    #### include candlestick with rangeselector
    fig2.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=True)   ## secondary_y=True 表示此圖形的y軸scale是在右邊而不是在左邊
    
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI+1:], y=KBar_df['RSI_long'][last_nan_index_RSI+1:], mode='lines',line=dict(color='red', width=2), name=f'{LongRSIPeriod}-根 K棒 移動 RSI'), 
                  secondary_y=False)
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI+1:], y=KBar_df['RSI_short'][last_nan_index_RSI+1:], mode='lines',line=dict(color='blue', width=2), name=f'{ShortRSIPeriod}-根 K棒 移動 RSI'), 
                  secondary_y=False)
    
    fig2.layout.yaxis2.showgrid=True
    st.plotly_chart(fig2, use_container_width=True)
















