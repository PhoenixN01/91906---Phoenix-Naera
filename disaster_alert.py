import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class disasterApp:
    def __init__(self, root):
        self.root = root
        self.locations = []
        self.root.title("Local Disaster Alert System")
        self.root.minsize(496, 496)
        self.root.geometry("496x496+500+0")

        self.create_frames()
    
    def create_frames(self):
        self.main_frame = ttk.Frame(self.root)
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
        
        
        



root = tk.Tk()