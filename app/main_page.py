import streamlit as st
import pandas as pd
import asyncio
from api_utils.api_download import fetch_all_temperatures, check_temperature
from analytics.statistics import seasonal_statistics, detect_anomalies
from app.plot_utils import plot_temperature_series, plot_seasonal_profiles


def main():
    st.title("Мониторинг температуры")
    st.sidebar.header("Настройки")

    uploaded_file = st.sidebar.file_uploader(
        "Загрузите файл с историческими данными", type=["csv"]
    )
    if uploaded_file is not None:
        historical_data = pd.read_csv(uploaded_file, parse_dates=["timestamp"])
        st.sidebar.success("Данные успешно загружены!")
    else:
        st.warning("Пожалуйста, загрузите файл для анализа.")
        return

    cities = historical_data["city"].unique().tolist()
    selected_city = st.sidebar.selectbox("Выберите город", cities)

    api_key = st.sidebar.text_input("Введите API ключ OpenWeatherMap", type="password")
    if api_key:
        st.sidebar.success("API ключ введён.")
    else:
        st.info("Введите API ключ для получения текущей температуры.")

    st.subheader(f"Анализ исторических данных: {selected_city}")
    city_data = historical_data[historical_data["city"] == selected_city]
    stats = seasonal_statistics(city_data)
    st.write(stats)

    st.subheader("График временного ряда температуры с аномалиями")
    anomalies = detect_anomalies(city_data)
    plot_temperature_series(city_data, anomalies)

    st.subheader("Сезонные профили температуры")
    plot_seasonal_profiles(stats)

    if api_key:
        st.subheader("Текущая температура")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            city, temp, dt = loop.run_until_complete(
                fetch_all_temperatures([selected_city], api_key)
            )[0]
            st.write(f"Текущая температура в {selected_city}: {temp:.2f} °C")

            result = check_temperature(city, temp, dt, historical_data)
            if result["is_normal"]:
                st.success("Текущая температура в пределах нормы.")
            else:
                st.error(
                    f"Температура аномальная! Ожидаемый диапазон: ({result['normal_range'][0]:.2f}; {result['normal_range'][1]:.2f})"
                )
        except Exception as e:
            st.error(f"Ошибка получения температуры: {e}")
