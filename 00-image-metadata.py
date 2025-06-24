#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Solar zenith angles

"""

# Import modules
import rasterio
import glob
import json
import pandas as pd
import os

# Define path
path1 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/data/'

# Define AOI
aoi = 'aoi4'

# Define image paths
image_paths = sorted(glob.glob(path1 + aoi + '/raw/*.tif'))

sun_elevation, sat_elevation, time_list = [], [], []
filename = []
for img in image_paths:
    
    # Read file
    src = rasterio.open(img)
    
    # Find tags
    if len(src.tags()) > 1:
    
        # Parse the JSON string from TIFFTAG_IMAGEDESCRIPTION
        description_json = json.loads(src.tags()['TIFFTAG_IMAGEDESCRIPTION'])
        
        # Append values
        sun_elevation.append(description_json["properties"]["sun_elevation"])
        sat_elevation.append(description_json["properties"]["satellite_elevation"])
        time_list.append(pd.to_datetime(src.tags()['TIFFTAG_DATETIME'], format='%Y:%m:%d %H:%M:%S'))
        filename.append(os.path.basename(img))
        
    else:
        pass
    

# Make a DataFrame
df = pd.DataFrame(list(zip(filename, sun_elevation, sat_elevation, time_list)))
df.columns = ['filename', 'sun_elevation', 'sat_eleavtion', 'datetime']
    
    
# Save
df.to_csv(path2 + 'metadata_' + aoi + '.csv')
    
