import pandas as pd
import requests
import asyncio
import aiohttp
import time
import numpy as np
from analytics.statistics import timestamp_to_season
from analytics.statistics import seasonal_statistics
from api_utils import API_KEY
from data import DATA_PATH


def fetch_current_temperature(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return city, data["main"]["temp"], data["dt"] + data["timezone"]
    else:
        raise Exception(f"API Error: {response.status_code}, {response.json()}")


async def fetch_current_temperature_async(city, api_key, session):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return city, data["main"]["temp"], data["dt"] + data["timezone"]
        else:
            raise Exception(f"API Error: {response.status}, {await response.json()}")


async def fetch_all_temperatures(cities, api_key):
    async with aiohttp.ClientSession(trust_env=True) as session:
        tasks = [
            fetch_current_temperature_async(city, api_key, session) for city in cities
        ]
        return await asyncio.gather(*tasks)


def check_temperature(city, current_temp, current_time, historical_data):
    season = timestamp_to_season(current_time)

    season_data = seasonal_statistics(historical_data[historical_data["city"] == city])
    season_data = season_data[season_data.index == season]

    lower_bound = season_data.loc[season, "lower_bound"]
    upper_bound = season_data.loc[season, "upper_bound"]
    return {
        "city": city,
        "current_temp": current_temp,
        "mean_temp": season_data.loc[season, "mean_temperature"],
        "std_temp": season_data.loc[season, "std_temperature"],
        "normal_range": (lower_bound, upper_bound),
        "is_normal": lower_bound <= current_temp <= upper_bound,
    }


if __name__ == "__main__":
    cities = ["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"]

    historical_data = pd.read_csv(f"{DATA_PATH}/temperature_data.csv")
    historical_data["timestamp"] = pd.to_datetime(historical_data["timestamp"])

    sync_times = []

    start_time = time.time()
    sync_results = []
    for city in cities:
        try:
            city, current_temp, current_time = fetch_current_temperature(city, API_KEY)
            result = check_temperature(
                city, current_temp, current_time, historical_data
            )
            sync_results.append(result)
        except Exception as e:
            print(e)
        end_time = time.time()
        sync_times.append(end_time - start_time)

    avg_sync_time = np.mean(sync_times)

    async_times = []
    start_time = time.time()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        city_temperatures = loop.run_until_complete(
            fetch_all_temperatures(cities, API_KEY)
        )
        async_results = [
            check_temperature(city, temp, dt, historical_data)
            for city, temp, dt in city_temperatures
        ]
    except Exception as e:
        print(e)
    end_time = time.time()
    async_times.append(end_time - start_time)

    avg_async_time = np.mean(async_times)
    print("Сравнение времени выполнения:")
    print(f"Синхронный подход: {avg_sync_time:.2f} секунд")
    print(f"Асинхронный подход: {avg_async_time:.2f} секунд")
    print(
        f"Разница (синхронный - aсинхронный): {avg_sync_time - avg_async_time:.2f} секунд"
    )
    print()
    print(sync_results[0])
    print(async_results[0])
