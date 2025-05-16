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
import rasterio
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import matplotlib.pyplot as plt

#%%

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/'

# Define model
unet = 'baseline-unet-20-epochs-adam-binary_crossentropy'
#unet = 'ronneberger-unet-20-epochs-adam-binary_crossentropy'

# Define csv of matching files
df = pd.read_csv(path1 + 'aoi2/training/aoi2.csv')

# Make a stratified training dataset with even numbers of non-water tiles, dates etc.
df_sample = df.groupby("datetime", group_keys=False).sample(n=80, random_state=42).reset_index()

# Add 400 images with most water in
df_high = df.sort_values(by=['water_fraction'], ascending=False).head(400).reset_index()

# Merge
matched_df = pd.concat([df_sample, df_high], ignore_index=True)

# Remove duplicates
matched_df = matched_df.drop_duplicates(keep='first')

# Load model
model = tf.keras.models.load_model(path2 + 'models/' + unet + '.keras')

# Define training, validation, and test datasets
image_files = list(matched_df['ortho'])
mask_files = list(matched_df['classified'])

# Split dataset
train_imgs, test_imgs, train_masks, test_masks = train_test_split(
    image_files, mask_files, test_size=0.2, random_state=42
)

train_imgs, val_imgs, train_masks, val_masks = train_test_split(
    train_imgs, train_masks, test_size=0.1, random_state=42  # 10% of remaining for validation
)

#%%

# Match test images to DataFrame
test_df = matched_df[matched_df['ortho'].isin(test_imgs)]

# Sample even number of tiles from classes representing: 0%, 0-10%, 10-20%, 20-30%, >30%
bins = [-0.1, 0, 0.05, 0.1, 0.15, 1.0]
labels = ['0', '0-0.05', '0.05-0.1', '0.1-0.15', '>0.15']

# Bin and count
test_df = test_df.copy()
test_df['bin']= pd.cut(test_df['water_fraction'], bins=bins, labels=labels)
bin_counts = test_df['bin'].value_counts().sort_index()

# Randomly samples rows
sampled_df = test_df.groupby('bin', group_keys=False, observed=True).sample(n=bin_counts.min(), random_state=42)
sample_imgs = list(sampled_df['ortho'])

# Predict all test images
predictions = []
class_images = []
acc, prec, rec = [], [], []
for i in sample_imgs:
    
    # Get corresponding classified image
    class_filename = os.path.basename(i)

    # Load the image
    src = rasterio.open(i)
    ortho_img = src.read()
    ortho_img = np.moveaxis(ortho_img, 0, -1)
    ortho_img = ortho_img.astype(np.float32)
    ortho_img = ortho_img / 255.0

    src = rasterio.open(path1 + 'aoi2/training/class-tiles/' + os.path.basename(i))
    clf = src.read()
    water = np.sum(clf == 1)
    
    # Add batch dimension
    img_input = tf.expand_dims(ortho_img, axis=0)

    # Make prediction
    prediction = model.predict(img_input)
    
    # Threshold
    pred_mask = (prediction[0, :, :, 0] > 0.5).astype(np.uint8)
    
    # Append
    predictions.append(pred_mask)
    
    # Load the image
    src = rasterio.open(path1 + 'aoi2/training/class-tiles/' + class_filename)
    class_img = src.read()
    class_img = np.moveaxis(class_img, 0, -1)
    class_images.append(class_img)
    
    # Calculate metrics
    gt = class_img.flatten()
    pred = pred_mask.flatten()
       
    # Compute metrics
    acc.append(accuracy_score(gt, pred))
    prec.append(precision_score(gt, pred, zero_division=0))
    rec.append(recall_score(gt, pred, zero_division=0))

rgb_images = []
for i in sample_imgs:
    # Load the image
    src = rasterio.open(i)
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    img = img[:,:,:3]
    rgb_images.append(img[..., ::-1])

#%%

# Add metrics to DataFrame
sampled_df['acc'] = acc
sampled_df['prec'] = prec
sampled_df['rec'] = rec

# Group water_fraction values by area_bin
grouped = sampled_df.groupby('bin', observed=True)['acc'].apply(list)

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')

# Create the boxplot
bp = ax.boxplot(grouped, patch_artist=True, tick_labels=grouped.index, showfliers=False)

# Customize plot
ax.set_xlabel("Water fraction", fontsize=12)
ax.set_ylabel("Accuracy", fontsize=12)
ax.tick_params(axis='both', rotation=0, labelsize=12)
ax.grid(True, linestyle='dashed', lw=1.5, alpha=0.5)

for box in bp['boxes']:
    box.set_facecolor('white')
    box.set_edgecolor('black')
    box.set_linewidth(1.5)

for median in bp['medians']:
    median.set_color('black')
    median.set_linewidth(1.5)

mean_acc = sampled_df['acc'].mean()
num_obs = len(sampled_df)
textstr = f'Mean accuracy: {mean_acc:.2f}\nNumber of tiles: {num_obs}'

# Add text box with mean value in lower left corner
ax.text(0.02, 0.05, textstr, 
        transform=ax.transAxes, fontsize=13, verticalalignment='bottom', 
        horizontalalignment='left', bbox=dict(facecolor='white', edgecolor='white'))

# Final layout
plt.savefig(path2 + 'figures/' + unet +'.png', dpi=300)

#%%


















