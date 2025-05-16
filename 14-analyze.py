#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Analyze data.

"""

# Import packages
import xarray as xr
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from scipy.integrate import simpson
import matplotlib

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'

# Define file
data = xr.open_dataset(path1 + 'aoi2/apply/aoi2.nc')

# Make mask showing counts
count = (data != 0).sum(dim="time")

#%%
    
x_vals_list, y_vals_list, date_list = [], [], []

for i in range(data['water_fraction'].shape[2]):
       
    # Size distribution
    binary_water_mask = (data['water_fraction'][:,:,i] == 2).values.astype(int)
    labeled = label(binary_water_mask)
    
    if labeled.max() > 0:
        props = regionprops(labeled)
        areas = [prop.area for prop in props]
        
        
        # Assume `areas` is already defined
        log_areas = np.log10(areas)
        
        # Perform KDE in log-space
        kde = gaussian_kde(log_areas)
        
        # Define log-space x values for evaluation
        log_x_vals = np.linspace(np.log10(np.min(areas)), np.log10(np.max(areas)), 200)
        x_vals_list.append(10 ** log_x_vals)
        y_vals_list.append(kde(log_x_vals))
        date_list.append(data['water_fraction'][:,:,i]['time'].values)
    else:
        pass

#%%

# Use a sequential colormap
cmap = matplotlib.colormaps['Blues']  # Or 'Purples', 'Oranges', etc.
colors = cmap(np.linspace(0.3, 1.0, len(x_vals_list)))  # Avoid very light tones

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Plot
fig, ax1 = plt.subplots(figsize=(6, 4), layout='constrained')

for j, (x_vals, y_vals) in enumerate(zip(x_vals_list, y_vals_list)):
    ax1.plot(x_vals_list[j], y_vals_list[j], color=colors[j], lw=2)

ax1.axvline(x=100, ls='dashed', lw=1.5, color='k')
ax1.axvline(x=1000, ls='dashed', lw=1.5, color='k')

ax1.set_xscale("log")
#ax1.set_yscale("log")
ax1.set_xlabel("Area (m$^2$)", fontsize=12)
ax1.set_ylabel("Density", fontsize=12)
#ax1.legend(fontsize=11)
ax1.grid(True, which="both", linestyle="--", linewidth=0.5, zorder=0)
ax1.tick_params(axis='both', which='major', labelsize=12)
ax1.set_xlim(1.2, 10000)
ax1.set_ylim(0, 0.9)


#%%


min_area = 100
max_area = 1000

log_x = np.linspace(np.log10(min_area), np.log10(max_area), 1000)
pdf_vals = kde(log_x)
area_under_curve = simpson(y=pdf_vals, x=log_x)
estimated_count = area_under_curve * len(areas)

# Filter actual blobs in the desired area range
mask = (np.array(areas) >= 100) & (np.array(areas) <= 1000)

# Total area of those blobs
total_area = np.sum(np.array(areas)[mask])

# Number of blobs in that range
num_blobs = np.count_nonzero(mask)

print(f"Total area of blobs between 100 and 1000 m²: {total_area:.2f} m²")
print(f"Number of blobs in that range: {num_blobs}")
print(f"Estimated number of blobs between {min_area} and {max_area} m²: {estimated_count:.1f}")




#%%



