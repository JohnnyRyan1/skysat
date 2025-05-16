#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Make shapefiles representing the intersections between SkySat scenes

"""

# Import packages
import geopandas as gpd
from shapely.geometry import GeometryCollection

#%%

# Define path
path = '/Volumes/meltwater-mapping_satellite-data/data/skysat/shapefiles/'

# Import shapefile
gdf = gpd.read_file(path + 'aoi2-index.shp')

#%%

# Merge polygons that are on the same month
dates = []
for i in range(len(gdf)):
    dates.append(gdf.iloc[i]['location'][0:6])

gdf['date'] = dates
unique_dates = list(set(dates))

dates_list = []
for d in unique_dates:
    new_gdf = gdf[gdf['date'] == d]
    dates_list.append(new_gdf.dissolve().iloc[0])
    
gdf_dates = gpd.GeoDataFrame(dates_list).reset_index()
gdf_dates = gdf_dates.drop('index', axis=1)
gdf_dates = gdf_dates.set_crs(gdf.crs)

#%%

# Find overlaps for all three months
overlap = gdf_dates.iloc[0].geometry.intersection(gdf_dates.iloc[1].geometry).intersection(gdf_dates.iloc[2].geometry)

# Remove LineStrings
filtered = GeometryCollection([geom for geom in overlap.geoms if not geom.geom_type == 'LineString'])

# Put back in GeoDataFrame
overlap_gdf = gpd.GeoDataFrame(geometry=[filtered], crs=gdf_dates.crs)
overlap_gdf = overlap_gdf.explode()
overlap_gdf.to_file(path + 'aoi2-index-overlaps.shp')

#%%






