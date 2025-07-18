#!/bin/bash

# Set your input directory and output directory
input_dir="/Volumes/meltwater-mapping_satellite-data/data/skysat/aoi1/raw/may/"
output_dir="/Users/jr555/Documents/research/skysat/aoi1/training/ortho-scenes/"

# Set NoData value
nodata=0

# Set target resolution (1 meter)
target_resolution="1"

# Loop through each .tif file in the input directory
for input_file in "$input_dir"*.tif; do
    # Extract the base name (filename without path and extension)
    base_name=$(basename "$input_file" .tif)
    
    # Define the output file path
    output_file="$output_dir${base_name}.tif"

    # Collect per-band min/max values and build scale args
    scale_args=""
    band=0
    while read -r line; do
        if [[ $line == Band* ]]; then
            ((band++))
        fi
        if [[ $line == *Minimum=* ]]; then
            min=$(echo $line | sed -n 's/.*Minimum=\([^,]*\).*/\1/p')
        fi
        if [[ $line == *Maximum=* ]]; then
            max=$(echo $line | sed -n 's/.*Maximum=\([^,]*\).*/\1/p')
            
            # Avoid division-by-zero or broken scaling
            if [[ $(echo "$max == $min" | bc) -eq 1 ]]; then
                max=$(echo "$min + 1" | bc)
            fi

            # Map min–max → 1–255 (reserving 0 for NoData)
            scale_args+=" -scale $min $max 1 255"
        fi
    done < <(gdalinfo -stats "$input_file")

    # Now run gdal_translate with scaling, resampling to 1m, and nodata set to 0
    gdal_translate -of GTiff -ot Byte $scale_args -a_nodata $nodata -tr $target_resolution $target_resolution "$input_file" "$output_file"

    echo "Processed: $input_file -> $output_file"
done




