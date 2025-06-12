#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Analyze data.

"""

# Import packages
import rasterio
from rasterio.mask import mask
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from scipy.integrate import simpson
import matplotlib
import glob
import os
import pandas as pd
import geopandas as gpd

# Define user 
user = 'johnnyryan'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'

# Define AOI
aoi = 'aoi1'

# Define files
files = sorted(glob.glob(path1 + 'data/ ' + aoi + '/apply/' + '*.tif'))

# Area of study site
site = gpd.read_file(path1 + 'data/' + 'shapefiles/aoi1-focused.shp')

#%%

# Loop over every GeoTIFF
x_vals_list, y_vals_list, total_area, water_area, date_list = [], [], [], [], []
area_list = []

for file in files:
    print(file)
    
    # Read
    src = rasterio.open(file)
    
    # Clip with shapefile
    clf, out_transform = mask(src, site.geometry.values, crop=True)

    # Size distribution
    binary_water_mask = (clf == 2).astype(int)
    labeled = label(binary_water_mask)
    
    if labeled.max() > 0:
        props = regionprops(labeled)
        areas = [prop.area for prop in props]
        log_areas = np.log10(areas)
        kde = gaussian_kde(log_areas)
        
        # Define log-space x values for evaluation
        log_x_vals = np.linspace(np.log10(np.min(areas)), np.log10(np.max(areas)), 200)
        x_vals_list.append(10 ** log_x_vals)
        y_vals_list.append(kde(log_x_vals))
        date_list.append(pd.to_datetime(os.path.basename(file)[0:8], format='%Y%m%d'))
        total_area.append((clf > 0).sum())
        water_area.append(np.sum(binary_water_mask))
        area_list.append(areas)
    else:
        pass

#%%
# Make DataFrame
df = pd.DataFrame(list(zip(date_list, total_area, water_area)), 
                  columns=['date','total_area', 'water_area'])

df['area_fraction'] = df['total_area'] / site.area.values[0]
df['water_fraction'] = df['water_area'] / df['total_area']

#%%

"""
Stats to describe distribution of water on Jun 13

"""

array = np.array(area_list[1])

min_area = 0
max_area = 100

# Total water
total_water = np.sum(array)

# Filter water in the desired area range
mask = (array >= min_area) & (array <= max_area)

# Area of water in this range
total_area = np.sum(array[mask])

# Number of blobs in that range
num_blobs = np.count_nonzero(mask)

# Fraction
fraction = (total_area / np.sum(array))*100

print(f"Area of water between {min_area} and {max_area} m²: {total_area:.2f} m²")
print(f"Number of water bodies in that range: {num_blobs}")
print(f"Fraction of water relaitve to total: {fraction:.2f} %")





#%%




# Convert to numpy arrays
x_vals = np.array(x_vals_list)
y_vals = np.array(y_vals_list)

# Compute mean and std
x_mean = x_vals.mean(axis=0)
y_mean = y_vals.mean(axis=0)
y_std = y_vals.std(axis=0)

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

ax1.plot(x_mean, y_mean, color=c2)
ax1.fill_between(x_mean, y_mean - y_std, y_mean + y_std, color=c2, alpha=0.3)
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
ax1.set_ylim(0, 0.8)

plt.savefig(path1 + 'figures/' + 'figX-mean-area-distribution.png', dpi=300)

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


min_area = 1
max_area = 10000

log_x = np.linspace(np.log10(min_area), np.log10(max_area), 1000)
pdf_vals = kde(log_x)
area_under_curve = simpson(y=pdf_vals, x=log_x)
estimated_count = area_under_curve * len(areas)

# Filter actual blobs in the desired area range
mask = (np.array(areas) >= min_area) & (np.array(areas) <= max_area)

# Total area of those blobs
total_area = np.sum(np.array(areas)[mask])

# Number of blobs in that range
num_blobs = np.count_nonzero(mask)

# Fraction
fraction = (total_area / np.sum(np.array(areas)))*100

print(f"Area of water between {min_area} and {max_area} m²: {total_area:.2f} m²")
print(f"Number of water bodies in that range: {num_blobs}")
print(f"Fraction of water relaitve to total: {fraction:.2f} %")

print(f"Estimated number of water borides between {min_area} and {max_area} m²: {estimated_count:.1f}")




#%%



