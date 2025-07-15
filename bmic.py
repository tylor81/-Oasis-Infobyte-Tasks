import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# Constants
DATA_FILE = "bmi_data.json"
BMI_CATEGORIES = [
    (0, 18.5, "Underweight"),
    (18.5, 24.9, "Normal weight"),
    (25, 29.9, "Overweight"),
    (30, 100, "Obese")
]

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

def classify_bmi(bmi):
    for lower, upper, category in BMI_CATEGORIES:
        if lower <= bmi <= upper:
            return category
    return "Unknown"

class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")
        self.data = load_data()
        self.create_widgets()

    def create_widgets(self):
        # User name
        tk.Label(self.root, text="User Name:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1)

        # Weight input
        tk.Label(self.root, text="Weight (kg):").grid(row=1, column=0, padx=5, pady=5)
        self.weight_entry = tk.Entry(self.root)
        self.weight_entry.grid(row=1, column=1)

        # Height input and unit
        tk.Label(self.root, text="Height:").grid(row=2, column=0, padx=5, pady=5)
        self.height_entry = tk.Entry(self.root)
        self.height_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Unit:").grid(row=2, column=2, padx=5, pady=5)
        self.height_unit = ttk.Combobox(self.root, values=["m", "cm", "ft", "in"], state="readonly")
        self.height_unit.set("m")  # default
        self.height_unit.grid(row=2, column=3)

        # Calculate Button
        tk.Button(self.root, text="Calculate BMI", command=self.calculate_bmi).grid(row=3, column=0, columnspan=4, pady=10)

        # Result display
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.grid(row=4, column=0, columnspan=4)

        # View history button
        tk.Button(self.root, text="View History", command=self.view_history).grid(row=5, column=0, pady=10)
        tk.Button(self.root, text="Show Trend", command=self.show_trend).grid(row=5, column=1, pady=10)

        # File handling buttons
        tk.Button(self.root, text="Export Data", command=self.export_data).grid(row=6, column=0, pady=10)
        tk.Button(self.root, text="Import Data", command=self.import_data).grid(row=6, column=1, pady=10)

    def calculate_bmi(self):
        try:
            username = self.username_entry.get().strip()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            unit = self.height_unit.get()

            if not username:
                raise ValueError("User name is required.")
            if not (30 <= weight <= 300):
                raise ValueError("Weight out of range (30-300 kg).")

            # Convert height to meters
            if unit == "cm":
                height /= 100
            elif unit == "ft":
                height *= 0.3048
            elif unit == "in":
                height *= 0.0254
            elif unit != "m":
                raise ValueError("Invalid height unit selected.")

            if not (1.0 <= height <= 2.5):
                raise ValueError("Height out of range (1.0-2.5 m after conversion).")

            bmi = calculate_bmi(weight, height)
            category = classify_bmi(bmi)
            self.result_label.config(text=f"BMI: {bmi} ({category})")

            # Store data
            entry = {"date": datetime.now().isoformat(), "bmi": bmi, "category": category}
            self.data.setdefault(username, []).append(entry)
            save_data(self.data)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def view_history(self):
        username = self.username_entry.get().strip()
        if not username or username not in self.data:
            messagebox.showinfo("No Data", "No data found for this user.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title(f"BMI History for {username}")
        tree = ttk.Treeview(history_window, columns=("Date", "BMI", "Category"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("BMI", text="BMI")
        tree.heading("Category", text="Category")
        tree.pack(fill=tk.BOTH, expand=True)

        for entry in self.data[username]:
            tree.insert("", "end", values=(entry["date"], entry["bmi"], entry["category"]))

    def show_trend(self):
        username = self.username_entry.get().strip()
        if not username or username not in self.data:
            messagebox.showinfo("No Data", "No data found for this user.")
            return

        dates = [datetime.fromisoformat(e["date"]) for e in self.data[username]]
        bmis = [e["bmi"] for e in self.data[username]]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, bmis, marker='o')
        plt.title(f"BMI Trend for {username}")
        plt.xlabel("Date")
        plt.ylabel("BMI")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_data = json.load(f)
                    for user, entries in imported_data.items():
                        self.data.setdefault(user, []).extend(entries)
                save_data(self.data)
                messagebox.showinfo("Import Successful", f"Data imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Import Failed", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
