## Raster utils
This repository contains a set of scripts that can be used to work with raster data in python.
The scripts are essentially wrappers around other libraries that contain the main functionalities.

## Installation
To install the package just run
```bash
pip install git+https://github.com/andreamusso96/raster_utils.git
```

## Usage
Here is a list of the main functionalities provided by the package.

### Dumping and loading rasters from postgis
To dump a raster to a postgis database you can use the following function
```python
dump_raster_to_postgis(con, data: xr.DataArray, table_name: str)
```
To load a raster from a postgis database you can use the following function
```python
load_raster_from_postgis(con, raster_table: str, raster_column: str = 'rast') -> xr.DataArray:
```
### Extracting zonal statistics
See ```raster_utils.utils``` for more information.

