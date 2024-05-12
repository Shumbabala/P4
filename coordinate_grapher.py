import numpy as np
import matplotlib.pyplot as plt

# Define file names
file_names = ["lp_2_3.txt", "lpcc_2_3.txt", "mfcc_2_3.txt"]

# Define plot titles
plot_titles = ["Linear Prediction Coefficients",
               "Linear Prediction Cepstrum Coefficients",
               "Mel Frequency Cepstrum Coefficients"]

# Define x and y axis labels
x_label = "Coefficient #4"
y_label = "Coefficient #5"

# Define colors for scatter plots
colors = ['blue', 'green', 'red']

# Initialize figure and axes
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

# Iterate over files
for i, file_name in enumerate(file_names):
    # Read data from file
    data = np.loadtxt(file_name)
    # Extract columns into arrays
    x = data[:, 0]
    y = data[:, 1]
    # Create scatter plot
    axes[i].scatter(x, y, color=colors[i], label=plot_titles[i])
    # Set axis labels and title
    axes[i].set_xlabel(x_label)
    axes[i].set_ylabel(y_label)
    axes[i].set_title(plot_titles[i])

# Add legend
axes[0].legend()

# Show plot
plt.tight_layout()
plt.show()
