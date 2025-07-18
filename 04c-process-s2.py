#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Lake analysis.

Classify S2 images using NDWI threshold.

"""

# Import packages
import rasterio
import numpy as np
import glob
import os

# Define user
user = 'jr555'

# Define paths
path = '/Users/jr555/Downloads/'
outpath = '/Volumes/meltwater-mapping_satellite-data/data/s2/aoi1/'

# Define files
filepaths = sorted(glob.glob(path + 'S2*/GRANULE/L2A_*/IMG_DATA/R10m'))

for fp in filepaths:

    # Paths to Band 3 (Green) and Band 8 (NIR)
    green_band_path = glob.glob(fp + '/*B03*.jp2')[0]
    nir_band_path = glob.glob(fp + '/*B08*.jp2')[0]
    
    # Filename
    filename = os.path.basename(green_band_path)
    
    # Open Green band
    with rasterio.open(green_band_path) as green_src:
        green = green_src.read(1).astype('float32')
        green_meta = green_src.meta
    
    # Open NIR band
    with rasterio.open(nir_band_path) as nir_src:
        nir = nir_src.read(1).astype('float32')
    
    # Avoid division by zero
    ndwi_numerator = green - nir
    ndwi_denominator = green + nir
    ndwi_denominator[ndwi_denominator == 0] = np.nan
    
    # NDWI Calculation
    ndwi = ndwi_numerator / ndwi_denominator
    
    # Save the NDWI as a GeoTIFF
    ndwi_meta = green_meta.copy()
    ndwi_meta.update(driver='GTiff', dtype='float32', count=1)
    
    with rasterio.open(outpath + filename[0:22] + '_NDWI.tif', 'w', **ndwi_meta) as dst:
        dst.write(ndwi, 1)

#%%
















