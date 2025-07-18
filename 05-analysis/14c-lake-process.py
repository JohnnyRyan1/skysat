#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Lake analysis.

NOTE: Removed 2019-08-02 and 2019-06-17 because there were some georeferencing issues.

"""

# Import packages
import rasterio
from rasterio.mask import mask
from skimage.measure import label, regionprops
import numpy as np
import glob
import os
import pandas as pd
import geopandas as gpd

# Define user 
user = 'jr555'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path3 = '/Users/' + user + '/Documents/research/skysat/'
path4 = '/Volumes/EXTERNAL_USB/skysat/'

# Define AOI
aoi = 'aoi1'

# Define files
files = sorted(glob.glob(path3 + aoi + '/apply/' + '*.tif'))

# Area of study site
lakes = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/lakes.shp')
lakes = lakes.sort_values(by='id')

# Area of study site
site = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/aoi1-focused.shp')

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
    
    # Total size distribution
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
lake_df.columns = lakes['id']
lake_df.rename(columns={i: f'lake{i}' for i in range(1, 13)}, inplace=True)


all_df = pd.DataFrame(list(zip(total_area, water_area)), 
                  columns=['total_area', 'water_area'])
all_df.index = date_list
all_df = all_df.replace(0, np.nan)
all_df['area_fraction'] = all_df['total_area'] / site.area.values[0]
all_df['water_fraction'] = all_df['water_area'] / all_df['total_area']

# Mean areas
area_df = pd.DataFrame(list(zip(mean_area, std_area)), columns=['area', 'std'])
area_df = area_df[area_df['area'] > 0]

# Compute area of water by threshold
thresholds = [0, 1000, 50000, 150000]
size_thresholds = []
for a in range(len(area_list)):
    inter_thres = []
    for t in range(len(thresholds) - 1):
        array = np.array(area_list[a])
        inter_thres.append(np.sum(array[(array>thresholds[t]) & (array<thresholds[t+1])]))
    size_thresholds.append(inter_thres)

all_df[['small', 'medium', 'large']] = size_thresholds

all_df = all_df[~np.isnan(all_df['total_area'])]

#%%

# Save as csv
all_df.to_csv(path1 + 'skysat/data/' + aoi + '/water-stats.csv')
lake_df.to_csv(path1 + 'skysat/data/' + aoi + '/lake-stats.csv')


#%%

















