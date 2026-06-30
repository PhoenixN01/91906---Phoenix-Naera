import openmeteo_requests

import datetime
import requests_cache
from retry_requests import retry
import json
from timezonefinder import TimezoneFinder

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
	# Setup the Open-Meteo API client with cache and retry on error
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
		# Process each location
		response = responses[n]

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

		for hour in range(num_hours):
			timestamp = datetime.datetime.fromtimestamp(
				start_time + hour * interval
			).strftime("%Y-%m-%d %H:%M")

			hourly_weather[timestamp] = {
				field: float(values[hour])
				for field, values in hourly_variables.items()
			}

		# Process daily data
		daily = response.Daily()
		daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
		daily_sunrise_converted = datetime.datetime.fromtimestamp(
			daily_sunrise[0])
		daily_sunrise_string = daily_sunrise_converted.strftime("%I:%M %p")

		daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()
		daily_sunset_converted = datetime.datetime.fromtimestamp(
			daily_sunset[0])
		daily_sunset_string = daily_sunset_converted.strftime("%I:%M %p")

		daily_timestamp = datetime.datetime.fromtimestamp(
			daily.Time(),
			tz=datetime.timezone.utc
		)

		daily_data = {
			"date": daily_timestamp.strftime("%Y-%m-%d"),
			"sunrise": daily_sunrise_string,
			"sunset": daily_sunset_string
		}
		all_hourly_weather[package["location"][n]] = hourly_weather
		all_daily_data[package["location"][n]] = daily_data

	return all_hourly_weather, all_daily_data

session = initialize_cache()

locations = {
	"location": ["Auckland, New Zealand"],
	"lat": [-36.852095],
	"lon": [174.7631803]
}

tf = TimezoneFinder()
timezone_name = tf.timezone_at(
	lng=locations["lon"][0], 
	lat=locations["lat"][0]
)

locations["timezone"] = [timezone_name]

hourly_weather, daily_data = get_weather_data(
	session, 
	locations,
	WEATHER_FIELDS
)

# print("\nHourly Weather:")
# print(json.dumps(hourly_weather, indent=4))

# print("\nDaily Data:")
# print(json.dumps(daily_data, indent=4))

# print(hourly_weather.keys())