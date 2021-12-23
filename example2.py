from get_obs_json import get_obs_json
from fetch_FRED_data import fetch_FRED_data

API_KEY = "ABC"

r = get_obs_json(API_KEY,"GNPCA",observation_end = "2013-01-01")
import sqlite3
conn = sqlite3.connect('time_series3.sqlite')
cur = conn.cursor()
r.df.to_sql("GNPCA",conn)
conn.commit()
conn.close()

fetch_FRED_data(db_file_name = 'time_series3.sqlite', series_id="GNPCA", api_key = API_KEY)