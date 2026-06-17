import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from geopy.geocoders import Nominatim
import json
import os

CITIES_FILE = "cities.json"
LOCATIONS_FILE = "stored_locations.json"
SYSTEM_FILE = "menu_history.json"

if not os.path.exists(LOCATIONS_FILE):
    with open(LOCATIONS_FILE, 'w') as locf:
        json.dump({}, locf, indent=4)
else:
    try:
        with open(LOCATIONS_FILE, 'r') as locf:
            location_data = json.load(locf)
    except (json.JSONDecodeError, OSError):
        location_data = {}

if not os.path.exists(SYSTEM_FILE):
    with open(SYSTEM_FILE, 'w') as sysf:
        json.dump({}, sysf, indent=4)
else:
    try:
        with open(SYSTEM_FILE, 'r') as sysf:
            system_data = json.load(sysf)
    except (json.JSONDecodeError, OSError):
        system_data = {}

def load_cities():
    with open(CITIES_FILE, "r") as ctyf:
        return json.load(ctyf)
    
CITIES = load_cities()

GEOLOCATOR = Nominatim(user_agent="my_geo_app")

class statusIndicator(tk.Canvas):
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
    """Edit menu for editing location details.

    This class is used to serve as a way to update and add details to
    new or existing location items. This class is paired with a location
    item class when created and draws information directly from its 
    designated location, allowing edit menu's to isolate their specific
    location for modification.
    """
    def __init__(self, frame, parent, locationItem, id, locationExists):
        super().__init__(frame)
        self.options = CITIES
        self.locationItem = locationItem
        self.parent = parent
        self.id = id
        self.location_exists = locationExists
        self.info = {
            "location": self.parent.locations[id]["location"],
            "radius": self.parent.locations[id]["radius"],
            "coords": self.parent.locations[id]["coords"]
        }

        self.create_display()
    
    def create_display(self):
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

    def update_suggestions(self, event):
        typed = self.location_entry.get().lower()

        self.listbox.delete(0, tk.END)

        if not typed:
            return
        
        matches = []

        for city in self.options:
            full_name = f"{city['city']}, {city['country']}"
            if typed in full_name.lower():
                matches.append(full_name)
        
        if matches:
            for match in matches:
                self.listbox.insert(tk.END, match)
        else:
            self.listbox.insert(tk.END, "No city found")

    def select_item(self, event):
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
        try:
            radius = int(self.info["radius"])
            if radius > 0:
                self.info["radius"] = radius
                return True
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            return False
        
        messagebox.showerror(
            "Input Error", 
            ("Radius Input Must be a " +
            "Positive Integer Value to continue")
        )
        return False
    
    def remove_location(self):
        l = self.parent.locations[self.id]["location"]
        ask_to_delete = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you would like to remove location: {l}"
        )

        if not ask_to_delete:
            return
        
        if self.parent.selected_location == self.locationItem.id:
            self.parent.update_display(False)

        self.parent.locations.pop(
            self.locationItem.id, None
        )
        self.parent.update_local_storage()
        self.locationItem.destroy()
        messagebox.showinfo(
            "Successfully Removed", 
            f"Location: {l} removed successfully."
        )
        self.destroy()
    
    def save_changes(self):
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

        self.parent.locations[self.id]["location"] = self.info[
            "location"]
        self.parent.locations[self.id]["radius"] = self.info["radius"]
        self.parent.locations[self.id]["coords"] = self.info["coords"]
        self.locationItem.location_label.config(
            text=self.info["location"]
        )
        self.locationItem.radius_label.config(
            text=f"Radius: {self.info["radius"]}km"
        )
        self.parent.update_local_storage()
        self.destroy()
    
    def cancel_changes(self):
        if self.location_exists:
            self.destroy()
        else:
            self.parent.locations.pop(
                self.locationItem.id, None
            )
            self.locationItem.destroy()
            self.destroy()
    
    def get_coordinates(self):
        address = self.location_entry.get()
        if "," not in address:
            messagebox.showerror(
                "Format Error", 
                "Locations must be written as: City, Country"
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
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            return False


class locationItem(ttk.Frame):
    """Creates a location item

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

        self.location_label = ttk.Label(
            self.info_frame,
            text=""
        )
        self.location_label.grid(row=0, column=0, sticky="w")

        self.radius_label = ttk.Label(
            self.info_frame,
            text=""
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
    
    def display_self(self):
        self.pack(fill="x", expand=False)

    def edit_location(self, locationExists):
        self.edit_menu = locationEditFrame(
            self.parent.location_popup_menu, 
            self.parent, 
            self,
            self.id,
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
        self.select_button.config(text="(Active)")
        self.select_button.state(["disabled"])
        self.parent.selected_location = self.id
        self.parent.update_display()

        for location in self.parent.locations.values():
            if not location["view"] == self:
                location["view"].deselect_location()
  
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

class disasterApp:
    def __init__(self, root, location_data, system_data):
        self.root = root
        self.root.title("Local Disaster Alert System")
        self.root.minsize(496, 496)
        self.root.geometry("600x500+500+0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.root.configure(bg="#F0F0F0")

        current_time = datetime.now()
        
        self.last_all_refresh = \
            current_time.strftime("%Y-%m-%d %I:%M %p")
        
        self.locations = location_data
        self.selected_location = 0
        self.nextid = 0
        
        self.create_styles()
        self.create_frames()
        self.create_widgets()
        self.create_location_menu()

    def create_styles(self):
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
    
    def create_widgets(self):
        """Creates the widgets for the GUI

        create_widgets is used when creating all of the elements seen 
        on-screen by users and is responsible for populating each
        frame regardless of their display setting
        """
        # Refresh tag at top of GUI
        self.last_refresh_label = ttk.Label(
            self.refresh_frame, 
            text=f"Last refreshed at:    {self.last_all_refresh}",
            style="LastRefresh.TLabel"
            )
        self.last_refresh_label.pack(side="top")

        # Current Location Display
        self.current_location_label = ttk.Label(
            self.location_frame,
            text="Current Location: Not Selected",
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
            text="Radius: Not Selected",
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
            width=17,
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
            width=17,
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
            width=17,
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
            style="MainBG.TButton"
        )
        self.all_sync_button.place(relx=0.5, rely=0.5, anchor="center")


        # ---- Weather Specific Window ----


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

        # ---- Flood Specific Window ----

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

        # ---- Earthquake Specific Window ----

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
        self.all_status_frame.pack(fill="x", expand=True)
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack_forget()
    
    def show_weather_display(self):
        self.all_status_frame.pack_forget()
        self.weather_frame.pack(fill="x", expand=True)
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack(side="left")

    def show_flood_display(self):
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack(fill="x", expand=True)
        self.earthquake_frame.pack_forget()
        self.back_home_button.pack(side="left")
    
    def show_earthquake_display(self):
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack(fill="x", expand=True)
        self.back_home_button.pack(side="left")
    
    def create_location_menu(self):
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
        if self.locations:
            for locationInfo in self.locations.values():
                locationInfo["view"].display_self()
        
        self.location_popup_menu.place(
            relx=0.5, 
            rely=0.5, 
            anchor="center",
            relheight=0.9,
            relwidth=0.9
        )
    
    def create_location(self):
        id = self.nextid
        self.nextid += 1
        self.locations[id] = {
            "location": "",
            "radius": "",
            "coords": "",
            "view": ""
        }

        self.locations[id]["view"] = locationItem(
            self.location_popup_list, 
            self, 
            id
        )
    
    def update_display(self, location=True):
        if location:
            location_info = self.locations[self.selected_location]

            self.current_location_label.config(
                text=f"Current Location: \n{location_info["location"]}",
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
    
    def update_local_storage(self):
        with open(LOCATIONS_FILE, 'w') as locf:
            locf = json.dump(self.locations, locf, indent=4)
            print(locf)

root = tk.Tk()
app = disasterApp(
    root, 
    location_data=location_data, 
    system_data=system_data
)
root.mainloop()