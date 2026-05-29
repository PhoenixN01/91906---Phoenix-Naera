import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

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

        # All frames for Weather-specific window
        self.weather_frame = ttk.Frame(self.main_frame)
        self.w_status_frame = \
            ttk.Frame(self.weather_frame, padding=10)
        self.w_info_container = \
            ttk.Frame(self.weather_frame, padding=10)
        self.w_info_row1 = \
            ttk.Frame(self.w_info_container, padding=10)
        self.w_info_row2 = \
            ttk.Frame(self.w_info_container, padding=10)
        self.w_info_sunCol = \
            ttk.Frame(self.w_info_row1, padding=10)
        self.w_footer_frame = \
            ttk.Frame(self.weather_frame, padding=10)
        
        # All frames for flood-specific window
        self.flood_frame = ttk.Frame(self.main_frame)
        self.f_title_frame = \
            ttk.Frame(self.flood_frame, padding=10)
        self.f_info_container = \
            ttk.Frame(self.flood_frame, padding=10)
        self.f_footer_frame = \
            ttk.Frame(self.flood_frame, padding=10)
        
        # All frames for earthquake-specific window
        self.earthquake_frame = ttk.Frame(self.main_frame, padding=10)
        self.q_status_frame = \
            ttk.Frame(self.earthquake_frame, padding=10)
        self.q_info_container = \
            ttk.Frame(self.earthquake_frame, padding=10)
        self.q_footer_frame = \
            ttk.Frame(self.earthquake_frame, padding=10)
        
        self.main_frame.pack(fill="both", expand=True)
        self.refresh_frame.pack(fill="x")
        self.location_frame.pack(fill="x", expand=True)
        self.location_frame.grid_columnconfigure(1, weight=1)
        self.all_status_frame.pack(fill="x", expand=True)
    
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
            padding=10
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
            text="Flood Risk: Moderate",
            padding=10
        )
        self.all_status_f_label.grid(row=0, column=1)

        self.all_status_f_button = ttk.Button(
            self.all_status_row2,
            text="View Flood Alerts",
            padding=10
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
            text="Earthquake Alert: Severe",
            padding=10
        )
        self.all_status_q_label.grid(row=0, column=1)

        self.all_status_q_button = ttk.Button(
            self.all_status_row3,
            text="View Earthquake Alerts",
            padding=10
        )
        self.all_status_q_button.grid(row=0, column=3, sticky="e")

        # API Sync Button ("Server sync")
        self.all_sync_button = ttk.Button(
            self.main_frame, 
            text="Sync all from servers", 
            padding=10
        )
        self.all_sync_button.pack(pady=10)


        # Weather Specific Window


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
        self.weather_sunrise = ttk.Label(
            self.w_info_sunCol,
            text="Sunrise: 7:15am",
            padding=10)
        



        
        
root = tk.Tk()
app = disasterApp(root)
root.mainloop()