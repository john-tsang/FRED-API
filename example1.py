from get_obs_json import get_obs_json
from fetch_FRED_data import fetch_FRED_data

API_KEY = "ABC"
fetch_FRED_data(db_file_name = 'time_series.sqlite', series_id="GNPCA", api_key=API_KEY)