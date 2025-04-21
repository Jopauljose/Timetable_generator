import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from models import Subject, Labs, Faculty, Class
from datetime import datetime

class ConfigurationGUI:
    def __init__(self, root=None):
        self.settings = {
            "school_day_start": "8:45",
            "school_day_end": "15:45",
            "hours_per_day": 9,
            "workdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "breaks": [
                {"name": "Morning Break", "duration_minutes": 10},
                {"name": "Lunch Break", "duration_minutes": 45},
                {"name": "Evening Break", "duration_minutes": 10}
            ]
        }
        
        self.subjects = []
        self.faculties = []
        self.classes = []
        
        # Default subjects if none exist
        self.core_subjects = []
        self.non_core_subjects = []
        self.lab_subjects = []
        
        # Create main window if not provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("Timetable Generator Configuration")
            self.root.geometry("900x700")
            self.standalone = True
        else:
            self.root = root
            self.standalone = False
            
        # Try to load existing configuration
        self.load_config()
        
        # Create the configuration interface
        self.create_gui()
        
    def create_gui(self):
        """Create the configuration GUI"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.general_tab = ttk.Frame(self.notebook)
        self.subjects_tab = ttk.Frame(self.notebook)
        self.faculty_tab = ttk.Frame(self.notebook)
        self.classes_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.general_tab, text="General Settings")
        self.notebook.add(self.subjects_tab, text="Subjects")
        self.notebook.add(self.faculty_tab, text="Faculty")
        self.notebook.add(self.classes_tab, text="Classes")
        
        # Build each tab
        self.build_general_tab()
        self.build_subjects_tab()
        self.build_faculty_tab()
        self.build_classes_tab()
        
        # Add control buttons at the bottom
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save Configuration", 
                   command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate Timetable", 
                   command=self.generate_timetable).pack(side=tk.RIGHT, padx=5)
        
        # Start the main loop if standalone
        if self.standalone:
            self.root.mainloop()
    
    def build_general_tab(self):
        """Build the general settings tab"""
        frame = ttk.LabelFrame(self.general_tab, text="School Hours")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # School day start/end
        ttk.Label(frame, text="School Day Start (HH:MM):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_time_var = tk.StringVar(value=self.settings["school_day_start"])
        ttk.Entry(frame, textvariable=self.start_time_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="School Day End (HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_time_var = tk.StringVar(value=self.settings["school_day_end"])
        ttk.Entry(frame, textvariable=self.end_time_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Periods Per Day:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hours_var = tk.IntVar(value=self.settings["hours_per_day"])
        ttk.Spinbox(frame, from_=5, to=12, textvariable=self.hours_var, width=5).grid(row=2, column=1, padx=5, pady=5)
        
        # Breaks
        break_frame = ttk.LabelFrame(self.general_tab, text="Breaks")
        break_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        ttk.Label(break_frame, text="Name", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=