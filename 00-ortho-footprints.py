#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Make footprints from orthos.

"""

# Import packages
import rioxarray as rio
import geopandas as gpd
from geocube.vector import vectorize
import pandas as pd
import glob
import os


#%%

# Define path
path1 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path2 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/shapefiles/'

# Define AOI
aoi = 'aoi2'

# Define orthomosaics
orthos = sorted(glob.glob(path1 + 'aoi2-scaled/*.tif'))

#%%

# Generate shapefiles
def raster_to_polygon(raster_file, infileshortname):
    
    # Open the raster file
    image = rio.open_rasterio(raster_file)
    
    # Get one band
    target_band = image.isel(band=0)
       
    # Create the mask (e.g., mask for non-zero values)
    mask = (target_band != 0).astype("uint8")
    
    # Vectorize
    gdf = vectorize(mask)
    
    # Filter 
    gdf = gdf[gdf['_data'] == 1]
    
    # Define projection
    gdf.crs = image.rio.crs
    
    # Add location
    gdf['location'] = infileshortname
    
    # Drop column
    gdf = gdf.drop(columns='_data')

    # Save to file
    gdf.to_file(path1 + aoi + '-outlines/' + infileshortname + '.shp')

for ortho in orthos:
    
    # Get the path and filename separately
    infilepath, infilename = os.path.split(ortho)
    
    # Get the short name (filename without extension)
    infileshortname, extension = os.path.splitext(infilename)
    
    # Get grandparent folder
    date = os.path.basename(os.path.dirname(os.path.dirname(ortho)))
    
    # Call function
    raster_to_polygon(ortho, infileshortname)
       
# Merge into one file
shapefile_paths = glob.glob(path1 + aoi + '-outlines/*.shp')

# Read and concatenate all shapefiles into one GeoDataFrame
gdf_list = [gpd.read_file(path) for path in shapefile_paths]
gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))

# Write
gdf.to_file(path2 + 'aoi2-index.shp')

#%%













