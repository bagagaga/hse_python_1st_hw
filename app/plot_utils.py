import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


def plot_temperature_series(df, anomalies):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="timestamp", y="temperature", label="Температура")
    sns.scatterplot(
        data=anomalies, x="timestamp", y="temperature", color="red", label="Аномалии"
    )
    plt.axhline(
        df["temperature"].mean(),
        color="blue",
        linestyle="--",
        label="Средняя температура",
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
