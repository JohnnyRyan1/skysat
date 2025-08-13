#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Evaluate model using stratified sampling.

"""

# Import packages
import pandas as pd
import numpy as np
import tensorflow as tf
import os
import glob
import rasterio
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

#%%

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/'

# Define AOI
aoi = 'aoi1'

# Define model
unet = 'baseline-unet-' + aoi + '-20-epochs-adam-binary_crossentropy'
#unet = 'ronneberger-unet-20-epochs-adam-binary_crossentropy'

# Define csv of matching files
df = pd.read_csv(path1 + aoi + '/training/' + aoi + '.csv')

# Load model
model = tf.keras.models.load_model(path2 + 'models/' + unet + '.keras')

# Define training, validation, and test datasets
image_files = sorted(glob.glob(path1 + aoi + '/training/ortho-tiles/*.tif'))
mask_files = sorted(glob.glob(path1 + aoi + '/training/class-tiles/*.tif'))

# Split dataset
train_imgs, test_imgs, train_masks, test_masks = train_test_split(
    image_files, mask_files, test_size=0.2, random_state=42
)

train_imgs, val_imgs, train_masks, val_masks = train_test_split(
    train_imgs, train_masks, test_size=0.1, random_state=42
)

#%%

# Find optimal global threshold
local_thresholds = []
for i in test_imgs:
    
    # Get corresponding classified image
    class_filename = os.path.basename(i)

    # Load the image
    src = rasterio.open(i)
    ortho_img = src.read()
    ortho_img = np.moveaxis(ortho_img, 0, -1)
    ortho_img = ortho_img.astype(np.float32)
    ndwi = (ortho_img[:,:,1] - ortho_img[:,:,3]) / (ortho_img[:,:,1] + ortho_img[:,:,3])

    # Load the ground-truth classified image
    src = rasterio.open(path1 + aoi + '/training/class-tiles/' + class_filename)
    class_img = src.read()
    class_img = np.moveaxis(class_img, 0, -1)
    
    # Find optimal threshold
    scores = []
    for j in np.arange(0, 0.31, 0.01):
        # Classify
        gt = class_img.flatten()
        pred = (ndwi>j).astype(int).flatten()
        scores.append(accuracy_score(gt, pred))
        
    # Find best local threshold
    local_thresholds.append(np.arange(0, 0.31, 0.01)[np.argmax(scores)])

# Define global threshold
global_threshold = np.mean(local_thresholds)

#%%

# Predict all test images
predictions = []
class_images = []
thresh_images = []
tile_metrics = []
for i in test_imgs:
    
    # Get corresponding classified image
    class_filename = os.path.basename(i)

    # Load the image
    src = rasterio.open(i)
    ortho_img = src.read()
    ortho_img = np.moveaxis(ortho_img, 0, -1)
    ortho_img = ortho_img.astype(np.float32)
    ndwi = (ortho_img[:,:,1] - ortho_img[:,:,3]) / (ortho_img[:,:,1] + ortho_img[:,:,3])
    ortho_img = ortho_img / 255.0
    
    # Add batch dimension
    img_input = tf.expand_dims(ortho_img, axis=0)

    # Make prediction
    prediction = model.predict(img_input)
    
    # Threshold
    pred_mask = (prediction[0, :, :, 0] > 0.5).astype(np.uint8)
    
    # Append
    predictions.append(pred_mask)
    
    # Load the ground-truth classified image
    src = rasterio.open(path1 + aoi + '/training/class-tiles/' + class_filename)
    class_img = src.read()
    class_img = np.moveaxis(class_img, 0, -1)
    class_images.append(class_img[:,:,0])
    
    # Classify with global threshold
    thresh_img = (ndwi>global_threshold).astype(int)
    thresh_images.append(thresh_img)
    
    # Define tile metrics
    cnn_acc = accuracy_score(class_img.ravel(), pred_mask.ravel())
    cnn_pre = precision_score(class_img.ravel(), pred_mask.ravel(), zero_division=0)
    cnn_rec = recall_score(class_img.ravel(), pred_mask.ravel(), zero_division=0)

    thres_acc = accuracy_score(class_img.ravel(), thresh_img.ravel())
    thres_pre = precision_score(class_img.ravel(), thresh_img.ravel(), zero_division=0)
    thres_rec = recall_score(class_img.ravel(), thresh_img.ravel(), zero_division=0)
    
    substrings = class_filename.split("_")
    if len(substrings) == 7:
        filetype = substrings[4] + '_' + substrings[5]
    else:
        filetype = substrings[4]
    
    tile_metrics.append((class_filename, filetype, cnn_acc, cnn_pre, cnn_rec,
                        thres_acc, thres_pre, thres_rec))    
    

#%%

# Compute global accuracy metrics
flat_pred = np.concatenate([a.ravel() for a in predictions])
flat_gt = np.concatenate([a.ravel() for a in class_images])
flat_thresh = np.concatenate([a.ravel() for a in thresh_images])

cnn_vs_gt_acc = accuracy_score(flat_gt, flat_pred)
cnn_vs_gt_pre = precision_score(flat_gt, flat_pred)
cnn_vs_gt_rec = recall_score(flat_gt, flat_pred)

thesh_vs_gt_acc = accuracy_score(flat_gt, flat_thresh)
thesh_vs_gt_pre = precision_score(flat_gt, flat_thresh)
thesh_vs_gt_rec = recall_score(flat_gt, flat_thresh)

#%%

new_df = pd.DataFrame(tile_metrics, columns=['filename', 'type', 'cnn_acc',
                                             'cnn_pre', 'cnn_rec', 'thres_acc',
                                             'thres_pre', 'thres_rec'])

new_df[new_df['type']=='pansharpened']['cnn_acc'].mean()
new_df[new_df['type']=='analytic_dn']['cnn_acc'].mean()
new_df[new_df['type']=='analytic']['cnn_acc'].mean()

new_df[new_df['type']=='analytic']['thres_acc'].mean()
new_df[new_df['type']=='pansharpened']['thres_acc'].mean()
new_df[new_df['type']=='analytic_dn']['thres_acc'].mean()













