import streamlit as st
from datetime import date
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

st.title("2019~2024年NDVI變化")
st.header("🛰️landsat")
# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)
roi = ee.Geometry.Polygon([
    [
        [120.271797, 22.628386],
        [120.271797, 22.587659],
        [120.322437, 22.587659],
        [120.322437, 22.628386],
        [120.271797, 22.628386]
    ]
])

# NDVI 計算 function
def addNDVI_L5(image):
    ndvi = image.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')
    return image.addBands(ndvi)

def addNDVI_L9(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    return image.addBands(ndvi)

landsat5 = ee.ImageCollection("LANDSAT/LT05/C02/T1_L2") \
    .filterDate('2010-01-01', '2010-12-31') \
    .filterBounds(roi) \
    .filter(ee.Filter.lt('CLOUD_COVER', 30)) \
    .map(addNDVI_L5)

median2010 = landsat5.select('NDVI').median().clip(roi)

# 讀取 Landsat 9 - 2024 年影像
landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
    .filterDate('2024-01-01', '2024-12-31') \
    .filterBounds(roi) \
    .filter(ee.Filter.lt('CLOUD_COVER', 30)) \
    .map(addNDVI_L9)

median2024 = landsat9.select('NDVI').median().clip(roi)

# NDVI 視覺化參數
ndvi_vis = {
    'min': -0.5,
    'max': 1.0,
    'palette': [
        '#640000',  # very low NDVI
        '#ff0000',  # low NDVI
        '#ffff00',  # medium NDVI
        '#00c800',  # high NDVI
        '#006400'   # very high NDVI
    ]
}

# 顯示地圖
my_Map = geemap.Map()
left_layer = geemap.ee_tile_layer(median2010, ndvi_vis, 'NDVI 2009')
right_layer = geemap.ee_tile_layer(median2024, ndvi_vis, 'NDVI 2024')

my_Map.centerObject(roi, 14)
my_Map.split_map(left_layer, right_layer)
my_Map.to_streamlit(height=600)
