#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Vectorize water masks

"""

# Import packages
import numpy as np
import rasterio
from rasterio.mask import mask
import xarray as xr
import glob
import os
import geopandas as gpd
from geocube.vector import vectorize

# Define user 
user = 'johnnyryan'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'

# Define AOI
aoi = 'aoi1'

# Define files
files = sorted(glob.glob(path1 + 'data/' + aoi + '/apply/' + '*.tif'))

# Area of study site
site = gpd.read_file(path1 + 'data/' + 'shapefiles/aoi1-focused.shp')

#%%

for file in files:
    print(file)
    
    # Get the path and filename separately
    infilepath, infilename = os.path.split(file)
    
    # Get the short name (filename without extension)
    infileshortname, extension = os.path.splitext(infilename)
    
    # Read
    src = rasterio.open(file)
    
    # Clip with shapefile
    clf, out_transform = mask(src, site.geometry.values, crop=True)

    # Size distribution
    binary_water_mask = (clf == 2).astype(np.uint8)
    
    # Convert to DataArray
    da = xr.DataArray(
        binary_water_mask[0,:,:],  # If single band; use clf if multiband
        dims=("y", "x"),
        coords={},
        name="classified"
    )
    
    # Attach spatial metadata
    da.rio.write_transform(out_transform, inplace=True)
    da.rio.write_crs(src.crs, inplace=True)
    
    # Vectorize
    gdf = vectorize(da)

    # Filter 
    gdf = gdf[gdf['classified'] == 1]
    gdf = gdf.set_crs("EPSG:32622")
    gdf['area'] = gdf.area
    
    # Save to file
    gdf.to_file(path1 + 'data/' + aoi + '/polygons/' + infileshortname + '.shp')


#%%













