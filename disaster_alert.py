import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

class statusIndicator:
    def __init__(self):
        pass

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

        self.main_frame.pack(fill="both", expand=True)
        self.refresh_frame.pack(fill="x")
        self.location_frame.pack(fill="x")
        self.all_status_frame.pack(fill="x", expand=True)
    
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
            ttk.Frame(self.w_info_container, padding=10)
        self.w_footer_frame = \
            ttk.Frame(self.weather_frame, padding=10)
        self.flood_frame = ttk.Frame(self.main_frame)
        self.f_title_frame = \
            ttk.Frame(self.flood_frame, padding=10)
        self.f_info_container = \
            ttk.Frame(self.flood_frame, padding=10)
        self.f_footer_frame = \
            ttk.Frame(self.flood_frame, padding=10)
        self.earthquake_frame = ttk.Frame(self.main_frame, padding=10)
        self.q_status_frame = \
            ttk.Frame(self.earthquake_frame, padding=10)
        self.q_info_container = \
            ttk.Frame(self.earthquake_frame, padding=10)
        self.q_footer_frame = \
            ttk.Frame(self.earthquake_frame, padding=10)
    
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
        self.change_location_button.grid(row=0, column=1)
        
        self.search_radius_label = ttk.Label(
            self.location_frame,
            text="Radius: _km",
            padding=(10, 0)
        )
        self.search_radius_label.grid(row=1, column=0)

        # Main Status Display (home screen)
        self.all_status_title = ttk.Label(
            self.all_status_frame,
            text="Status",
            padding=10
        )

        self.all_status_row1 = ttk.Frame(
            self.all_status_frame,
            padding=(10,2.5)
        )
        self.all_status_row1.pack()

        # Status Indicator Here

        self.all_status_w_label = ttk.Label(
            self.all_status_row1,
            text="Weather: Normal",
            padding=10
        )
        self.all_status_w_label.pack()
        
        self.all_status_w_button = ttk.Button(
            self.all_status_row1,
            text="View Weather Details",
        )
        self.all_status_w_button.pack(side="right", anchor="w")

        self.all_status_row2 = ttk.Frame(
            self.all_status_frame,
            padding=(10,2.5)
        )
        self.all_status_row2.pack()

        self.all_status_f_label = ttk.Label(
            self.all_status_row2,
            text="Flood Risk: Moderate",
            padding=10
        )
        self.all_status_f_label.pack()

        self.all_status_f_button = ttk.Button(
            self.all_status_row2,
            text="View Flood Alerts",
            padding=10
        )
        self.all_status_f_button.pack(side="right", anchor="w")

        self.all_status_row3 = ttk.Frame(
            self.all_status_frame,
            padding=(10,2.5)
        )
        self.all_status_row3.pack()

        self.all_status_q_label = ttk.Label(
            self.all_status_row3,
            text="Earthquake Alert: Severe"
        )
        self.all_status_q_label.pack()

        self.all_status_q_button = ttk.Button(
            self.all_status_row3,
            text="View Earthquake Alerts",
            padding=10
        )
        self.all_status_q_button.pack(side="right", anchor="w")






        
        
        
root = tk.Tk()
app = disasterApp(root)
root.mainloop()