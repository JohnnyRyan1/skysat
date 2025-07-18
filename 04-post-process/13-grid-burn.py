#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Burn values to common grid for analysis.

NOTE: Removed one ortho scene from 2019-06-13 because there were some georeferencing issues.


"""

# Import packages
import rioxarray as rio
from rioxarray.merge import merge_arrays
import xarray as xr
import geopandas as gpd
import numpy as np
import pandas as pd
import glob
import os
from affine import Affine

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path3 = '/Volumes/EXTERNAL_USB/skysat/'

# Define AOI
aoi = 'aoi1'

# Define files
files = sorted(glob.glob(path2 + aoi + '/apply/prob-scenes/*.tif'))

# Import intersections
gdf = gpd.read_file(path2 + 'shapefiles/' + aoi + '-index-overlaps.shp')

# Get bounds and CRS
minx, miny, maxx, maxy = gdf.total_bounds
crs = gdf.crs

# Define raster resolution (pixel size)
pixel_size = 1

# Calculate raster dimensions
width = int((maxx - minx) / pixel_size)
height = int((maxy - miny) / pixel_size)

# Define affine transform
transform = Affine.translation(minx, maxy) * Affine.scale(pixel_size, -pixel_size)

# Create an empty array
data = np.zeros((height, width), dtype=np.uint8)

# Create xarray DataArray and attach spatial metadata
da = xr.DataArray(
    data,
    dims=("y", "x"),
    coords={
        "x": np.arange(minx + pixel_size / 2, maxx, pixel_size),
        "y": np.arange(maxy - pixel_size / 2, miny, -pixel_size),
    },
    name="empty_band"
)

# Attach CRS and transform using rioxarray
da = da.rio.write_crs(crs)
da = da.rio.set_spatial_dims(x_dim="x", y_dim="y")
da = da.rio.write_transform(transform)

# Merge scenes on same day
dates = []
for f in range(len(files)):
    dates.append(os.path.basename(files[f])[0:8])
unique_dates = list(set(dates))

#%%
arrays = np.zeros((height, width), dtype="int8")
date_list = []
for date in sorted(unique_dates):
    if os.path.exists(path2 + aoi + '/apply/' + date + '.tif'):
        pass
    else:
        print(date)
        collected_files = []
        for file in files:
            if os.path.basename(file)[0:8] == date:
                collected_files.append(file)
            
        # Read all rasters into a list
        src_files = [rio.open_rasterio(r, masked=True) for r in collected_files]
        
        # Align and stack using rioxarray merge_arrays
        stacked_max = merge_arrays(src_files, method='max')
       
        # Threshold
        pred_mask = np.where(np.isnan(stacked_max[0, :, :]), np.nan, stacked_max[0, :, :] > 0.5)
        
        # Set water values to 2
        pred_mask[pred_mask == 1] = 2
        
        # Set snow/ice values to 1
        pred_mask[pred_mask == 0] = 1
        
        # Set no values back to zero
        pred_mask[np.isnan(pred_mask)] = 0
        
        # Make new DataArray
        new_da = xr.DataArray(
        pred_mask,
        dims=('y', 'x'),
        coords={
            'y': stacked_max.coords['y'],
            'x': stacked_max.coords['x']
        },
        )
        new_da = new_da.rio.write_crs(da.rio.crs)
    
        # Check that they overlap
        a_left, a_bottom, a_right, a_top = new_da.rio.bounds()
        b_left, b_bottom, b_right, b_top = da.rio.bounds()
        
        # Check for overlap
        x_overlap = (a_left < b_right) and (a_right > b_left)
        y_overlap = (a_bottom < b_top) and (a_top > b_bottom)
        
        overlap = x_overlap and y_overlap
        
        # If true, match projections
        if overlap == True:
            # Match projection
            matched_scene = new_da.rio.reproject_match(da)
            
            # Stack
            arrays = np.dstack((arrays, matched_scene.values.astype(np.uint8)))
            
            # Export
            matched_scene = matched_scene.rio.write_nodata(None)
            matched_scene.astype("uint8").rio.to_raster(path2 + aoi + '/apply/' + date + '.tif')
    
            # Append date
            date_list.append(date)
        else:
            pass
    
# Remove first layer
arrays = arrays[:, :, 1:]
#%%

# Save as NetCDF
time_index = pd.to_datetime(date_list, format='%Y%m%d')
x_coords = da.coords["x"]
y_coords = da.coords["y"]

# Create new DataArray with a third dimension (e.g., "band")
da3d = xr.DataArray(
    data=arrays,
    dims=("y", "x", "time"),
    coords={
        "x": x_coords,
        "y": y_coords,
        "time": time_index  
    },
    name="water_fraction")

# Attach CRS and transform
da3d = da3d.rio.write_crs(da.rio.crs)
da3d = da3d.rio.set_spatial_dims(x_dim="x", y_dim="y")
da3d = da3d.rio.write_transform(da.rio.transform())

# Export
da3d.to_netcdf(path1 + aoi + '/apply/' + aoi + '.nc')

#%%

# OPTIONAL export single layer for visualization

x_coords = np.arange(minx + pixel_size / 2, maxx, pixel_size)
y_coords = np.arange(maxy - pixel_size / 2, miny, -pixel_size)

# Create DataArray
da = xr.DataArray(
    data=arrays[:,:,5],
    dims=("y", "x"),
    coords={"x": x_coords, "y": y_coords},
    name="single_band")

# Attach spatial metadata
da = da.rio.write_crs(crs)  # crs should be like "EPSG:32617" or a CRS object
da = da.rio.set_spatial_dims(x_dim="x", y_dim="y")
da = da.rio.write_transform(transform)  # transform from rasterio or calculated

# Export to GeoTIFF
da.rio.to_raster('/Users/jr555/Documents/research/skysat/aoi2/apply/test.tif')

#%%

# Make a count raster
arrays = np.zeros((height, width), dtype="int8")
for date in sorted(unique_dates):

    print(date)
    collected_files = []
    for file in files:
        if os.path.basename(file)[0:8] == date:
            collected_files.append(file)
        
    # Read all rasters into a list
    src_files = [rio.open_rasterio(r, masked=True) for r in collected_files]
    
    # Align and stack using rioxarray merge_arrays
    stacked_max = merge_arrays(src_files, method='max')
   
    # Threshold
    pred_mask = np.where(np.isnan(stacked_max[0, :, :]), np.nan, stacked_max[0, :, :] > 0.5)
    
    # Set valid values to 0
    pred_mask[pred_mask >= 0] = 1
    
    # Set no values back to zero
    pred_mask[np.isnan(pred_mask)] = 0

    # Make new DataArray
    new_da = xr.DataArray(
    pred_mask,
    dims=('y', 'x'),
    coords={
        'y': stacked_max.coords['y'],
        'x': stacked_max.coords['x']
    },
    )
    new_da = new_da.rio.write_crs(da.rio.crs)
    
    # Match projection
    matched_scene = new_da.rio.reproject_match(da)
    
    # Stack
    arrays = arrays + matched_scene













