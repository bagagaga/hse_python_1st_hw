import pandas as pd
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor


def parallel_analysis_threading(df: pd.DataFrame, func, n_threads=4) -> pd.DataFrame:
    city_groups = [group for _, group in df.groupby("city")]

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        results = list(executor.map(func, city_groups))

    return pd.concat(results)


def parallel_analysis_multiprocessing(df, func, n_processes=4):
    city_groups = [group for _, group in df.groupby("city")]

    with Pool(n_processes) as pool:
        results = pool.map(func, city_groups)

    return pd.concat(results)
