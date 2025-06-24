#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Randomly sample 320x320 tiles from classified and ortho images.

"""

# Import modules
import rioxarray as rio
import glob
import numpy as np
import pandas as pd
import os

# Define paths
path1 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path2 = '/Users/jr555/Documents/research/skysat/'

# Define AOI
aoi = 'aoi1'

# Define ortho scenes
ortho_scenes = sorted(glob.glob(path1 + aoi + '/training/ortho-scenes/*.tif'))
class_scenes = sorted(glob.glob(path1 + aoi + '/training/class-scenes/*.tif'))

# Define number of random samples from each image
tile_size = 320
num_samples = int(2000 / len(class_scenes))
bins = np.arange(-0.05, 0.5, .05)
bins = np.append(bins, 1)

#%%

file_list, water_fraction = [], []
for f in range(len(ortho_scenes)):
    print('%.0f out of %.0f' %(f+1, len(ortho_scenes)))
    
    # Filename
    filename = os.path.splitext(os.path.basename(ortho_scenes[f]))[0]

    # Load the raster
    cla = rio.open_rasterio(class_scenes[f], masked=True).squeeze()
    ort = rio.open_rasterio(ortho_scenes[f], masked=True).squeeze()
    
    # Make a grid of possible tile positions
    ys, xs = cla.shape
    ys_idx = np.arange(0, ys - tile_size, tile_size)
    xs_idx = np.arange(0, xs - tile_size, tile_size)
    
    tile_centers = []
    tile_means = []
    
    for y in ys_idx:
        for x in xs_idx:
            tile = cla[y:y+tile_size, x:x+tile_size]
            if (tile == 2).any().values:
                pass
            else:
                if tile.count() == tile_size * tile_size:
                    mean_val = tile.mean().item()
                    tile_centers.append((y, x))
                    tile_means.append(mean_val)
                else:
                    pass
    
    # Make a DataFrame of tiles
    tile_df = pd.DataFrame(tile_centers, columns=["y", "x"])
    tile_df["mean"] = tile_means
    tile_df["bin"] = pd.cut(tile_df["mean"], bins=bins)
    
    unique_bins = tile_df["bin"].dropna().unique()
    num_bins = len(unique_bins)
    
    # Compute base number of samples per bin
    base_n = num_samples // num_bins
    remainder = num_samples % num_bins
    
    # Sort bins to deterministically assign remainder
    sorted_bins = sorted(unique_bins)
    
    # Distribute samples
    samples = []
    for i, b in enumerate(sorted_bins):
        n = base_n + (1 if i < remainder else 0)
        bin_df = tile_df[tile_df["bin"] == b]
        if len(bin_df) >= n:
            samples.append(bin_df.sample(n=n, random_state=42))
        else:
            # Skip or take all if not enough tiles in bin
            samples.append(bin_df)
            
    # Concatenate all sampled tiles
    samples_df = pd.concat(samples).reset_index(drop=True)
    
    # Extract the actual tiles
    tiles = []
    
    for j, row in samples_df.iterrows():
        y, x = int(row.y), int(row.x)
        cla_tile = cla[y:y+tile_size, x:x+tile_size]
        ort_tile = ort[:, y:y+tile_size, x:x+tile_size]

        # Ensure the tile has spatial referencing
        cla_tile = cla_tile.rio.write_crs(cla_tile.rio.crs)
        ort_tile = ort_tile.rio.write_crs(ort_tile.rio.crs)

        # Export to GeoTIFF
        cla_tile.rio.to_raster(path2 + aoi + '/training/class-tiles/' + filename + '_' + str(j).zfill(2) + '.tif')
        ort_tile.rio.to_raster(path2 + aoi + '/training/ortho-tiles/' + filename + '_' + str(j).zfill(2) + '.tif')
        
        # Append to list
        file_list.append(path2 + aoi + '/training/ortho-tiles/' + filename + '_' + str(j).zfill(2) + '.tif')
        water_fraction.append(row['mean'])


df = pd.DataFrame(list(zip(file_list, water_fraction)), columns=['filename', 'water_fraction'])

# Save
df.to_csv(path2 + aoi + '/training/' + aoi + '.csv', index=False)


