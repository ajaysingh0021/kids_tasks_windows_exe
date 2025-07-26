# Kids Task Tracker Application
# A local, multi-page app for parents to manage and kids to complete daily tasks.
# Uses only Python's built-in tkinter library and does not require an internet connection.
# VERSION: No Images - This version removes all icon/image dependencies to prevent errors.

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys 
import hashlib
from datetime import datetime

# --- Helper function to handle file paths for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Constants ---
DATA_FILE = "kid_tasks_data.json"
FONT_FAMILY = "Balsamiq Sans"  # A playful, rounded font. Falls back to Arial if not installed.

# --- Color Themes ---
THEMES = {
    "dark": {
        "bg_primary": "#2d2d2d",
        "bg_secondary": "#404040",
        "fg_primary": "#ffffff",
        "fg_secondary": "#b0b0b0",
        "accent": "#5cacee",
        "task_todo": "#3a7ca5",
        "task_active": "#f7b731",
        "task_overdue": "#e74c3c",
        "task_done": "#2ecc71",
        "clock_bg": "#4a4a4a"
    },
    "light": {
        "bg_primary": "#f5f5f5",
        "bg_secondary": "#ffffff",
        "fg_primary": "#000000",
        "fg_secondary": "#555555",
        "accent": "#0078d7",
        "task_todo": "#a9d6e5",
        "task_active": "#f9d423",
        "task_overdue": "#ff6b6b",
        "task_done": "#57cc99",
        "clock_bg": "#e0e0e0"
    }
}

# --- Helper Functions ---
def hash_pin(pin):
    """Hashes the PIN for secure storage."""
    return hashlib.sha256(pin.encode()).hexdigest()

def get_font(size, weight="normal"):
    """Returns the preferred font, with a fallback."""
    try:
        return (FONT_FAMILY, size, weight)
    except tk.TclError:
        return ("Arial", size, weight)

# --- Main Application Class ---
class KidsTaskTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = self.load_data()
        self.current_user = self.data["settings"].get("last_logged_in_user")
        self.current_theme = self.data["settings"].get("theme", "light")
        
        self.title("Kids Task Tracker")
        self.geometry("1024x768")
        self.minsize(800, 600)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, RegistrationPage, DashboardPage, SettingsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.apply_theme()
        
        # Check for a logged-in user and show the appropriate page
        if self.current_user and self.current_user in self.data["users"]:
            self.show_frame("DashboardPage")
        else:
            self.show_frame("LoginPage")

    def show_frame(self, page_name):
        """Show a frame for the given page name."""
        frame = self.frames[page_name]
        # Call a refresh/update method if it exists
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()

    def load_data(self):
        """Loads user and task data from the local JSON file."""
        if not os.path.exists(DATA_FILE):
            return {"users": {}, "settings": {"theme": "light"}}
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
             return {"users": {}, "settings": {"theme": "light"}}

    def save_data(self):
        """Saves the current data to the local JSON file."""
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def logout(self):
        """Logs out the current user."""
        self.data["settings"]["last_logged_in_user"] = None
        self.current_user = None
        self.save_data()
        self.show_frame("LoginPage")

    def toggle_theme(self):
        """Switches between light and dark themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.data["settings"]["theme"] = self.current_theme
        self.apply_theme()
        self.save_data()

    def apply_theme(self):
        """Applies the current theme colors to all widgets."""
        colors = THEMES[self.current_theme]
        self.config(bg=colors["bg_primary"])
        self.container.config(bg=colors["bg_primary"])
        for frame in self.frames.values():
            frame.configure(bg=colors["bg_primary"])
            for widget in frame.winfo_children():
                self.apply_widget_theme(widget, colors)
        # Refresh the dashboard to update task colors
        if hasattr(self.frames["DashboardPage"], 'rebuild_dashboard'):
             self.frames["DashboardPage"].rebuild_dashboard()


    def apply_widget_theme(self, widget, colors):
        """Recursively applies theme to a widget and its children."""
        widget_type = widget.winfo_class()
        try:
            if widget_type in ('Frame', 'TFrame', 'Label', 'TLabel', 'Canvas'):
                widget.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
            elif widget_type in ('Button', 'TButton'):
                if 'task' not in widget.cget("style"): # Don't override task buttons
                    widget.config(bg=colors["accent"], fg=colors["bg_secondary"])
            elif widget_type in ('Entry', 'TEntry'):
                widget.config(bg=colors["bg_secondary"], fg=colors["fg_primary"], insertbackground=colors["fg_primary"])
            elif widget_type in ('Radiobutton', 'TRadiobutton', 'Checkbutton', 'TCheckbutton'):
                 widget.config(bg=colors["bg_primary"], fg=colors["fg_primary"], activebackground=colors["bg_primary"], selectcolor=colors["bg_secondary"])
        except tk.TclError:
            pass # Ignore errors for widgets that don't support an option

        for child in widget.winfo_children():
            self.apply_widget_theme(child, colors)

# --- Base Page Class ---
class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def on_show(self):
        """This method is called when the frame is shown."""
        pass

# --- Authentication Pages ---
class AuthPage(BasePage):
    """A base class for Registration and Login pages for shared layout."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.center_frame = tk.Frame(self, bg=THEMES[controller.current_theme]["bg_secondary"])
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=350)
        
        self.title_label = tk.Label(self.center_frame, text="Auth Page", font=get_font(28, "bold"), bg=self.center_frame.cget("bg"), fg=THEMES[controller.current_theme]["fg_primary"])
        self.title_label.pack(pady=(40, 20))

        self.email_label = tk.Label(self.center_frame, text="Email", font=get_font(12), bg=self.center_frame.cget("bg"), fg=THEMES[controller.current_theme]["fg_secondary"])
        self.email_label.pack(padx=40, anchor="w")
        self.email_entry = ttk.Entry(self.center_frame, font=get_font(14))
        self.email_entry.pack(padx=40, pady=(0, 15), fill="x")

        self.pin_label = tk.Label(self.center_frame, text="6-Digit PIN", font=get_font(12), bg=self.center_frame.cget("bg"), fg=THEMES[controller.current_theme]["fg_secondary"])
        self.pin_label.pack(padx=40, anchor="w")
        self.pin_entry = ttk.Entry(self.center_frame, font=get_font(14), show="*")
        self.pin_entry.pack(padx=40, pady=(0, 20), fill="x")

        self.action_button = ttk.Button(self.center_frame, text="Action", style="Accent.TButton")
        self.action_button.pack(pady=10, ipadx=20, ipady=5)

        self.switch_button = ttk.Button(self.center_frame, text="Switch", style="Link.TButton")
        self.switch_button.pack(pady=5)
    
    def on_show(self):
        """Clear fields when page is shown."""
        self.email_entry.delete(0, 'end')
        self.pin_entry.delete(0, 'end')
        self.update_colors()

    def update_colors(self):
        colors = THEMES[self.controller.current_theme]
        self.config(bg=colors["bg_primary"])
        self.center_frame.config(bg=colors["bg_secondary"])
        for widget in self.center_frame.winfo_children():
            try:
                if isinstance(widget, (tk.Label, ttk.Label)):
                    widget.config(bg=colors["bg_secondary"], fg=colors["fg_primary"])
                elif isinstance(widget, (ttk.Entry)):
                    pass # Handled by style
                elif isinstance(widget, (ttk.Button)):
                    pass # Handled by style
            except tk.TclError:
                pass
        self.title_label.config(fg=colors["fg_primary"])
        self.email_label.config(fg=colors["fg_secondary"])
        self.pin_label.config(fg=colors["fg_secondary"])


class LoginPage(AuthPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.title_label.config(text="Login")
        self.action_button.config(text="Login", command=self.login)
        self.switch_button.config(text="Don't have an account? Register", command=lambda: controller.show_frame("RegistrationPage"))

    def login(self):
        email = self.email_entry.get().lower()
        pin = self.pin_entry.get()

        if not email or not pin:
            messagebox.showerror("Error", "Email and PIN cannot be empty.")
            return
        
        user_data = self.controller.data["users"].get(email)
        if user_data and user_data["pin"] == hash_pin(pin):
            self.controller.current_user = email
            self.controller.data["settings"]["last_logged_in_user"] = email
            self.controller.save_data()
            self.controller.show_frame("DashboardPage")
        else:
            messagebox.showerror("Error", "Invalid email or PIN.")

class RegistrationPage(AuthPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.title_label.config(text="Register")
        self.action_button.config(text="Register", command=self.register)
        self.switch_button.config(text="Already have an account? Login", command=lambda: controller.show_frame("LoginPage"))

    def register(self):
        email = self.email_entry.get().lower()
        pin = self.pin_entry.get()

        if not email or not pin:
            messagebox.showerror("Error", "Email and PIN cannot be empty.")
            return
        if len(pin) != 6 or not pin.isdigit():
            messagebox.showerror("Error", "PIN must be exactly 6 digits.")
            return
        if email in self.controller.data["users"]:
            messagebox.showerror("Error", "This email is already registered.")
            return

        self.controller.data["users"][email] = {
            "pin": hash_pin(pin),
            "children": []
        }
        self.controller.save_data()
        messagebox.showinfo("Success", "Registration successful! Please log in.")
        self.controller.show_frame("LoginPage")

# --- Main Application Pages ---
class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.task_widgets = {}
        self.blinking_tasks = []

        # --- Header ---
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(fill="x", pady=10, padx=20)
        
        self.clock_label = tk.Label(self.header_frame, font=get_font(22, "bold"))
        self.clock_label.pack(side="left")

        self.header_buttons_frame = tk.Frame(self.header_frame)
        self.header_buttons_frame.pack(side="right")

        # Create buttons with text instead of images
        self.theme_button = ttk.Button(self.header_buttons_frame, text="Dark/Light Mode", command=controller.toggle_theme, style="Tool.TButton")
        self.theme_button.pack(side="left", padx=5)
        
        self.settings_button = ttk.Button(self.header_buttons_frame, text="Settings", command=lambda: controller.show_frame("SettingsPage"), style="Tool.TButton")
        self.settings_button.pack(side="left", padx=5)

        self.logout_button = ttk.Button(self.header_buttons_frame, text="Logout", command=controller.logout, style="Tool.TButton")
        self.logout_button.pack(side="left", padx=5)

        # --- Main Content ---
        self.main_canvas = tk.Canvas(self, highlightthickness=0)
        self.main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.dashboard_frame = tk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.dashboard_frame, anchor="nw")
        
        self.dashboard_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind('<Enter>', self._bind_to_mousewheel)
        self.main_canvas.bind('<Leave>', self._unbind_from_mousewheel)

        self.update_clock()
        self.update_tasks_loop()

    def _bind_to_mousewheel(self, event):
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_from_mousewheel(self, event):
        self.main_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_show(self):
        self.rebuild_dashboard()

    def rebuild_dashboard(self):
        """Clears and rebuilds the entire dashboard UI."""
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        self.task_widgets = {}
        self.blinking_tasks = []

        user_data = self.controller.data["users"].get(self.controller.current_user)
        if not user_data:
            return
        
        children = user_data.get("children", [])
        colors = THEMES[self.controller.current_theme]
        self.header_frame.config(bg=colors["bg_primary"])
        self.header_buttons_frame.config(bg=colors["bg_primary"])
        self.clock_label.config(bg=colors["clock_bg"], fg=colors["fg_primary"], padx=15, pady=5)
        self.dashboard_frame.config(bg=colors["bg_primary"])
        self.main_canvas.config(bg=colors["bg_primary"])

        for i, child in enumerate(children):
            col_frame = tk.Frame(self.dashboard_frame, bg=colors["bg_primary"])
            col_frame.grid(row=0, column=i, sticky="ns", padx=10)
            self.dashboard_frame.grid_columnconfigure(i, weight=1)

            # --- Child Header ---
            header_frame = tk.Frame(col_frame, bg=colors["bg_primary"])
            header_frame.pack(fill="x", pady=(0, 10))
            
            # Use text for gender instead of an icon
            gender_symbol = "♂" if child['gender'] == 'male' else '♀'
            gender_color = "#6ca0dc" if child['gender'] == 'male' else "#e882a8"
            tk.Label(header_frame, text=gender_symbol, font=get_font(24, "bold"), bg=colors["bg_primary"], fg=gender_color).pack(side="left", padx=(0, 5))
            tk.Label(header_frame, text=child["name"], font=get_font(20, "bold"), bg=colors["bg_primary"], fg=colors["fg_primary"]).pack(side="left")

            # --- To-Do Section ---
            tk.Label(col_frame, text="To-Do", font=get_font(16), bg=colors["bg_primary"], fg=colors["fg_secondary"]).pack(fill="x", pady=5)
            todo_frame = tk.Frame(col_frame, bg=colors["bg_secondary"], bd=2, relief="groove")
            todo_frame.pack(fill="both", expand=True, ipady=10)
            todo_frame.grid_propagate(False)

            # --- Completed Section ---
            tk.Label(col_frame, text="Completed!", font=get_font(16), bg=colors["bg_primary"], fg=colors["fg_secondary"]).pack(fill="x", pady=(15, 5))
            completed_frame = tk.Frame(col_frame, bg=colors["bg_secondary"], bd=2, relief="groove")
            completed_frame.pack(fill="both", expand=True, ipady=10)
            completed_frame.grid_propagate(False)

            # --- Populate Tasks ---
            self.populate_tasks_for_child(child, todo_frame, completed_frame)
    
    def populate_tasks_for_child(self, child, todo_frame, completed_frame):
        """Fills the To-Do and Completed frames with tasks for a specific child."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_weekday = datetime.now().strftime("%A")

        for task in child.get("tasks", []):
            # Check if task is for today
            if "all" not in task["days"] and today_weekday not in task["days"]:
                continue

            task_id = task["id"]
            is_completed = task.get("completed_on", {}).get(today_str, False)
            
            parent_frame = completed_frame if is_completed else todo_frame
            
            task_bubble = self.create_task_bubble(parent_frame, task, child)
            task_bubble.pack(pady=5, padx=10, fill="x")
            
            self.task_widgets[task_id] = {
                "widget": task_bubble,
                "task_data": task,
                "child_data": child,
                "is_blinking": False
            }
            if not is_completed:
                self.blinking_tasks.append(task_id)


    def create_task_bubble(self, parent, task, child):
        """Creates a single styled task bubble widget."""
        colors = THEMES[self.controller.current_theme]
        
        start_time_obj = datetime.strptime(task["start_time"], "%H:%M").time()
        end_time_obj = datetime.strptime(task["end_time"], "%H:%M").time()
        time_str = f"{start_time_obj.strftime('%I:%M %p')} - {end_time_obj.strftime('%I:%M %p')}"
        
        bubble_text = f"{task['text']}\n{time_str}"
        
        bubble = tk.Label(parent, text=bubble_text, font=get_font(12), wraplength=180, justify="center", pady=10, padx=10, relief="raised", bd=2)
        bubble.bind("<Button-1>", lambda e, t=task, c=child: self.toggle_task_completion(t, c))
        
        return bubble

    def toggle_task_completion(self, task, child):
        """Handles clicking a task bubble to mark it as complete or incomplete."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        task_id = task["id"]
        
        is_currently_completed = task.get("completed_on", {}).get(today_str, False)
        
        if "completed_on" not in task:
            task["completed_on"] = {}
            
        task["completed_on"][today_str] = not is_currently_completed
        
        self.controller.save_data()
        
        if not is_currently_completed:
            self.play_completion_animation(task_id)
        else:
            self.rebuild_dashboard() # Just rebuild for simplicity on undo

    def play_completion_animation(self, task_id):
        """A simple animation when a task is completed."""
        widget_info = self.task_widgets.get(task_id)
        if not widget_info: return
        widget = widget_info["widget"]
        
        original_bg = widget.cget("background")
        
        def animate(step=0):
            if step < 5:
                # Flash a bright color
                color = "#FFD700" if step % 2 == 0 else original_bg
                widget.config(bg=color)
                self.after(80, animate, step + 1)
            else:
                self.rebuild_dashboard() # Rebuild the whole UI to move the task
        
        animate()

    def update_clock(self):
        """Updates the digital clock every second."""
        now = datetime.now()
        # Format: 10:15 AM Thursday, July-24-2025
        clock_text = now.strftime("%I:%M:%S %p %A, %B-%d-%Y")
        self.clock_label.config(text=clock_text)
        self.after(1000, self.update_clock)
        
    def update_tasks_loop(self):
        """Periodically updates the state and color of task bubbles."""
        now = datetime.now().time()
        colors = THEMES[self.controller.current_theme]
        
        for task_id in self.blinking_tasks:
            widget_info = self.task_widgets.get(task_id)
            if not widget_info: continue
            
            widget = widget_info["widget"]
            task = widget_info["task_data"]
            
            start_time = datetime.strptime(task["start_time"], "%H:%M").time()
            end_time = datetime.strptime(task["end_time"], "%H:%M").time()
            
            color = colors["task_todo"]
            is_blinking = False

            if start_time <= now < end_time:
                color = colors["task_active"]
                is_blinking = True
            elif now >= end_time:
                color = colors["task_overdue"]
            
            # Blinking logic
            if is_blinking:
                if widget_info["is_blinking"]:
                    widget.config(bg=colors["bg_secondary"]) # Blink off
                else:
                    widget.config(bg=color) # Blink on
                widget_info["is_blinking"] = not widget_info["is_blinking"]
            else:
                widget.config(bg=color)
                widget_info["is_blinking"] = False
            
            widget.config(fg=colors["fg_primary"])

        self.after(1000, self.update_tasks_loop)

# --- Add Task Popup Window (as a class) ---
class AddTaskPopup(tk.Toplevel):
    def __init__(self, parent, controller, settings_page, child_name):
        super().__init__(parent)
        self.controller = controller
        self.settings_page = settings_page
        self.child_name = child_name

        self.title(f"Add Task for {self.child_name}")
        self.geometry("450x450")
        self.transient(parent)
        self.grab_set()

        # Task Text
        tk.Label(self, text="Task Description:", font=get_font(12)).pack(pady=(10,0), anchor='w', padx=20)
        self.task_text_entry = ttk.Entry(self, font=get_font(12))
        self.task_text_entry.pack(pady=5, padx=20, fill="x")

        # Time Interval
        time_frame = tk.Frame(self)
        time_frame.pack(pady=5, padx=20, fill="x")
        tk.Label(time_frame, text="From:", font=get_font(12)).pack(side="left")
        self.start_hour = ttk.Spinbox(time_frame, from_=0, to=23, wrap=True, width=3, format="%02.0f")
        self.start_hour.pack(side="left")
        tk.Label(time_frame, text=":", font=get_font(12)).pack(side="left")
        self.start_min = ttk.Spinbox(time_frame, from_=0, to=59, wrap=True, width=3, format="%02.0f")
        self.start_min.pack(side="left")
        
        tk.Label(time_frame, text="  To:", font=get_font(12)).pack(side="left", padx=(10,0))
        self.end_hour = ttk.Spinbox(time_frame, from_=0, to=23, wrap=True, width=3, format="%02.0f")
        self.end_hour.pack(side="left")
        tk.Label(time_frame, text=":", font=get_font(12)).pack(side="left")
        self.end_min = ttk.Spinbox(time_frame, from_=0, to=59, wrap=True, width=3, format="%02.0f")
        self.end_min.pack(side="left")
        
        # Days of the week
        days_frame = ttk.LabelFrame(self, text="Repeat on Days", padding=10)
        days_frame.pack(pady=10, padx=20, fill="x")
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # THIS IS THE FIX: Explicitly set the master of the BooleanVars to self (the Toplevel window)
        self.day_vars = {day: tk.BooleanVar(master=self) for day in self.days}
        self.all_days_var = tk.BooleanVar(master=self)

        ttk.Checkbutton(days_frame, text="All Days", variable=self.all_days_var, command=self.toggle_all_days).grid(row=0, column=0, columnspan=2, sticky='w')
        
        for i, day in enumerate(self.days):
            ttk.Checkbutton(days_frame, text=day, variable=self.day_vars[day]).grid(row=i//2 + 1, column=i%2, sticky='w')

        ttk.Button(self, text="Save Task", command=self.save).pack(pady=10)

    def toggle_all_days(self):
        is_checked = self.all_days_var.get()
        for day in self.days:
            self.day_vars[day].set(is_checked)

    def save(self):
        task_text = self.task_text_entry.get()
        start_h, start_m = self.start_hour.get(), self.start_min.get()
        end_h, end_m = self.end_hour.get(), self.end_min.get()
        
        if not task_text or not start_h or not start_m or not end_h or not end_m:
            messagebox.showerror("Error", "All fields must be filled.", parent=self)
            return

        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        if not selected_days:
            messagebox.showerror("Error", "Please select at least one day.", parent=self)
            return

        new_task = {
            "id": f"task_{int(datetime.now().timestamp())}",
            "text": task_text,
            "start_time": f"{start_h}:{start_m}",
            "end_time": f"{end_h}:{end_m}",
            "days": ["all"] if len(selected_days) == 7 else selected_days,
            "completed_on": {}
        }
        
        user_data = self.controller.data["users"][self.controller.current_user]
        child_data = next((c for c in user_data["children"] if c['name'] == self.child_name), None)
        if child_data:
            child_data["tasks"].append(new_task)
        
        self.controller.save_data()
        self.settings_page.on_show()
        self.destroy()

class SettingsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # --- Header ---
        header = tk.Frame(self)
        header.pack(fill="x", padx=20, pady=20)
        tk.Label(header, text="Settings", font=get_font(24, "bold")).pack(side="left")
        ttk.Button(header, text="< Back to Dashboard", command=lambda: controller.show_frame("DashboardPage"), style="Link.TButton").pack(side="right")

        # --- Main Frame ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20)

        # --- Change PIN ---
        pin_frame = ttk.LabelFrame(main_frame, text="Change PIN", padding=15)
        pin_frame.pack(fill="x", pady=10)
        tk.Label(pin_frame, text="New 6-Digit PIN:", font=get_font(12)).grid(row=0, column=0, padx=5, pady=5)
        self.new_pin_entry = ttk.Entry(pin_frame, font=get_font(12), show="*")
        self.new_pin_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(pin_frame, text="Save PIN", command=self.change_pin).grid(row=0, column=2, padx=10)

        # --- Manage Children ---
        children_frame = ttk.LabelFrame(main_frame, text="Manage Children", padding=15)
        children_frame.pack(fill="x", pady=10)
        self.children_list_frame = tk.Frame(children_frame)
        self.children_list_frame.pack(fill="x")
        ttk.Button(children_frame, text="+ Add Child", command=self.add_child_popup).pack(pady=10)
        
        # --- Manage Tasks ---
        tasks_frame = ttk.LabelFrame(main_frame, text="Manage Tasks", padding=15)
        tasks_frame.pack(fill="x", pady=10)
        tk.Label(tasks_frame, text="Select Child:", font=get_font(12)).pack(anchor='w')
        self.child_selector = ttk.Combobox(tasks_frame, state="readonly", font=get_font(12))
        self.child_selector.pack(fill="x", pady=5)
        self.child_selector.bind("<<ComboboxSelected>>", self.populate_tasks_for_selected_child)
        
        self.tasks_list_frame = tk.Frame(tasks_frame)
        self.tasks_list_frame.pack(fill="x", pady=5)
        
        ttk.Button(tasks_frame, text="+ Add Task for Selected Child", command=self.add_task_popup).pack(pady=10)

    def on_show(self):
        """Refresh the page with current data."""
        self.populate_children_list()
        self.populate_child_selector()
        self.populate_tasks_for_selected_child()

    def change_pin(self):
        new_pin = self.new_pin_entry.get()
        if len(new_pin) != 6 or not new_pin.isdigit():
            messagebox.showerror("Error", "PIN must be exactly 6 digits.")
            return
        
        user_data = self.controller.data["users"][self.controller.current_user]
        user_data["pin"] = hash_pin(new_pin)
        self.controller.save_data()
        self.new_pin_entry.delete(0, 'end')
        messagebox.showinfo("Success", "PIN has been updated.")

    def populate_children_list(self):
        for widget in self.children_list_frame.winfo_children():
            widget.destroy()
        
        user_data = self.controller.data["users"].get(self.controller.current_user, {})
        children = user_data.get("children", [])
        
        for i, child in enumerate(children):
            child_frame = tk.Frame(self.children_list_frame)
            child_frame.pack(fill="x", pady=2)
            tk.Label(child_frame, text=f"{child['name']} ({child['gender']})", font=get_font(12)).pack(side="left")
            ttk.Button(child_frame, text="Remove", command=lambda c=child: self.remove_child(c)).pack(side="right")

    def add_child_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add Child")
        popup.transient(self)
        popup.grab_set()

        tk.Label(popup, text="Child's Name:", font=get_font(12)).pack(pady=(10,0))
        name_entry = ttk.Entry(popup, font=get_font(12))
        name_entry.pack(pady=5, padx=20, fill="x")

        gender_var = tk.StringVar(value="male")
        gender_frame = tk.Frame(popup)
        gender_frame.pack(pady=5)
        tk.Label(gender_frame, text="Gender:", font=get_font(12)).pack(side="left")
        ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="male").pack(side="left")
        ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="female").pack(side="left")

        def save():
            name = name_entry.get()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty.", parent=popup)
                return
            
            user_data = self.controller.data["users"][self.controller.current_user]
            user_data["children"].append({"name": name, "gender": gender_var.get(), "tasks": []})
            self.controller.save_data()
            self.on_show()
            popup.destroy()

        ttk.Button(popup, text="Save Child", command=save).pack(pady=10)

    def remove_child(self, child_to_remove):
        if not messagebox.askyesno("Confirm", f"Are you sure you want to remove {child_to_remove['name']} and all their tasks?"):
            return
        user_data = self.controller.data["users"][self.controller.current_user]
        user_data["children"].remove(child_to_remove)
        self.controller.save_data()
        self.on_show()

    def populate_child_selector(self):
        user_data = self.controller.data["users"].get(self.controller.current_user, {})
        children = user_data.get("children", [])
        self.child_selector['values'] = [child['name'] for child in children]
        if children:
            self.child_selector.current(0)

    def populate_tasks_for_selected_child(self, event=None):
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
            
        selected_child_name = self.child_selector.get()
        if not selected_child_name:
            return
            
        user_data = self.controller.data["users"].get(self.controller.current_user, {})
        child_data = next((c for c in user_data.get("children", []) if c['name'] == selected_child_name), None)

        if not child_data:
            return

        for task in child_data.get("tasks", []):
            task_frame = tk.Frame(self.tasks_list_frame)
            task_frame.pack(fill="x", pady=2)
            days = ", ".join(task['days']) if "all" not in task['days'] else "All Days"
            label_text = f"{task['text']} ({task['start_time']}-{task['end_time']}) - [{days}]"
            tk.Label(task_frame, text=label_text, font=get_font(12)).pack(side="left")
            ttk.Button(task_frame, text="Remove", command=lambda t=task: self.remove_task(t)).pack(side="right")

    def add_task_popup(self):
        selected_child_name = self.child_selector.get()
        if not selected_child_name:
            messagebox.showerror("Error", "Please select a child first.")
            return
        
        # Create an instance of the new popup class
        AddTaskPopup(self, self.controller, self, selected_child_name)


    def remove_task(self, task_to_remove):
        selected_child_name = self.child_selector.get()
        user_data = self.controller.data["users"][self.controller.current_user]
        child_data = next((c for c in user_data["children"] if c['name'] == selected_child_name), None)
        
        if child_data and task_to_remove in child_data["tasks"]:
            child_data["tasks"].remove(task_to_remove)
            self.controller.save_data()
            self.populate_tasks_for_selected_child()


# --- Main execution block ---
if __name__ == "__main__":
    # --- Style Configuration ---
    # This needs to be done before the main app window is created
    style = ttk.Style()
    style.theme_use('clam') # A good base theme for customization

    # Button styles
    style.configure("TButton", font=get_font(12), padding=10, borderwidth=0)
    style.map("TButton",
        background=[('active', '#cccccc')],
        foreground=[('active', '#000000')])
    
    style.configure("Accent.TButton", font=get_font(12, "bold"), foreground="white", background=THEMES["light"]["accent"])
    style.map("Accent.TButton", background=[('active', THEMES["light"]["accent"])])
    
    style.configure("Link.TButton", font=get_font(10), foreground=THEMES["light"]["accent"], borderwidth=0, padding=0)
    style.map("Link.TButton", background=[('active', THEMES["light"]["bg_secondary"])])

    style.configure("Tool.TButton", padding=5, relief="flat", background=THEMES["light"]["bg_primary"])
    style.map("Tool.TButton", background=[('active', THEMES["light"]["bg_secondary"])])

    # Entry style
    style.configure("TEntry", font=get_font(12), padding=8, borderwidth=1, relief="flat")
    
    # Other styles
    style.configure("TLabel", font=get_font(12), padding=5)
    style.configure("TLabelframe", font=get_font(14, "bold"), padding=10)
    style.configure("TLabelframe.Label", font=get_font(14, "bold"))
    style.configure("TCombobox", font=get_font(12), padding=5)
    
    app = KidsTaskTracker()
    app.mainloop()
