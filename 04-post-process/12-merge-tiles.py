#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Merge predicted probabilities tiles to scenes.

"""

# Import packages
import rasterio
from rasterio.merge import merge
import glob
import os

# Define AOI
aoi = 'aoi1'

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'
path2 = '/Volumes/EXTERNAL_USB/skysat/'
path3 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'

# Define files
tile_files = sorted(glob.glob(path2 + aoi + '/' + 'apply/pred-tiles/*.tif'))
scene_files = sorted(glob.glob(path1 + aoi + '/' + 'training/ortho-scenes/*.tif'))

# Define a list of scenes
scene_names = []
for file in scene_files:
    scene_names.append(os.path.basename(file)[:-4])

for scene in scene_names:
    if os.path.exists(path3 + aoi + '/' + 'apply/prob-scenes/' + scene + '.tif'):
        pass
    else:
        # Get a list of scenes
        scene_list = []
        for f in range(len(tile_files)):
            if scene in os.path.basename(tile_files[f]):
                scene_list.append(tile_files[f])
    
        # Read all rasters into a list
        src_files = [rasterio.open(p) for p in scene_list]
        out_meta = src_files[0].meta.copy()
        nodata = -1
        
        # Align and stack using rasterio.merge (aligns bounds, resampling if needed)
        stacked_count, out_transform = merge(src_files, method='count')
        stacked_sum, out_transform = merge(src_files, method='sum')
    
        mask = (stacked_count == 0)
        merged_mean = stacked_sum/stacked_count
        merged_mean[mask] = nodata
        
        # Save the output GeoTIFF
        out_meta.update({
            "driver": "GTiff",
            "dtype": "float32",
            "count": stacked_count.shape[0],
            "height": stacked_count.shape[1],
            "width": stacked_count.shape[2],
            "transform": out_transform,
            "nodata": nodata
        })
        
        with rasterio.open(path2 + aoi + '/' + 'apply/prob-scenes/' + scene + '.tif', "w", **out_meta) as dest:
            dest.write(merged_mean[0,:,:], 1)

        
#%%











