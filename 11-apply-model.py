#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Apply over all ortho tiles for all scenes. 

Pads ortho tiles with zeros if not 320x320.

Replaces zero-valued pixels at edges of image using edge padding to remove artifacts
at the edges

"""

# Import packages
import numpy as np
import tensorflow as tf
import rasterio
import os
import glob
from scipy.ndimage import distance_transform_edt

# Define AOI
aoi = 'aoi1'

# Define model
model = 'baseline-unet-aoi1-20-epochs-adam-binary_crossentropy.keras'

# Define path
path1 = '/Volumes/EXTERNAL_USB/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/models/'

# List images
image_list = sorted(glob.glob(path1 + aoi + '/apply/ortho-tiles/*.tif'))

# Load model
model = tf.keras.models.load_model(path2 + model)

# Define target shape
target_shape = (320, 320, 4)

# Define pad width
w = 3

#%%

predictions = []
for i in image_list:
    
    # Define filename
    filename = os.path.basename(i)
    
    if os.path.exists(path1 + aoi + '/' + 'apply/pred-tiles/' + filename):
        pass
    else:

        # Load the image
        src = rasterio.open(i)
        profile = src.profile
        img = src.read()
        img = np.moveaxis(img, 0, -1)
        img = img.astype(np.float32)
        img = img / 255.0
        
        if img.shape == target_shape:
            
            # Mask of zero pixels
            zero_mask = np.all(img == 0, axis=-1)
            non_zero_mask = ~zero_mask
            distances, indices = distance_transform_edt(zero_mask, return_indices=True)
            
            # Define a "near-edge" region: zero pixels within threshold of non-zero
            near_edge_mask = (zero_mask & (distances <= 3))
            
            # Copy image and fill in only near-edge zero pixels
            padded = img.copy()
            padded[near_edge_mask] = img[tuple(idx[near_edge_mask] for idx in indices)]
            
            # Add batch dimension
            img_input = tf.expand_dims(padded, axis=0)
    
            # Make prediction
            prediction = model.predict(img_input)
            
            # Set no data to NaN
            mask = padded[:,:,0] == 0 
            prediction = prediction[0,:,:,0]
            prediction[mask] = np.nan
            
            # Pad mask
            mask_pad_width = [(0, target - current) for current, target in zip(near_edge_mask.shape, (320,320))]
            
            # Apply padding
            padded_mask = np.pad(near_edge_mask, mask_pad_width, mode='constant', constant_values=0)

            # Convert padded pixels back to zero
            prediction[padded_mask] = 0
            
            # Export
            profile.update(count=1, dtype=rasterio.float32)
            with rasterio.open(path1 + aoi + '/' + 'apply/pred-tiles/' + filename, "w", **profile) as dst:
                dst.write(prediction, 1)
        
        elif (img.shape[0] != 320) & (img.shape[1] == 320):
            
            # Mask of zero pixels
            zero_mask = np.all(img == 0, axis=-1)
            non_zero_mask = ~zero_mask
            distances, indices = distance_transform_edt(zero_mask, return_indices=True)
            
            # Define a "near-edge" region: zero pixels within threshold of non-zero
            near_edge_mask = (zero_mask & (distances <= w))
            
            # Copy image and fill in only near-edge zero pixels
            padded = img.copy()
            padded[near_edge_mask] = img[tuple(idx[near_edge_mask] for idx in indices)]
            
            # Pad to the right
            pad_width = [(0, target - current) for current, target in zip(padded.shape, target_shape)]
            
            # Apply padding (right-side only)
            padded_img = np.pad(padded, pad_width, mode='constant', constant_values=0)
            
            # Update profile
            profile.update(height=320)
            
            # Add batch dimension
            img_input = tf.expand_dims(padded_img, axis=0)
    
            # Make prediction
            prediction = model.predict(img_input)
            
            # Set no data to NaN
            mask = padded_img[:,:,0] == 0 
            prediction = prediction[0,:,:,0]
            prediction[mask] = np.nan
            
            # Pad mask
            mask_pad_width = [(0, target - current) for current, target in zip(near_edge_mask.shape, (320,320))]
            
            # Apply padding
            padded_mask = np.pad(near_edge_mask, mask_pad_width, mode='constant', constant_values=0)

            # Convert padded pixels back to zero
            prediction[padded_mask] = 0
                    
            # Export
            profile.update(count=1, dtype=rasterio.float32)
            with rasterio.open(path1 + aoi + '/' + 'apply/pred-tiles/' + filename, "w", **profile) as dst:
                dst.write(prediction, 1)
        
        elif (img.shape[0] == 320) & (img.shape[1] != 320):
            
            # Mask of zero pixels
            zero_mask = np.all(img == 0, axis=-1)
            non_zero_mask = ~zero_mask
            distances, indices = distance_transform_edt(zero_mask, return_indices=True)
            
            # Define a "near-edge" region: zero pixels within threshold of non-zero
            near_edge_mask = (zero_mask & (distances <= w))
            
            # Copy image and fill in only near-edge zero pixels
            padded = img.copy()
            padded[near_edge_mask] = img[tuple(idx[near_edge_mask] for idx in indices)]
            
            # Pad to the right
            pad_width = [(0, target - current) for current, target in zip(padded.shape, target_shape)]
            
            # Apply padding (right-side only)
            padded_img = np.pad(padded, pad_width, mode='constant', constant_values=0)
            
            # Update profile
            profile.update(width=320)
            
            # Add batch dimension
            img_input = tf.expand_dims(padded_img, axis=0)
    
            # Make prediction
            prediction = model.predict(img_input)
            
            # Set no data to NaN
            mask = padded_img[:,:,0] == 0 
            prediction = prediction[0,:,:,0]
            prediction[mask] = np.nan
            
            # Pad mask
            mask_pad_width = [(0, target - current) for current, target in zip(near_edge_mask.shape, (320,320))]
            
            # Apply padding
            padded_mask = np.pad(near_edge_mask, mask_pad_width, mode='constant', constant_values=0)

            # Convert padded pixels back to zero
            prediction[padded_mask] = 0
                    
            # Export
            profile.update(count=1, dtype=rasterio.float32)
            with rasterio.open(path1 + aoi + '/' + 'apply/pred-tiles/' + filename, "w", **profile) as dst:
                dst.write(prediction, 1)
        
        elif (img.shape[0] != 320) & (img.shape[1] != 320):
            
            # Mask of zero pixels
            zero_mask = np.all(img == 0, axis=-1)
            non_zero_mask = ~zero_mask
            distances, indices = distance_transform_edt(zero_mask, return_indices=True)
            
            # Define a "near-edge" region: zero pixels within threshold of non-zero
            near_edge_mask = (zero_mask & (distances <= w))
            
            # Copy image and fill in only near-edge zero pixels
            padded = img.copy()
            padded[near_edge_mask] = img[tuple(idx[near_edge_mask] for idx in indices)]
            
            # Pad to the right
            pad_width = [(0, target - current) for current, target in zip(padded.shape, target_shape)]
            
            # Apply padding (right-side only)
            padded_img = np.pad(padded, pad_width, mode='constant', constant_values=0)
            
            # Update profile
            profile.update(width=320, height=320)
            
            # Add batch dimension
            img_input = tf.expand_dims(padded_img, axis=0)
    
            # Make prediction
            prediction = model.predict(img_input)
            
            # Set no data to NaN
            mask = padded_img[:,:,0] == 0 
            prediction = prediction[0,:,:,0]
            prediction[mask] = np.nan
            
            # Pad mask
            mask_pad_width = [(0, target - current) for current, target in zip(near_edge_mask.shape, (320,320))]
            
            # Apply padding
            padded_mask = np.pad(near_edge_mask, mask_pad_width, mode='constant', constant_values=0)

            # Convert padded pixels back to zero
            prediction[padded_mask] = 0

            # Export
            profile.update(count=1, dtype=rasterio.float32)
            with rasterio.open(path1 + aoi + '/' + 'apply/pred-tiles/' + filename, "w", **profile) as dst:
                dst.write(prediction, 1)
    
        else:
            
            pass

#%%












































