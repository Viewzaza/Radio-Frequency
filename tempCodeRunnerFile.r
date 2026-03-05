import matplotlib.pyplot as plt

# Quarters from 2015 Q1 to 2025 Q4
quarters = [
    "15 Q1", "15 Q2", "15 Q3", "15 Q4", "16 Q1", "16 Q2", "16 Q3", "16 Q4",
    "17 Q1", "17 Q2", "17 Q3", "17 Q4", "18 Q1", "18 Q2", "18 Q3", "18 Q4",
    "19 Q1", "19 Q2", "19 Q3", "19 Q4", "20 Q1", "20 Q2", "20 Q3", "20 Q4",
    "21 Q1", "21 Q2", "21 Q3", "21 Q4", "22 Q1", "22 Q2", "22 Q3", "22 Q4",
    "23 Q1", "23 Q2", "23 Q3", "23 Q4", "24 Q1", "24 Q2", "24 Q3", "24 Q4",
    "25 Q1", "25 Q2", "25 Q3", "25 Q4"
]

# Quarterly Revenue data in Billions (USD)
nvidia_revenue = [1.15, 1.15, 1.31, 1.40, 1.31, 1.43, 2.00, 2.17, 1.94, 2.23, 2.64, 2.91, 3.21, 3.12, 3.18, 2.21, 2.22, 2.58, 3.01, 3.11, 3.08, 3.87, 4.73, 5.00, 5.66, 6.51, 7.10, 7.64, 8.29, 6.70, 5.93, 6.05, 7.19, 13.51, 18.12, 22.10, 26.04, 30.00, 35.08, 39.33, 44.06, 46.74, 57.01, 68.13]
intel_revenue = [12.78, 13.20, 14.47, 14.91, 13.70, 13.50, 15.80, 16.40, 14.80, 14.80, 16.10, 17.10, 16.10, 17.00, 19.20, 18.60, 16.10, 16.50, 19.20, 20.20, 19.80, 19.70, 18.30, 20.00, 19.70, 19.60, 19.20, 20.50, 18.40, 15.30, 15.30, 14.00, 11.70, 12.90, 14.20, 15.40, 12.70, 12.80, 13.28, 14.26, 12.67, 12.86, 13.65, 13.67]
amd_revenue = [1.03, 0.94, 1.06, 0.96, 0.83, 1.03, 1.31, 1.15, 1.18, 1.15, 1.58, 1.34, 1.65, 1.76, 1.65, 1.42, 1.27, 1.53, 1.80, 2.13, 1.79, 1.93, 2.80, 3.24, 3.45, 3.85, 4.31, 4.83, 5.89, 6.55, 5.57, 5.60, 5.35, 5.36, 5.80, 6.17, 5.47, 5.80, 6.86, 7.66, 7.44, 7.69, 9.25, 10.27]

# Set up the plot
plt.figure(figsize=(14, 7))

# Plot the lines for each company
plt.plot(quarters, nvidia_revenue, label='Nvidia', color='#76B900', linewidth=2.5, marker='o', markersize=4)
plt.plot(quarters, intel_revenue, label='Intel', color='#0068B5', linewidth=2.5, marker='o', markersize=4)
plt.plot(quarters, amd_revenue, label='AMD', color='#ED1C24', linewidth=2.5, marker='o', markersize=4)

# Add titles and labels
plt.title('Quarterly Revenue: Nvidia vs Intel vs AMD (2015 - 2025)', fontsize=16, fontweight='bold')
plt.xlabel('Quarter', fontsize=12)
plt.ylabel('Revenue (Billions USD)', fontsize=12)

# Formatting
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=12, loc='upper left')
plt.tight_layout()

# Display the graph
plt.show()