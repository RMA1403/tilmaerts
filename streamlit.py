import os

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Functions
def get_station_date_range(start_date, end_date, station):
    temp_df = dataset.loc[(dataset["datetime"] >= start_date) & (dataset["datetime"] <= end_date) & (dataset["station"] == station)].copy()
    temp_df["hour"] = temp_df["datetime"].dt.hour
    return temp_df

def plot_pm10(start_date, end_date, stations):
    visual_df = pd.concat([get_station_date_range(start_date, end_date, station) for station in stations], ignore_index=True)
    
    sns.lineplot(data=visual_df, x="hour", y="PM2.5", hue="station")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.xticks(range(0, 24, 2))
    
    st.pyplot(plt)

# Data initialization and processing
DATA_FOLDER = "PRSA_Data_20130301-20170228"

files = os.listdir(DATA_FOLDER)
dataset = pd.read_csv(os.path.join(DATA_FOLDER, files[0]))
for file in files[1:]:
    temp_df = pd.read_csv(os.path.join(DATA_FOLDER, file))
    dataset = pd.concat([dataset, temp_df], ignore_index=True)

dataset["datetime"] = pd.to_datetime(dataset[["year", "month", "day", "hour"]])
dataset.drop(["year", "month", "day", "hour"], axis=1, inplace=True)

for column in dataset.select_dtypes(include=np.number):
    dataset[column] = dataset[column].fillna(value=dataset[column].median())

for column in dataset.select_dtypes(exclude=np.number):
    dataset[column] = dataset[column].fillna(value=dataset[column].mode()[0])

# Streamlit
st.set_page_config(layout="wide")
st.write(
    """
    # Air Quality Index Dashboard
    """
)
col1, col2 = st.columns(2)

with col1:
  st.write(
    """
    ### **Pola harian tingkat PM2.5 pada setiap stasiun**
    """
  )

  start_date, end_date = st.date_input(
      "Select Date Range",
      value=(pd.to_datetime('2013-03-01'), pd.to_datetime('2013-03-02'))
  )
  stations = st.multiselect(
      label="Select Stations",
      options=(x for x in dataset["station"].unique()),
      default=["Gucheng", "Huairou"]
  )

  plot_pm10(pd.to_datetime(start_date), pd.to_datetime(end_date), stations)
  plt.close()

  st.write(
     """
      Berdasarkan analisis, **tidak ditemukan pola berulang yang muncul harian pada data**. Dengan tidak adanya pola ini, dapat disimpulkan bahwa
      tingkat PM2.5 yang muncul disebabkan oleh faktor yang lebih kompleks yang cenderung bersifat acak. Walaupun tidak ada pola harian berulang
      yang muncul, terdapat dua insight yang dapat diambil.
      1. **Tingkat PM2.5 antar stasiun cenderung memiliki tren yang sama**. Jika tingkat PM2.5 sedang mengalami kenaikan pada satu waktu untuk satu stasiun,
        tingkat PM2.5 pada stasiun lain juga akan cenderung mengalami kenaikan. Hal ini menunjukkan bahwa perubahan tingkat PM2.5 terjadi dalam cakupan
        geografis yang luas.

      2. **Tingkat PM2.5 memiliki tren yang menaik dari waktu ke waktu**. Tren kenaikan ini terjadi pada seluruh stasiun pengukuran yang ada. Hal ini
        menunjukkan bahwa kualitas udara dari waktu ke waktu semakin buruk sehingga diperlukan upaya untuk menghentikan kenaikan tingkat PM2.5 ini.
        Upaya yang dibutuhkan harus mencakup lokasi geografis yang luas karena kenaikan tingkat PM2.5 terjadi pada seluruh stasiun pengukuran.
    """
  )

with col2:
  st.write(
    """
    ### **Tingkat variasi masing-masing polutan**
    """
  )

  station = st.selectbox(
      label="Select Station",
      options=(x for x in dataset["station"].unique()),
      index=0
  )

  polutants = ["SO2", "NO2", "CO", "O3"]
  station_df = dataset[dataset['station'] == station].drop(columns='station')[polutants]
  variances = station_df.var().sort_values(ascending=False)

  sns.boxplot(data=station_df[variances.index], showfliers=False)
  plt.xlabel('Polutants')
  plt.ylabel('Values')
  st.pyplot(plt)
  plt.close()

  st.write(
     """
    **Kolom-kolom yang diidentifikasi sebagai polutan adalah
    "CO", "O3", "NO2", dan "SO2"**. "PM2.5" dan "PM10" tidak diidentifikasi sebagai polutan karena merupakan tingkat partikel pada udara dan
    tidak merujuk ke satu zat spesifik. Berdasarkan analisis, **ditemukan bahwa polutan "CO" memiliki tingkat variasi tertinggi**.      

    Plotting dilakukan untu melihat perbedaan tingkat variasi lebih lanjut. Boxplot dipilih untuk visualisasi karena menampilkan nilai
    Q1 dan Q3 yang berkaitan dengan tingkat variasi data. Berdasarkan plot, ditemukan bahwa **tingkat variasi "CO" jauh lebih tinggi 
    dibanding polutan lainnya**. Tingkat variasi "O3", "NO2", dan "SO2" mirip dan jauh lebih rendah daripada tingkat variasi "CO". Hal ini
    menunjukkan bahwa upaya peningkatan kualitas dengan mengurangi polutan yang fluktuatif dapat difokuskan pada polutan jenis "CO".
    """
  )