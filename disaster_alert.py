import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import json
import os

from api_files import WeatherAPI
from api_files import EarthquakeAPI


CITIES_FILE = "cities.json"
LOCATIONS_FILE = "stored_locations.json"
SYSTEM_FILE = "menu_history.json"
TF = TimezoneFinder()

if not os.path.exists(LOCATIONS_FILE):
    with open(LOCATIONS_FILE, 'w', encoding='utf-8') as locf:
        json.dump({}, locf, indent=4)
else:
    try:
        with open(LOCATIONS_FILE, 'r', encoding='utf-8') as locf:
            location_data = json.load(locf)
    except (json.JSONDecodeError, OSError):
        location_data = {}

if not os.path.exists(SYSTEM_FILE):
    with open(SYSTEM_FILE, 'w', encoding='utf-8') as sysf:
        json.dump({}, sysf, indent=4)
else:
    try:
        with open(SYSTEM_FILE, 'r', encoding='utf-8') as sysf:
            system_data = json.load(sysf)
    except (json.JSONDecodeError, OSError):
        system_data = {}

def load_cities():
    with open(CITIES_FILE, "r", encoding='utf-8') as ctyf:
        return json.load(ctyf)
    
CITIES = load_cities()

GEOLOCATOR = Nominatim(user_agent="my_geo_app")

class statusIndicator(tk.Canvas):
    """Creates an indicator widget

    This class creates and contains the functionality of the indicator
    lights of the app
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

        self.light = self.create_oval(
            2, 2,
            12, 12,
            fill="#33FF00",
            outline="black"
        )

    def setColour(self, colour):
        self.itemconfig(self.light, fill=colour)
    
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

        self.create_display()
    
    def create_display(self):
        """Creates the display of a locationEditFrame"""
        self.input_frame = ttk.Frame(self, padding=10)
        self.input_frame.pack()
        self.input_frame.columnconfigure(1, weight=1)

        self.location_label = ttk.Label(
            self.input_frame, 
            text="Location: ", 
            padding=10
        )
        self.location_label.grid(row=0, column=0, sticky="e")

        self.location_entry = ttk.Entry(self.input_frame, width=30)
        self.location_entry.insert(0, self.info["location"])
        self.location_entry.grid(row=0, column=1)

        self.radius_label = ttk.Label(
            self.input_frame, 
            text="Radius(km): ",
            padding=10
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

        self.actions_frame = ttk.Frame(self)
        self.actions_frame.pack()

        if self.location_exists:
            self.remove_button = ttk.Button(
                self.actions_frame, 
                text="Remove",
                width=8,
                command=self.remove_location
            )
            self.remove_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(
            self.actions_frame,
            text="Save",
            width=8,
            command=self.save_changes
        )
        self.save_button.grid(row=0, column=1, padx=5)
        self.cancel_button = ttk.Button(
            self.actions_frame,
            text="Cancel",
            width=8,
            command=self.cancel_changes
        )
        self.cancel_button.grid(row=0, column=2, padx=5)

    def validate_city(self, value):
        """Validates a city input against CITIES stored data"""
        valid_list = []
        for city in self.options:
            full_name = f"{city['city']}, {city['country']}"
            if value.lower() in full_name.lower():
                valid_list.append(full_name)
        return valid_list

    def update_suggestions(self, event):
        """Updates location suggestions in locationEditItem's listbox"""
        typed = self.location_entry.get().lower()

        self.listbox.delete(0, tk.END)

        if not typed:
            return
        
        matches = self.validate_city(typed)
        
        if matches:
            for match in matches:
                self.listbox.insert(tk.END, match)
        else:
            self.listbox.insert(tk.END, "No city found")

    def select_item(self, event):
        """Gets value of selected locationEditItem listbox"""
        selection = self.listbox.curselection()

        if not selection:
            return

        value = self.listbox.get(selection[0])

        if value == "No city found":
            return
        
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, value)

        self.listbox.delete(0, tk.END)
    
    def validate_radius(self):
        """Checks if radius input value is a positive integer"""
        try:
            radius = int(self.info["radius"])
            if radius > 0:
                self.info["radius"] = radius
                return True
        except:
            messagebox.showerror(
                "Input Error", 
                ("Radius Input Must be a " +
                "Positive Integer Value to continue")
            )
            return False
    
    def remove_location(self):
        """Removes the locationItem's location"""
        l = self.parent.locations[self.id]["location"]
        ask_to_delete = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you would like to remove location: {l}"
        )

        if not ask_to_delete:
            return
        
        if self.parent.selected_location == self.locationItem.id:
            self.parent.update_main_display(False)

        self.parent.locations.pop(self.locationItem.id, None)
        self.parent.update_local_storage()
        self.parent.location_items.pop(self.locationItem.id, None)
        self.locationItem.destroy()
        messagebox.showinfo(
            "Successfully Removed", 
            f"Location: {l} removed successfully."
        )
        self.destroy()
    
    def save_changes(self):
        """Saves changes for locationItem's location
        
        Only updates location if the input values are all valid.
        Error shown if unsuccessfully validated
        """
        self.info["location"] = self.location_entry.get().strip()
        self.info["radius"] = self.radius_entry.get().strip()

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
        validated_location = self.get_coordinates()
        validated_radius = self.validate_radius()

        if not validated_radius or not validated_location:
            return
        self.info["timezone"] = TF.timezone_at(
            lng=self.info["coords"][1], 
            lat=self.info["coords"][0]
        )
        self.parent.locations[self.id]["location"] = self.info[
            "location"]
        self.parent.locations[self.id]["radius"] = self.info["radius"]
        self.parent.locations[self.id]["coords"] = self.info["coords"]
        self.parent.locations[self.id]["timezone"] = self.info[
            "timezone"]
        self.locationItem.location_label.config(
            text=self.info["location"]
        )
        self.locationItem.radius_label.config(
            text=f"Radius: {self.info["radius"]}km"
        )
        self.parent.update_local_storage()
        self.destroy()
    
    def cancel_changes(self):
        """Cancel any changes made to locationItem's location
        
        Removes the locationItem and its value if a new location was
        created without any values
        """
        if self.location_exists:
            self.destroy()
        else:
            self.parent.locations.pop(
                self.locationItem.id, None
            )
            self.locationItem.destroy()
            self.destroy()
    
    def get_coordinates(self):
        """Gets lat lon coordinates from a 'City, Country' address"""
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
        
        try:
            location = GEOLOCATOR.geocode(address)

            if location:
                self.info["coords"] = (
                    location.latitude, 
                    location.longitude
                )
                return True
            else:
                messagebox.showerror("Error", "Location Not Found")
                return False
        except:
            messagebox.showerror(
                "Error", 
                "An error occured while trying to get location info"
            )
            return False


class locationItem(ttk.Frame):
    """Creates a location item

    :param frame: The Parent container of the locationItem
    :param parent: The disasterApp that contains the location dict
    :param id: The location id assigned to the locationItem

    This class is responsible for housing a saved location within the
    program, serving as a modular element that can be cloned and 
    removed, retaining its own information for API access and window 
    configuration.
    """
    def __init__(self, frame, parent, id):
        super().__init__(frame)
        self.parent = parent
        self.id = id

        self.pack(fill="x", expand=False)
        self.columnconfigure(0, weight=1)

        self.info_frame = ttk.Frame(self, padding=10)
        self.info_frame.grid(row=0, column=0, sticky="w")

        # Reinstate previous save data if created from existing 
        # location stored in local storage
        previous_info = parent.locations[id]

        self.location_label = ttk.Label(
            self.info_frame,
            text=previous_info["location"]
        )
        self.location_label.grid(row=0, column=0, sticky="w")

        self.radius_label = ttk.Label(
            self.info_frame,
            text=f"Radius: {previous_info["radius"]}km"
        )
        self.radius_label.grid(row=1, column=0, sticky="w")
    
        self.edit_button = ttk.Button(
            self,
            text="Edit",
            width=4,
            command=lambda: self.edit_location(True)
        )
        self.edit_button.grid(row=0, column=1, sticky="e")

        self.select_button = ttk.Button(
            self,
            text="Select",
            width=6,
            command=self.select_location
        )
        self.select_button.grid(row=0, column=2, sticky="e", padx=5)

        if not (self.parent.locations[id]["location"] or 
                self.parent.locations[id]["radius"] or 
                self.parent.locations[id]["coords"]):
            self.edit_location(False)

    def edit_location(self, locationExists):
        """Open a locationEditFrame to edit / remove the location
        
        Allows the user to edit the locationItem by opening a 
        locationEditFrame class that can edit or remove this items 
        location data from temporary and local storage 
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
    
    def select_location(self):
        """Sets this locationItem's location as the active location
        
        Updates the selected location for the menu to the corresponding
        locationItem's assigned location, automatically deselecting all
        other locations when doing so
        """
        self.select_button.config(text="(Active)")
        self.select_button.state(["disabled"])
        self.parent.selected_location = self.id
        self.parent.update_main_display()

        for location in self.parent.location_items.values():
            if not location == self:
                location.deselect_location()
  
    def deselect_location(self):
        self.select_button.config(text="Select")
        self.select_button.state(["!disabled"])
    
    def refresh_location(self):
        data = self.parent.locations[self.id]
        self.location_label.config(
            text=data["location"]
        )
        self.radius_label.config(
            text=f"Radius: {data["location"]}km"
        )

class AppCache:
    def __init__(self):
        self.live_data = None
        self.history = []
        self.last_live_update = None
        self.last_history_update = None

class disasterApp:
    """Creates an instance of the disasterApp
    
    :param root: The root window for the app
    :param location_data: The locally stored location data
    :param system_data: The locally stored system data

    This class is responsible for initiating and operating the disaster
    app
    """
    def __init__(self, root, location_data, system_data):
        self.root = root
        self.root.title("Local Disaster Alert System")
        self.root.minsize(496, 496)
        self.root.geometry("600x500+500+0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.root.configure(bg="#F0F0F0")
        
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        self.next_refresh = None

        self.refresh_minute = 5
        
        self.locations = {}
        self.location_items = {}
        self.selected_location = 0

        if location_data:
            self.locations = location_data
            self.nextid = int(list(location_data)[-1]) + 1
        else:
            self.nextid = 0
        
        self.cache = AppCache()

        self.weather_session = WeatherAPI.initialize_cache()
        # self.earthquake_log = EarthquakeAPI.initialize_log()

        self.weather_data = {}

        
        self.create_styles()
        self.create_frames()
        self.create_widgets_all()
        self.create_location_menu()

        self.refresh_all_data()

    def create_styles(self):
        """Creates the ttk styles for the disasterApp"""
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
            "Location.TLabel",
            font=("TkDefaultFont", 18),
            background="#F0F0F0"
        )
        self.style.configure(
            "Radius.TLabel",
            font=("TkDefaultFont", 10),
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
            font=("TkDefaultFont", 28)
        )
        self.style.configure(
            "AllStatusBG.TFrame",
            background="#FFFFFF"
        )
        self.style.configure(
            "AllStatusText.TLabel",
            font=("TkDefaultFont", 20),
            background="#FFFFFF"
        )

    
    def create_frames(self):
        """Creates the layout structure of the GUI
        
        The usage of create_frames when creating frames used to control 
        the positioning and layout of items on screen keeps code
        consisten and separate from the widgets (elements) of the GUI
        """
        
        self.main_frame = ttk.Frame(self.root, style="MainBG.TFrame")

        self.refresh_frame = ttk.Frame(
            self.main_frame, 
            style="MainBG.TFrame"
        )
        self.location_frame = ttk.Frame(
            self.main_frame, 
            padding=10,
            style="MainBG.TFrame"
        )

        self.all_status_frame = ttk.Frame(
            self.main_frame, 
            padding=10,
            style="InfoBG.TFrame"
        )
        self.footer_frame = ttk.Frame(
            self.main_frame, 
            style="MainBG.TFrame"
        )

        # All frames for Weather-specific window
        self.weather_frame = ttk.Frame(self.main_frame)

        self.w_status_frame =ttk.Frame(
            self.weather_frame, padding=10
        )
        self.w_status_frame.pack()

        self.w_info_container = ttk.Frame(
            self.weather_frame, padding=10
        )
        self.w_info_container.pack()

        self.w_info_row1 = ttk.Frame(
            self.w_info_container, padding=10
        )
        self.w_info_row1.pack()

        self.w_info_row2 = ttk.Frame(
            self.w_info_container, padding=10
        )
        self.w_info_row2.pack()

        self.w_info_sunCol = ttk.Frame(
            self.w_info_row1, padding=10
        )
        self.w_info_sunCol.grid(row=0, column=0)

        self.w_info_rainCol = ttk.Frame(
            self.w_info_row1, padding=10
        )
        self.w_info_rainCol.grid(row=0, column=2)
        
        # All frames for flood-specific window
        self.flood_frame = ttk.Frame(self.main_frame)

        self.f_title_frame = ttk.Frame(
            self.flood_frame, padding=10
        )
        self.f_title_frame.pack()

        self.f_info_container = ttk.Frame(
            self.flood_frame, padding=10
        )
        self.f_info_container.rowconfigure(1, weight=1)
        self.f_info_container.pack()

        self.f_status_container = ttk.Frame(
            self.f_info_container, padding=10
        )
        self.f_status_container.columnconfigure(1, weight=1)
        self.f_status_container.grid(row=0, column=0, sticky="nw")
        
        # All frames for earthquake-specific window
        self.earthquake_frame = ttk.Frame(self.main_frame)

        self.q_title_frame = ttk.Frame(
            self.earthquake_frame, padding=10
        )
        self.q_title_frame.pack()

        self.q_info_container = ttk.Frame(
            self.earthquake_frame, padding=10
        )
        self.q_info_container.rowconfigure(1, weight=1)
        self.q_info_container.pack()
        
        self.q_status_container = ttk.Frame(
            self.q_info_container, padding=10
        )
        self.q_status_container.columnconfigure(1, weight=1)
        self.q_status_container.grid(row=0, column=0, sticky="nw")
        
        self.main_frame.pack(fill="both", expand=True)
        self.refresh_frame.pack(fill="x")
        self.location_frame.pack(fill="x", expand=False)
        self.location_frame.grid_columnconfigure(1, weight=1)
        self.all_status_frame.pack(fill="x", expand=True)
        self.footer_frame.pack(
            side=tk.BOTTOM, 
            fill="both", 
            expand=True,
        )

    def create_widgets_all(self):
        self.create_widgets_main()
        self.create_widgets_weather()
        self.create_widgets_flood()
        self.create_widgets_earthquake()
    
    def create_widgets_main(self):
        """Creates the widgets for the Main GUI

        this method is used when creating all of the elements seen 
        on the home screen by users and is responsible for populating 
        the main gui frame
        """
        # Refresh tag at top of GUI
        self.last_refresh_label = ttk.Label(
            self.refresh_frame, 
            text=f"Last refreshed at: {self.last_refresh}",
            style="LastRefresh.TLabel"
            )
        self.last_refresh_label.pack(side="top")

        # Current Location Display
        self.current_location_label = ttk.Label(
            self.location_frame,
            text=f"Current Location: Not Selected",
            padding=(10, 0),
            style="Location.TLabel"
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
            text=f"Radius: Not Selected",
            padding=(10, 0),
            style="Radius.TLabel"
        )
        self.search_radius_label.grid(row=1, column=0, sticky="w")

        # Main Status Display (home screen)
        self.all_status_title = ttk.Label(
            self.all_status_frame,
            text="Status Monitoring",
            padding=5,
            style="MainStatus.TLabel"
        )
        self.all_status_title.pack()

        # Row 1: Weather Status
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
            text="Weather: Normal",
            padding=10,
            style="AllStatusText.TLabel"
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

        # Row 2: Flood Status
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
            text="Flood Risk: Low",
            padding=10,
            style="AllStatusText.TLabel"
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

        # Row 3: Earthquake Status
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
            text="Earthquake Alert: Low",
            padding=10,
            style="AllStatusText.TLabel"
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

        # Footer Buttons
        self.back_home_button = ttk.Button(
            self.footer_frame,
            text="Back home",
            padding=5,
            command=self.show_home_display
        )

        self.all_sync_button = ttk.Button(
            self.footer_frame, 
            text="Sync from Servers", 
            padding=5,
            style="MainBG.TButton",
            command=self.refresh_all_data
        )
        self.all_sync_button.place(relx=0.5, rely=0.5, anchor="center")

    def create_widgets_weather(self):
        """Creates the widgets for the Weather GUI

        this method is used when creating all of the elements seen 
        on the weather screen by users and is responsible for populating 
        the weather gui frame
        """
        # Weather Main Status
        self.weather_status_indicator = statusIndicator(
            self.w_status_frame,
            "#F0F0F0"
        )
        self.weather_status_indicator.grid(
            row=0,
            column=0, 
            padx=10, 
            pady=10
        )
        
        self.weather_status_message = ttk.Label(
            self.w_status_frame,
            text="Weather Status: Normal",
            padding=10
        )
        self.weather_status_message.grid(
            row=0, 
            column=1, 
            padx=10, 
            pady=10
        )

        # Weather Information (From API)
        self.weather_sunrise_label = ttk.Label(
            self.w_info_sunCol,
            text="Sunrise: 7:15am",
            padding=[0, 10]
        )
        self.weather_sunrise_label.grid(row=0, column=0)

        self.weather_sunset_label = ttk.Label(
            self.w_info_sunCol,
            text="Sunset: 6:50pm",
            padding=[0, 10]
        )
        self.weather_sunset_label.grid(row=1, column=0)

        self.weather_temp_label = ttk.Label(
            self.w_info_row1,
            text="Current Temperature: 18℃\n\n(feels like: 14℃)",
            padding=10
        )
        self.weather_temp_label.grid(row=0, column=1)

        self.weather_rain_chance_label = ttk.Label(
            self.w_info_rainCol,
            text="Chance of Rain:\n20%",
            padding=10
        )
        self.weather_rain_chance_label.grid(row=0, column=0)

        self.weather_cloud_cover_label = ttk.Label(
            self.w_info_rainCol,
            text="40% Cloud Cover",
            padding=[0, 10]
        )
        self.weather_cloud_cover_label.grid(row=1, column=0)

        self.weather_wind_speed_label = ttk.Label(
            self.w_info_row2,
            text="Wind Speeds: \n10km/h",
            padding=10
        )
        self.weather_wind_speed_label.grid(row=0, column=0)
        
        self.weather_wind_gusts_label = ttk.Label(
            self.w_info_row2,
            text="Wind Gusts: \n10km/h",
            padding=10
        )
        self.weather_wind_gusts_label.grid(row=0, column=1)

        self.weather_humidity_label = ttk.Label(
            self.w_info_row2,
            text="Humidity: \n85%",
            padding=10
        )
        self.weather_humidity_label.grid(row=0, column=2)
        
        self.weather_surface_pressure_label = ttk.Label(
            self.w_info_row2,
            text="Surface Pressure: \n1013hPa",
            padding=10
        )
        self.weather_surface_pressure_label.grid(row=0, column=3)

    def create_widgets_flood(self):
        """Creates the widgets for the Flood GUI

        This method is used when creating all of the elements seen 
        on the flood screen by users and is responsible for populating 
        the flood gui frame
        """
        # Flood Screen Title
        self.flood_screen_title = ttk.Label(
            self.f_title_frame,
            text="Flood Alerts: ",
            padding=10
        )
        self.flood_screen_title.pack()

        # Flood Information (From API)
        self.flood_status_indicator = statusIndicator(
            self.f_status_container,
            "#D9D9D9"
        )
        self.flood_status_indicator.grid(row=0, column=0)

        self.flood_status_message = ttk.Label(
            self.f_status_container,
            text="Flood Risk: Low"
        )
        self.flood_status_message.grid(row=0, column=1, padx=10)

        self.flood_status_description = ttk.Label(
            self.f_info_container,
            text="",
            padding=10
        )
        self.flood_status_description.grid(row=1, column=0)

        self.flood_rainfall_activity = ttk.Treeview(
            self.f_info_container,
            columns=("Datetime", "Rainfall", "Change")
        )
        self.flood_rainfall_activity.column(
            "#0", width=0, stretch=tk.NO
        )
        self.flood_rainfall_activity.column(
            "Datetime", width=130, anchor=tk.E
        )
        self.flood_rainfall_activity.column(
            "Rainfall", width=100, anchor=tk.CENTER
        )
        self.flood_rainfall_activity.column(
            "Change", width=100, anchor=tk.W
        )
        self.flood_rainfall_activity.heading(
            "Datetime", text="Date & Time"
        )
        self.flood_rainfall_activity.heading(
            "Rainfall", text="Rainfall"
        )
        self.flood_rainfall_activity.heading(
            "Change", text="Change"
        )
        self.flood_rainfall_activity.grid(
            row=0, 
            column=1, 
            rowspan=1,
            sticky="e"
        )

    def create_widgets_earthquake(self):
        """Creates the widgets for the Earthquake GUI

        This method is used when creating all of the elements seen 
        on the earthquake screen by users and is responsible for 
        populating the earthquake gui frame
        """
        # Earthquake Screen Title
        self.earthquake_screen_title = ttk.Label(
            self.q_title_frame,
            text="Earthquake Alerts: ",
            padding=10
        )
        self.earthquake_screen_title.pack()

        # Earthquake Information (From API)
        self.earthquake_status_indicator = statusIndicator(
            self.q_status_container,
            "#D9D9D9"
        )
        self.earthquake_status_indicator.grid(row=0, column=0)

        self.earthquake_status_message = ttk.Label(
            self.q_status_container,
            text="Earthquake Activity: \nLow"
        )
        self.earthquake_status_message.grid(row=0, column=1, padx=10)

        self.earthquake_status_description = ttk.Label(
            self.q_info_container,
            text="",
            padding=10
        )
        self.earthquake_status_description.grid(row=1, column=0)

        self.earthquake_seismic_activity = ttk.Treeview(
            self.q_info_container,
            columns=("Datetime", "Seismic")
        )
        self.earthquake_seismic_activity.column(
            "#0", width=0, stretch=tk.NO
        )
        self.earthquake_seismic_activity.column(
            "Datetime", width=130, anchor=tk.E
        )
        self.earthquake_seismic_activity.column(
            "Seismic", width=170, anchor=tk.CENTER
        )
        self.earthquake_seismic_activity.heading(
            "Datetime", text="Date & Time"
        )
        self.earthquake_seismic_activity.heading(
            "Seismic", text="Seismic Activity"
        )
        self.earthquake_seismic_activity.grid(
            row=0, 
            column=1, 
            rowspan=1,
            sticky="e"
        )
    
    def show_home_display(self):
        """Updates disasterApp view to show home info"""
        self.all_status_frame.pack(fill="x", expand=True)
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack_forget()
    
    def show_weather_display(self):
        """Updates disasterApp view to show weather info"""
        self.all_status_frame.pack_forget()
        self.weather_frame.pack(fill="x", expand=True)
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack(side="left")

    def show_flood_display(self):
        """Updates disasterApp view to show flood info"""
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack(fill="x", expand=True)
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack(side="left")
    
    def show_earthquake_display(self):
        """Updates disasterApp view to show earthquake info"""
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack(fill="x", expand=True)
        self.back_home_button.pack(side="left")
    
    def create_location_menu(self):
        """Initiates the disasterApp location menu popup"""
        self.location_popup_menu = ttk.Frame(
            self.root,
            borderwidth=3,
            relief="groove"
        )

        self.location_popup_list = ttk.Frame(
            self.location_popup_menu,
            padding=10
        )
        self.location_popup_list.pack(fill="both", expand=True)
        self.location_popup_list.propagate(False)
                
        self.close_location_menu_button = ttk.Button(
            self.location_popup_menu,
            text="Close",
            padding=(0, 10),
            command=self.location_popup_menu.place_forget
        )
        self.close_location_menu_button.pack(side="left", padx=5)
        
        self.new_location_button = ttk.Button(
            self.location_popup_menu,
            text="New Location",
            padding=10,
            command=self.create_location
        )
        self.new_location_button.place(relx=0.5, rely=1, anchor="s")
        
    def show_location_menu(self):
        """Opens the disasterApp location menu
        
        If location data exists then the menu will be populated with 
        locationItems assigned to each existing location found
        """
        if self.locations:
            if self.location_items:
                for location in self.location_items.values():
                    location.display_self()
            else:
                for id in self.locations.keys():
                    self.location_items[id] = locationItem(
                        self.location_popup_list,
                        self,
                        id
                    )
        
        self.location_popup_menu.place(
            relx=0.5, 
            rely=0.5, 
            anchor="center",
            relheight=0.9,
            relwidth=0.9
        )
    
    def create_location(self):
        """Creates a new location
        
        This method initiates a blank location item in the disasterApp
        and assigns a locationItem to it
        """
        id = self.nextid
        self.nextid += 1
        self.locations[id] = {
            "location": "",
            "radius": "",
            "coords": "",
            "timezone": ""
        }

        self.location_items[id] = locationItem(
            self.location_popup_list, 
            self, 
            id
        )
    
    def update_main_display(self, location=True):
        """Update the disasterApp display"""
        if location:
            location_info = self.locations[self.selected_location]

            self.current_location_label.config(
                text=f"Current Location:\n{location_info["location"]}",
                wraplength=self.current_location_label.winfo_width()
            )

            self.search_radius_label.config(
                text=f"Radius: {location_info["radius"]}km"
            )
        else:
            self.current_location_label.config(
                text="Current Location: Not Selected" 
            )

            self.search_radius_label.config(
                text=f"Radius: Not Selected"
            )
        
    def update_weather_display(self):
        location_key = self.locations[self.selected_location]
        timestamps = self.weather_data["hourly"][location_key].keys()
        hour_data = self.weather_data["hourly"][location_key].values()
        daily_data = self.weather_data["daily"][location_key]

        self.weather_sunrise_label.config(
            text=f"Sunrise: {daily_data["sunrise"]}"
        )
        self.weather_sunset_label.config(
            text=f"Sunset: {daily_data["sunset"]}"
        )

        self.weather_temp_label.config(
            text="Current Temperature: " + 
            f"{round(hour_data[0]["temperature_2m"])}℃\n\n" + 
            "(feels like: " + 
            f"{round(hour_data[0]["apparent_temperature"])}℃)"
        )
        self.weather_rain_chance_label.config(
            text="Chance of Rain: \n" + 
            f"{round(hour_data[0]["precipitation_probability"])}%"
        )
        self.weather_cloud_cover_label.config(
            text=f"{hour_data[0]["cloud_cover"]}"
        )
    
    def update_local_storage(self):
        """Rewrites local storage with stored data from disasterApp"""
        with open(LOCATIONS_FILE, 'w', encoding='utf-8') as locf:
            locf = json.dump(self.locations, locf, indent=4)

    def refresh_all_data(self):
        """Calls all api fetches to update current data
        
        This function builds a collated package of all available 
        locations and sends it to each api method to refresh current
        stored data
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
                "Syncing Information",
                "To refresh information shown, please first create a " +
                "new location to continue"
            )
            return
        
        for location in self.locations.values():
            api_package["location"].append(location["location"])
            api_package["radius"].append(location["radius"])
            api_package["lat"].append(location["coords"][0])
            api_package["lon"].append(location["coords"][1])
            api_package["timezone"].append(location["timezone"])

        self.refresh_weather_api(api_package)
        self.refresh_earthquake_api(api_package)
        self.schedule_refresh()
        self.last_all_refresh = datetime.now().strftime(
            "%Y-%m-%d %I:%M %p"
        )
        self.last_refresh_label.config(
            text=f"Last refreshed at: {self.last_all_refresh}"
        )

    def get_next_refresh_time(self):
        """Get next timestamp for cache refresh
        
        Determines the next available timestamp for an auto refresh to
        execute based from a offset from the hour
        """
        now = datetime.now()

        next_refresh = now.replace(
            minute=self.refresh_minute,
            second=0,
            microsecond=0
        )

        if next_refresh <= now:
            next_refresh += timedelta(hours=1)
        
        self.next_refresh = next_refresh
        return next_refresh
    
    def schedule_refresh(self):
        self.next_refresh = self.get_next_refresh_time()

        delay_ms = int(
            (self.next_refresh - datetime.now()).total_seconds() * 1000
        )

        self.root.after(
            delay_ms,
            self.refresh_all_data
        )

    def refresh_weather_api(self, package):
        """Pull information from the WeatherAPI"""
        hourly_data, daily_data = \
            WeatherAPI.get_weather_data(
                self.weather_session,
                package
            )
        
        self.weather_data = {
            "hourly": hourly_data,
            "daily": daily_data
        }
        
        self.update_weather_display()
    
    def refresh_earthquake_api(self, package):
        pass

root = tk.Tk()
app = disasterApp(
    root, 
    location_data=location_data, 
    system_data=system_data
)
root.mainloop()
