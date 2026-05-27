import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

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
        """Creates the layout structure of the GUI\
        
        The usage of frames allows GUI elements to be placed without 
        encountering issues of mixing information across the GUI
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
        self.last_refresh_label = ttk.Label(
            self.refresh_frame, 
            text=f"Last refreshed at:    {self.last_all_refresh}",
            padding=10
            )
        self.last_refresh_label.pack(side="top")

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

        
        
        
root = tk.Tk()
app = disasterApp(root)
root.mainloop()