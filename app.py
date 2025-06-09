import streamlit as st
from datetime import date
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap


st.set_page_config(layout="wide", page_title="這是Streamlit App第二次練習！")

st.title("亞灣區的發展與變遷🌊")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io), [GEE](https://earthengine.google.com/), 
    [geemap](https://leafmap.org) and [leafmap](https://leafmap.org). 
    """
)

st.header("亞灣區簡介")

markdown = """
1. You can use it as a template for your own project.
2. Customize the sidebar by changing the sidebar text and logo in each Python file.
3. Find your favorite emoji from https://emojipedia.org.
4. Add a new app to the `pages/` directory with an emoji in the file name, e.g., `1_🚀_Chart.py`.

"""
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
st.markdown(markdown)
st.title("🌏2017~2024年衛星影像Split Map")

# 地理區域
my_Map = geemap.Map()# If we have not defined any box region on the canvas,# If we have not defined any box region on the canvas,
roi = ee.Geometry.BBox(120.271797, 22.587659, 120.322437, 22.628386)
my_Map.addLayer(roi)
my_Map.centerObject(roi, 14)

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
my_Map
my_Map.to_streamlit(height=600)

st.markdown(markdown)
st.title("利用擴充器示範")

with st.expander("展示gif檔"):
    st.image("pucallpa.gif")

with st.expander("播放mp4檔"):
    video_file = open("pucallpa.mp4", "rb")  # "rb"指的是讀取二進位檔案（圖片、影片）
    video_bytes = video_file.read()
    st.video(video_bytes)
    
