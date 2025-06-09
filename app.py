import streamlit as st
from datetime import date
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap


st.set_page_config(layout="wide", page_title="這是Streamlit App第二次練習！")

st.title("亞灣區的發展與變遷🌊")
st.header("🚩亞灣區簡介")
st.markdown("亞灣區全名為亞洲新灣區，位於高雄市，範圍橫跨高雄市前鎮區、苓雅區、鹽埕區、鼓山區")

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)
###############################################
st.header("🚩研究範圍")
# 地理區域
my_Map = geemap.Map()# If we have not defined any box region on the canvas,# If we have not defined any box region on the canvas,
roi = ee.Geometry.BBox(120.271797, 22.587659, 120.322437, 22.628386)
my_Map.addLayer(roi)
my_Map.centerObject(roi, 14)
my_Map.to_streamlit(height=600)

st.header("🌏2017~2024年衛星影像Split Map")
st.markdown("波段組成：B11、B8、B3")
my_img2017 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(roi)
    .filterDate('2017-01-01', '2018-01-01')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
    .clip(roi)
)
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

my_img2024 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(roi)
    .filterDate('2024-01-01', '2025-01-01')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
    .clip(roi)
)
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

my_Map = geemap.Map()
left_layer = geemap.ee_tile_layer(my_img2017, vis_params, '2017年')
right_layer = geemap.ee_tile_layer(my_img2024, vis_params, '2024年')

my_Map.centerObject(my_img2017.geometry(), 14)
my_Map.split_map(left_layer, right_layer)
my_Map.to_streamlit(height=600)

st.title("2016~2024timelapse")

# 建立左右兩欄
col1, col2 = st.columns(2)

# 左邊欄放第一張 GIF
with col1:
    st.header("2016 ~ 2020")
    st.image('timelapse2016-2020.gif')

# 右邊欄放第二張 GIF
with col2:
    st.header("2021 ~ 2024")
    st.image('timelapse2021-2024.gif')

    
