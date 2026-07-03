from datetime import datetime, timedelta, timezone
import requests
import requests_cache
from retry_requests import retry
from zoneinfo import ZoneInfo

def initialize_cache():
    """Initiate the cache system for the Earthquake API

    Setup the Open-Meteo client with cache and retry on error so that
    API calls per day is kept at a minimum.
    """
    cache_session = requests_cache.CachedSession(
        'earthquake.cache',
        expire_after = 300
    )

    # Initiates retry session that will handle retrieving data and 
    # allow api call retrying in the event of an unsuccessful initial
    # call.
    retry_session = retry(
        cache_session,
        retries = 5,
        backoff_factor = 0.2
    )
    return retry_session

def get_earthquake_data(session, package):
    """Fetch the USGS data and returning the results
      
      Get requested details and passing the results back in a dictionary.
    """
    starttime = (
        datetime.now(timezone.utc) - timedelta(days=60)
    ).isoformat()

    all_earthquakes = {}
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    if not package:
        return None

    for n in range(len(package["location"])):
        core_params = {
        "format": "geojson",
        "jsonerror": True,
        "latitude": package["lat"][n],
        "longitude": package["lon"][n],
        "maxradiuskm": package["radius"][n],
        "starttime": starttime,
        "orderby": "time",
        "eventtype": "earthquake",
        "minmagnitude": 2.5
    }
        try:
            response = session.get(url, params=core_params)
            response.raise_for_status()
            data = response.json()

            earthquakes = []

            for feature in data["features"]:
                properties = feature["properties"]
                geometry = feature["geometry"]

                location_tz = ZoneInfo(package["timezone"][n])
                time = datetime.fromtimestamp(
                    properties["time"] / 1000,
                    tz=location_tz
                )
                time_formatted = time.strftime(
                    "%Y-%m-%d %I:%M %p"
                )
                abbreviated_tz = time.strftime("%Z")

                earthquake = {
                    "magnitude": properties["mag"],
                    "place": properties["place"],
                    "time": time_formatted,
                    "timezone": abbreviated_tz,
                    "longitude": geometry["coordinates"][0],
                    "latitude": geometry["coordinates"][1],
                    "depth": geometry["coordinates"][2]
                }
                earthquakes.append(earthquake)
            all_earthquakes[package["location"][n]] = earthquakes
        except requests.RequestException as e:
            message = (
                "Failed to fetch earthquake data for " + 
                f"{package['location']}: {e}"
            )
            return message
            
    return all_earthquakes