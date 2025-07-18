#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Remove ortho files that don't have a matching classification.

"""

# Import packages
import glob
import os

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'

# Define AOI
aoi = 'aoi1'

class_files = sorted(glob.glob(path1 + aoi + '/training/class-scenes/*.tif'))
ortho_files = sorted(glob.glob(path1 + aoi + '/training/ortho-scenes/*.tif'))

#%%

class_filenames = []
for file in class_files:
    # Get file name
    class_filenames.append(os.path.basename(file))


# Remove files that are not classified
for file in ortho_files:
    # Get file name
    filename = os.path.basename(file)
    
    if filename in class_filenames:
        pass
    else:
        os.remove(file)
    

#%%