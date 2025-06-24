#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Calculate mean surface-parallel strain rates from MEaSUREs Ice Sheet Velocity Mosaics.

Annual ice sheet velocity mosaics can be downloaded from:
    https://nsidc.org/data/nsidc-0725/versions/5
    

"""

# Import packages
import numpy as np
import rioxarray as rxr
import strain_tools

#%%

# Define user
user = 'johnnyryan'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/skysat/data'

vx_fpath = path1 + "maeasures/GL_vel_mosaic_Annual_01Dec18_30Nov19_vx_v05.0.tif"
vy_fpath = path1 + "maeasures/GL_vel_mosaic_Annual_01Dec18_30Nov19_vy_v05.0.tif"

vx = rxr.open_rasterio(vx_fpath).squeeze(drop=True)
vy = rxr.open_rasterio(vy_fpath).squeeze(drop=True)

resolution = 200    # metres
length_scale = 750  # metres

# Get absolute velocity
vv = np.sqrt(vx**2 + vy**2)

#%%

log_strain_rates = strain_tools.log_strain_rates(vx, vy, resolution, length_scale, tol=10e-4, ydir=1)

principal_strain_rates = strain_tools.principal_strain_rate_directions(
    log_strain_rates.e_xx, log_strain_rates.e_yy, log_strain_rates.e_xy)

principal_strain_rates_alt = strain_tools.principal_strain_rate_magnitudes(
    log_strain_rates.e_xx, log_strain_rates.e_yy, log_strain_rates.e_xy)

#%%

# Difference between two methods used to calculate principal strain rates are minimal - 
# related to different numpy methods, floating points, etc.

print('Mean differences between the two approaches:')
print('`e_1`: ',np.nanmean(principal_strain_rates.e_1 - principal_strain_rates_alt.e_1))
print('`e_2`: ',np.nanmean(principal_strain_rates.e_2 - principal_strain_rates_alt.e_2))

angle = strain_tools.flow_direction(vx, vy)

rotated_strain_rates = strain_tools.rotated_strain_rates(
    log_strain_rates.e_xx, 
    log_strain_rates.e_yy, 
    log_strain_rates.e_xy, 
    angle
)

e_E = strain_tools.effective_strain_rate(
    log_strain_rates.e_xx, 
    log_strain_rates.e_yy, 
    log_strain_rates.e_xy,
)

e_M = 0.5 * (principal_strain_rates.e_1 + principal_strain_rates.e_2) # mean surface-parallel strain rate (see Chudley _et al._ 2021)


#%%


e_M.rio.to_raster(path1 + 'strain-rates/strain-rate-01Dec15_30Nov16.tif', tiled=True)

vv.rio.to_raster(path1 + 'velocities/GL_vel_mosaic_Annual_01Dec15_30Nov16_vv_v05.0.tif', tiled=True)





























