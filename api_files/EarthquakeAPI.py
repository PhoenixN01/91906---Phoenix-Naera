from datetime import datetime, timedelta, timezone
import requests_cache
from retry_requests import retry

import json

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

cache_session = requests_cache.CachedSession('.cache', expire_after = 300)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)

starttime = (
    datetime.now(timezone.utc) - timedelta(hours=1)
).isoformat()

core_params = {
    "format": "geojson",
	"latitude": -36.85,
	"longitude": 174.76,
	"maxradiuskm": 500,
    "starttime": starttime,
    "orderby": "time",
    "eventtype": "earthquake",
    "minmagnitude": 2.5
} 

response = retry_session.get(URL, params=core_params)

data = response.json()

print(json.dumps(data["features"], indent=2))

