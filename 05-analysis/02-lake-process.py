#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Lake analysis.

NOTE: Removed 2019-08-02, 2019-06-17, 2019-05-24 because there were some georeferencing issues.

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
import xarray as xr
from geocube.vector import vectorize

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
files = sorted(glob.glob(path3 + aoi + '/clipped/' + '*.tif'))

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
    
    # Get the path and filename separately
    infilepath, infilename = os.path.split(file)
    
    # Get the short name (filename without extension)
    infileshortname, extension = os.path.splitext(infilename)
    
    # Read
    src = rasterio.open(file)
    
    areas1, areas2 = [], []
    for i in range(lakes.shape[0]):
        
        # Clip with region shapefile
        lake_clf, out_transform = mask(src, [lakes.iloc[i].geometry], crop=True)
        
        # Label
        lake_binary_water_mask = (lake_clf == 2).astype(int)
        lake_labeled = label(lake_binary_water_mask)
        lake_props = regionprops(lake_labeled)
        lake_area_values = np.array([prop.area for prop in lake_props])
        
        # Append
        areas1.append(np.sum(lake_area_values[lake_area_values>15000]).astype(int))
        areas2.append(np.sum(lake_clf > 0).astype(int))
    
    lake_areas.append(areas1)
    mask_areas.append(areas2)
    date_list.append(pd.to_datetime(os.path.basename(file)[0:8], format='%Y%m%d'))
    
    # Read mask
    data = src.read(1)
    
    # Clip with lake shapefile
    clf, out_transform = mask(src, lakes.geometry.values)
    
    # Label
    binary_water_mask = (clf == 2).astype(int)
    labeled = label(binary_water_mask)
    props = regionprops(labeled)

    for region in props:
        if region.area > 15000:
            coords = region.coords
            data[coords[:, 1], coords[:, 2]] = 1
    
    # Total size distribution
    binary_water_mask = (data == 2).astype(np.uint8)
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
        total_area.append((data > 0).sum())
        water_area.append(np.sum(data==2))
        area_list.append(areas)
    
    # Vectorize
    binary_lake = (clf == 2).astype(np.uint8)
    
    # Convert to DataArray
    da_lakes = xr.DataArray(
        binary_lake[0,:,:],
        dims=("y", "x"),
        coords={},
        name="polys"
    )
    
    # Attach spatial metadata
    da_lakes.rio.write_transform(out_transform, inplace=True)
    da_lakes.rio.write_crs(src.crs, inplace=True)
    
    da_water = xr.DataArray(
        binary_water_mask,
        dims=("y", "x"),
        coords={},
        name="polys"
    )
    
    # Attach spatial metadata
    da_water.rio.write_transform(out_transform, inplace=True)
    da_water.rio.write_crs(src.crs, inplace=True)
    
    # Vectorize
    gdf_lakes = vectorize(da_lakes)
    gdf_water = vectorize(da_water)
    
    # Filter 
    gdf_lakes = gdf_lakes[gdf_lakes['polys'] == 1]
    gdf_lakes = gdf_lakes.set_crs("EPSG:32622")
    gdf_lakes['area'] = gdf_lakes.area
    gdf_lakes = gdf_lakes[gdf_lakes['area'] > 15000]
    
    gdf_water = gdf_water[gdf_water['polys'] == 1]
    gdf_water = gdf_water.set_crs("EPSG:32622")
    gdf_water['area'] = gdf_water.area
    
    # Merge
    gdf = pd.concat([gdf_lakes, gdf_water], ignore_index=True)
    
    # Save to file
    gdf.to_file(path1 + 'skysat/data/' + aoi + '/water-polygons/' + infileshortname + '.shp')
    gdf_lakes.to_file(path1 + 'skysat/data/' + aoi + '/lake-polygons/' + infileshortname + '.shp')

    
#%%

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
lake_df.to_csv(path1 + 'skysat/data/' + aoi + '/lake-stats.csv')

# Export a total area csv
total_area_df = pd.DataFrame(total_area, columns=['total_area'])
total_area_df['date'] = date_list
total_area_df.to_csv(path1 + 'skysat/data/' + aoi + '/total-area.csv', index=False)

#%%


#%%

















