import tkinter as tk
from tkinter import ttk, simpledialog
import random
import json
import os
import math

class DiceRollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DS TTRPG Helper")
        
        # Set window size and icon
        self.root.geometry("520x560")
        self.root.iconbitmap("icon.ico")  # Add your app icon here

        # Define attributes
        self.attributes = ["Strength", "Technique", "Constitution", "Resolve", "Instinct", "Celerity"]

        # Create main frame
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill="both", expand=True)

        # Add "New Roller" button
        new_roller_button = tk.Button(main_frame, text="New Roller", command=self.add_roller_tab, bg="#470701", fg="white", borderwidth=0)
        new_roller_button.pack(pady=10, side=tk.TOP, anchor=tk.W)

        # Set up notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Log frame
        self.log_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.log_frame, text="Log")

        self.logs = []

        # Log display
        self.log_text = tk.Text(self.log_frame, height=20, width=60, bg="white", fg="black", borderwidth=0)
        self.log_text.pack(pady=10, fill="both", expand=True)

        # Notes frame
        self.notes_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.notes_frame, text="Notes")

        # Notes display
        self.notes_text = tk.Text(self.notes_frame, height=20, width=60, bg="white", fg="black", borderwidth=0)
        self.notes_text.pack(pady=10, fill="both", expand=True)

        # Add initial roller tab
        self.add_roller_tab()

        # Handle app close event to save inputs
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_roller_tab(self):
        tab_frame = tk.Frame(self.notebook, bg="white")
        tab_frame.pack(fill="both", expand=True)

        # Default tab name
        tab_name = tk.StringVar(value="Roller")
        
        # Name entry field
        name_label = tk.Label(tab_frame, text="Name:", bg="white", fg="#470701")
        name_label.grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab_frame, textvariable=tab_name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Input fields and roll buttons
        entries = {}

        for i, attribute in enumerate(self.attributes):
            label = tk.Label(tab_frame, text=attribute, bg="white", fg="#470701")
            label.grid(row=i+1, column=0, padx=10, pady=5)

            entry = tk.Entry(tab_frame)
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            entries[attribute] = entry

            roll_button = tk.Button(tab_frame, text="Roll", command=lambda attr=attribute: self.roll_dice(attr, entries, tab_name.get()), bg="#470701", fg="white", borderwidth=0)
            roll_button.grid(row=i+1, column=2, padx=10, pady=5)

            # Tooltip setup for the label
            def get_tooltip_text(entry=entry):
                try:
                    value = int(entry.get())
                except ValueError:
                    value = 0
                return self.create_tooltip_text(value)

            Tooltip(label, get_tooltip_text)

        # Output text box
        output_text = tk.Text(tab_frame, height=10, width=50, bg="white", fg="black", borderwidth=0)
        output_text.grid(row=len(self.attributes)+1, column=0, columnspan=3, padx=10, pady=10)

        # Add the new tab to the left of the Log tab
        index = self.notebook.index("end") - 2
        self.notebook.insert(index, tab_frame, text=tab_name.get())
        self.notebook.select(tab_frame)

        # Bind name entry field update to load data
        name_entry.bind("<FocusOut>", lambda event: self.update_tab_name(tab_frame, tab_name.get(), entries, output_text))

    def create_tooltip_text(self, value):
        # Calculate tooltip text
        values = {
            "1/2": max(math.floor(value / 2), 1),
            "1/5": max(math.floor(value / 5), 1),
            "1/10": max(math.floor(value / 10), 1),
            "1/12": max(math.floor(value / 12), 1),
            "1/20": max(math.floor(value / 20), 1)
        }
        return "\n".join(f"{k}: {v}" for k, v in values.items())

    def update_tab_name(self, tab_frame, new_name, entries, output_text):
        # Update tab name
        index = self.notebook.index(tab_frame)
        self.notebook.tab(tab_frame, text=new_name)

        # Save current tab data if needed
        old_name = self.notebook.tab(tab_frame, "text")
        if old_name and old_name != new_name:
            self.save_data_for_tab(old_name, entries)

        # Load data for new tab name
        self.load_data_for_tab(new_name, entries, output_text)

    def roll_dice(self, attribute, entries, tab_name):
        try:
            value = int(entries[attribute].get())
        except ValueError:
            tab = self.notebook.select()
            output_text = [widget for widget in self.notebook.nametowidget(tab).winfo_children() if isinstance(widget, tk.Text)][0]
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"Invalid input for {attribute}.\n")
            return

        # Clear the output text box before each roll
        tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(tab)
        output_text = [widget for widget in tab_frame.winfo_children() if isinstance(widget, tk.Text)][0]

        output_text.delete(1.0, tk.END)

        num_rolls = simpledialog.askinteger("Input", f"How many rolls for {attribute}?")
        if not num_rolls:
            return

        results = []
        result_str = f"{attribute} rolls:\n"
        for _ in range(num_rolls):
            base_roll = random.randint(1, 100)
            modifier = max(math.floor(int(entries[attribute].get()) / 5), 1)  # Rounds down the modifier to the nearest whole number with a minimum of 1
            total_roll = base_roll + modifier
            result_str += f"Base: {base_roll}, Modifier: {modifier}, Total: {total_roll}\n"
            results.append(f"Base Roll: {base_roll}")

        output_text.insert(tk.END, result_str + "\n")

        success = self.ask_success_fail()
        log_entry = f"Tab: {self.notebook.tab(self.notebook.select(), 'text')} | {attribute} | Rolls: {results} | {'Success' if success else 'Failure'}"
        self.logs.append(log_entry)

        # Update log tab
        self.update_log()

    def get_entries_from_frame(self, frame):
        entries = {}
        for child in frame.winfo_children():
            if isinstance(child, tk.Entry):
                row = int(child.grid_info()['row'])
                if row > 0:
                    attribute = self.attributes[row-1]
                    entries[attribute] = child
        return entries

    def load_data_for_tab(self, tab_name, entries, output_text):
        filename = f"{tab_name}.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                for attribute, value in data.items():
                    if attribute in entries:
                        entries[attribute].delete(0, tk.END)
                        entries[attribute].insert(0, value)
                output_text.delete(1.0, tk.END)  # Clear the output text box when loading new data

    def save_data_for_tab(self, tab_name, entries):
        filename = f"{tab_name}.json"
        data = {attribute: entries[attribute].get() for attribute in self.attributes if attribute in entries}
        with open(filename, "w") as file:
            json.dump(data, file)

    def ask_success_fail(self):
        # Create a dialog box with Yes and No buttons
        dialog = tk.Toplevel(self.root)
        dialog.title("Success or Failure")

        # Center the dialog relative to the main window
        dialog_width, dialog_height = 200, 100  # Set dimensions for the dialog
        main_window_x = self.root.winfo_x()
        main_window_y = self.root.winfo_y()
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()

        # Calculate position
        dialog_x = main_window_x + (main_window_width // 2) - (dialog_width // 2)
        dialog_y = main_window_y + (main_window_height // 2) - (dialog_height // 2)

        dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")

        label = tk.Label(dialog, text="Did it succeed?", bg="white", fg="#470701")
        label.pack(pady=10)

        success = tk.BooleanVar(value=False)

        yes_button = tk.Button(dialog, text="Yes", command=lambda: [success.set(True), dialog.destroy()], bg="#470701", fg="white", borderwidth=0)
        yes_button.pack(side=tk.LEFT, padx=10, pady=10)

        no_button = tk.Button(dialog, text="No", command=lambda: [success.set(False), dialog.destroy()], bg="#470701", fg="white", borderwidth=0)
        no_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Wait for the dialog to close
        dialog.grab_set()
        dialog.wait_window()

        # Return True if Yes was clicked, otherwise False
        return success.get()

    def update_log(self):
        self.log_text.delete(1.0, tk.END)
        for log in self.logs:
            self.log_text.insert(tk.END, log + "\n")

    def on_closing(self):
        # Save data for all tabs
        for tab in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab)
            tab_name = self.notebook.tab(tab_frame, "text")
            entries = self.get_entries_from_frame(tab_frame)
            self.save_data_for_tab(tab_name, entries)
        self.root.destroy()

class Tooltip:
    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text_func(), background="white", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceRollerApp(root)
    root.mainloop()
