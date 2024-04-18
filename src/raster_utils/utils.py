from typing import List

import geopandas as gpd
import rasterio
import numpy as np
import xarray as xr
from geocube.api.core import make_geocube
from geocube.rasterize import rasterize_image
import rasterstats
import shapely
import pandas as pd


def rasterize_points(gdf: gpd.GeoDataFrame, measurements: List[str], tile_size: float, no_data: float, epsg: int) -> xr.DataArray:
    raster = make_geocube(
        vector_data=gdf,
        measurements=measurements,
        resolution=(-tile_size, tile_size),
        output_crs=f"epsg:{epsg}",
        rasterize_function=rasterize_image,
        fill=no_data
    ).to_array()
    return raster


def extract_zonal_stats(raster: xr.DataArray, no_data: float, vector: gpd.GeoDataFrame) -> pd.DataFrame:
    _check_xarray_is_2d_raster(raster=raster)
    mean_val = rasterstats.zonal_stats(vectors=vector.geometry, raster=raster.values, affine=raster.rio.transform(), nodata=no_data, stats=['mean'], all_touched=True)
    mean_val = pd.DataFrame([r['mean'] for r in mean_val], columns=['mean_raster_value'], index=vector.index)
    vector_with_zonal_stats = gpd.GeoDataFrame(pd.merge(vector, mean_val, left_index=True, right_index=True, how='left'))
    # Returns null for vectors that do not intersect the raster
    return vector_with_zonal_stats


def extract_vector_within_raster_coverage(raster: xr.DataArray, vector: gpd.GeoDataFrame, coverage_threshold: float = 0.8) -> gpd.GeoDataFrame:
    _check_xarray_is_2d_raster(raster=raster)
    binary_raster_np = np.where(np.isnan(raster.values), 0, 1).astype(rasterio.uint8)
    level_curve_vector = gpd.GeoDataFrame([{'geometry': shapely.geometry.shape(s), 'value': v} for s, v in rasterio.features.shapes(binary_raster_np, mask=None, transform=raster.rio.transform())], crs=raster.rio.crs)
    level_curve_vector['geometry'] = level_curve_vector['geometry'].buffer(1)
    raster_coverage = level_curve_vector[level_curve_vector.value == 1].unary_union
    vector = vector.loc[vector.intersection(raster_coverage).area / vector.area > coverage_threshold].copy()
    return vector


def _check_xarray_is_2d_raster(raster: xr.DataArray):
    assert raster.ndim == 2, "The input raster must be 2D"
    assert raster.rio is not None, "The input raster must have a CRS"
    assert raster.rio.transform() is not None, "The input raster must have a transform"
    assert raster.rio.crs is not None, "The input raster must have a CRS"