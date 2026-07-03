import openmeteo_requests
import datetime
import requests_cache
from retry_requests import retry
from zoneinfo import ZoneInfo

WEATHER_FIELDS = [
	"temperature_2m",
	"apparent_temperature",
	"precipitation_probability",
	"rain",
	"cloud_cover",
	"wind_speed_10m",
	"wind_direction_10m",
	"wind_gusts_10m",
	"relative_humidity_2m",
	"surface_pressure"
]

def initialize_cache():
	"""Setup the Open-Meteo API client with cache and retry on error 

	This feature is used so that the hourly data isn't repetitively 
	fetched for the same result all the time.
	"""
	cache_session = requests_cache.CachedSession(
		'weather.cache', 
		expire_after = 3600
	)
	retry_session = retry(
		cache_session, 
		retries = 5, 
		backoff_factor = 0.2
	)
	return retry_session

def get_weather_data(session, package, fields):
	"""Fetch the Openmeteo data and returning the results

	Get requested details and passing the results back in a tuple of 
	dictionaries for each type of data.
	"""
	if not package:
		return None

	openmeteo = openmeteo_requests.Client(session = session)
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": package["lat"],
		"longitude": package["lon"],
		"daily": ["sunrise", "sunset"],
		"hourly": fields,
		"timezone": package["timezone"]
	}
	responses = openmeteo.weather_api(url, params = params)
	all_hourly_weather = {}
	all_daily_data = {}

	for n in range(len(package["location"])):
		# Process each location in the openmeteo response
		response = responses[n]
	
		if isinstance(response, dict):
			if "error" in response:
				return response

		# Process hourly data.
		hourly = response.Hourly()
		hourly_weather = {}

		hourly_variables = {
			field: hourly.Variables(i).ValuesAsNumpy()
			for i, field in enumerate(fields)
		}

		start_time = hourly.Time()
		interval = hourly.Interval()

		num_hours = len(next(iter(hourly_variables.values())))

		location_tz = ZoneInfo(package["timezone"][n])

		for hour in range(num_hours):
			timestamp = datetime.datetime.fromtimestamp(
				start_time + hour * interval,
				tz=location_tz
			).strftime("%Y-%m-%d %H:%M")

			hourly_weather[timestamp] = {
				field: float(values[hour])
				for field, values in hourly_variables.items()
			}

		# Process daily data
		# Output data in the format HH:MM AM/PM Timezone
		daily = response.Daily()
		daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
		daily_sunrise_converted = datetime.datetime.fromtimestamp(
			daily_sunrise[0],
			tz=location_tz
		)
		daily_sunrise_string = daily_sunrise_converted.strftime(
			"%I:%M %p %Z"
		)

		daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()
		daily_sunset_converted = datetime.datetime.fromtimestamp(
			daily_sunset[0],
			tz=location_tz
		)
		daily_sunset_string = daily_sunset_converted.strftime(
			"%I:%M %p %Z"
		)

		daily_timestamp = datetime.datetime.fromtimestamp(
			daily.Time(),
			tz=datetime.timezone.utc
		)

		daily_data = {
			"date": daily_timestamp.strftime("%Y-%m-%d"),
			"timezone": package["timezone"][n],
			"sunrise": daily_sunrise_string,
			"sunset": daily_sunset_string
		}
		all_hourly_weather[package["location"][n]] = hourly_weather
		all_daily_data[package["location"][n]] = daily_data

	return (all_hourly_weather, all_daily_data)