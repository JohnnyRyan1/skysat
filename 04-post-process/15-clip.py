#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Clip to study area.

"""

# Import packages
import rasterio
from rasterio.mask import mask
import glob
import os
import geopandas as gpd

# Define user 
user = 'jr555'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/'
path2 = '/Users/' + user + '/Documents/research/skysat/'

# Define AOI
aoi = 'aoi1'

# Area of study site
site = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/aoi1-focused.shp')

# Define files
files = sorted(glob.glob(path2 + aoi + '/apply/' + '*.tif'))

# Loop over every GeoTIFF
for file in files:
    print(file)
    
    # Define filename
    filename = os.path.basename(file)
    
    # Read
    src = rasterio.open(file)
    
    # Clip with region shapefile
    clf, out_transform = mask(src, site.geometry.values, crop=True)
    
    # Export
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": clf.shape[1],
        "width": clf.shape[2],
        "transform": out_transform
    })

    with rasterio.open(path2 + aoi + '/clipped/' + filename, "w", **out_meta) as dest:
        dest.write(clf)
    
    
#%%
    
    
    
    