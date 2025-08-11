#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Remove files that contain NaNs.

"""

# Import packages
import rioxarray as rio
import pandas as pd
import numpy as np
import glob
import os

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'
class_files = sorted(glob.glob(path1 + 'aoi2/training/class-tiles/*.tif'))
ortho_files = sorted(glob.glob(path1 + 'aoi2/training/ortho-tiles/*.tif'))

# Define image size
class_img_size = (1, 320, 320)
orth_img_size = (4, 320, 320)

#%%

# Remove files that are not 320x320
for file in class_files:
    # Get file name
    filename = os.path.basename(file)
    
    # Open file with rioxarray
    xarr = rio.open_rasterio(file)
    
    if xarr.shape != class_img_size:
        os.remove(file)
    else:
        pass

class_files = sorted(glob.glob(path1 + 'aoi2/training/class-tiles/*.tif'))
ortho_files = sorted(glob.glob(path1 + 'aoi2/training/ortho-tiles/*.tif'))

# Remove files that are no 320x320
for file in ortho_files:
    # Get file name
    filename = os.path.basename(file)

    # Open file with rioxarray
    xarr = rio.open_rasterio(file)
    
    if xarr.shape != orth_img_size:
        os.remove(file)
    else:
        pass

class_files = sorted(glob.glob(path1 + 'aoi2/training/class-tiles/*.tif'))
ortho_files = sorted(glob.glob(path1 + 'aoi2/training/ortho-tiles/*.tif'))

# Remove class files with no match
for file in class_files:
    
    # Get file name
    filename = os.path.basename(file)

    # Open file with rioxarray
    xarr = rio.open_rasterio(file)
    
    # Find matching file
    matching_files = []
    for ortho_filename in ortho_files:
        if filename in ortho_filename:
            matching_files.append(ortho_filename)
    
    if (len(matching_files) == 0):
        os.remove(file)
    else:
        pass

class_files = sorted(glob.glob(path1 + 'aoi2/training/class-tiles/*.tif'))
ortho_files = sorted(glob.glob(path1 + 'aoi2/training/ortho-tiles/*.tif'))

# Remove ortho files with no match
for file in ortho_files:
    
    # Get file name
    filename = os.path.basename(file)

    # Open file with rioxarray
    xarr = rio.open_rasterio(file)
    
    # Find matching file
    matching_files = []
    for class_filename in class_files:
        if filename in class_filename:
            matching_files.append(class_filename)
    
    if (len(matching_files) == 0):
        os.remove(file)
    else:
        pass

class_files = sorted(glob.glob(path1 + 'aoi2/training/class-tiles/*.tif'))
ortho_files = sorted(glob.glob(path1 + 'aoi2/training/ortho-tiles/*.tif'))


#%%
matched_tiles = []
# Loop through each .tif file
for f in range(len(class_files)):
    
    # Get file name
    filename = os.path.basename(class_files[f])
       
    # Open file with rioxarray
    class_xarr = rio.open_rasterio(class_files[f])
    ortho_xarr = rio.open_rasterio(ortho_files[f])
    
    # Remove if any value is classified as NoData
    if (class_xarr[0,:,:].values == 2).any() | (ortho_xarr[0,:,:].values == 0).any():
        os.remove(class_files[f])
        os.remove(ortho_files[f])
                
    else:
        water_fraction = np.sum(class_xarr.values == 1) / np.sum(class_xarr.values >= 0)
        matched_tiles.append((pd.to_datetime(filename[0:8], format='%Y%m%d'), 
                              class_files[f], ortho_files[f], water_fraction))
        

# Make a csv file with matching tiles
df = pd.DataFrame(matched_tiles, columns=['datetime', 'classified', 'ortho', 'water_fraction'])

# Save
df.to_csv(path1 + 'aoi2/training/aoi2.csv', index=False)



#%%









