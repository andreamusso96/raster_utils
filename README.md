## Raster utils
This repository contains a set of scripts that can be used to work with raster data in python.
The scripts are essentially wrappers around other libraries that contain the main functionalities.

## Installation
To install the package just clone the repostiory on your computer running
```bash
git clone https://github.com/andreamusso96/raster_utils.git
```

Then navigate to the directory and run
```bash
pip install -e .
```
The -e flag is used to install the package in editable mode, so that you can modify the code and see the changes without having to reinstall the package.

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

