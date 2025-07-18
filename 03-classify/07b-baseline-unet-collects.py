#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Baseline U-Net model.

"""

# Import packages
import numpy as np
import tensorflow as tf
import rasterio
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import img_to_array
import glob

#%%

# Define path
path1 = '/Users/jr555/Documents/research/skysat/'
path2 = '/Users/jr555/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/'

# Define AOI
aoi = 'aoi1'

#%%
# Define config
batch_size = 16
epochs = 20
optimizer = 'adam'
loss = 'binary_crossentropy'
img_size = (320, 320)
img_height = 320
img_width = 320
img_bands = 4

# === MATCH FILES ===
image_files = sorted(glob.glob(path1 + aoi + '/training/ortho-tiles/*.tif'))
mask_files = sorted(glob.glob(path1 + aoi + '/training/class-tiles/*.tif'))

# Split dataset
train_imgs, test_imgs, train_masks, test_masks = train_test_split(
    image_files, mask_files, test_size=0.2, random_state=42
)

train_imgs, val_imgs, train_masks, val_masks = train_test_split(
    train_imgs, train_masks, test_size=0.1, random_state=42  # 10% of remaining for validation
)

#%%

# Functions for loading data
def load_geotiff_image(image_path):
    with rasterio.open(image_path) as src:
        # Read image as a 4-band array
        img_array = src.read([1, 2, 3, 4])  # Red, Green, Blue, and NIR bands
        img_array = np.moveaxis(img_array, 0, -1)  # Change to HxWx4 shape
        img_array = img_array.astype(np.float32)
        img_array = img_array / 255.0
    return img_array

def load_mask_image(mask_path):
    with rasterio.open(mask_path) as src:
        # Read the 1-band mask
        mask_array = src.read(1)  # 1-band mask
        mask_array = mask_array.astype(np.uint8)
    return mask_array

        
def create_tf_dataset(image_paths, mask_paths, batch_size=batch_size, img_size=img_size):
    images = []
    masks = []
    
    for img_path, mask_path in zip(image_paths, mask_paths):
        image = load_geotiff_image(img_path)
        mask = load_mask_image(mask_path)
              
        images.append(img_to_array(image))  # Convert to numpy array if needed
        masks.append(np.expand_dims(mask, axis=-1))  # Add channel dimension for the mask
        
    # Convert lists to numpy arrays
    images = np.array(images)
    masks = np.array(masks)
    
    # Create a TensorFlow dataset
    dataset = tf.data.Dataset.from_tensor_slices((images, masks))
    dataset = dataset.shuffle(buffer_size=len(images)).batch(batch_size)
    return dataset

# Create the dataset
train_ds = create_tf_dataset(train_imgs, train_masks, batch_size=batch_size, img_size=img_size)
val_ds   = create_tf_dataset(val_imgs, val_masks, batch_size=batch_size, img_size=img_size)
test_ds  = create_tf_dataset(test_imgs, test_masks, batch_size=batch_size, img_size=img_size)

#%%

# U-Net model
def unet_model(input_shape=(img_width, img_height, img_bands)):
    inputs = tf.keras.Input(shape=input_shape)

    # Encoder
    c1 = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')(inputs)
    c1 = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')(c1)
    p1 = tf.keras.layers.MaxPooling2D(2)(c1)

    c2 = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')(p1)
    c2 = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')(c2)
    p2 = tf.keras.layers.MaxPooling2D(2)(c2)

    # Bottleneck
    b = tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same')(p2)

    # Decoder
    u1 = tf.keras.layers.UpSampling2D(2)(b)
    u1 = tf.keras.layers.Concatenate()([u1, c2])
    c3 = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')(u1)

    u2 = tf.keras.layers.UpSampling2D(2)(c3)
    u2 = tf.keras.layers.Concatenate()([u2, c1])
    c4 = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')(u2)

    outputs = tf.keras.layers.Conv2D(1, 1, activation='sigmoid')(c4)

    return tf.keras.Model(inputs, outputs)

# Compile model
model = unet_model()
model.compile(optimizer=optimizer, loss=loss, metrics=['Precision'])

# Train
model.fit(train_ds, validation_data=val_ds, epochs=epochs)

# Evaluate
test_loss, test_acc = model.evaluate(test_ds)
print(f"\n✅ Final test accuracy: {test_acc:.4f}")

# Save model
model.save(path2 + 'models/baseline-unet-' + aoi + '-' + str(epochs) + '-epochs-' + optimizer + '-' + loss + '.keras')





