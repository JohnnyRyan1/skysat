#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Lake analysis for S2

"""

# Import packages
import rasterio
from skimage.measure import label, regionprops
from rasterio.mask import mask
import numpy as np
import pandas as pd
import geopandas as gpd
import glob
import os

# Define user
user = 'jr555'

# Define AOI
aoi = 'aoi1'

# Define paths
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/s2/'+ aoi + '/'

# Define files
files = sorted(glob.glob(path2 + '*_NDWI.tif'))

# Area of study site
lakes = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/lakes.shp')
lakes = lakes.sort_values(by='id')

#%%

# Loop over every GeoTIFF
lake_areas, mask_areas = [], []
date_list = []

for file in files:
    print(file)
    
    # Read
    src = rasterio.open(file)
    
    areas1, areas2 = [], []
    for i in range(lakes.shape[0]):
        
        # Clip with region shapefile
        clf, out_transform = mask(src, [lakes.iloc[i].geometry], crop=True)
        
        # Label
        binary_water_mask = (clf > 0.2).astype(int)
        
        labeled = label(binary_water_mask)
        props = regionprops(labeled)
        areas = np.array([prop.area for prop in props])
        
        # Append
        areas1.append(np.sum(areas[areas>150]).astype(int))
        areas2.append(np.sum(clf > 0).astype(int))
    
    lake_areas.append(areas1)
    mask_areas.append(areas2)
    date_list.append(pd.to_datetime(os.path.basename(file)[7:15], format='%Y%m%d'))

# Append to DataFrame
lake_df = pd.DataFrame(lake_areas)
lake_df = lake_df.replace(0, np.nan)
lake_df = lake_df / 10000
lake_df.index = date_list
lake_df.columns = lakes['id']
lake_df.rename(columns={i: f'lake{i}' for i in range(1, 13)}, inplace=True)
lake_df.to_csv(path1 + 'skysat/data/' + aoi + '/lake-stats-s2.csv')


#%%









