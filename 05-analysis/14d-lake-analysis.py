#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Lake analysis.

NOTE: Removed 2019-08-02 and 2019-06-17 because there were some georeferencing issues.

"""

# Import packages
import xarray as xr
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

# Define user 
user = 'jr555'

# Define path
path1 = '/Users/' + user + '/Library/CloudStorage/OneDrive-DukeUniversity/research/'

# Define AOI
aoi = 'aoi1'

# Import data
all_df = pd.read_csv(path1 + 'skysat/data/' + aoi + '/water-stats.csv')
lake_df = pd.read_csv(path1 + 'skysat/data/' + aoi + '/lake-stats.csv')
s2_df = pd.read_csv(path1 + 'skysat/data/' + aoi + '/lake-stats-s2.csv')
all_df[all_df.columns[0]] = pd.to_datetime(all_df.iloc[:, 0])
all_df.index = all_df.iloc[:,0]
lake_df[lake_df.columns[0]] = pd.to_datetime(lake_df.iloc[:, 0])
lake_df.index = lake_df.iloc[:,0]
s2_df[s2_df.columns[0]] = pd.to_datetime(s2_df.iloc[:, 0])
s2_df.index = s2_df.iloc[:,0]

# Area of study site
site = gpd.read_file(path1 + 'skysat/data/' + 'shapefiles/aoi1-focused.shp')

# MAR runoff
mar = xr.open_dataset(path1 + 'hydrology/data/mar/MARv3.12.1-10km-daily-ERA5-2019.nc')

# Zhang
z_src = rasterio.open(path1 + 'hydrology/data/zhang/surface_water_mask_2019.tif')

#%%

"""
STATS
"""

may_mask = all_df.index.month == 5
may_water_fraction = all_df['water_fraction'][may_mask].mean()
may_water_area = (may_water_fraction * site.area / 1000000).values[0]


jun_mask = all_df.index.month == 6
jun_water_fraction = all_df['water_fraction'][jun_mask].mean()
jun_water_area = (jun_water_fraction * site.area / 1000000).values[0]

jul_mask = all_df.index.month == 7
jul_water_fraction = all_df['water_fraction'][jul_mask].mean()
jul_water_area = (jul_water_fraction * site.area / 1000000).values[0]

aug_mask = all_df.index.month == 8
aug_water_fraction = all_df['water_fraction'][aug_mask].mean()
aug_water_area = (aug_water_fraction * site.area / 1000000).values[0]

print('We find that surface water attained was \
%.2f %% of our study site in May June' %(may_water_fraction*100))

print('We find that surface water attained a \
maximum area of %.2f %% of our study site during June' %(jun_water_fraction*100))

print('By July, surface water decreases to \
%.2f %% ' %(jul_water_fraction*100))

print('By August, surface water decreases to \
%.2f %% ' %(aug_water_fraction*100))

print("Loss between Jun and Aug is %.2f %%" %(((jun_water_area-aug_water_area)/jun_water_area)*100))
      
#%%

"""
Compute area of water for different size fractions.

"""

may_mask = all_df.index.month == 5
may_water_fraction_small = (all_df['small']/all_df['water_area'])[may_mask].mean()
may_water_fraction_medium = (all_df['medium']/all_df['water_area'])[may_mask].mean()
may_water_fraction_large = (all_df['large']/all_df['water_area'])[may_mask].mean()
may_water_area_small = (may_water_fraction_small * may_water_fraction) * (site.area / 1000000).values[0]
may_water_area_medium = (may_water_fraction_medium * may_water_fraction) * (site.area / 1000000).values[0]
may_water_area_large = (may_water_fraction_large * may_water_fraction) * (site.area / 1000000).values[0]

jun_mask = all_df.index.month == 6
jun_water_fraction_small = (all_df['small']/all_df['water_area'])[jun_mask].mean()
jun_water_fraction_medium = (all_df['medium']/all_df['water_area'])[jun_mask].mean()
jun_water_fraction_large = (all_df['large']/all_df['water_area'])[jun_mask].mean()
jun_water_area_small = (jun_water_fraction_small * jun_water_fraction) * (site.area / 1000000).values[0]
jun_water_area_medium = (jun_water_fraction_medium * jun_water_fraction) * (site.area / 1000000).values[0]
jun_water_area_large = (jun_water_fraction_large * jun_water_fraction) * (site.area / 1000000).values[0]

jul_mask = all_df.index.month == 8
jul_water_fraction_small = (all_df['small']/all_df['water_area'])[jul_mask].mean()
jul_water_fraction_medium = (all_df['medium']/all_df['water_area'])[jul_mask].mean()
jul_water_fraction_large = (all_df['large']/all_df['water_area'])[jul_mask].mean()
jul_water_area_small = (jul_water_fraction_small * jul_water_fraction) * (site.area / 1000000).values[0]
jul_water_area_medium = (jul_water_fraction_medium * jul_water_fraction) * (site.area / 1000000).values[0]
jul_water_area_large = (jul_water_fraction_large * jul_water_fraction) * (site.area / 1000000).values[0]

aug_mask = all_df.index.month == 8
aug_water_fraction_small = (all_df['small']/all_df['water_area'])[aug_mask].mean()
aug_water_fraction_medium = (all_df['medium']/all_df['water_area'])[aug_mask].mean()
aug_water_fraction_large = (all_df['large']/all_df['water_area'])[aug_mask].mean()
aug_water_area_small = (aug_water_fraction_small * aug_water_fraction) * (site.area / 1000000).values[0]
aug_water_area_medium = (aug_water_fraction_medium * aug_water_fraction) * (site.area / 1000000).values[0]
aug_water_area_large = (aug_water_fraction_large * aug_water_fraction) * (site.area / 1000000).values[0]

# Find stacked values
small_values = np.array([may_water_area_small, jun_water_area_small, jul_water_area_small, aug_water_area_small])
medium_values = np.array([may_water_area_medium, jun_water_area_medium, jun_water_area_medium, aug_water_area_medium])
large_values = np.array([may_water_area_large, jun_water_area_large, jul_water_area_large, aug_water_area_large])
upper_values = np.array([may_water_area-(may_water_area_large+may_water_area_medium+may_water_area_small),
                jun_water_area-(jun_water_area_large+jun_water_area_medium+jun_water_area_small),
                jul_water_area-(jul_water_area_large+jul_water_area_medium+jul_water_area_small), 
                aug_water_area-(aug_water_area_large+aug_water_area_medium+aug_water_area_small)])

#%%
may_small = may_water_area_large+may_water_area_medium+may_water_area_small
jun_small = jun_water_area_large+jun_water_area_medium+jun_water_area_small
jul_small = jul_water_area_large+jul_water_area_medium+jul_water_area_small
aug_small = aug_water_area_large+aug_water_area_medium+aug_water_area_small

may_large = may_water_area-(may_water_area_large+may_water_area_medium+may_water_area_small)
jun_large = jun_water_area-(jun_water_area_large+jun_water_area_medium+jun_water_area_small)
jul_large = jul_water_area-(jul_water_area_large+jul_water_area_medium+jul_water_area_small)
aug_large = aug_water_area-(aug_water_area_large+aug_water_area_medium+aug_water_area_small)

print('Lakes >0.15 km2 account for %.2f %% of \
total surface water in June' % ((jun_large/jun_water_area)*100))

print('Lakes >0.15 km2 increase by %.2f km2 between May and Jun while smaller \
lakes decrease by %.2f km2' %((jun_large-may_large), (jun_small-may_small)))

print('Lakes >0.15 km2 decrease by %.2f km2 between Jun and \
Jul' %((jun_large-jul_large)))

print('Lakes >0.15 km2 decrease by %.2f km2 between Jul and \
Aug' %((jul_large-aug_large)))

print('Large lakes responsible for %.2f of total decrease' %(((jun_large-aug_large)/(jun_water_area-aug_water_area))*100))

#%%

print('Lakes <0.15 km2 account for %.2f %% of \
total surface water in May' % ((may_small/may_water_area)*100))

print('Lakes <0.15 km2 account for %.2f %% of \
total surface water in Aug' % ((aug_small/aug_water_area)*100))

print('Lakes <0.001 km2 account for %.2f %% of \
total surface water in May' % ((may_water_area_small/may_water_area)*100))

print('Lakes <0.001 km2 account for %.2f %% of \
total surface water in Aug' % ((aug_water_area_small/aug_water_area)*100))

print('Difference between max and min small water bodies is %.1f km2' % (may_small-aug_small))
print('Difference between max and min large water bodies is %.1f km2' % (jun_large-may_large))
print('Difference between max and min tiny water bodies is %.1f km2' % (may_water_area_small-aug_water_area_small))


#%%

"""
Compute water area from Zhang et al. (2023)

"""

# Reproject study site
site_nps = site.to_crs('EPSG:3413')

# Clip with region shapefile
z_clf, out_transform = mask(z_src, site_nps.geometry, crop=True)
z_area = np.sum(z_clf[z_clf == 1])

print('Area of surface water in Zhang et al. (2023) is %.1f %%' %((z_area*100/site.area.iloc[0])*100))

#%%

# Define latitude and longitude of three grid cells for Store Glacier
lat, lon = 68.90, -48.86

def find_idx(lat, lon):
    
    # Compute the Euclidean distance (not accounting for Earth curvature)
    distance = np.sqrt((mar['LAT'].values - lat)**2 + (mar['LON'].values - lon)**2)
    
    # Find the indices of the minimum distance
    idx = np.unravel_index(np.argmin(distance), distance.shape)
    
    return idx

idx = find_idx(lat, lon)

mar_runoff = mar['RU'][:,0, idx[0], idx[1]].values / 1000


#%%

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Create 3x3 subplots
fig, ax1 = plt.subplots(1, 1, figsize=(10, 4),layout='constrained', sharex=True)


# Define start and end dates for each month
start_dates = pd.to_datetime(['2019-05-01', '2019-06-01', '2019-07-01', '2019-08-01'])
end_dates = pd.to_datetime(['2019-05-31', '2019-06-30', '2019-07-31', '2019-08-31'])
total_values = [may_water_area, jun_water_area, jul_water_area, aug_water_area]

# Compute widths in days
widths = (end_dates - start_dates).days + 1

# Create the bar plot
ax1.bar(start_dates, small_values, color=c1,  width=widths, align='edge', zorder=2, 
        edgecolor='k', alpha=0.7, label='<0.001 km$^2$')
ax1.bar(start_dates, medium_values, bottom=small_values, color=c3, width=widths, 
        align='edge', zorder=2, edgecolor='k', alpha=0.7, label='<0.05 & >0.001 km$^2$')
ax1.bar(start_dates, large_values, bottom=small_values+medium_values, color=c2,  
        width=widths, align='edge', zorder=2, edgecolor='k', alpha=0.7,
        label='<0.15 & >0.05 km$^2$')
ax1.bar(start_dates, upper_values, bottom=small_values+medium_values+large_values, 
        color=c4, width=widths, align='edge', zorder=2, edgecolor='k', alpha=0.7,
        label='>0.15 km$^2$')

ax2 = ax1.twinx()
ax2.plot(mar['TIME'].values, mar_runoff, color='k', lw=2, ls='dashed', 
         zorder=3, alpha=0.7, label='Runoff')        

# Compute midpoints of each bar
midpoints = start_dates + pd.to_timedelta(widths // 2, unit='D')

# Set x-ticks at midpoints and label with month names
ax1.set_xticks(midpoints)
ax1.set_xticklabels(['May', 'Jun', 'Jul', 'Aug'], fontsize=12)

ax1.set_ylabel("Surface water area (km$^2$)", fontsize=12)  
ax2.set_ylabel("Meltwater runoff (m d$^{-1}$)", fontsize=12)  
ax1.legend(loc=2, fontsize=12)
ax2.legend(loc=1, fontsize=12)

ax1.tick_params(axis='both', which='major', labelsize=12)
ax2.tick_params(axis='both', which='major', labelsize=12)
ax1.grid(True, which="both", linestyle="--", linewidth=1, zorder=0)
ax1.set_xlim(all_df.index[0], all_df.index[-1])

plt.savefig(path1 + 'skysat/figures/' + 'figX-lake-change.png', dpi=300)

plt.show()

#%%

"""
NOTE: Lake 7 drains between Jun 8 and 13 because it establishes a channel into 
Lake 6 causing it to grow massively.

"""

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Create 3x3 subplots
fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, figsize=(10, 7), sharex=True)
fig.subplots_adjust(hspace=0.1)

# Plot with shared y-axis by row and left-only y-axis labels
ax6.scatter(s2_df.index, s2_df['lake1'], color=c1, zorder=2, s=50)
ax6.scatter(lake_df.index, lake_df['lake1'], zorder=3, s=50)
ax5.scatter(s2_df.index, s2_df['lake2'] + s2_df['lake3'], color=c1, zorder=2, s=50)
ax5.scatter(lake_df.index, lake_df['lake2'] + lake_df['lake3'], zorder=3, s=50)
ax4.scatter(s2_df.index, s2_df['lake4'], color=c1, zorder=2, s=50)
ax4.scatter(lake_df.index, lake_df['lake4'], zorder=3, s=50)
ax3.scatter(s2_df.index, s2_df['lake5'], color=c1, zorder=2, s=50)
ax3.scatter(lake_df.index, lake_df['lake5'], zorder=3, s=50)
ax2.scatter(s2_df.index, s2_df['lake6'], color=c1, zorder=2, s=50)
ax2.scatter(lake_df.index, lake_df['lake6'], zorder=3, s=50)
ax1.scatter(s2_df.index, s2_df['lake7'], color=c1, zorder=2, s=50, label='Sentinel-2')
ax1.scatter(lake_df.index, lake_df['lake7'], zorder=3, s=50, label='SkySat')

ax6.axvline(x=pd.to_datetime('2019-06-13'), ls='dashed', color='k', lw=2, alpha=0.5)
ax5.axvline(x=pd.to_datetime('2019-06-13'), ls='dashed', color='k', lw=2, alpha=0.5)
ax4.axvline(x=pd.to_datetime('2019-06-13'), ls='dashed', color='k', lw=2, alpha=0.5)
ax3.axvline(x=pd.to_datetime('2019-06-11'), ls='dashed', color='k', lw=2, alpha=0.5)
ax2.axvline(x=pd.to_datetime('2019-06-08'), ls='dashed', color='k', lw=2, alpha=0.5)
ax1.axvline(x=pd.to_datetime('2019-06-08'), ls='dashed', color='k', lw=2, alpha=0.5)

ax6.text(0.5, 0.75, "Lake 1", transform=ax6.transAxes,
    fontsize=12, ha='center', va='bottom')
ax5.text(0.5, 0.75, "Lake 2 + 3", transform=ax5.transAxes,
    fontsize=12, ha='center', va='bottom')
ax4.text(0.5, 0.75, "Lake 4", transform=ax4.transAxes,
    fontsize=12, ha='center', va='bottom')
ax3.text(0.5, 0.75, "Lake 5", transform=ax3.transAxes,
    fontsize=12, ha='center', va='bottom')
ax2.text(0.5, 0.75, "Lake 6", transform=ax2.transAxes,
    fontsize=12, ha='center', va='bottom')
ax1.text(0.5, 0.75, "Lake 7", transform=ax1.transAxes,
    fontsize=12, ha='center', va='bottom')

fig.text(0.07, 0.5, "Area (km$^2$)", va='center', rotation='vertical', fontsize=12)
ax1.legend(loc=4, fontsize=12)

# Custom formatter for multiline day/month
def multiline_date_formatter(x, pos=None):
    dt = mdates.num2date(x)
    return f"{dt.day}\n{dt.strftime('%b')}"
    
for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
    ax.set_yticks(np.arange(0, 3.1, 1))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(multiline_date_formatter))
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, which="both", linestyle="--", linewidth=1, zorder=1)
    ax.set_xlim(pd.to_datetime('2019-06-01'), lake_df.index[-1])
    tick_labels = ax.get_yticklabels()
    for label in tick_labels:
        if label.get_text() == '0':
            label.set_text('')
    ax.set_yticklabels(tick_labels)

plt.savefig(path1 + 'skysat/figures/cascading-drainage/' + 'figX-cascading-lakes.svg')

plt.show()



#%%

# Define colour map
c1 = '#E05861'
c2 = '#616E96'
c3 = '#F8A557'
c4 = '#3CBEDD'

# Create 3x3 subplots
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(10, 6), sharex=True)
fig.subplots_adjust(hspace=0.1)

# Plot with shared y-axis by row and left-only y-axis labels
ax1.scatter(s2_df.index, s2_df['lake8'], color=c1, zorder=1, s=50, label='Sentinel-2')
ax1.scatter(lake_df.index, lake_df['lake8'], zorder=2, label='SkySat')
ax2.scatter(s2_df.index, s2_df['lake9'], color=c1, zorder=2, s=50)
ax2.scatter(lake_df.index, lake_df['lake9'], zorder=3)
ax3.scatter(s2_df.index, s2_df['lake10'], color=c1, zorder=2, s=50)
ax3.scatter(lake_df.index, lake_df['lake10'], zorder=3)
ax4.scatter(s2_df.index, s2_df['lake11'], color=c1, zorder=2)
ax4.scatter(lake_df.index, lake_df['lake11'], zorder=3)
ax5.scatter(s2_df.index, s2_df['lake12'], color=c1, zorder=2)
ax5.scatter(lake_df.index, lake_df['lake12'], zorder=3)

ax1.axvline(x=pd.to_datetime('2019-06-11'), ls='dashed', color='k', lw=2, alpha=0.5)
ax2.axvline(x=pd.to_datetime('2019-06-24'), ls='dashed', color='k', lw=2, alpha=0.5)
ax3.axvline(x=pd.to_datetime('2019-06-26'), ls='dashed', color='k', lw=2, alpha=0.5)
ax4.axvline(x=pd.to_datetime('2019-06-11'), ls='dashed', color='k', lw=2, alpha=0.5)
ax5.axvline(x=pd.to_datetime('2019-07-16'), ls='dashed', color='k', lw=2, alpha=0.5)

ax1.set_yticks(np.arange(0, 0.33, 0.1))
ax2.set_yticks(np.arange(0, 2.3, 0.6))
ax3.set_yticks(np.arange(0, 1, 0.3))
ax4.set_yticks(np.arange(0, 0.7, 0.2))
ax5.set_yticks(np.arange(0, 2.2, 0.6))

ax1.text(0.5, 0.75, "Lake 8", transform=ax1.transAxes,
    fontsize=12, ha='center', va='bottom')
ax2.text(0.5, 0.75, "Lake 9", transform=ax2.transAxes,
    fontsize=12, ha='center', va='bottom')
ax3.text(0.5, 0.75, "Lake 10", transform=ax3.transAxes,
    fontsize=12, ha='center', va='bottom')
ax4.text(0.5, 0.75, "Lake 11", transform=ax4.transAxes,
    fontsize=12, ha='center', va='bottom')
ax5.text(0.6, 0.75, "Lake 12", transform=ax5.transAxes,
    fontsize=12, ha='center', va='bottom')


fig.text(0.06, 0.5, "Area (km$^2$)", va='center', rotation='vertical', fontsize=12)
ax1.legend(loc=4, fontsize=12)

# Custom formatter for multiline day/month
def multiline_date_formatter(x, pos=None):
    dt = mdates.num2date(x)
    return f"{dt.day}\n{dt.strftime('%b')}"
    
for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(multiline_date_formatter))
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, which="both", linestyle="--", linewidth=1, zorder=1)
    ax.set_xlim(pd.to_datetime('2019-06-01'), lake_df.index[-1])
    tick_labels = ax.get_yticklabels()
    for label in tick_labels:
        if label.get_text() == '0.0':
            label.set_text('')
    ax.set_yticklabels(tick_labels)

plt.savefig(path1 + 'skysat/figures/isolated-lakes/' + 'figX-isolated-lakes.svg')

plt.show()



