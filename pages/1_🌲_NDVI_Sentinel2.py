import streamlit as st
from datetime import date
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

st.title("🌲2019~2024年NDVI變化")
st.header("🛰️Sentinel 2")
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

st.header("📊NDVI比較")
st.subheader("2024年的NDVI指數-2017年的NDVI指數")
st.subheader("🟥植生減少 🟩植生減少 ⬜不變" )
ndvi_diff = median2024.select('NDVI').subtract(median2017.select('NDVI'))

diff_vis = {
    'min': -0.5,
    'max': 0.5,
    'palette': ['red', 'white', 'green']
}

my_Map = geemap.Map()
my_Map.add_basemap('HYBRID')
my_Map.centerObject(roi, 14)
my_Map.add_legend(title='NDVI Difference', legend_dict={
    '-0.5 ~ -0.2': 'red',
    '-0.2 ~ 0': 'white',
    '0 ~ 0.2': 'lightgreen',
    '0.2 ~ 0.5': 'green'
})
my_Map.addLayer(ndvi_diff, diff_vis, 'NDVI Difference (2024 - 2017)')
my_Map.to_streamlit(height=600)

   # 定義 classify_ndvi_diff 函數
def classify_ndvi_diff(image):
    # 紅色區域 mask：差異 < -0.1
    red = image.lt(-0.1).rename('red')
    # 綠色區域 mask：差異 > 0.1
    green = image.gt(0.1).rename('green')
    # 中性區域 mask：-0.1 <= 差異 <= 0.1
    neutral = image.gte(-0.1).And(image.lte(0.1)).rename('neutral')

    # 回傳原圖加上三個 mask band
    return image.addBands(red).addBands(green).addBands(neutral)

# 執行分類
ndvi_diff_classified = classify_ndvi_diff(ndvi_diff)

# 計算分類區域的統計數據
stats = ndvi_diff_classified.reduceRegion(
    reducer = ee.Reducer.sum(),
    geometry = roi,
    scale = 10,  # Sentinel-2 解像度 10m
    maxPixels = 1e9
)

# 取得各區域的像素數
red_count = stats.get('red').getInfo()
green_count = stats.get('green').getInfo()
neutral_count = stats.get('neutral').getInfo()

# 計算總像素數
total_count = red_count + green_count + neutral_count

# 計算比例
red_ratio = red_count / total_count
green_ratio = green_count / total_count
neutral_ratio = neutral_count / total_count

# 輸出結果
print(f"紅色區域比例: {red_ratio:.2%}")
print(f"綠色區域比例: {green_ratio:.2%}")
print(f"中性區域比例: {neutral_ratio:.2%}")
