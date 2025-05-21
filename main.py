import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
import random
import json
import os
import math
import sys

if sys.platform == "win32":
    import winaccent

class DiceRollerApp:
    
    def __init__(self, root):
        self.root = root
        super(DiceRollerApp, self).__init__()
        self.root.title("DS TTRPG Helper")

        # Set window size and icon
        self.root.geometry("520x560")
        self.root.iconbitmap("icon.ico")  # Add your app icon here

        # Define attributes
        self.attributes = ["Strength", "Technique", "Constitution", "Charisma", "Instinct", "Celerity"]

        self.background_color = "#2E2E2E"
        self.background_variation_color = "#525252"

        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.background_color)
        main_frame.pack(fill="both", expand=True)

        # Add buttons for new roller, load, and save
        button_frame = tk.Frame(main_frame, bg=self.background_color)
        button_frame.pack(pady=10, side=tk.TOP, anchor=tk.W)

        new_roller_button = tk.Button(button_frame, text="New Roller", command=self.add_roller_tab, bg=self.background_variation_color, fg="white", borderwidth=0)
        new_roller_button.pack(side=tk.LEFT, padx=5)

        load_button = tk.Button(button_frame, text="Load", command=self.load_save, bg=self.background_variation_color, fg="white", borderwidth=0)
        load_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(button_frame, text="Save", command=self.save_current_tab, bg=self.background_variation_color, fg="white", borderwidth=0)
        save_button.pack(side=tk.LEFT, padx=5)

        close_tab_button = tk.Button(button_frame, text="Close Roller", command=self.close_current_tab, bg=self.background_variation_color, fg="white", borderwidth=0)
        close_tab_button.pack(side=tk.LEFT, padx=5)

        noteStyle = ttk.Style()
        noteStyle.theme_use('default')
        noteStyle.configure("TNotebook", background=self.background_color, borderwidth=0)
        noteStyle.configure("TNotebook.Tab", background=self.background_variation_color, borderwidth=0)
        noteStyle.map("TNotebook", background=[("selected", self.background_variation_color)])

        # Set up notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Log frame
        self.log_frame = tk.Frame(self.notebook, bg=self.background_variation_color)
        self.notebook.add(self.log_frame, text="Log")

        self.logs = []

        # Log display
        self.log_text = tk.Text(self.log_frame, height=20, width=60, bg=self.background_color, fg="white", borderwidth=0)
        self.log_text.pack(pady=10, fill="both", expand=True)

        # Notes frame
        self.notes_frame = tk.Frame(self.notebook, bg=self.background_variation_color)
        self.notebook.add(self.notes_frame, text="Notes")

        # Notes display
        self.notes_text = tk.Text(self.notes_frame, height=20, width=60, bg=self.background_color, fg="white", borderwidth=0)
        self.notes_text.pack(pady=10, fill="both", expand=True)

        # Handle app close event to save inputs
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_roller_tab(self):
        tab_frame = tk.Frame(self.notebook, bg=self.background_variation_color)
        tab_frame.pack(fill="both", expand=True)

        # Default tab name
        tab_name = tk.StringVar(value="Roller")
        
        # Name entry field
        name_label = tk.Label(tab_frame, text="Name:", bg=self.background_color, fg="white")
        name_label.grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(tab_frame, textvariable=tab_name, name="name", bg=self.background_color, fg="white")
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Input fields and roll buttons
        entries = {}

        for i, attribute in enumerate(self.attributes):
            label = tk.Label(tab_frame, text=attribute, bg=self.background_color, fg="white")
            label.grid(row=i+1, column=0, padx=10, pady=5)

            entry = tk.Entry(tab_frame, bg=self.background_color, fg="white")
            entry.grid(row=i+1, column=1, padx=10, pady=5)
            entries[attribute] = entry

            roll_button = tk.Button(tab_frame, text="Roll", command=lambda attr=attribute: self.roll_dice(attr, entries, tab_name.get()), bg=self.background_color, fg="white", borderwidth=0)
            roll_button.grid(row=i+1, column=2, padx=10, pady=5)

            # Tooltip setup for the label
            def get_tooltip_text(entry=entry):
                try:
                    value = int(entry.get())
                except ValueError:
                    value = 0
                return self.create_tooltip_text(value)

            Tooltip(label, get_tooltip_text, self.background_color, self.background_variation_color)

        # Output text box
        output_text = tk.Text(tab_frame, height=10, width=50, bg="white", fg="black", borderwidth=0)
        output_text.grid(row=len(self.attributes)+1, column=0, columnspan=3, padx=10, pady=10)

        # Add the new tab to the left of the Log tab
        index = self.notebook.index("end") - 2
        self.notebook.insert(index, tab_frame, text=tab_name.get())
        self.notebook.select(tab_frame)

        # Bind name entry field update to load data
        name_entry.bind("<FocusOut>", lambda event: self.update_tab_name(tab_frame, tab_name.get()))

    def update_tab_name(self, tab_frame, new_name):
        # Update tab name
        index = self.notebook.index(tab_frame)
        self.notebook.tab(tab_frame, text=new_name)

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

        num_rolls = simpledialog.askinteger("Input", f"How many rolls for {attribute}?", parent=self.root)
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

        self.logs.append(result_str)

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

    def load_save(self):
        # Ensure the parent window is correctly referenced
        if not hasattr(self, 'root'):
            raise AttributeError("The application instance must have a 'root' attribute referencing the Tk window.")

        # Create a new window for file selection
        selection_window = tk.Toplevel(self.root)  # Use self.root or the correct attribute referencing your main window
        selection_window.title("Load Save")
        selection_window.geometry("300x150")

        # Label for the dropdown
        label = tk.Label(selection_window, text="Select a save file:")
        label.pack(pady=5)

        # Create a dropdown (Combobox)
        save_files = [f for f in os.listdir('.') if f.endswith('.json')]
        if not save_files:
            messagebox.showinfo("Load Save", "No save files found.")
            selection_window.destroy()
            return

        combobox = ttk.Combobox(selection_window, values=save_files)
        combobox.pack(pady=5)
        combobox.set("Select a file")

        # Function to load the selected file
        def confirm_selection():
            selected_file = combobox.get()
            if selected_file and selected_file in save_files:
                tab_name = selected_file.replace('.json', '')
                self.add_roller_tab()
                new_tab = self.notebook.nametowidget(self.notebook.select())
                entries = self.get_entries_from_frame(new_tab)
                output_text = [widget for widget in new_tab.winfo_children() if isinstance(widget, tk.Text)][0]
                self.load_data_for_tab(tab_name, entries, output_text)
                selection_window.destroy()
            else:
                messagebox.showwarning("Load Save", "Please select a valid save file.")

        # Button to confirm selection
        confirm_button = tk.Button(selection_window, text="Load", command=confirm_selection)
        confirm_button.pack(pady=5)

        # Make the window modal
        selection_window.transient(self.root)  # Use self.root for modality
        selection_window.grab_set()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        win_x = root_x + 100
        win_y = root_y + 150
        selection_window.geometry(f'+{win_x}+{win_y}')
         # Wait for the window to be closed before proceeding
        selection_window.wait_window()  # Call wait_window on the selection_window, not self

    def save_current_tab(self):
        tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(tab)
        tab_name = self.notebook.tab(tab_frame, "text")
        entries = self.get_entries_from_frame(tab_frame)
        self.save_data_for_tab(tab_name, entries)

    def close_current_tab(self):
        self.save_current_tab()
        tab = self.notebook.select()
        tab_frame = self.notebook.nametowidget(tab)
        tab_name = self.notebook.tab(tab_frame, "text")
        for item in self.notebook.winfo_children():
            if str(item) == (tab) and tab_name != "Log" and tab_name != "Notes":
                item.destroy()
                return  #Necessary to break or for loop can destroy all the tabs when first tab is deleted

    def load_data_for_tab(self, tab_name, entries, output_text):
        filename = f"{tab_name}.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                tab = self.notebook.select()
                tab_frame = self.notebook.nametowidget(tab)
                self.update_tab_name(tab_frame, tab_name)
                tab_frame.nametowidget("name").delete(0, tk.END)
                tab_frame.nametowidget("name").insert(0, tab_name)
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

    def update_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "\n".join(self.logs))

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?", parent = self.root):
            self.save_all_tabs()
            self.root.destroy()

    def save_all_tabs(self):
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            tab_name = self.notebook.tab(tab_frame, "text")
            if tab_name != "Log" and tab_name != "Notes":
                entries = self.get_entries_from_frame(tab_frame)
                self.save_data_for_tab(tab_name, entries)

class Tooltip:
    def __init__(self, widget, text_function, background_color, background_color_variation):
        self.widget = widget
        self.background_color = background_color
        self.background_color_variation = background_color_variation
        self.text_function = text_function
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.geometry(f"+{x}+{y}")
        self.tooltip_window.config(bg=self.background_color)

        tooltip_label = tk.Label(self.tooltip_window, text=self.text_function(), bg=self.background_color, fg="white", justify="left", relief="solid", borderwidth=1)
        tooltip_label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceRollerApp(root)
    root.mainloop()
