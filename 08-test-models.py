#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Test models.

"""

# Import packages
import numpy as np
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

# Define model
unet = 'baseline-unet-20-epochs-adam-binary-crossentropy.keras'
unet = 'ronneberger-unet-20-epochs-adam-binary_crossentropy.keras'

#%%

# List images
image_list = sorted(glob.glob(path2 + 'aoi2/training/ortho-tiles/*.tif'))

# Define five test images to evaluate on
images = random.sample(image_list, 5)

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

    src = rasterio.open(path2 + 'aoi2/training/class-tiles/' + os.path.basename(i))
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
    src = rasterio.open(path2 + 'aoi2/training/class-tiles/' + class_filename)
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    class_images.append(img)
    

# Make a plot showing all five images, their classifications, and the CNN
fig, axes = plt.subplots(3, 5, figsize=(18, 11), layout='constrained')

for i in range(5):
    axes[0, i].imshow(rgb_images[i])
    axes[0, i].set_title(os.path.basename(images[i]), fontsize=9)
    axes[0, i].axis('off')

    axes[1, i].imshow(class_images[i], cmap='gray')
    axes[1, i].set_title("Ground truth")
    axes[1, i].axis('off')

    axes[2, i].imshow(predictions[i], cmap='gray')
    axes[2, i].set_title("Prediction")
    axes[2, i].axis('off')
    
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
        0.01, 0.01, metrics_text, fontsize=9,
        ha='left', va='bottom', transform=axes[2, i].transAxes,
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3')
    )
    
for ax in axes.flat:
    ax.axis('off')
    
plt.savefig(path1 + 'figures/' + os.path.splitext(os.path.basename(images[0]))[0] + '.png', dpi=300)


#%%


















    
    
    

