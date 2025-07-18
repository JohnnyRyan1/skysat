#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Test models.

"""

# Import packages
import numpy as np
import pandas as pd
import tensorflow as tf
import rasterio
import matplotlib.pyplot as plt
import os
import glob
import random
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Define path
path1 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/'
path2 = '/Users/jr555/Documents/research/skysat/'

# Define AOI
aoi = 'aoi1'

# Import file
df = pd.read_csv(path2 + aoi + '/training/' + aoi + '.csv')

# Define model
#unet = 'baseline-unet-20-epochs-adam-binary-crossentropy.keras'
#unet = 'ronneberger-unet-20-epochs-adam-binary_crossentropy.keras'
unet = 'baseline-unet-aoi1-20-epochs-adam-binary_crossentropy.keras'

#%%

# List images
image_list = sorted(glob.glob(path2 + aoi + '/training/ortho-tiles/*.tif'))

# Define five test images to evaluate on
images = [path2 + aoi + '/training/ortho-tiles/20190703_181449_ssc11_u0002_analytic_13.tif',
          path2 + aoi + '/training/ortho-tiles/20190820_175415_ssc10_u0003_analytic_14.tif',
          path2 + aoi + '/training/ortho-tiles/20190708_175258_ssc10_u0002_pansharpened_05.tif',
          path2 + aoi + '/training/ortho-tiles/20190715_150144_ssc1_u0004_pansharpened_10.tif',
          path2 + aoi + '/training/ortho-tiles/20190712_180823_ssc10_u0002_analytic_06.tif']

# Load model
model = tf.keras.models.load_model(path1 + 'models/' + unet)

predictions = []
for i in images:

    # Load the image
    src = rasterio.open(i)
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    img = img.astype(np.float32)
    img = img / 255.0

    src = rasterio.open(path2 + aoi + '/training/class-tiles/' + os.path.basename(i))
    clf = src.read()
    water = np.sum(clf == 1)
    
    # Add batch dimension
    img_input = tf.expand_dims(img, axis=0)

    # Make prediction
    prediction = model.predict(img_input)
    
    # Threshold
    pred_mask = (prediction[0, :, :, 0] > 0.5).astype(np.uint8)
    
    # Append
    predictions.append(pred_mask)

rgb_images = []
for i in images:
    # Load the image
    src = rasterio.open(i)
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    img = img[:,:,:3]
    rgb_images.append(img[..., ::-1])
    
class_images = []
for i in images:
    # Get corresponding classified image
    class_filename = os.path.basename(i)
    
    # Load the image
    src = rasterio.open(path2 + aoi + '/training/class-tiles/' + class_filename)
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    class_images.append(img)


# Make a plot showing all five images, their classifications, and the CNN
fig, axes = plt.subplots(3, 5, figsize=(13, 8), layout='constrained')

for i in range(5):
    axes[0, i].imshow(rgb_images[i])
    axes[0, i].axis('off')

    axes[1, i].imshow(class_images[i], cmap='Blues')
    axes[1, i].axis('off')

    axes[2, i].imshow(predictions[i], cmap='Blues')
    axes[2, i].axis('off')
    
    # Set row labels on the first column only
    if i == 0:
        axes[1, i].set_ylabel("Ground truth", fontsize=12, rotation=0, labelpad=20, va='center')
        axes[2, i].set_ylabel("Prediction", fontsize=12, rotation=0, labelpad=20, va='center')
    
    # Flatten ground truth and prediction
    gt = class_images[i].flatten()
    pred = predictions[i].flatten()
       
    # Compute metrics
    acc = accuracy_score(gt, pred)
    prec = precision_score(gt, pred, zero_division=0)
    rec = recall_score(gt, pred, zero_division=0)
    
    # Annotate metrics in the lower-left corner of the prediction panel
    metrics_text = f"Acc: {acc:.2f}\nPrec: {prec:.2f}\nRec: {rec:.2f}"
    axes[2, i].text(
        0.01, 0.01, metrics_text, fontsize=12,
        ha='left', va='bottom', transform=axes[2, i].transAxes,
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', 
                  boxstyle='round,pad=0.3')
    )
fig.align_ylabels(axes[:, 0])
plt.savefig(path1 + 'figures/classification/layout-classified.png', dpi=300)


#%%


















    
    
    

