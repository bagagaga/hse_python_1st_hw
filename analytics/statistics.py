import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def timestamp_to_season(timestamp):
    month = datetime.fromtimestamp(timestamp).month

    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"


def seasonal_statistics(df: pd.DataFrame) -> pd.DataFrame:
    stats = df.groupby("season").agg(
        mean_temperature=("temperature", "mean"), std_temperature=("temperature", "std")
    )
    stats["lower_bound"] = stats["mean_temperature"] - 2 * stats["std_temperature"]
    stats["upper_bound"] = stats["mean_temperature"] + 2 * stats["std_temperature"]
    return stats


def calculate_moving_average_city(city_data):
    city_data = city_data.sort_index()
    city_data["rolling_mean"] = city_data["temperature"].rolling(window=30).mean()
    return city_data["rolling_mean"]


def calculate_moving_std_city(city_data):
    city_data = city_data.sort_index()
    city_data["rolling_mean"] = city_data["temperature"].rolling(window=30).std()
    return city_data["rolling_mean"]


def detect_anomalies(df):
    data = df.copy()
    data['rolling_mean'] = calculate_moving_average_city(data)
    data['rolling_std'] = calculate_moving_std_city(data)

    data['upper_bound'] = data['rolling_mean'] + 2 * data['rolling_std']
    data['lower_bound'] = data['rolling_mean'] - 2 * data['rolling_std']

    anomalies = data[
        (data['temperature'] < data['lower_bound']) |
        (data['temperature'] > data['upper_bound'])
    ]

    return anomalies


def plot_long_term_trends(data):
    trends = data.groupby("year")["temperature"].mean()
    plt.figure(figsize=(10, 6))
    plt.plot(trends.index, trends.values, marker="o")
    plt.title("Long-term Temperature Trends")
    plt.xlabel("Year")
    plt.ylabel("Average Temperature")
    plt.grid()
    plt.show()
