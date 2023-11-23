import csv
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor
from heapq import nlargest

# Function to generate battery configurations
def generate_configurations():
    # Function to process CSV files
    def process_csv(file_path):
        if not file_path:  # Check if file_path is empty
            return  # Skip processing empty file paths
        
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                thickness = float(row['Thickness'])
                if from_thickness <= thickness <= to_thickness:
                    total_capacity = int(float(row['Capacity']) * (
                        (max_width_allowed // float(row['Width']))
                        * (max_length_allowed // float(row['Length']))
                        * (to_thickness // thickness)
                    ))
                    size = f"{int(float(row['Width']))}x{int(float(row['Length']))}x{int(thickness)}"
                    stacks = f"{int(max_width_allowed // float(row['Width']))}x{int(max_length_allowed // float(row['Length']))}x{int(to_thickness // thickness)}"
                    
                    individual_thickness = int(thickness * (to_thickness // thickness))
                    volume = float(row['Width']) * float(row['Length']) * thickness
                    energy_density = float(row['Capacity']) / volume
                    
                    yield {
                        'Product': row['Product'],
                        'Total Capacity': total_capacity,
                        'Individual Capacity': int(float(row['Capacity'])),
                        'Size': size,
                        'Stacks': stacks,
                        'Config Thickness': individual_thickness,
                        'Energy Density (Wh/cm³)': round(energy_density, 2)
                    }
    
    # Function to get battery configurations using ThreadPoolExecutor
    def get_battery_configurations():
        with ThreadPoolExecutor() as executor:
            for result in executor.map(process_csv, [file_path for file_path in csv_files if file_path]):
                yield from result
    
    # Get parameters from user inputs
    max_width_allowed = int(max_width_entry.get())
    max_length_allowed = int(max_length_entry.get())
    from_thickness = int(from_thickness_entry.get())
    to_thickness = int(to_thickness_entry.get())
    
    # Get CSV file paths from the text widget
    csv_files = file_list.get("1.0", tk.END).strip().split('\n')
    
    # Find top configurations based on a criterion
    num_configurations = int(num_configurations_entry.get())
    top_configurations = nlargest(
        num_configurations,
        get_battery_configurations(),
        key=lambda battery: battery['Total Capacity'] * battery['Energy Density (Wh/cm³)']
    )
    
    # Output CSV file
    output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    
    # Check if a file path was provided for saving
    if output_file:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Product', 'Total Capacity', 'Individual Capacity', 'Size', 'Stacks', 'Config Thickness', 'Energy Density (Wh/cm³)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for idx, config in enumerate(top_configurations, start=1):
                writer.writerow(config)
    else:
        print("No file selected for saving.")

# Function to browse files
def browse_files():
    files = filedialog.askopenfilenames()
    file_list.delete(1.0, tk.END)
    file_list.insert(tk.END, '\n'.join(files))

# Function to create labels and entries within the input frame
def create_entry(input_frame, label_text):
    label = ttk.Label(input_frame, text=label_text)
    label.pack(side='top', pady=(5, 2))
    entry = ttk.Entry(input_frame)
    entry.pack(side='top', fill='x', padx=5, pady=(0, 5))
    return entry

# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Battery Configuration Generator")

    # Set the theme to 'clam' and configure a modern theme
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', foreground='#333', background='#f0f0f0', font=('Arial', 10))
    style.configure('TButton', foreground='#fff', background='#333', font=('Arial', 10))
    style.configure('TEntry', fieldbackground='#f0f0f0', foreground='#333', font=('Arial', 10))

    # Create a frame for inputs
    input_frame = ttk.Frame(root)
    input_frame.pack(padx=20, pady=20)

    # GUI elements
    global max_width_entry, max_length_entry, from_thickness_entry, to_thickness_entry, num_configurations_entry, file_list
    max_width_entry = create_entry(input_frame, "Max Width Allowed:")
    max_length_entry = create_entry(input_frame, "Max Length Allowed:")
    from_thickness_entry = create_entry(input_frame, "From Thickness:")
    to_thickness_entry = create_entry(input_frame, "To Thickness:")
    num_configurations_entry = create_entry(input_frame, "Number of Configurations:")

    # Create a frame for the file list and buttons
    file_frame = ttk.Frame(root)
    file_frame.pack(padx=20, pady=(10, 0), anchor='center')

    file_list_label = ttk.Label(file_frame, text="Select CSV files:")
    file_list_label.pack(side='top', anchor='w', padx=10, pady=(10, 5))

    file_list = tk.Text(file_frame, height=4, width=40)
    file_list.pack(fill='both', padx=10)

    button_frame = ttk.Frame(root)
    button_frame.pack(pady=(10, 20), anchor='center')

    browse_button = ttk.Button(button_frame, text="Browse", command=browse_files)
    browse_button.pack(side='left', padx=10)

    generate_button = ttk.Button(button_frame, text="Generate Configurations", command=generate_configurations)
    generate_button.pack(side='right', padx=10)

    root.mainloop()

# Create GUI
create_gui()
