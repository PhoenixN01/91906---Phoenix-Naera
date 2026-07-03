import tkinter as tk

from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta, timezone
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import requests
import json
import os

from api_files import WeatherAPI
from api_files import EarthquakeAPI


CITIES_FILE = "cities.json"
LOCATIONS_FILE = "stored_locations.json"
TF = TimezoneFinder()

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
FLOOD_FIELDS = [
    "precipitation_probability",
    "rain",
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "soil_moisture_3_to_9cm"
]
FLOOD_SCORES = [
    ("soil_saturation", [(0.9, 4), (0.75, 3)]),
    ("rain_1h", [(30, 3), (15, 2)]),
    ("rain_6h", [(70, 2), (40, 1)]),
    ("rain_24h", [(80, 2), (40, 1)]),
    ("rain_chance", [(90, 1)]),
]
EARTHQUAKE_SCORES = [
    ("magnitude", [(6.0, 4), (5.0, 3), (4.0, 2)]),
    ("depth", [(30, 3), (70, 2), (150, 1)]),
    ("recency_hours", [
        (timedelta(hours=1), 5), 
        (timedelta(hours=6), 4), 
        (timedelta(hours=24), 2), 
        (timedelta(hours=72), 1)
    ]),
]
WEATHER_API_PARAMETERS = [
    "temperature_2m",
    "apparent_temperature",
    "precipitation_probability",
    "rain",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "relative_humidity_2m",
    "surface_pressure",
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "soil_moisture_3_to_9cm"
]

WEATHER_MESSAGES = {
    "GENERAL": {
        "INACTIVE": {
            "title": "Monitoring unavailable",
            "description": 
            "Weather information is currently unavailable. " + 
            "Refresh the data or check your internet connection."
        },
        "NORMAL": {
            "title": "Weather conditions are stable",
            "description": 
            "No significant weather hazards are expected " + ""
            "during the next 24 hours."
        },
        "WARNING": {
            "title": "Unsettled weather expected",
            "description": 
            "Weather conditions may become hazardous around {time}. " + 
            "Continue monitoring forecasts throughout the day."
        },
        "SEVERE_WARNING": {
            "title": "Dangerous weather conditions",
            "description": 
            "Severe weather is expected around {time}." + 
            "Avoid unnecessary travel and follow official advice."
        }
    },

    "RAIN": {
        "NORMAL": {
            "title": "Light rainfall expected",
            "description": 
            "Rain is forecast, but is not expected to " + 
            "cause significant disruption."
        },
        "WARNING": {
            "title": "Heavy rainfall expected",
            "description": 
            "Periods of heavy rain around {time} may reduce " + 
            "visibility, create surface flooding and affect travel."
        },
        "SEVERE_WARNING": {
            "title": "Dangerous rainfall",
            "description": 
            "Very heavy rainfall around {time} may cause flash " + 
            "flooding, slips and hazardous driving conditions."
        }
    },

    "WIND": {
        "NORMAL": {
            "title": "Light to moderate winds",
            "description": 
            "Wind conditions are not expected to present " + 
            "a significant hazard."
        },
        "WARNING": {
            "title": "Strong winds expected",
            "description": 
            "Strong wind gusts around {time} may affect travel and " + 
            "unsecured outdoor objects."
        },
        "SEVERE_WARNING": {
            "title": "Damaging winds expected",
            "description": 
            "Very strong wind gusts around {time} may damage trees, " + 
            "power lines and structures. Stay indoors where possible."
        }
    },

    "STORM": {
        "NORMAL": {
            "title": "Wet and windy conditions",
            "description": 
            "Rain and wind are expected but are unlikely " + 
            "to cause significant disruption."
        },
        "WARNING": {
            "title": "Storm conditions developing",
            "description": 
            "Heavy rain and strong winds around {time} may cause " + 
            "local disruption and hazardous travel conditions."
        },
        "SEVERE_WARNING": {
            "title": "Severe storm conditions",
            "description": 
            "Dangerous rain and damaging winds are expected " + 
            "around {time}. Significant impacts are possible."
        }
    }
}

FLOOD_MESSAGES = {
    "GENERAL": {
        "INACTIVE": {
            "title": "Monitoring unavailable",
            "description": 
            "Flood information is currently unavailable. " + 
            "Refresh the data or check your internet connection."
        },
        "NORMAL": {
            "title": "Low flood risk",
            "description": 
            "Current rainfall and ground conditions indicate " + 
            "little risk of flooding around {time}."
        },
        "WARNING": {
            "title": "Elevated flood risk",
            "description": 
            "Heavy rainfall and saturated ground may increase the " + 
            "likelihood of localised flooding around {time}."
        },
        "SEVERE_WARNING": {
            "title": "High flood risk",
            "description": 
            "Flooding is likely or imminent around {time}. " + 
            "Be prepared to move to higher ground if necessary."
        }
    },

    "SATURATED_GROUND": {
        "NORMAL": {
            "title": "Ground moisture increasing",
            "description": 
            "Soil moisture is elevated around {time}, but flooding " + 
            "is not currently expected."
        },
        "WARNING": {
            "title": "Ground becoming saturated",
            "description": 
            "Saturated ground conditions expected around {time}. " + 
            "Further rainfall could quickly produce surface flooding."
        },
        "SEVERE_WARNING": {
            "title": "Ground fully saturated",
            "description": 
            "The ground can absorb little additional rainfall, " + 
            "greatly increasing flood risk around {time}."
        }
    },

    "HEAVY_RAIN": {
        "NORMAL": {
            "title": "Rainfall expected",
            "description": 
            "Forecast rainfall is unlikely to cause flooding."
        },
        "WARNING": {
            "title": "Heavy rainfall may cause flooding",
            "description": 
            "Low-lying and poorly drained areas could " + 
            "experience flooding around {time}."
        },
        "SEVERE_WARNING": {
            "title": "Flash flooding possible",
            "description": 
            "Very heavy rainfall around {time} may produce dangerous " + 
            "flash flooding with little warning."
        }
    },

    "COMBINED": {
        "NORMAL": {
            "title": "Conditions being monitored",
            "description": 
            "Rainfall and soil moisture remain within safe limits."
        },
        "WARNING": {
            "title": "Flood conditions developing",
            "description": 
            "Heavy rainfall together with saturated ground around " + 
            "{time} significantly increases flood potential."
        },
        "SEVERE_WARNING": {
            "title": "Dangerous flood conditions",
            "description": 
            "Ground saturation and forecast rainfall around {time} " + 
            "indicate a high likelihood of flooding."
        }
    }
}

EARTHQUAKE_MESSAGES = {
    "GENERAL": {
        "INACTIVE": {
            "title": "Monitoring unavailable",
            "description": 
            "Earthquake data is currently unavailable. " + 
            "Refresh the data or check your internet connection."
        },
        "NORMAL": {
            "title": "Low seismic activity",
            "description": 
            "Only minor background earthquakes have been " + 
            "detected in the region."
        },
        "WARNING": {
            "title": "Increased seismic activity",
            "description": 
            "Recent earthquakes of magnitude {mag} indicate elevated " + 
            "activity nearby. Stay aware of updates."
        },
        "SEVERE_WARNING": {
            "title": "Significant seismic activity detected",
            "description": 
            "A strong magnitude {mag} earthquake has occurred " + 
            "or activity levels are unusually high. " + 
            "Be prepared for aftershocks."
        }
    },

    "SMALL_EVENTS": {
        "NORMAL": {
            "title": "Minor tremors detected",
            "description": 
            "Small earthquakes have been recorded but are not " + 
            "expected to cause damage."
        },
        "WARNING": {
            "title": "Frequent minor earthquakes",
            "description": 
            "A series of small magnitude {mag} earthquakes suggests " + 
            "increased local seismic movement."
        },
        "SEVERE_WARNING": {
            "title": "Persistent tremor activity",
            "description": 
            "Ongoing small magnitude {mag} earthquakes may indicate " + 
            "developing seismic instability in the region."
        }
    },

    "MODERATE_EVENT": {
        "NORMAL": {
            "title": "Light earthquake detected",
            "description": 
            "A light magnitude {mag} earthquake has been recorded " +
            "nearby."
        },
        "WARNING": {
            "title": "Moderate earthquake detected",
            "description": 
            "A moderate magnitude {mag} earthquake may have been " + 
            "felt in surrounding areas. Aftershocks are possible."
        },
        "SEVERE_WARNING": {
            "title": "Strong earthquake detected",
            "description": 
            "A strong magnitude {mag} earthquake has occurred. " + 
            "Check for local impacts and remain alert for aftershocks."
        }
    },

    "MAJOR_EVENT": {
        "WARNING": {
            "title": "Strong earthquake detected",
            "description": 
            "A strong magnitude {mag} earthquake has been recorded. " + 
            "Check for hazards and follow local guidance."
        },
        "SEVERE_WARNING": {
            "title": "Major earthquake detected",
            "description": 
            "A major magnitude {mag} earthquake has occurred. " + 
            "Expect aftershocks and possible damage. " +
            "Follow emergency instructions."
        }
    }
}

# Initiate Local JSON Storage - Create a new file if none exists
if not os.path.exists(LOCATIONS_FILE):
    with open(LOCATIONS_FILE, 'w', encoding='utf-8') as locf:
        json.dump({}, locf, indent=4)
else:
    try:
        with open(LOCATIONS_FILE, 'r', encoding='utf-8') as locf:
            location_data = json.load(locf)
    except (json.JSONDecodeError, OSError):
        location_data = {}

# Load Cites file for location auto-suggestions
def load_cities():
    with open(CITIES_FILE, "r", encoding='utf-8') as ctyf:
        return json.load(ctyf)
    
CITIES = load_cities()

GEOLOCATOR = Nominatim(user_agent="my_geo_app")

class statusIndicator(tk.Canvas):
    """Creates an indicator widget.

    This class creates and contains the functionality of the indicator
    lights of the app.
    """
    def __init__(self, parent, bg_colour):
        super().__init__(
            parent,
            width=14,
            height=14,
            highlightthickness=0,
            bd=0,
            relief="flat",
            bg=bg_colour
        )

        # Assigning indicator colours to every alert status.
        self.status = {
            "SEVERE_WARNING": "#FF0000",
            "WARNING": "#FFDD00",
            "NORMAL": "#00FF00",
            "INACTIVE": "#9CA3AF"
        }

        self.light = self.create_oval(
            2, 2,
            12, 12,
            fill="#9CA3AF",
            outline="black"
        )

    def setColour(self, status):
        """Set the colour of the StatusIndicator.

        :param status: The alert status from disasterApp to correspond \
        to the disaster alert.
        """
        self.itemconfig(self.light, fill=self.status[status])
    
class locationEditFrame(ttk.Frame):
    """Edit menu for editing locationItem details.

    :param frame: The parent container of the edit frame
    :param parent: The disasterApp containing the location dict
    :param locationItem: The corresponding locationItem
    :param locationExists: False if a new location is being created

    This class is used to serve as a way to update and add details to
    new or existing location items. This class is paired with a location
    item class when created and draws information directly from its 
    designated location, allowing edit menu's to isolate their specific
    location for modification.
    """
    def __init__(self, frame, parent, locationItem, locationExists):
        super().__init__(frame)
        self.options = CITIES
        self.locationItem = locationItem
        self.parent = parent
        self.id = locationItem.id
        self.location_exists = locationExists
        self.info = {
            "location": self.parent.locations[self.id]["location"],
            "radius": self.parent.locations[self.id]["radius"],
            "coords": self.parent.locations[self.id]["coords"]
        }

        self.configure(
            style="MainBG.TFrame"
        )

        self.create_display()
    
    def create_display(self):
        """Creates the display of a locationEditFrame."""
        self.input_frame = ttk.Frame(
            self, 
            padding=10,
            style="MainBG.TFrame"
        )
        self.input_frame.pack()
        self.input_frame.columnconfigure(1, weight=1)

        self.location_label = ttk.Label(
            self.input_frame, 
            text="Location: ", 
            padding=10,
            style="LocationField.TLabel"
        )
        self.location_label.grid(row=0, column=0, sticky="e")

        self.location_entry = ttk.Entry(self.input_frame, width=30)
        self.location_entry.insert(0, self.info["location"])
        self.location_entry.grid(row=0, column=1)

        self.radius_label = ttk.Label(
            self.input_frame, 
            text="Radius(km): ",
            padding=10,
            style="LocationField.TLabel"
        )
        self.radius_label.grid(row=1, column=0, sticky="e")

        self.radius_entry = ttk.Entry(self.input_frame, width=30)
        self.radius_entry.insert(0, self.info["radius"])
        self.radius_entry.grid(row=1, column=1)

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True)

        self.location_entry.bind(
            "<KeyRelease>", self.update_suggestions
        )
        self.listbox.bind(
            "<<ListboxSelect>>", self.select_item
        )

        self.actions_frame = ttk.Frame(self, style="MainBG.TFrame")
        self.actions_frame.pack()
        
        # Displays Remove button only if the location pre-existed and 
        # isn't being created as a new location.
        if self.location_exists:
            self.remove_button = ttk.Button(
                self.actions_frame, 
                text="Remove",
                width=8,
                style="EditField.TButton",
                command=self.remove_location
            )
            self.remove_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(
            self.actions_frame,
            text="Save",
            width=8,
            style="EditField.TButton",
            command=self.save_changes
        )
        self.save_button.grid(row=0, column=1, padx=5)
        self.cancel_button = ttk.Button(
            self.actions_frame,
            text="Cancel",
            width=8,
            style="EditField.TButton",
            command=self.cancel_changes
        )
        self.cancel_button.grid(row=0, column=2, padx=5)

    def validate_city(self, value):
        """Validates a city input against CITIES stored data."""
        valid_list = []
        # Checks if the input value is in the valid city options.
        for city in self.options:
            full_name = f"{city['city']}, {city['country']}"
            if value.lower() in full_name.lower():
                valid_list.append(full_name)
        return valid_list

    def update_suggestions(self, event):
        """Updates location suggestions in locationEditItem's listbox."""
        typed = self.location_entry.get().lower()
        self.listbox.delete(0, tk.END)

        # Exit condition if the location input field is empty.
        if not typed:
            return
        
        matches = self.validate_city(typed)
        
        # Populate the listbox according to potential location matches.
        if matches:
            for match in matches:
                self.listbox.insert(tk.END, match)
        else:
            self.listbox.insert(tk.END, "No city found")

    def select_item(self, event):
        """Gets value of selected locationEditItem listbox."""
        selection = self.listbox.curselection()

        # Exit condition if no selection is found.
        if not selection:
            return

        value = self.listbox.get(selection[0])

        # Exit if the listbox returned 'No city found'.
        if value == "No city found":
            return
        
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, value)
        self.listbox.delete(0, tk.END)
    
    def validate_radius(self):
        """Checks if radius input value is a positive integer.
        
        This method attempts to return the radius as a positive real 
        integer and returns an error message upon failure.
        """
        error = False
        try:
            radius = int(self.info["radius"])
            if radius > 0:
                self.info["radius"] = radius
            else:
                error = True
        except TypeError, ValueError:
            error = True

        if error:
            messagebox.showerror(
                    "Input Error", 
                    ("Radius Input Must be a " +
                    "Positive Integer Value to continue")
            )
            return False
        else:
            return True
    
    def remove_location(self):
        """Removes the locationItem's location."""
        l = self.parent.locations[self.id]["location"]
        ask_to_delete = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you would like to remove location: {l}"
        )

        if not ask_to_delete:
            return
        
        # If the location was the disasterApp's selected location, 
        # change the selected location to none and refresh display's.
        if self.parent.selected_location == self.locationItem.id:
            self.parent.selected_location = None
            self.parent.update_all_display()

        self.parent.locations.pop(self.locationItem.id, None)
        self.parent.update_local_storage()
        
        self.parent.location_items.pop(self.locationItem.id, None)
        self.locationItem.destroy()

        if self.parent.locations == {}:
            self.parent.location_empty_label.config(
                text="No locations stored. " + 
                "Create a new location to begin."
            )
        else:
            self.parent.refresh_all_data()
        messagebox.showinfo(
            "Successfully Removed", 
            f"Location: {l} removed successfully."
        )
        self.destroy()
    
    def save_changes(self):
        """Saves changes for locationItem's location.
        
        Only updates location if the input values are all valid.
        Error shown if unsuccessfully validated.
        """
        self.info["location"] = self.location_entry.get().strip()
        self.info["radius"] = self.radius_entry.get().strip()

        # Check if the input fields have been entered in correctly.
        if self.info["location"] == "" or\
           self.info["location"] == "No city found":
            messagebox.showerror(
                "Input Error",
                "A valid location is required to save changes"
            )
            return
        if self.info["radius"] == "":
            messagebox.showerror(
                "Input Error",
                "A valid radius is required to save changes"
            )
            return
        
        # Run validation checks on all inputs to confirm inputs are 
        # acceptable.
        validated_location = self.get_coordinates()
        validated_radius = self.validate_radius()

        if not (validated_radius and validated_location):
            return
        self.info["timezone"] = TF.timezone_at(
            lng=self.info["coords"][1], 
            lat=self.info["coords"][0]
        )

        self.parent.locations[self.id]["location"] = self.info[
            "location"]
        self.parent.locations[self.id]["radius"] = self.info["radius"]
        self.parent.locations[self.id]["coords"] = self.info["coords"]
        self.parent.locations[self.id]["timezone"] = \
            self.info["timezone"]
        self.parent.locations[self.id]["emergency"] = \
            self.info["emergency"]
        
        self.locationItem.location_label.config(
            text=self.info["location"]
        )
        self.locationItem.radius_label.config(
            text=f"Radius: {self.info['radius']}km"
        )

        self.parent.update_local_storage()
        self.parent.refresh_all_data()
        self.parent.location_empty_label.config(
            text="Locations List: "
        )
        self.destroy()
    
    def cancel_changes(self):
        """Cancel any changes made to locationItem's location.
        
        Removes the locationItem and its value if a new location was
        created without any values.
        """
        if self.location_exists:
            self.destroy()
        else:
            self.parent.locations.pop(
                self.locationItem.id, None
            )
            self.locationItem.destroy()
            if not self.parent.locations:
                self.parent.location_empty_label.config(
                    text="No locations stored. " + 
                    "Create a new location to begin."
                )
            self.destroy()
    
    def get_coordinates(self):
        """Gets lat lon coordinates from a 'City, Country' address."""
        # Validate location input to ensure geolocator call has a 
        # viable input.
        address = self.location_entry.get()
        if "," not in address:
            messagebox.showerror(
                "Format Error", 
                "Locations must be written as: City, Country"
            )
            return False
        
        valid_city = self.validate_city(address)
        
        if valid_city == []:
            messagebox.showerror(
                "Value Error", 
                "Location Not Found.\n\n" + 
                "Please use suggestions provided for available cities"
            )
            return False
        
        # Attempt to get location coordinates for API data.
        # Produce error upon failure.
        location = GEOLOCATOR.geocode(address, addressdetails=True)

        if not location:
            messagebox.showerror(
                "Location Error", 
                "An error occured while trying to get location info" +
                "\nPlease try again later"
            )
            return False
        
        self.info["coords"] = (
            location.latitude, 
            location.longitude
        )

        country_code = location.raw.get(
            'address', {}).get('country_code', '').upper()
        
        if not country_code:
            messagebox.showerror(
                "Country Error", 
                "Could not determine country code"
            )
            return False
        
        emergency_api_url = \
            f"https://emergencynumberapi.com/api/country/{country_code}"
        response = requests.get(emergency_api_url)

        if not response.status_code == 200:
            messagebox.showerror(
                "Error", 
                "Failed to retrieve emergency contact information " + 
                f"for: {address}"
            )
            return False
        
        data = response.json().get("data", {})

        if data["member_112"]:
            self.info["emergency"] = [data["dispatch"]["all"][0]]
        else:
            self.info["emergency"] = [
                data["fire"]["all"][0],
                data["ambulance"]["all"][0],
                data["police"]["all"][0]
            ]
        return True
        
            


class locationItem(ttk.Frame):
    """Creates a location item.

    :param frame: The Parent container of the locationItem
    :param parent: The disasterApp that contains the location dict
    :param id: The location id assigned to the locationItem

    This class is responsible for housing a saved location within the
    program, serving as a modular element that can be cloned and 
    removed, retaining its own information for API access and window 
    configuration.
    """
    def __init__(self, frame, parent, id):
        super().__init__(frame, padding=0, style="InfoBG.TFrame")
        self.parent = parent
        self.id = id

        self.pack(fill="x", padx=5, pady=5, expand=False)
        self.columnconfigure(0, weight=1)
        
        self.info_frame = ttk.Frame(
            self, 
            padding=10, 
            style="InfoBG.TFrame"
        )
        self.info_frame.grid(row=0, column=0, sticky="w")

        # Reinstate previous save data if created from existing 
        # location stored in local storage.
        previous_info = parent.locations[id]

        self.location_label = ttk.Label(
            self.info_frame,
            text=previous_info["location"],
            style="LocationOption.TLabel",
        )
        self.location_label.grid(row=0, column=0, sticky="w")

        self.radius_label = ttk.Label(
            self.info_frame,
            text=f"Radius: {previous_info['radius']}km",
            style="RadiusOption.TLabel"
        )
        self.radius_label.grid(row=1, column=0, sticky="w")
    
        self.edit_button = ttk.Button(
            self,
            text="Edit",
            width=4,
            style="LocationAction.TButton",
            command=lambda: self.edit_location(True)
        )
        self.edit_button.grid(row=0, column=1, sticky="e")

        self.select_button = ttk.Button(
            self,
            text="Select",
            width=6,
            style="LocationAction.TButton",
            command=self.select_location
        )
        self.select_button.grid(row=0, column=2, sticky="e", padx=5)

        if not self.parent.locations[id]["location"]:
            self.edit_location(False)
    
    def display_self(self):
        """Show the locationItem."""
        self.pack(fill="x", expand=False)

    def edit_location(self, locationExists):
        """Open a locationEditFrame to edit / remove the location.
        
        Allows the user to edit the locationItem by opening a 
        locationEditFrame class that can edit or remove this items 
        location data from temporary and local storage.
        """
        self.edit_menu = locationEditFrame(
            self.parent.location_popup_menu, 
            self.parent, 
            self,
            locationExists
        )
        self.edit_menu.lift()
        self.edit_menu.place(
            relx=0.5, 
            rely=0.5, 
            relheight=1, 
            relwidth=1, 
            anchor="center"
        )
        self.edit_menu.update_idletasks()
    
    def select_location(self):
        """Sets this locationItem's location as the active location"""
        self.parent.set_selected_location(self.id)
    
    def select_location_ui_only(self):
        """Change ui of select button to active"""
        self.select_button.config(text="(Active)")
        self.select_button.state(["disabled"])
  
    def deselect_location(self):
        """Change ui of select button to inactive"""
        self.select_button.config(text="Select")
        self.select_button.state(["!disabled"])
    
    def refresh_location(self):
        """Update locationItem info display"""
        data = self.parent.locations[self.id]
        self.location_label.config(
            text=data["location"],
            wraplength=self.location_label.winfo_width()
        )
        self.radius_label.config(
            text=f"Radius: {data["radius"]}km"
        )

class disasterApp:
    """Creates an instance of the disasterApp.
    
    :param root: The root window for the app
    :param location_data: The locally stored location data
    :param system_data: The locally stored system data

    This class is responsible for initiating and operating the disaster
    app.
    """
    def __init__(self, root, location_data):
        self.root = root
        self.root.title("Local Disaster Alert System")
        self.root.minsize(600, 600)
        self.root.geometry("600x600+500+0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.root.configure(bg="#F0F0F0")
        
        self.locations = {}
        self.location_items = {}
        self.selected_location = None

        if location_data:
            self.locations = location_data
            self.nextid = int(list(location_data)[-1]) + 1
        else:
            self.nextid = 0

        self.weather_session = WeatherAPI.initialize_cache()
        self.earthquake_session = EarthquakeAPI.initialize_cache()

        self.alert_messages = {
            "weather": WEATHER_MESSAGES,
            "flood": FLOOD_MESSAGES,
            "earthquake": EARTHQUAKE_MESSAGES
        }

        self.weather_data = {}
        self.flood_data = {}
        self.earthquake_data = {}
        
        # The forecast value for alerts in hours
        self.data_forecast = 24

        self.alert_strings = {
            "INACTIVE": ["Inactive"],
            "NORMAL": ["Normal"],
            "WARNING": ["Warning"],
            "SEVERE_WARNING": ["Severe", "Severe Warning"]
        }
        
        self.create_styles()
        self.create_frames()
        self.create_widgets_all()
        self.create_location_menu()
        self.show_home_display()
        if self.locations:
            self.refresh_all_data()

    def create_styles(self):
        """Creates the ttk styles for the disasterApp."""
        self.style.configure(
            "MainBG.TFrame",
            background="#F0F0F0"
        )
        self.style.configure(
            "InfoBG.TFrame",
            background="#D9D9D9"
        )
        self.style.configure(
            "LastRefresh.TLabel",
            background="#F0F0F0",
            foreground="#575757"
        )
        self.style.configure(
            "CurrentLocation.TLabel",
            font=("TkDefaultFont", 24),
            background="#F0F0F0"
        )
        self.style.configure(
            "CurrentRadius.TLabel",
            font=("TkDefaultFont", 15),
            background="#F0F0F0"
        )
        self.style.configure(
            "MainBG.TButton",
            background="#D9D9D9",
            relief="flat",
            borderwidth=0
        )
        self.style.configure(
            "MainStatus.TLabel",
            font=("TkDefaultFont", 25)
        )
        self.style.configure(
            "AllStatusBG.TFrame",
            background="#FFFFFF"
        )
        self.style.configure(
            "AllStatusText.TLabel",
            font=("TkDefaultFont", 16),
            background="#FFFFFF"
        )
        self.style.configure(
            "SubtleBG.TButton",
            background="#D9D9D9",
            foreground="#575757",
            relief="flat",
            borderwidth=0
        )
        self.style.configure(
            "LocationOption.TLabel",
            font=("TkDefaultFont", 15),
            background="#D9D9D9"
        )
        self.style.configure(
            "RadiusOption.TLabel",
            font=("TkDefaultFont", 11),
            background="#D9D9D9"
        )
        self.style.configure(
            "LocationAction.TButton",
            background="#EBEBEB",
            relief="flat",
            borderwidth=0
        )
        self.style.configure(
            "LocationEmpty.TLabel",
            font=("TkDefaultFont", 16),
            background="#F0F0F0"
        )
        self.style.configure(
            "LocationField.TLabel",
            font=("TkDefaultFont", 14),
            background="#F0F0F0"
        )
        self.style.configure(
            "EditField.TButton",
            background="#D9D9D9",
            relief="flat",
            borderwidth=0
        )
        self.style.configure(
            "WeatherStatus.TLabel",
            font=("TkDefaultFont", 16),
            background="#F0F0F0"
        )
        self.style.configure(
            "WeatherMainCard.TFrame",
            background="#FFFFFF"
        )
        self.style.configure(
            "WeatherSubCard.TFrame",
            background="#F2F2F2"
        )
        self.style.configure(
            "WeatherMainInfo.TLabel",
            font=("TkDefaultFont", 12),
            background="#FFFFFF"
        )
        self.style.configure(
            "WeatherRainInfo.TLabel",
            font=("TkDefaultFont", 12),
            background="#FFFFFF"
        )
        self.style.configure(
            "WeatherCloudInfo.TLabel",
            font=("TkDefaultFont", 8),
            background="#FFFFFF"
        )
        self.style.configure(
            "WeatherSubInfo.TLabel",
            font=("TkDefaultFont", 12),
            background="#F2F2F2",
            foreground="#555555"
        )

    
    def create_frames(self):
        """Creates the layout structure of the GUI.
        
        The usage of create_frames when creating frames used to control 
        the positioning and layout of items on screen keeps code
        consisten and separate from the widgets (elements) of the GUI.
        """
        
        self.main_frame = ttk.Frame(self.root, style="MainBG.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        self.refresh_frame = ttk.Frame(
            self.main_frame, 
            style="MainBG.TFrame"
        )
        self.refresh_frame.pack(fill="x")

        self.location_frame = ttk.Frame(
            self.main_frame, 
            padding=10,
            style="MainBG.TFrame"
        )
        self.location_frame.pack(fill="both", expand=True)
        self.location_frame.grid_columnconfigure(1, weight=1)

        self.all_status_frame = ttk.Frame(
            self.main_frame, 
            padding=(10, 30),
            style="InfoBG.TFrame"
        )
        self.all_status_frame.pack(fill="x", expand=True)

        self.footer_frame = ttk.Frame(
            self.main_frame, 
            style="MainBG.TFrame"
        )
        self.footer_frame.pack(
            side=tk.BOTTOM, 
            fill="both",
            expand=True,
            pady=(0, 5)
        )

        # All frames for Weather-specific window.
        self.weather_frame = ttk.Frame(
            self.main_frame,
            style="MainBG.TFrame"
        )
        self.weather_frame.columnconfigure(0, weight=1)

        self.w_status_frame =ttk.Frame(
            self.weather_frame, 
            style="MainBG.TFrame"
        )
        self.w_status_frame.grid(row=0, column=0)

        self.w_info_container = ttk.Frame(
            self.weather_frame, 
            style="InfoBG.TFrame"
        )
        self.w_info_container.grid(row=2, column=0, sticky="nsew")

        self.w_info_row1 = ttk.Frame(
            self.w_info_container, 
            style="InfoBG.TFrame"
        )
        self.w_info_row1.pack(
            fill="both", 
            expand=True,
            pady=(15, 5),
            padx=2
        )
        self.w_info_row1.columnconfigure([0, 2], weight=1)
        self.w_info_row1.columnconfigure(1, weight=2)

        self.w_info_row2 = ttk.Frame(
            self.w_info_container, 
            style="InfoBG.TFrame"
        )
        self.w_info_row2.pack(
            fill="both", 
            expand=True,
            pady=(5, 15),
            padx=2
        )
        self.w_info_row2.columnconfigure([0, 1, 2, 3], weight=1)

        self.w_info_sunCol = ttk.Frame(
            self.w_info_row1, 
            style="InfoBG.TFrame"
        )
        self.w_info_sunCol.grid(row=0, column=0, sticky="nsew")
        self.w_info_sunCol.rowconfigure(0, weight=1)
        self.w_info_sunCol.rowconfigure(1, weight=1)
        self.w_info_sunCol.columnconfigure(0, weight=1)

        self.w_info_rainCol = ttk.Frame(
            self.w_info_row1, 
            style="InfoBG.TFrame"
        )
        self.w_info_rainCol.grid(row=0, column=2, sticky="nsew")
        self.w_info_rainCol.rowconfigure(0, weight=1)
        self.w_info_rainCol.rowconfigure(1, weight=1)
        self.w_info_rainCol.columnconfigure(0, weight=1)
        
        # All frames for flood-specific window.
        self.flood_frame = ttk.Frame(self.main_frame)

        self.f_info_container = ttk.Frame(
            self.flood_frame, 
            padding=10,
            style="InfoBG.TFrame"
        )
        self.f_info_container.pack()

        self.f_description_container = ttk.Frame(
            self.f_info_container, 
            padding=10,
            style="InfoBG.TFrame"
        )
        self.f_description_container.grid(
            row=0, 
            column=0, 
            sticky="nsew"
        )

        self.f_status_container = ttk.Frame(
            self.f_description_container, 
            padding=10,
            style="InfoBG.TFrame"
        )
        self.f_status_container.grid(row=0, column=0, sticky="nsew")

        self.f_details_container = ttk.Frame(
            self.f_info_container, padding=10
        )
        self.f_details_container.grid(
            row=0, 
            column=1, 
            sticky="nsew"
        )
        
        # All frames for earthquake-specific window.
        self.earthquake_frame = ttk.Frame(self.main_frame)

        self.q_info_container = ttk.Frame(
            self.earthquake_frame, 
            padding=10,
            style="InfoBG.TFrame"
        )
        self.q_info_container.pack()
        self.q_info_container.columnconfigure(0, weight=1)
        
        self.q_status_container = ttk.Frame(
            self.q_info_container, 
            padding=10,
            style="InfoBG.TFrame"
        )
        self.q_status_container.grid(row=0, column=0)

    def create_widgets_all(self):
        """Run all create_widget methods in disasterApp."""
        self.create_widgets_main()
        self.create_widgets_weather()
        self.create_widgets_flood()
        self.create_widgets_earthquake()
    
    def create_widgets_main(self):
        """Creates the widgets for the Main GUI.

        this method is used when creating all of the elements seen 
        on the home screen by users and is responsible for populating 
        the main gui frame.
        """
        # Refresh tag at top of GUI.
        self.last_refresh_label = ttk.Label(
            self.refresh_frame, 
            text=f"Last refreshed at: --",
            style="LastRefresh.TLabel"
            )
        self.last_refresh_label.pack(side="top")

        # Current Location Display.
        self.current_location_label = ttk.Label(
            self.location_frame,
            text="Current Location: Not Selected",
            padding=(10, 0),
            style="CurrentLocation.TLabel",
        )
        self.current_location_label.grid(row=0, column=0)

        self.change_location_button = ttk.Button(
            self.location_frame,
            text="Change",
            width=8,
            style="MainBG.TButton",
            command=self.show_location_menu
        )
        self.change_location_button.grid(row=0, column=2, sticky="e")
        
        self.search_radius_label = ttk.Label(
            self.location_frame,
            text="Radius: Not Selected",
            padding=(10, 0),
            style="CurrentRadius.TLabel"
        )
        self.search_radius_label.grid(row=1, column=0, sticky="w")

        # Main Status Display (home screen).
        self.all_status_title = ttk.Label(
            self.all_status_frame,
            text="Status Monitoring",
            padding=5,
            style="MainStatus.TLabel"
        )
        self.all_status_title.pack()

        # Row 1: Weather Status.
        self.all_status_row1 = ttk.Frame(
            self.all_status_frame,
            padding=2.5,
            style="AllStatusBG.TFrame"
        )
        self.all_status_row1.pack(fill="x", expand=True, pady=2.5)
        self.all_status_row1.grid_columnconfigure(2, weight=1)

        self.all_status_w_indicator = statusIndicator(
            self.all_status_row1,
            "#FFFFFF"
        )
        self.all_status_w_indicator.grid(
            row=0, 
            column=0, 
            padx=[20, 0], 
            pady=10
        )

        self.all_status_w_label = ttk.Label(
            self.all_status_row1,
            text="Weather: Monitoring Unavailable",
            padding=10,
            style="AllStatusText.TLabel",
            wraplength=300
        )
        self.all_status_w_label.grid(row=0, column=1)
        
        self.all_status_w_button = ttk.Button(
            self.all_status_row1,
            text="View Weather Details",
            width=22,
            padding=(0, 6),
            style="MainBG.TButton",
            command=self.show_weather_display
        )
        self.all_status_w_button.grid(
            row=0, 
            column=3, 
            sticky="e", 
            padx=8
        )

        # Row 2: Flood Status.
        self.all_status_row2 = ttk.Frame(
            self.all_status_frame,
            padding=2.5,
            style="AllStatusBG.TFrame"
        )
        self.all_status_row2.pack(fill="x", expand=True, pady=2.5)
        self.all_status_row2.grid_columnconfigure(2, weight=1)

        self.all_status_f_indicator = statusIndicator(
            self.all_status_row2,
            "#FFFFFF"
        )
        self.all_status_f_indicator.grid(
            row=0, 
            column=0, 
            padx=[20, 0], 
            pady=10
        )

        self.all_status_f_label = ttk.Label(
            self.all_status_row2,
            text="Flood Risk: Monitoring Unavailable",
            padding=10,
            style="AllStatusText.TLabel",
            wraplength=300
        )
        self.all_status_f_label.grid(row=0, column=1)

        self.all_status_f_button = ttk.Button(
            self.all_status_row2,
            text="View Flood Alerts",
            width=22,
            padding=(0, 6),
            style="MainBG.TButton",
            command=self.show_flood_display
        )
        self.all_status_f_button.grid(
            row=0, 
            column=3, 
            sticky="e", 
            padx=8
        )

        # Row 3: Earthquake Status.
        self.all_status_row3 = ttk.Frame(
            self.all_status_frame,
            padding=2.5,
            style="AllStatusBG.TFrame"
        )
        self.all_status_row3.pack(fill="x", expand=True, pady=2.5)
        self.all_status_row3.grid_columnconfigure(2, weight=1)

        self.all_status_q_indicator = statusIndicator(
            self.all_status_row3,
            "#FFFFFF"
        )
        self.all_status_q_indicator.grid(
            row=0, 
            column=0, 
            padx=[20, 0], 
            pady=10
        )

        self.all_status_q_label = ttk.Label(
            self.all_status_row3,
            text="Earthquake Alert: Monitoring Unavailable",
            padding=10,
            style="AllStatusText.TLabel",
            wraplength=300
        )
        self.all_status_q_label.grid(row=0, column=1)

        self.all_status_q_button = ttk.Button(
            self.all_status_row3,
            text="View Earthquake Alerts",
            width=22,
            padding=(0, 6),
            style="MainBG.TButton",
            command=self.show_earthquake_display
        )
        self.all_status_q_button.grid(
            row=0, 
            column=3, 
            sticky="e", 
            padx=8
        )

        # Footer Buttons.
        self.back_home_button = ttk.Button(
            self.footer_frame,
            text="Back home",
            padding=(0, 8),
            style="MainBG.TButton",
            command=self.show_home_display
        )

        self.all_sync_button = ttk.Button(
            self.footer_frame, 
            text="Sync from Servers", 
            padding=(10, 8),
            style="MainBG.TButton",
            command=self.refresh_all_data
        )
        self.all_sync_button.place(relx=0.5, rely=0.5, anchor="center")

    def create_widgets_weather(self):
        """Creates the widgets for the Weather GUI.

        this method is used when creating all of the elements seen 
        on the weather screen by users and is responsible for populating 
        the weather gui frame.
        """
        # Weather Main Status.
        self.weather_status_indicator = statusIndicator(
            self.w_status_frame,
            "#F0F0F0"
        )
        self.weather_status_indicator.grid(
            row=0,
            column=0, 
        )
        
        self.weather_status_message = ttk.Label(
            self.w_status_frame,
            text="Weather Status:",
            padding=10,
            style="WeatherStatus.TLabel",
            wraplength=350
        )
        self.weather_status_message.grid(
            row=0, 
            column=1, 
        )

        self.weather_status_description = ttk.Label(
            self.weather_frame,
            text="Inactive",
            padding=10,
            style="WeatherStatus.TLabel",
            wraplength=350
        )
        self.weather_status_description.grid(row=1, column=0)

        # Weather Information (From API).
        self.weather_sunrise_card = ttk.Frame(
            self.w_info_sunCol,
            padding=(6, 3),
            style="WeatherMainCard.TFrame"
        )
        self.weather_sunrise_card.grid(
            row=0, 
            column=0, 
            sticky="nsew",
            pady=(0, 3),
            padx=(10, 5)
        )
        self.weather_sunrise_label = ttk.Label(
            self.weather_sunrise_card,
            text="Sunrise: --",
            style="WeatherMainInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_sunrise_label.pack(expand=True)

        self.weather_sunset_card = ttk.Frame(
            self.w_info_sunCol,
            padding=(6, 3),
            style="WeatherMainCard.TFrame"
        )
        self.weather_sunset_card.grid(
            row=1, 
            column=0, 
            sticky="nsew",
            pady=(3, 0),
            padx=(10, 5)
        )
        self.weather_sunset_label = ttk.Label(
            self.weather_sunset_card,
            text="Sunset: --",
            style="WeatherMainInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_sunset_label.pack(expand=True)

        self.weather_temp_card = ttk.Frame(
            self.w_info_row1,
            padding=(5, 0),
            style="WeatherMainCard.TFrame"
        )
        self.weather_temp_card.grid(
            row=0, 
            column=1,
            rowspan=1, 
            sticky="nsew",
            padx=5
        )
        self.weather_temp_label = ttk.Label(
            self.weather_temp_card,
            text="Current Temperature: --℃\n\nfeels like: --℃",
            padding=15,
            style="WeatherMainInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_temp_label.pack(expand=True)

        self.weather_rain_card = ttk.Frame(
            self.w_info_rainCol,
            padding=(6, 3),
            style="WeatherMainCard.TFrame"
        )
        self.weather_rain_card.grid(
            row=0, 
            column=0, 
            sticky="nsew",
            padx=(5, 10)
        )
        self.weather_rain_chance_label = ttk.Label(
            self.weather_rain_card,
            text="Chance of Rain:\n--%",
            style="WeatherRainInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_rain_chance_label.pack(expand=True)

        self.weather_cloud_card = ttk.Frame(
            self.w_info_rainCol,
            padding=(6, 3),
            style="WeatherMainCard.TFrame"
        )
        self.weather_cloud_card.grid(
            row=1, 
            column=0, 
            sticky="nsew",
            padx=(5, 10)
        )
        self.weather_cloud_cover_label = ttk.Label(
            self.weather_cloud_card,
            text="--% Cloud Cover",
            style="WeatherCloudInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_cloud_cover_label.pack(expand=True)

        self.weather_wind_speeds_card = ttk.Frame(
            self.w_info_row2,
            padding=10,
            style="WeatherSubCard.TFrame"
        )
        self.weather_wind_speeds_card.grid(
            row=0, 
            column=0, 
            sticky="nsew", 
            padx=(10, 5)
        )
        self.weather_wind_speeds_label = ttk.Label(
            self.weather_wind_speeds_card,
            text="Wind Speeds: \n--km/h",
            style="WeatherSubInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_wind_speeds_label.pack(expand=True)
        
        self.weather_wind_gusts_card = ttk.Frame(
            self.w_info_row2,
            padding=10,
            style="WeatherSubCard.TFrame"
        )
        self.weather_wind_gusts_card.grid(
            row=0, 
            column=1,
            sticky="nsew",
            padx=5
        )
        self.weather_wind_gusts_label = ttk.Label(
            self.weather_wind_gusts_card,
            text="Wind Gusts: \n--km/h",
            style="WeatherSubInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_wind_gusts_label.pack(expand=True)

        self.weather_humidity_card = ttk.Frame(
            self.w_info_row2,
            padding=10,
            style="WeatherSubCard.TFrame"
        )
        self.weather_humidity_card.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=5
        )
        self.weather_humidity_label = ttk.Label(
            self.weather_humidity_card,
            text="Humidity: \n--%",
            style="WeatherSubInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_humidity_label.pack(expand=True)
        
        self.weather_surface_pressure_card = ttk.Frame(
            self.w_info_row2,
            padding=10,
            style="WeatherSubCard.TFrame"
        )
        self.weather_surface_pressure_card.grid(
            row=0, 
            column=3,
            sticky="nsew",
            padx=(5, 10)
        )
        self.weather_surface_pressure_label = ttk.Label(
            self.weather_surface_pressure_card,
            text="Surface Pressure: \n--hPa",
            style="WeatherSubInfo.TLabel",
            anchor="center",
            justify="center"
        )
        self.weather_surface_pressure_label.pack(expand=True)

    def create_widgets_flood(self):
        """Creates the widgets for the Flood GUI.

        This method is used when creating all of the elements seen 
        on the flood screen by users and is responsible for populating 
        the flood gui frame.
        """

        # Flood Status.
        self.flood_status_indicator = statusIndicator(
            self.f_status_container,
            "#D9D9D9"
        )
        self.flood_status_indicator.grid(row=0, column=0)

        self.flood_status_message = ttk.Label(
            self.f_status_container,
            text="Flood Risk: Inactive",
            justify="left"
        )
        self.flood_status_message.grid(row=0, column=1, padx=10)

        self.flood_status_description = ttk.Label(
            self.f_description_container,
            text="",
            padding=10,
            wraplength=200
        )
        self.flood_status_description.grid(row=1, column=0)

        # Flood Information (From API).
        self.flood_conditions_label = ttk.Label(
            self.f_details_container,
            text="Current Flood Conditions\n",
        )
        self.flood_conditions_label.grid(row=0, column=0, sticky="nsew")
        
        self.flood_ground_sat_label = ttk.Label(
            self.f_details_container,
            text="Ground Saturation \t--",
        )
        self.flood_ground_sat_label.grid(row=1, column=0, sticky="nsew")

        self.flood_rain_1hr_label = ttk.Label(
            self.f_details_container,
            text="Current Rainfall \t--mm/h",
        )
        self.flood_rain_1hr_label.grid(row=2, column=0, sticky="nsew")

        self.flood_rain_6hr_label = ttk.Label(
            self.f_details_container,
            text="6-hour Forecast \t--mm",
        )
        self.flood_rain_6hr_label.grid(row=3, column=0, sticky="nsew")

        self.flood_rain_24hr_label = ttk.Label(
            self.f_details_container,
            text="24-hour Rainfall \t--mm"
        )
        self.flood_rain_24hr_label.grid(row=4, column=0, sticky="nsew")

        self.flood_rain_prob_label = ttk.Label(
            self.f_details_container,
            text="Rain Probability \t--%"
        )
        self.flood_rain_prob_label.grid(row=5, column=0, sticky="nsew")

    def create_widgets_earthquake(self):
        """Creates the widgets for the Earthquake GUI.

        This method is used when creating all of the elements seen 
        on the earthquake screen by users and is responsible for 
        populating the earthquake gui frame.
        """

        # Earthquake Status.
        self.earthquake_status_indicator = statusIndicator(
            self.q_status_container,
            "#D9D9D9"
        )
        self.earthquake_status_indicator.grid(row=0, column=0)

        self.earthquake_status_message = ttk.Label(
            self.q_status_container,
            text="Earthquake Activity: Inactive"
        )
        self.earthquake_status_message.grid(row=0, column=1, padx=10)

        self.earthquake_status_description = ttk.Label(
            self.q_info_container,
            text="",
            padding=10
        )
        self.earthquake_status_description.grid(
            row=1, 
            column=0, 
            sticky="nsew"
        )

        # Earthquake Information (From API).
        self.nearby_earthquake_label = ttk.Label(
            self.q_info_container,
            text="Nearby Earthquakes: ",
            padding=10,
            anchor="center"
        )
        self.nearby_earthquake_label.grid(
            row=2,
            column=0,
            sticky="nsew"
        )
        self.earthquake_seismic_activity = ttk.Treeview(
            self.q_info_container,
            columns=("time", "place", "depth", "magnitude")
        )
        self.earthquake_seismic_activity.column(
            "#0", width=0, stretch=tk.NO
        )
        self.earthquake_seismic_activity.heading(
            "time", text="Date & Time"
        )
        self.earthquake_seismic_activity.column(
            "time", width=150
        )
        self.earthquake_seismic_activity.heading(
            "place", text="Location"
        )
        self.earthquake_seismic_activity.column(
            "place", width=270
        )
        self.earthquake_seismic_activity.heading(
            "depth", text="Depth (m)"
        )
        self.earthquake_seismic_activity.column(
            "depth", width=80
        )
        self.earthquake_seismic_activity.heading(
            "magnitude", text="Magnitude"
        )
        self.earthquake_seismic_activity.column(
            "magnitude", width=80
        )
        
        self.earthquake_seismic_activity.grid(
            row=3, 
            column=0, 
            sticky="nsew"
        )
    
    def show_home_display(self):
        """Updates disasterApp view to show home info."""
        self.all_status_frame.pack(fill="x", expand=True)
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack_forget()
    
    def show_weather_display(self):
        """Updates disasterApp view to show weather info."""
        self.all_status_frame.pack_forget()
        self.weather_frame.pack(fill="x", expand=True)
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack(side="left", padx=10)

    def show_flood_display(self):
        """Updates disasterApp view to show flood info."""
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack(fill="x", expand=True)
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack(side="left", padx=10)
    
    def show_earthquake_display(self):
        """Updates disasterApp view to show earthquake info."""
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack(fill="x", expand=True)
        self.back_home_button.pack(side="left", padx=10)
    
    def create_location_menu(self):
        """Initiates the disasterApp location menu popup."""
        self.location_popup_menu = ttk.Frame(
            self.root,
            borderwidth=3,
            relief="groove",
            style="MainBG.TFrame"
        )

        self.location_empty_frame = ttk.Frame(
            self.location_popup_menu,
            style="MainBG.TFrame"
        )
        self.location_empty_frame.pack()
        self.location_empty_label = ttk.Label(
            self.location_empty_frame,
            text="No locations stored. Create a new location to begin.",
            padding=10,
            style="LocationEmpty.TLabel"
        )
        self.location_empty_label.pack()

        self.location_popup_list = ttk.Frame(
            self.location_popup_menu,
            padding=10,
            style="MainBG.TFrame"
        )
        self.location_popup_list.pack(fill="both", expand=True)
        self.location_popup_list.propagate(False)
                
        self.close_location_menu_button = ttk.Button(
            self.location_popup_menu,
            text="Close",
            padding=5,
            width=6,
            style="SubtleBG.TButton",
            command=self.location_popup_menu.place_forget
        )
        self.close_location_menu_button.pack(side="left", padx=5)
        
        self.new_location_button = ttk.Button(
            self.location_popup_menu,
            text="New Location",
            padding=5,
            style="SubtleBG.TButton",
            command=self.create_location
        )
        self.new_location_button.place(relx=0.5, rely=1, anchor="s")
        
    def show_location_menu(self):
        """Opens the disasterApp location menu.
        
        If location data exists then the menu will be populated with 
        locationItems assigned to each existing location found.
        """
        if self.locations:
            if self.location_items:
                for location in self.location_items.values():
                    location.display_self()
                    location.refresh_location()
            else:
                for id in self.locations.keys():
                    self.location_items[id] = locationItem(
                        self.location_popup_list,
                        self,
                        id
                    )
            self.location_empty_label.config(
                text="Locations List: "
            )
        else:
            self.location_empty_label.config(
                text="No locations stored. " + 
                "Create a new location to begin."
            )
        self.location_popup_menu.place(
            relx=0.5, 
            rely=0.5, 
            anchor="center",
            relheight=0.9,
            relwidth=0.9
        )
        self.location_popup_menu.update_idletasks()
    
    def create_location(self):
        """Creates a new location.
        
        This method initiates a blank location item in the disasterApp
        and assigns a locationItem to it.
        """
        id = f"{self.nextid}"
        self.nextid += 1
        self.locations[id] = {
            "location": "",
            "radius": "",
            "coords": "",
            "timezone": "",
            "emergency": ""
        }

        self.location_items[id] = locationItem(
            self.location_popup_list, 
            self, 
            id
        )

    def set_selected_location(self, new_id):
        """Activates the selected location and deselect other locations.
        
        :param new_id: The id of the new selected location
        """
        if self.selected_location is not None:
            old = self.location_items.get(self.selected_location)
            if old:
                old.deselect_location()

        self.selected_location = f"{new_id}"

        new = self.location_items.get(new_id)
        if new:
            new.select_location_ui_only()

        self.update_all_display()
        self.location_popup_menu.place_forget()
    
    def update_all_display(self):
        """Run all update_display methods."""
        self.update_main_display()
        self.update_weather_display()
        self.update_flood_display()
        self.update_earthquake_display()

    def update_main_display(self):
        """Update the disasterApp display."""
        if self.selected_location:
            location_info = self.locations[self.selected_location]

            self.current_location_label.config(
                text=f"Current Location:\n{location_info['location']}",
                wraplength=self.current_location_label.winfo_width()
            )

            self.search_radius_label.config(
                text=f"Radius: {location_info['radius']}km"
            )
        else:
            self.current_location_label.config(
                text="Current Location: Not Selected" 
            )

            self.search_radius_label.config(
                text=f"Radius: Not Selected"
            )
    
    def get_alert_message(self, type, level, subtype="GENERAL"):
        """Get the relevant alert message from MESSAGE constants."""
        return self.alert_messages[type][subtype][level]

    def convert_timestamp_message(self, time):
        if not time:
            return time
        
        time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        time_string = time.strftime("%I:%M %p")
        now = datetime.now()

        if time.day != now.day:
            time_string = time_string + " tomorrow"
        else:
            time_string = time_string + " today"
        return time_string

    def weather_alert(self, upcoming_weather_data):
        """Get the weather alert based on upcoming weather data."""
        if not upcoming_weather_data:
            return {
                "level": "INACTIVE",
                "category": "GENERAL",
                "worst_timestamp": None
            }

        worst_timestamp = None
        worst_data = None
        highest_score = -1
        
        # Find worst weather conditions in upcoming data.
        for timestamp, hour in upcoming_weather_data:
            score = max(
                hour["wind_gusts_10m"],
                hour["rain"]
            )
            if score > highest_score:
                highest_score = score
                worst_timestamp = timestamp
                worst_data = hour
        
        wind = worst_data["wind_gusts_10m"]
        rain = worst_data["rain"]

        # Determine alert type based off severity of weather conditions.
        if rain >= 5 and wind >= 40:
            category = "STORM"
        elif rain >= 5:
            category = "RAIN"
        elif wind >= 40:
            category = "WIND"
        else:
            category = "GENERAL"

        # Determine weather alert severity
        if wind >= 60 or rain >= 10:
            level = "SEVERE_WARNING"
        elif wind >= 40 or rain >= 5:
            level = "WARNING"
        else:
            level = "NORMAL"

        return {
            "level": level,
            "category": category,
            "worst_timestamp": worst_timestamp
        }

    def get_wind_direction(self, degrees):
        """Get relative wind direction based of compass degrees.
        
        :param degrees: a float point value from 0 to 360 degrees
        """
        directions = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW"
        ]

        index = round(degrees / 22.5) % 16
        return directions[index]

    def round_weather_data(self, hour_data):
        """Round all of the weather api data."""
        for key, value in hour_data.items():
            if isinstance(value, (float, int)):
                hour_data[key] = round(value)
        return hour_data
        
    def update_weather_display(self):
        """Updates the weather specific display.

        Format weather data based off currently selected location 
        ready for gui display to be updated accordingly.

        (No selected location displays placeholder data).
        """
        if self.selected_location:
            location_key = self.locations[
                f"{self.selected_location}"]["location"]
            
            timestamps = list(
                self.weather_data["hourly"][location_key].keys()
            )
            hour_data = list(
                self.weather_data["hourly"][location_key].values()
            )
            
            upcoming_weather_data = list(zip(
                timestamps[:self.data_forecast], 
                hour_data[:self.data_forecast]
            ))

            hour_data = hour_data[0]

            degrees = hour_data["wind_direction_10m"]
            wind_direction = self.get_wind_direction(degrees)

            hour_data = self.round_weather_data(hour_data)

            daily_data = self.weather_data[
                "daily"][location_key]
        else:
            hour_data = {key: "--" for key in WEATHER_FIELDS}
            wind_direction = ""
            daily_data = {
                "sunrise": "--",
                "sunset": "--"
            }
            upcoming_weather_data = {}
        
        # Get weather alert from formatted upcoming weather data.
        alert_result = self.weather_alert(upcoming_weather_data)
        level = alert_result["level"]
        category = alert_result["category"]
        time = self.convert_timestamp_message(
            alert_result["worst_timestamp"]
        )

        message = self.get_alert_message("weather", level, category)
        message["description"] = \
            message["description"].format(time=time)

        # Update all Weather Widgets.
        self.all_status_w_indicator.setColour(level)
        self.weather_status_indicator.setColour(level)

        self.all_status_w_label.config(
            text=f"Weather: {message['title']}"
        )

        self.weather_status_description.config(
            text=f"{message['description']}"
        )

        self.weather_sunrise_label.config(
            text=f"Sunrise: {daily_data['sunrise']}"
        )
        self.weather_sunset_label.config(
            text=f"Sunset: {daily_data['sunset']}"
        )

        self.weather_temp_label.config(
            text="Current Temperature: " + 
            f"{hour_data['temperature_2m']}℃\n\n" + 
            f"feels like: {hour_data['apparent_temperature']}℃"
        )
        self.weather_rain_chance_label.config(
            text="Chance of Rain: \n" + 
            f"{hour_data['precipitation_probability']}%"
        )
        self.weather_cloud_cover_label.config(
            text=f"{hour_data['cloud_cover']}% Cloud cover"
        )

        self.weather_wind_speeds_label.config(
            text="Wind Speeds:\n" +
            f"{hour_data['wind_speed_10m']}km/h {wind_direction}"
        )
        self.weather_wind_gusts_label.config(
            text="Wind Gusts:\n" +
            f"{hour_data['wind_gusts_10m']}km/h"
        )

        self.weather_humidity_label.config(
            text="Humidity:\n" + 
            f"{hour_data['relative_humidity_2m']}%"
        )
        self.weather_surface_pressure_label.config(
            text="Surface Pressure:\n" + 
            f"{hour_data['surface_pressure']}hPa"
        )

    def build_flood_context(self, worst_data, worst_time):
        """Create worst Flood Data context.
        
        Format a dict containing the contextual flood data needed for
        a flood alert.
        """
        return {
            "time": worst_time,
            "rain_1h": worst_data["rain_1h"],
            "rain_24h": worst_data["rain_24h"],
            "saturation": worst_data["soil_saturation"]
        }
    
    def get_saturation_average(self, hour_data):
        """Return a weighted average of the soil_moisture readings."""
        saturation = (
            hour_data["soil_moisture_0_to_1cm"] * 0.5 +
            hour_data["soil_moisture_1_to_3cm"] * 0.3 + 
            hour_data["soil_moisture_3_to_9cm"] * 0.2
        )
        return saturation
    
    def get_saturation_string(self, hour_data):
        """Format soil saturation level into keyword ranges.
        
        Converts the soil saturation value into a keyword depicting the 
        relative range from Low to Very High saturation.
        """
        saturation = hour_data["soil_saturation"]
        saturation_level = [
            "Low",
            "Normal",
            "High",
            "Very High"
        ]
        index = round(saturation * 4) - 1

        return saturation_level[index]
    
    def prepare_flood_data(self, hour_data, display_data):
        """Convert hour_data into displayable data for the gui.
        
        Get hour data from API and calculate required values for 
        alert system and gui.
        """
        for i in range(self.data_forecast):
            display_data[i]["soil_saturation"] = \
                self.get_saturation_average(hour_data[i])

            display_data[i]["rain_1h"] = hour_data[i]["rain"]

            rain_6h = sum(hour["rain"] for hour in hour_data[i:(i+6)])
            display_data[i]["rain_6h"] = rain_6h

            rain_24h = sum(hour["rain"] for hour in hour_data[i:(i+24)])
            display_data[i]["rain_24h"] = rain_24h

            display_data[i]["rain_chance"] = hour_data[i][
                "precipitation_probability"
            ]

        return display_data
    
    def calculate_flood_points(self, data, thresholds):
        """Calculate flood score against flood ruling.
        
        Compare flood data to threshold ruling for alert severity
        calculations.
        """
        total_score = 0
        for key, rules in thresholds:
            value = data[key]
            for threshold, points in rules:
                if value >= threshold:
                    total_score += points
                    break
        return total_score

    def flood_alert(self, upcoming_flood_data):
        """Get the flood alert based off the upcoming flood data"""
        if not upcoming_flood_data:
            return {
                "level": "INACTIVE",
                "category": "GENERAL",
                "worst_timestamp": None
            }
        
        worst_timestamp = None
        worst_data = None
        highest_score = -1

        # Find worst flood conditions in upcoming data.
        for timestamp, hour in upcoming_flood_data.items():
            score = self.calculate_flood_points(
                hour,
                FLOOD_SCORES
            )
            if score > highest_score:
                highest_score = score
                worst_timestamp = timestamp
                worst_data = hour

        ground = worst_data["soil_saturation"]
        rain = worst_data["rain_24h"]

        # Determine alert type based off severity of flood conditions.
        if ground >= 0.8 and rain >= 50:
            category = "COMBINED"
        elif ground >= 0.8:
            category = "SATURATED_GROUND"
        elif rain >= 50:
            category = "HEAVY_RAIN"
        else:
            category = "GENERAL"
        
        # Determine flood alert severity.
        if highest_score>= 9:
            level = "SEVERE_WARNING"
        elif highest_score >= 6:
            level = "WARNING"
        else:
            level = "NORMAL"

        return {
            "level": level,
            "category": category,
            "worst_timestamp": worst_timestamp
        }
            
    def update_flood_display(self):
        """Updates the flood specific display.
        
        Format flood data based off currently selected location ready 
        for gui display to be updated accordingly.

        (No selected location displays placeholder data).
        """
        data_template = {score[0]: "--" for score in FLOOD_SCORES}
        display_data = []
        if self.selected_location:
            location_key = self.locations[
                f"{self.selected_location}"]["location"]
            
            timestamps = list(
                self.flood_data[location_key].keys()
            )
            
            hour_data = list(
                self.flood_data[location_key].values()
            )

            for _ in range(len(hour_data)):
                display_data.append(data_template)
            
            display_data = self.prepare_flood_data(
                hour_data, 
                display_data
            )

            upcoming_flood_data = dict(zip(
                timestamps[:self.data_forecast],
                display_data[:self.data_forecast]
            ))

            display_data = display_data[0]

            saturation_string = self.get_saturation_string(display_data)
            display_data = self.round_weather_data(display_data)
        else:
            display_data = data_template
            upcoming_flood_data = {}
            saturation_string = "--"
        
        # Get flood alert from formatted upcoming flood data.
        alert_result = self.flood_alert(upcoming_flood_data)
        level = alert_result["level"]
        category = alert_result["category"]
        time = self.convert_timestamp_message(
            alert_result["worst_timestamp"]
        )

        message = self.get_alert_message("flood", level, category)
        message["description"] = \
            message["description"].format(time=time)

        # Update all flood widgets.
        self.all_status_f_indicator.setColour(level)
        self.flood_status_indicator.setColour(level)

        self.all_status_f_label.config(
            text=f"Flood: {message['title']}"
        )
        self.flood_status_message.config(
            text=f"Flood Status: {message['title']}"
        )
        self.flood_status_description.config(
            text=f"{message['description']}"
        )

        self.flood_ground_sat_label.config(
            text=f"Ground Saturation\t{saturation_string}"
        )

        self.flood_rain_1hr_label.config(
            text=f"Current Rainfall\t{display_data['rain_1h']}mm/h"
        )

        self.flood_rain_6hr_label.config(
            text=f"6-hour Forecast\t{display_data['rain_6h']}mm"
        )

        self.flood_rain_24hr_label.config(
            text=f"24-Hour Rainfall\t{display_data['rain_24h']}mm"
        )

        self.flood_rain_prob_label.config(
            text=f"Rain Probability\t{display_data['rain_chance']}"
        )

    def calculate_earthqauke_points(self, data, thresholds):
        """Calculate earthquake score against earthquake ruling.
        
        Compare the earthquake data to threshold ruling for alert 
        severity calculations.
        """
        total_score = 0
        for key, rules in thresholds:
            value = data[key]
            for threshold, points in rules:
                if value >= threshold:
                    total_score += points
                    break
        return total_score

    def earthquake_alert(self, recent_earthquake_data, alert_active):
        """Get the earthquake alert based off the upcoming earthquake \
            data
        """
        if not recent_earthquake_data and alert_active:
            return {
                "level": "NORMAL",
                "category": "GENERAL",
                "largest_magnitude": None
            }
        elif not (recent_earthquake_data and alert_active):
            return {
                "level": "INACTIVE",
                "category": "GENERAL",
                "largest_magnitude": None
            }

        # Get earthquake score for each event to find most severe case.
        earthquake_ranking = {}
        score_keys = []
        for rule in EARTHQUAKE_SCORES:
            score_keys.append(rule[0])
        
        time_format = "%Y-%m-%d %I:%M %p"

        for earthquake in recent_earthquake_data:
            magnitude = earthquake["magnitude"]
            depth = earthquake["depth"]
            time = datetime.strptime(earthquake["time"], time_format)
            recency = datetime.now() - time
            values = [magnitude, depth, recency]
            score = self.calculate_earthqauke_points(
                dict(zip(score_keys, values)),
                EARTHQUAKE_SCORES
            )
            earthquake_ranking[score] = earthquake["magnitude"]
        
        all_scores = list(earthquake_ranking.keys())

        peak_score = max(all_scores)
        total_score = sum(all_scores)
        largest_magnitude = earthquake_ranking[peak_score]

        # Determine earthquake alert severity to adjust alert status.
        if peak_score >= 10 or total_score >= 18:
            level = "SEVERE_WARNING"
        elif peak_score >= 6 or total_score >= 10:
            level = "WARNING"
        else:
            level = "NORMAL"

        # Determine alert type based off severity of earthquake
        # properties.
        if largest_magnitude >= 6.0:
            category = "MAJOR_EVENT"
        elif largest_magnitude >= 5.0:
            category = "MODERATE_EVENT"
        elif largest_magnitude >= 4.0:
            category = "SMALL_EVENT"
        else:
            category = "GENERAL"
        
        return {
            "level": level,
            "category": category,
            "largest_magnitude": largest_magnitude
        }

    def update_earthquake_display(self):
        """Updates the earthquake specific display.
        
        Format earthquake data based off currently selected location
        ready for gui display to be updated accordingly.

        (No selected location displays placeholder data).
        """
        alert_active = False
        if self.selected_location:
            alert_active = True
            location_key = self.locations[
                f"{self.selected_location}"]["location"]
            
            earthquake_data = self.earthquake_data[location_key]

            offset = datetime.now(timezone.utc) - timedelta(days=3)
            offset = offset.strptime(
                datetime.strftime(offset, "%Y-%m-%d %I:%M %p"),
                "%Y-%m-%d %I:%M %p"
            )

            recent_earthquake_data = [
                earthquake
                for earthquake in earthquake_data
                if datetime.strptime(
                    earthquake["time"], 
                    "%Y-%m-%d %I:%M %p"
                ) >= (offset)
            ]
        else:
            recent_earthquake_data = None
            self.earthquake_seismic_activity.heading(
                "time", text="Date & Time"
            )
            self.earthquake_seismic_activity.insert(
                "",
                "end",
                values=("", "No recent earthquakes", "", "")
            )

        alert_result = self.earthquake_alert(
            recent_earthquake_data,
            alert_active
        )
        level = alert_result["level"]
        category = alert_result["category"]
        magnitude = alert_result["largest_magnitude"]

        message = self.get_alert_message("earthquake", level, category)
        message["description"] = \
            message["description"].format(mag=magnitude)
        
        self.all_status_q_indicator.setColour(level)
        self.earthquake_status_indicator.setColour(level)
        self.all_status_q_label.config(
            text=f"Earthquake: {message['title']}"
        )
        self.earthquake_status_description.config(
            text=f"{message['description']}"
        )

        events = self.earthquake_seismic_activity.get_children()
        if events:
            self.earthquake_seismic_activity.delete(*events)
        
        if recent_earthquake_data:
            location_tz = recent_earthquake_data[0]["timezone"]
            self.earthquake_seismic_activity.heading(
                "time", text=f"Date & Time ({location_tz})"
            )
            for n in range(len(recent_earthquake_data)):
                self.earthquake_seismic_activity.insert(
                    '',
                    index=n,
                    values=(
                        recent_earthquake_data[n]["time"],
                        recent_earthquake_data[n]["place"],
                        recent_earthquake_data[n]["depth"],
                        recent_earthquake_data[n]["magnitude"]
                    )
                )


    def update_local_storage(self):
        """Rewrites local storage with stored data from disasterApp."""
        with open(LOCATIONS_FILE, 'w', encoding='utf-8') as locf:
            locf = json.dump(self.locations, locf, indent=4)

    def refresh_all_data(self):
        """Calls all api fetches to update current data.
        
        This function builds a collated package of all available 
        locations and sends it to each api method to refresh current
        stored data.
        """
        api_package = {
            "location": [],
            "radius": [],
            "lat": [],
            "lon": [],
            "timezone": []
        }
        if not self.locations:
            messagebox.showinfo(
                "Sync Information",
                "Create a new location to refresh information shown"
            )
            return
        
        # Populate api_package with location info ready for api calling.
        for location in self.locations.values():
            api_package["location"].append(location["location"])
            api_package["radius"].append(location["radius"])
            api_package["lat"].append(location["coords"][0])
            api_package["lon"].append(location["coords"][1])
            api_package["timezone"].append(location["timezone"])

        weather_api = self.refresh_weather_api(api_package)
        earthquake_api = self.refresh_earthquake_api(api_package)
        
        # Bypass updating latest refresh if a failed api call occurred.
        if not (weather_api and earthquake_api):
            return
        
        self.last_all_refresh = datetime.now().strftime(
            "%Y-%m-%d %I:%M %p"
        )
        self.last_refresh_label.config(
            text=f"Last refreshed at: {self.last_all_refresh}"
        )

    def refresh_weather_api(self, package):
        """Pull information from the WeatherAPI"""
        raw_data = WeatherAPI.get_weather_data(
            self.weather_session,
            package, 
            WEATHER_API_PARAMETERS
        )

        if not raw_data:
            messagebox.showerror(
                "API Error",
                "Unable to retrieve weather information " + 
                "at this time. Please try again later."
            )
            return False

        if isinstance(raw_data, dict):
            if "error" in raw_data:
                messagebox.showerror(
                    "API Error", 
                    raw_data["reason"]
                )
                return False
        
        raw_hourly_data = raw_data[0]
        daily_data = raw_data[1]
        
        self.weather_data["daily"] = daily_data
        self.weather_data["hourly"] = {}

        for location, output in raw_hourly_data.items():
            self.weather_data["hourly"][location] = {}
            self.flood_data[location] = {}
            for timestamp, data in output.items():
                self.weather_data["hourly"][location][timestamp] = {}
                self.flood_data[location][timestamp] = {}
                for key, value in data.items():
                    if key in WEATHER_FIELDS:
                        self.weather_data["hourly"]\
                            [location][timestamp][key] = value
                    if key in FLOOD_FIELDS:
                        self.flood_data\
                            [location][timestamp][key] = value
        
        self.update_weather_display()
        self.update_flood_display()
        return True
    
    def refresh_earthquake_api(self, package):
        earthquake_data = EarthquakeAPI.get_earthquake_data(
            self.earthquake_session,
            package
        )

        if not earthquake_data:
            messagebox.showerror(
                "API Error",
                "Unable to retrieve earthquake information " + 
                "at this time. Please try again later."
            )
            return False

        if isinstance(earthquake_data, dict):
            if "error" in earthquake_data:
                messagebox.showerror(
                    "API Error", 
                    earthquake_data["error"]["message"]
                )
                return False
        
        self.earthquake_data = earthquake_data
        self.update_earthquake_display()
        return True

root = tk.Tk()
app = disasterApp(
    root, 
    location_data=location_data
)
root.mainloop()