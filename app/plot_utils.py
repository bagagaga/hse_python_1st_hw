import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from analytics.statistics import calculate_moving_average_city


def plot_temperature_series(df, anomalies):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="timestamp", y="temperature", label="Температура")
    sns.scatterplot(
        data=anomalies, x="timestamp", y="temperature", color="red", label="Аномалии"
    )
    data = df.copy()
    data['rolling_mean'] = calculate_moving_average_city(df)
    sns.lineplot(
        data=data[::10],
        x="timestamp",
        y="temperature",
        label="Скользящая средняя температура",
        color="magenta",
    )
    plt.legend()
    plt.title("Временной ряд температуры")
    st.pyplot(plt.gcf())


def plot_seasonal_profiles(stats):
    plt.figure(figsize=(8, 4))
    plt.bar(
        stats.index, stats["mean_temperature"], yerr=stats["std_temperature"], capsize=5
    )
    plt.title("Средняя температура и стандартное отклонение по сезонам")
    plt.xlabel("Сезон")
    plt.ylabel("Температура")
    st.pyplot(plt.gcf())
