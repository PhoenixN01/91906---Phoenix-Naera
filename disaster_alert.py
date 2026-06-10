import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from geopy.geocoders import Nominatim
import json
import os

CITIES_FILE = "cities.json"

def load_cities():
    with open(CITIES_FILE, "r") as f:
        return json.load(f)
    
CITIES = load_cities()

class statusIndicator(tk.Canvas):
    def __init__(self, parent):
        super().__init__(
            parent,
            width=14,
            height=14,
            highlightthickness=0
        )
 
        self.light = self.create_oval(
            2, 2,
            12, 12,
            fill="#33FF00",
            outline="black"
        )

    def setColour(self, colour):
        self.itemconfig(self.light, fill=colour)
    
class autocompleteEntry(ttk.Frame):
    def __init__(self, parent, options, current_info):
        super().__init__(parent)

        self.options = options

        self.current_info = current_info

        self.location_entry = ttk.Entry(self, width=30)
        self.radius_entry = ttk.Entry(self, width=30)

        if current_info:
            self.location_entry.insert(0, self.current_info[0])
            self.radius_entry.insert(0, self.current_info[1])

        self.location_entry.pack(fill="x")
        self.radius_entry.pack(fill="x")

        self.listbox = tk.Listbox(self, height=5)
        self.listbox.pack(fill="x")

        self.location_entry.bind(
            "<KeyRelease>", self.update_suggestions
        )
        self.listbox.bind(
            "<<ListboxSelect>>", self.select_item
        )

        self.actions_frame = ttk.Frame(self)
        self.actions_frame.pack(fill="x")

        self.delete_button = ttk.Button(
            self.actions_frame, 
            text="Delete",
            padding=10,
            command=lambda: self.return_location("delete")
        )
        self.delete_button.grid(row=0, column=0)

        self.save_button = ttk.Button(
            self.actions_frame,
            text="Save",
            command=lambda: self.return_location("save")
        )
        self.save_button.grid(row=0, column=1)

        self.cancel_button = ttk.Button(
            self.actions_frame,
            text="Cancel",
            padding=10
        )
        self.cancel_button.grid(row=0, column=2)

    def update_suggestions(self):
        typed = self.entry.get().lower()

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

    def select_item(self):
        selection = self.listbox.curselection()

        if not selection:
            return

        value = self.listbox.get(selection[0])

        if value == "No city found":
            return
        
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

        self.listbox.delete(0, tk.END)
    
    def validate_int(self, input):
        try:
            valid_int = int(input)
        except:
            return False
        
        if valid_int > 0:
            return valid_int
        else:
            return False
        
    
    def return_info(self, action, info):
        validated_radius = self.validate_int(info[1])
        
        return info, action
    
class locationItem(ttk.Frame):
    def __init__(self, parent, location="", radius=0):
        super().__init__(parent)

        self.location = location
        self.radius = radius

        self.location_label = ttk.Label(
            self,
            text=f"{self.location}",
            padding=10
        )
        self.location_label.grid(row=0, column=0, sticky="e")

        self.radius_label = ttk.Label(
            self,
            text=f"{self.radius}",
            padding=10
        )
        self.radius_label.grid(row=1, column=0, sticky="e")
    
        self.edit_button = ttk.Button(
            self,
            text="Edit",
            padding=10,
            command=self.edit_location
        )
        self.edit_button.grid(row=0, column=2, rowspan=1, sticky="w")

        self.select_button = ttk.Button(
            self,
            text="Select",
            padding=10
        )
        self.select_button.grid(row=0, column=3, rowspan=1, sticky="w")
    
    def edit_location(self):
        autocomplete = autocompleteEntry(options=CITIES, )

class disasterApp:
    def __init__(self, root):
        self.root = root
        self.locations = []
        self.root.title("Local Disaster Alert System")
        self.root.minsize(496, 496)
        self.root.geometry("496x496+500+0")

        current_time = datetime.now()
        
        self.last_all_refresh = \
            current_time.strftime("%Y-%m-%d %I:%M:%S %p")
        
        self.city_input = ""
        self.country_input = ""
        self.locations = {}
        
        self.create_frames()
        self.create_widgets()
    
    def create_frames(self):
        """Creates the layout structure of the GUI
        
        The usage of create_frames when creating frames used to control 
        the positioning and layout of items on screen keeps code
        consisten and separate from the widgets (elements) of the GUI
        """
        
        self.main_frame = ttk.Frame(self.root)

        self.refresh_frame = ttk.Frame(self.main_frame)
        self.location_frame = ttk.Frame(self.main_frame, padding=10)

        self.all_status_frame = ttk.Frame(self.main_frame, padding=10)
        self.footer_frame = ttk.Frame(self.main_frame, padding=10)
        self.footer_frame.columnconfigure(0, weight=0)
        self.footer_frame.columnconfigure(1, weight=1)
        self.footer_frame.columnconfigure(2, weight=1)

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
        self.location_frame.pack(fill="x", expand=True)
        self.location_frame.grid_columnconfigure(1, weight=1)
        self.all_status_frame.pack(fill="x", expand=True)
        # self.weather_frame.pack(fill="x", expand=True)
        # self.flood_frame.pack(fill="x", expand=True)
        # self.earthquake_frame.pack(fill="x", expand=True)
        self.footer_frame.pack(side=tk.BOTTOM, fill="x", expand=False)
    
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
            padding=10
            )
        self.last_refresh_label.pack(side="top")

        # Current Location Display
        self.current_location_label = ttk.Label(
            self.location_frame,
            text="Current Location: ____, ______",
            padding=(10, 0)
        )
        self.current_location_label.grid(row=0, column=0)

        self.change_location_button = ttk.Button(
            self.location_frame,
            text="Change",
        )
        self.change_location_button.grid(row=0, column=2, sticky="e")
        
        self.search_radius_label = ttk.Label(
            self.location_frame,
            text="Radius: _km",
            padding=(10, 0)
        )
        self.search_radius_label.grid(row=1, column=0, sticky="w")

        # Main Status Display (home screen)
        self.all_status_title = ttk.Label(
            self.all_status_frame,
            text="Status",
            padding=10
        )

        # Row 1: Weather Status
        self.all_status_row1 = ttk.Frame(
            self.all_status_frame,
            padding=(10,2.5)
        )
        self.all_status_row1.pack(fill="x", expand=True)
        self.all_status_row1.grid_columnconfigure(2, weight=1)

        self.all_status_w_indicator = statusIndicator(
            self.all_status_row1
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
            padding=10
        )
        self.all_status_w_label.grid(row=0, column=1)
        
        self.all_status_w_button = ttk.Button(
            self.all_status_row1,
            text="View Weather Details",
            padding=10,
            command=self.show_weather_display
        )
        self.all_status_w_button.grid(row=0, column=3, sticky="e")

        # Row 2: Flood Status
        self.all_status_row2 = ttk.Frame(
            self.all_status_frame,
            padding=(10,2.5)
        )
        self.all_status_row2.pack(fill="x", expand=True)
        self.all_status_row2.grid_columnconfigure(2, weight=1)

        self.all_status_f_indicator = statusIndicator(
            self.all_status_row2
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
            padding=10
        )
        self.all_status_f_label.grid(row=0, column=1)

        self.all_status_f_button = ttk.Button(
            self.all_status_row2,
            text="View Flood Alerts",
            padding=10,
            command=self.show_flood_display
        )
        self.all_status_f_button.grid(row=0, column=3, sticky="e")

        # Row 3: Earthquake Status
        self.all_status_row3 = ttk.Frame(
            self.all_status_frame,
            padding=(10,2.5)
        )
        self.all_status_row3.pack(fill="x", expand=True)
        self.all_status_row3.grid_columnconfigure(2, weight=1)

        self.all_status_q_indicator = statusIndicator(
            self.all_status_row3
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
            padding=10
        )
        self.all_status_q_label.grid(row=0, column=1)

        self.all_status_q_button = ttk.Button(
            self.all_status_row3,
            text="View Earthquake Alerts",
            padding=10,
            command=self.show_earthquake_display
        )
        self.all_status_q_button.grid(row=0, column=3, sticky="e")

        self.back_home_button = ttk.Button(
            self.footer_frame,
            text="Back home",
            padding=5,
            command=self.show_home_display
        )
        self.back_home_button.grid(row=0, column=0, sticky="w")
        self.back_home_button.state(['disabled'])

        # Footer Buttons
        self.all_sync_button = ttk.Button(
            self.footer_frame, 
            text="Sync from Servers", 
            padding=5
        )
        self.all_sync_button.grid(row=0, column=1, sticky="s")


        # ---- Weather Specific Window ----


        # Weather Main Status
        self.weather_status_indicator = statusIndicator(
            self.w_status_frame
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
            column=0, 
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
            self.f_status_container
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
            self.q_status_container
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
        self.back_home_button.grid_forget()
        self.footer_frame.columnconfigure(0, weight=0)
    
    def show_weather_display(self):
        self.all_status_frame.pack_forget()
        self.weather_frame.pack(fill="x", expand=True)
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack_forget()
        self.back_home_button.grid(row=0, column=0, sticky="w")
        self.footer_frame.columnconfigure(0, weight=1)

    def show_flood_display(self):
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack(fill="x", expand=True)
        self.earthquake_frame.pack_forget()
        self.back_home_button.grid(row=0, column=0, sticky="w")
        self.footer_frame.columnconfigure(0, weight=1)
    
    def show_earthquake_display(self):
        self.all_status_frame.pack_forget()
        self.weather_frame.pack_forget()
        self.flood_frame.pack_forget()
        self.earthquake_frame.pack(fill="x", expand=True)
        self.back_home_button.grid(row=0, column=0, sticky="w")
        self.footer_frame.columnconfigure(0, weight=1)
    
    def get_coordinates(self):
        geolocator = Nominatim(user_agent="my_geo_app")
        address = f"{self.city_input}, {self.country_input}"

        try:
            location = geolocator.geocode(address)

            if location:
                return (location.latitude, location.longitude)
            else:
                return "Location Not Found"
        except Exception as e:
            messagebox.showerror("Location Error", f"Error: {e}")
            return "Error"
        
    def show_location_menu(self):
        self.location_popup_menu = tk.Toplevel(self.root)
        self.location_popup_menu.title("Location Menu")
        self.location_popup_menu.geometry("250x250+1000+0")

        self.location_popup_list = ttk.Frame(
            self.location_popup_menu,
        )

    
        
root = tk.Tk()
app = disasterApp(root)
root.mainloop()