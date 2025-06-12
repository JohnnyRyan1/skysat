#!/bin/bash

# Note that the output directory should be local to make it much faster

# Directory containing your input raster files
input_dir="/Users/jr555/Documents/research/skysat/aoi1/training/ortho-scenes"
output_dir="/Volumes/EXTERNAL_USB/skysat/aoi1/apply/ortho-tiles"

# Loop through each .tif file in the input directory
for file in "$input_dir"/*.tif; do
    # Run gdal_retile.py for each file to create 320x320 tiles
    gdal_retile.py -targetDir "$output_dir" -ps 320 320 -overlap 32 -co "TILED=YES" "$file"
    
    echo "Processed $file"
done
