import rasterio
import xarray as xr
import rioxarray as riox

from .utils import _check_xarray_is_2d_raster


def load_raster_from_postgis(con, raster_table: str, raster_column: str = 'rast') -> xr.DataArray:
    with con.cursor() as cursor:
        cursor.execute(f"SELECT ST_AsGDALRaster({raster_column}, 'GTIff') FROM {raster_table}")
        raster = cursor.fetchone()

    in_memory_raster = rasterio.io.MemoryFile(bytes(raster[0]))
    raster_dataset = riox.open_rasterio(in_memory_raster)
    return raster_dataset


def dump_raster_to_postgis(con, data: xr.DataArray, table_name: str):
    _check_xarray_is_2d_raster(raster=data)

    raster_array = data.rio
    width, height = raster_array.width, raster_array.height
    bands = raster_array.count
    srid = raster_array.crs.to_epsg()
    nodata = raster_array.nodata
    with rasterio.io.MemoryFile() as memory_file:
        with memory_file.open(driver='GTiff', width=width, height=height, count=bands, dtype=raster_array._obj.dtype, crs=f'EPSG:{srid}', transform=raster_array.transform(), nodata=nodata) as dataset:
            dataset.write(raster_array._obj.expand_dims('band'))
        geotiff_data = memory_file.read()

    with con.cursor() as cursor:
        cursor.execute(f"CREATE TABLE {table_name} (rast raster);")
        cursor.execute(f"INSERT INTO {table_name} (rast) VALUES (ST_FromGDALRaster(%s))", (geotiff_data,))
        cursor.execute(f"SELECT AddRasterConstraints('{table_name}'::name, 'rast'::name);")
        con.commit()
