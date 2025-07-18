#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Classify SkySat images using NDWI threshold and subset to 256x256 tiles.

"""

# Import packages
import rioxarray as rio
import xarray as xr
import pandas as pd
import numpy as np
import glob
import os

# Define path
path1 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/data/'
path3 = '/Users/jr555/Documents/research/skysat/'

# Define AOI
aoi = 'aoi1'

# Read threshold file
df = pd.read_csv(path2 + 'thresholds_' + aoi + '.csv')

# Define files
files = sorted(glob.glob(path1 + aoi + '/raw/*.tif'))
basenames = [os.path.basename(path) for path in files]

# Remove duplicates
df = df[~df['filename'].duplicated(keep='last')]

#%%

for f in range(len(df)):
    # Define filename
    filename = df.iloc[f]['filename']
    
    # Define threshold
    final_threshold = df.iloc[f]['threshold']
    if final_threshold == 0:
        pass
    else:
        print('%.0f out of %.0f' %(f+1, len(df)-1))
        # Read corresponding file
        file = rio.open_rasterio(path1 + aoi + '/raw/' + filename)
        
        # Compute NDWI
        ndwi = ((file[1, :, :] - file[3,:, :]) / \
            (file[1, :, :] + file[3,:, :])).values
                    
        # Convert to Dataset
        ndwi_da = xr.DataArray(np.repeat(ndwi[np.newaxis, :, :], 4, axis=0), 
                               dims=file.dims, coords=file.coords)
        ndwi_da = ndwi_da[3:,:,:]
        
        # Classify
        classified = xr.where(ndwi_da > final_threshold, 1, xr.where(ndwi_da <= final_threshold, 0, 2))
    
        # Export to GeoTIFF
        classified = classified.astype('uint8')
        classified = classified.rio.write_crs(file.rio.crs)
        
        if classified.rio.transform()[0] == 1:
            classified.rio.to_raster(path3 + aoi + '/training/class-scenes/' + filename)
        else:           
            # Resample to 1 m
            output_raster = classified.rio.reproject(dst_crs=classified.rio.crs, resolution=1.0)
            
            # Export to GeoTIFF
            output_raster.rio.to_raster(path3 + aoi + '/training/class-scenes/' + filename)
    
#%%

















