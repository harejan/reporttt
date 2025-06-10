import streamlit as st
from datetime import date
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

st.title("2019~2024年NDVI變化")
st.header("🛰️Sentinel")
# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)

roi = ee.Geometry.Polygon([[
    [120.271797, 22.628386],
    [120.271797, 22.587659],
    [120.322437, 22.587659],
    [120.322437, 22.628386],
    [120.271797, 22.628386]
]])

def maskS2clouds(image):
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
           qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask) \
                .select("B.*") \
                .copyProperties(image, ["system:time_start"])

def addNDVI(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)


s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')

filtered2017 = (s2
    .filter(ee.Filter.date('2017-01-01', '2017-12-31'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .filter(ee.Filter.bounds(roi))
    .map(maskS2clouds)
    .map(addNDVI)
)

median2017 = filtered2017.median().clip(roi)


ndvi_vis = {
    'min': -0.5,
    'max': 1.0,
    'palette':['#640000',  # very low NDVI
          '#ff0000',  # low NDVI
          '#ffff00',  # medium NDVI
          '#00c800',  # high NDVI
          '#006400']   # very high NDVI
}

legend_dict = {
    '-1 ~ -0.6': '#640000',
    '-0.6 ~ -0.2': '#ff0000',
    '-0.2 ~ 0.2': '#ffff00',
    '0.2 ~ 0.6': '#00c800',
    '0.6 ~ 1': '#006400'
}

s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')

filtered2024 = (s2
    .filter(ee.Filter.date('2024-01-01', '2024-12-31'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .filter(ee.Filter.bounds(roi))
    .map(maskS2clouds)
    .map(addNDVI)
)

median2024 = filtered2024.median().clip(roi)

ndvi_vis = {
    'min': -0.5,
    'max': 1.0,
    'palette': ['#640000',  # very low NDVI
          '#ff0000',  # low NDVI
          '#ffff00',  # medium NDVI
          '#00c800',  # high NDVI
          '#006400']   # very high NDVI
}
legend_dict = {
    '-1 ~ -0.6': '#640000',
    '-0.6 ~ -0.2': '#ff0000',
    '-0.2 ~ 0.2': '#ffff00',
    '0.2 ~ 0.6': '#00c800',
    '0.6 ~ 1': '#006400'
}



my_Map = geemap.Map()
left_layer = geemap.ee_tile_layer(median2017.select('NDVI'), ndvi_vis, '2017年')
right_layer = geemap.ee_tile_layer(median2024.select('NDVI'), ndvi_vis, '2024年')

my_Map.centerObject(median2017.geometry(), 14)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='NDVI', legend_dict=legend_dict)
my_Map.to_streamlit(height=600)
