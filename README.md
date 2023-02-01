# bookcases-delivrez
Public bookcases extracted from delivrez.fr

## How to use this script

1. Create a folder for current date. Example: 2023-01-29
1. Open this link: https://delivrez.fr/boundary/json?east=180&west=-180&north=90&south=-90
1. Save the file in the newly created folder as `data.json`
1. Edit ParseData.py: change dirData value to the new date
1. Run the script ParseData.py

The script will create `geojson` files in the new folder.

- `bookcases.geojson` contains all bookcase
- `giveboxes.geojson` contains all give boxes
- `edibles.geojson` contains location of Incredible Edibles

You will find in folder `region` all bookcases filtered by region.

## About region files in asset folder

You can add your own 'regions' in the `asset/region` folder.
For example another country, etc.

To do so:

1. Create or find a shape (geojson or other)
1. Open your shape with JOSM
1. Select your shape in JOSM
1. In the menu, click on '**Create a multipolygon**'
1. Export your layer as `geojson` file

Note, if you use a geojson file as a region, you have to convert it as a multipolygon with this technique.
Otherwise GeoPandas will not be able to parse them correctly.
