#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Determine initial NDWI threshold for classiyfing SkySat imagery.

"""

# Import modules
import rioxarray as rio
import cv2
import pandas as pd
import numpy as np
import os
import csv
import glob
import matplotlib.pyplot as plt

# Define path
path1 = '/Volumes/meltwater-mapping_satellite-data/data/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/data/'

# Define AOI
aoi = 'aoi3'

# Define image paths
image_paths = sorted(glob.glob(path1 + aoi + '/' + 'raw/*.tif'))

# Read thresholds
threshold_results = []

# Define starting threshold
previous_threshold = 128

csv_path = path2 + 'thresholds_' + aoi + '.csv'
file_exists = os.path.isfile(csv_path)
with open(csv_path, mode='a', newline='') as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(['filename', 'threshold'])

# Read csv
df = pd.read_csv(csv_path)

#%%

# Process images
for img_path in image_paths:
    
    # Define filename
    img_name = os.path.basename(img_path)
    
    if img_name in list(df['filename']):
        pass
    else:
            
        # Read file
        file = rio.open_rasterio(img_path)
        
        # Compute NDWI
        ndwi = ((file[1, :, :] - file[3,:, :]) / \
            (file[1, :, :] + file[3,:, :])).values
        
        # Convert to 8-bit for OpenCV
        img_8bit = (ndwi * 255).astype(np.uint8)
        
        # Scale to 0-255
        img = np.dstack((file[2, :, :].values, file[1, :, :].values, file[0, :, :].values))
        if img.max() < 700:
            img_rgb_display = img
        elif (img.max() > 700) & (img.max() < 4096):
            img_rgb_display = cv2.convertScaleAbs(img, alpha=(255.0/4096.0))
        else:
            img_rgb_display = cv2.convertScaleAbs(img, alpha=(255.0/65535.0))  
        
        # Window names
        win_thresh = f"Threshold Adjuster - {img_name}"
        win_rgb = f"Original - {img_name}"
    
        # Create windows and slider
        cv2.namedWindow(win_thresh)
        cv2.createTrackbar('Threshold (0-255)', win_thresh, previous_threshold, 255, lambda x: None)
        cv2.imshow(win_rgb, cv2.cvtColor(img_rgb_display, cv2.COLOR_RGB2BGR))
    
        final_threshold = None
        should_exit = False
    
        while True:
            t = cv2.getTrackbarPos('Threshold (0-255)', win_thresh)
            _, thresh_img = cv2.threshold(img_8bit, t, 255, cv2.THRESH_BINARY)
    
            # Overlay threshold value
            display_img = cv2.putText(thresh_img.copy(), f"Threshold: {t}/255", (10, 25),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, 255, 2, cv2.LINE_AA)
            cv2.imshow(win_thresh, display_img)
    
            key = cv2.waitKey(50) & 0xFF
    
            if key == 13:  # Enter
                final_threshold = t / 255.0
                previous_threshold = t
                threshold_results.append([img_name, final_threshold])
                break
            elif key in [27, ord('q')]:  # Esc or 'q' to skip
                final_threshold = 0
                threshold_results.append([img_name, final_threshold])
                break
            elif key == ord('a') and t > 0:
                cv2.setTrackbarPos('Threshold (0-255)', win_thresh, t - 1)
            elif key == ord('d') and t < 255:
                cv2.setTrackbarPos('Threshold (0-255)', win_thresh, t + 1)
    
        # Close both windows
        cv2.destroyWindow(win_thresh)
        cv2.destroyWindow(win_rgb)

#%%

with open(csv_path, mode='a', newline='') as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(['filename', 'threshold'])
    writer.writerows(threshold_results)

print(f"\n✅ Thresholds saved to: {csv_path}")

#%%

# Remove zeros and duplicates












