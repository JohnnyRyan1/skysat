#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  9 15:04:11 2025

@author: jr555
"""

import rasterio
from rasterio.merge import merge
import matplotlib.pyplot as plt
import rioxarray as rio
from rioxarray.merge import merge_arrays


file1 = '/Users/jr555/Documents/research/skysat/aoi2/apply/prob-scenes/20190829_172710_ssc7d3_0028_analytic.tif'
file2 = '/Users/jr555/Documents/research/skysat/aoi2/apply/prob-scenes/20190829_172710_ssc7d3_0029_pansharpened.tif'
file3 = '/Users/jr555/Documents/research/skysat/aoi2/apply/prob-scenes/20190829_172710_ssc7d3_0033_analytic_dn.tif'

r1 = rio.open_rasterio(file1, masked=True)
r2 = rio.open_rasterio(file2, masked=True)
r3 = rio.open_rasterio(file3, masked=True)

# Read all rasters into a list
src_files = [rio.open_rasterio(r, masked=True) for r in [file1, file2, file3]]

# Align and stack using rioxarray merge_arrays
merged_raster = merge_arrays(src_files, method='max')

#merged_raster = merge_arrays(dataarrays = [r1, r2, r3], method='max')

merged_raster.rio.to_raster("/Users/jr555/Documents/research/skysat/aoi2/apply/merged-v3.tif")












