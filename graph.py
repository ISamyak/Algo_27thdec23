import csv
import matplotlib.pyplot as plt
import tkinter as tk
import datetime

# Load the CSV data
x_data = []
y_data = []
with open('./Nirmal_Fincap/Nifty/banknifty.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row

    i=0
    for row in reader:
        x_data.append((i))
        y_data.append(float(row[3]))
        i=i+1

# Create the bar graph
plt.plot(x_data, y_data)
plt.xlabel('time')
plt.ylabel('price')
plt.title('Test')


# Create the GUI window
root = tk.Tk()
root.title('Bar Graph with Zoom')

# Create the zoom in/out buttons or sliders
# Implement the zoom in/out functionality using the "plt.xlim()" and "plt.ylim()" functions

# Display the graph in the GUI window
canvas = plt.gcf().canvas
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Run the GUI
tk.mainloop()
