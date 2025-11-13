#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Make water size distribution tables from vectorized maps.

"""

# Import packages
import numpy as np
import glob
import pandas as pd
import geopandas as gpd

# Define user 
user = 'jr555'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/'

# Define AOI
aoi = 'aoi1'

# Define shapefiles
shapefiles = sorted(glob.glob(path1 + 'skysat/data/' + aoi + '/water-polygons/*.shp'))

# Import data
df = pd.read_csv(path1 + '/skysat/data/' + aoi + '/total-area.csv', 
                         index_col=['date'], parse_dates=['date'])

#%%

water_area = []
area_small, area_medium, area_large, area_xlarge = [], [], [], []
for file in shapefiles:
    gdf = gpd.read_file(file)
    water_area.append(gdf['area'].sum())
    area_small.append(gdf[gdf['area'] < 15000]['area'].sum())
    area_medium.append(gdf[(gdf['area'] > 15000) & (gdf['area'] < 50000)]['area'].sum())
    area_large.append(gdf[(gdf['area'] > 50000) & (gdf['area'] < 150000)]['area'].sum())
    area_xlarge.append(gdf[gdf['area'] > 150000]['area'].sum())
    
# Define total
df['water_area'] = water_area
df['small'] = area_small
df['medium'] = area_medium
df['large'] = area_large
df['xlarge'] = area_xlarge

df = df.replace(0, np.nan)
df['water_fraction'] = df['water_area'] / df['total_area']
df = df[~np.isnan(df['total_area'])]

#%%
df.to_csv(path1 + '/skysat/data/' + aoi + '/water-stats.csv',)




