#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Lake analysis.

NOTE: Removed 2019-08-02 and 2019-06-17 because there were some georeferencing issues.

"""

# Import packages
import rasterio
import xarray as xr
from rasterio.mask import mask
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas as pd
import geopandas as gpd
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

# Define user 
user = 'jr555'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path3 = '/Users/' + user + '/Documents/research/skysat/'

# Define AOI
aoi = 'aoi1'

# Define files
files = sorted(glob.glob(path3 + aoi + '/apply/' + '*.tif'))

# Area of study site
lakes = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/lakes.shp')

# Area of study site
site = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/aoi1-focused.shp')

# MAR runoff
mar = xr.open_dataset(path1 + 'hydrology/data/mar/MARv3.12.1-10km-daily-ERA5-2019.nc')

# Zhang surface water map
z_src = rasterio.open(path1 + '/hydrology/data/zhang/surface_water_mask_2019.tif')

#%%

# Loop over every GeoTIFF
lake_areas, mask_areas = [], []
date_list = []
total_area, water_area = [], []
mean_area, std_area = [], []
area_list = []

for file in files:
    print(file)
    
    # Read
    src = rasterio.open(file)
    
    areas1, areas2 = [], []
    for i in range(lakes.shape[0]):
        
        # Clip with region shapefile
        clf, out_transform = mask(src, [lakes.iloc[i].geometry], crop=True)
        
        # Label
        binary_water_mask = (clf == 2).astype(int)
        labeled = label(binary_water_mask)
        props = regionprops(labeled)
        areas = np.array([prop.area for prop in props])
        
        # Append
        areas1.append(np.sum(areas[areas>15000]).astype(int))
        areas2.append(np.sum(clf > 0).astype(int))
    
    lake_areas.append(areas1)
    mask_areas.append(areas2)
    date_list.append(pd.to_datetime(os.path.basename(file)[0:8], format='%Y%m%d'))
    
    # Clip with region shapefile
    clf, out_transform = mask(src, site.geometry.values, crop=True)
    
    # Size distribution
    binary_water_mask = (clf == 2).astype(int)
    labeled = label(binary_water_mask)
    
    if labeled.max() == 0:
        total_area.append(0)
        water_area.append(0)
        mean_area.append(0)
        std_area.append(0)
        area_list.append(0)
    else:
        props = regionprops(labeled)
        areas = [prop.area for prop in props]
        mean_area.append(np.nanmean(areas))
        std_area.append(np.nanstd(areas))
        total_area.append((clf > 0).sum())
        water_area.append(np.sum(binary_water_mask))
        area_list.append(areas)

# Make DataFrame
df1 = pd.DataFrame(mask_areas)

# Set all non-max values per column to NaN
df_max_only = df1.eq(df1.max())

lake_df = pd.DataFrame(lake_areas)
lake_df = lake_df.replace(0, np.nan)
lake_df = lake_df.where(df_max_only)
lake_df = lake_df / 1000000
lake_df.index = date_list

all_df = pd.DataFrame(list(zip(total_area, water_area)), 
                  columns=['total_area', 'water_area'])
all_df.index = date_list
all_df = all_df.replace(0, np.nan)
all_df['area_fraction'] = all_df['total_area'] / site.area.values[0]
all_df['water_fraction'] = all_df['water_area'] / all_df['total_area']

# Mean areas
area_df = pd.DataFrame(list(zip(mean_area, std_area)), columns=['area', 'std'])

# Compute area of water by threshold
thresholds = [1000, 15000, 45000, 100000]
size_thresholds = []
for a in range(len(area_list)):
    inter_thres = []
    for t in thresholds:
        array = np.array(area_list[a])
        inter_thres.append(np.sum(array[array<t]))
    size_thresholds.append(inter_thres)

all_df[['tiny', 'small', 'medium', 'large']] = size_thresholds

#%%

"""
STATS
"""

jun_mask = all_df.index.month == 6
jun_water_fraction = all_df['water_fraction'][jun_mask].mean()
jun_water_area = (jun_water_fraction * site.area / 1000000).values[0]

jul_mask = all_df.index.month == 7
jul_water_fraction = all_df['water_fraction'][jul_mask].mean()
jul_water_area = (jul_water_fraction * site.area / 1000000).values[0]

aug_mask = all_df.index.month == 8
aug_water_fraction = all_df['water_fraction'][aug_mask].mean()
aug_water_area = (aug_water_fraction * site.area / 1000000).values[0]

print('We find that surface water attained a \
maximum area of %.2f %% of our study site during June' %(jun_water_fraction*100))

print('By July, surface water decreases to \
%.2f %% ' %(jul_water_fraction*100))

print('By August, surface water decreases to \
%.2f %% ' %(aug_water_fraction*100))
      
#%%

jun_mask = lake_df.index.month == 6
jun_lake_means = lake_df[jun_mask].mean()
jun_lake_sum = np.nansum(jun_lake_means)

print('Eleven supraglacial lakes (with areas >0.15 km2) \
account for %.2f %% of the total surface water area in June' % ((jun_lake_sum/jun_water_area)*100))

aug_mask = lake_df.index.month == 8
aug_lake_means = lake_df[aug_mask].mean()
aug_lake_sum = np.nansum(aug_lake_means)

print('Eleven supraglacial lakes (with areas >0.15 km2) \
account for %.2f %% of the total surface water area in August' % ((aug_lake_sum/aug_water_area)*100))


#%%

aug_mask = lake_df.index.month == 8
aug_lake_means = lake_df[aug_mask].mean()
aug_lake_sum = np.nansum(aug_lake_means)

aug_mask = all_df.index.month == 8
aug_water_fraction = all_df['water_fraction'][aug_mask].mean()
aug_water_area = (aug_water_fraction * site.area / 1000000).values[0]

print('Between June and August, the combined area of the eleven supraglacial \
lakes (>0.15 km2) decreased from %.1f km2 to %.1f km2' % (jun_lake_sum, aug_lake_sum))

print('the total surface water area decreased by %.1f km2 in our study \
site' % (jun_water_area-aug_water_area))

print('Large supraglacial lakes therefore account for %.1f %% of the change \
in surface water area' % (((jun_lake_sum-aug_lake_sum)/(jun_water_area-aug_water_area))*100))

#%%

jun_mask = all_df.index.month == 6
jun_water_fraction_small = (all_df['small']/all_df['water_area'])[jun_mask].mean()
jun_water_fraction_medium = (all_df['medium']/all_df['water_area'])[jun_mask].mean()
jun_water_fraction_large = (all_df['large']/all_df['water_area'])[jun_mask].mean()
jun_water_area = (jun_water_fraction_large * jun_water_fraction) * (site.area / 1000000).values[0]

aug_mask = all_df.index.month == 8
aug_water_fraction_tiny = (all_df['tiny']/all_df['water_area'])[aug_mask].mean()
aug_water_fraction_small = (all_df['small']/all_df['water_area'])[aug_mask].mean()
aug_water_fraction_medium = (all_df['medium']/all_df['water_area'])[aug_mask].mean()
aug_water_fraction_large = (all_df['large']/all_df['water_area'])[aug_mask].mean()
aug_water_area = (aug_water_fraction_large * aug_water_fraction) * (site.area / 1000000).values[0]

#%%

"""
Compute water area from Zhang et al. (2023)

"""

# Reproject study site
site_nps = site.to_crs('EPSG:3413')

# Clip with region shapefile
z_clf, out_transform = mask(z_src, site_nps.geometry, crop=True)
z_area = np.sum(z_clf[z_clf == 1])

print('Area of surface water in Zhang et al. (2023) is %.1f %%' %((z_area*100/site.area.iloc[0])*100))

#%%

# Define latitude and longitude of three grid cells for Store Glacier
lat, lon = 68.90, -48.86

def find_idx(lat, lon):
    
    # Compute the Euclidean distance (not accounting for Earth curvature)
    distance = np.sqrt((mar['LAT'].values - lat)**2 + (mar['LON'].values - lon)**2)
    
    # Find the indices of the minimum distance
    idx = np.unravel_index(np.argmin(distance), distance.shape)
    
    return idx

idx = find_idx(lat, lon)

mar_runoff = mar['RU'][:,0, idx[0], idx[1]].values / 1000


#%%

# Reoder columns for plotting
lake_df_plot = lake_df[lake_df.max().sort_values(ascending=False).index]

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Create 3x3 subplots
fig, axes = plt.subplots(3, 3, figsize=(10, 6), layout='constrained', sharex=True)

# Plot with shared y-axis by row and left-only y-axis labels
for row in range(3):
    for col in range(3):
        ax = axes[row, col]
        col_idx = row * 3 + col
        if col_idx >= len(lake_df_plot.columns):
            fig.delaxes(ax)
            continue

        ax.scatter(date_list, lake_df_plot[lake_df_plot.columns[col_idx]])
        ax1 = ax.twinx()
        ax1.plot(mar['TIME'].values, mar_runoff, 
                 color=c1, lw=2, zorder=3)
        
        # Set y-label only on left-most column
        if col == 0:
            ax.set_ylabel("Area (km$^2$)", fontsize=12)  
        else:
            ax.tick_params(labelleft=False)

        if col > 0:
            ax.sharey(axes[row, 0])
            ax.tick_params(labelleft=False)

        if row < 2:
            ax.tick_params(labelbottom=False)
            
        # Use AutoDateLocator for good tick spacing on uneven dates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        # Custom formatter for multiline day/month
        def multiline_date_formatter(x, pos=None):
            dt = mdates.num2date(x)
            return f"{dt.day}\n{dt.strftime('%b')}"

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(multiline_date_formatter))

axes_flat = axes.flatten()
for i, ax in enumerate(axes_flat):
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, which="both", linestyle="--", linewidth=1, zorder=0)
    ax.set_xlim(date_list[0], date_list[-1])

#plt.savefig(path1 + 'figures/' + 'figX-lake-change.png', dpi=300)

plt.show()

#%%

"""
NOTE: Lake 4 drains between Jun 8 and 13 because it establishes a channel into 
Lake 3 causing it to grow massively.

"""

# Plot chained lakes
chained_df = lake_df[[2,5,7,8,9,10,11]]

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Create 3x3 subplots
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 6), 
                                          layout='constrained', sharex=True)

# Plot with shared y-axis by row and left-only y-axis labels
ax1.scatter(date_list, chained_df[11], zorder=1)
ax2.scatter(date_list, chained_df[9], zorder=1)
ax3.scatter(date_list, chained_df[10], zorder=1)
ax4.scatter(date_list, chained_df[2], zorder=1)
ax5.scatter(date_list, chained_df[5], zorder=1)
ax6.scatter(date_list, chained_df[7]+chained_df[8], zorder=1)

ax1.set_ylabel("Area (km$^2$)", fontsize=12)  
ax4.set_ylabel("Area (km$^2$)", fontsize=12)  

for ax in [ax1, ax2, ax3]:
    ax.set_ylim(0, 1.05)
    
for ax in [ax2, ax3, ax5, ax6]:
    ax.set_yticklabels([])

for ax in [ax4, ax5, ax6]:
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.set_ylim(0, 2.2)
    
    # Custom formatter for multiline day/month
    def multiline_date_formatter(x, pos=None):
        dt = mdates.num2date(x)
        return f"{dt.day}\n{dt.strftime('%b')}"
    
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(multiline_date_formatter))

axes_flat = axes.flatten()
for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, which="both", linestyle="--", linewidth=1, zorder=1)
    ax.set_xlim(date_list[0], date_list[-1])

#plt.savefig(path1 + 'figures/' + 'figX-lake-change.png', dpi=300)

plt.show()



#%%

# Plot chained lakes
isolated_df = lake_df[[0,1,3,4,6]]

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Create 3x3 subplots
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 6), 
                                          layout='constrained', sharex=True)

# Plot with shared y-axis by row and left-only y-axis labels
ax1.scatter(date_list, isolated_df[6], zorder=1)
ax2.scatter(date_list, isolated_df[3], zorder=1)
ax3.scatter(date_list, isolated_df[1], zorder=1)
ax4.scatter(date_list, isolated_df[4], zorder=1)
ax5.scatter(date_list, isolated_df[0], zorder=1)

ax1.set_ylabel("Area (km$^2$)", fontsize=12)  
ax4.set_ylabel("Area (km$^2$)", fontsize=12)  

for ax in [ax1, ax2, ax3]:
    ax.set_ylim(0, 2.0)
    
for ax in [ax2, ax3, ax5, ax6]:
    ax.set_yticklabels([])

for ax in [ax4, ax5, ax6]:
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.set_ylim(0, 1.0)
    
    # Custom formatter for multiline day/month
    def multiline_date_formatter(x, pos=None):
        dt = mdates.num2date(x)
        return f"{dt.day}\n{dt.strftime('%b')}"
    
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(multiline_date_formatter))

axes_flat = axes.flatten()
for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, which="both", linestyle="--", linewidth=1, zorder=1)
    ax.set_xlim(date_list[0], date_list[-1])

#plt.savefig(path1 + 'figures/' + 'figX-lake-change.png', dpi=300)

plt.show()




















