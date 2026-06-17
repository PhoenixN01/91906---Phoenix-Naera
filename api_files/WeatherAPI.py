import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

def get_weather_data():
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)


	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": -36.85,
		"longitude": 174.76,
		"daily": ["sunrise", "sunset"],
		"hourly": ["temperature_2m", "apparent_temperature", "precipitation_probability", "rain", "cloud_cover", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "relative_humidity_2m", "surface_pressure"],
		"timezone": "Pacific/Auckland"
	}
	responses = openmeteo.weather_api(url, params = params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
	hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
	hourly_rain = hourly.Variables(3).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
	hourly_wind_direction_10m = hourly.Variables(6).ValuesAsNumpy()
	hourly_wind_gusts_10m = hourly.Variables(7).ValuesAsNumpy()
	hourly_relative_humidity_2m = hourly.Variables(8).ValuesAsNumpy()
	hourly_surface_pressure = hourly.Variables(9).ValuesAsNumpy()

	hourly_data = {
		"date": pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		).tz_convert(response.Timezone().decode())
	}

	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["apparent_temperature"] = hourly_apparent_temperature
	hourly_data["precipitation_probability"] = hourly_precipitation_probability
	hourly_data["rain"] = hourly_rain
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
	hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
	hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["surface_pressure"] = hourly_surface_pressure

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print("\nHourly data\n", hourly_dataframe)

	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
	daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()

	daily_data = {
		"date": pd.date_range(
			start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = daily.Interval()),
			inclusive = "left"
		).tz_convert(response.Timezone().decode())
	}

	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset

	daily_dataframe = pd.DataFrame(data = daily_data)
	print("\nDaily data\n", daily_dataframe)

get_weather_data()