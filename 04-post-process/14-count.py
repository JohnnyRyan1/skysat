#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Make GeoTIFF containing counts

"""

# Import packages
import rasterio
from rasterio.mask import mask
import numpy as np
import glob
import geopandas as gpd

# Define user 
user = 'johnnyryan'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/data/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'

# Define AOI
aoi = 'aoi1'

# Define files
files = sorted(glob.glob(path1 + aoi + '/apply/' + '*.tif'))

# Area of study site
site = gpd.read_file(path1 + 'shapefiles/aoi1-index-overlaps.shp')

# Loop over every GeoTIFF
counts = np.zeros((83901, 20224))

for file in files:
    print(file)
    
    # Read
    src = rasterio.open(file)
    
    # Clip with shapefile
    clf, out_transform = mask(src, site.geometry.values, crop=False)

    # Add
    counts = counts + (clf > 0).astype(int)
# Save counts as raster
with rasterio.open(path2 + aoi + '/counts.tif', "w", **src.meta.copy()) as dst:
        dst.write(counts)
        
        
#%%
        
        
