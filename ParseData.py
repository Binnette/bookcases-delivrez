'''
This script take the 'data.json' source file from `dirData` and parse it.
It will create geojson file as output.
'''
import geopandas as gpd
import json
import os

########################
# Parameters
########################
dirData = '2023-01-29'

########################
# Constantes
########################
dirAsset = 'assets'
dirRegion = 'regions'

edibleFile = 'edibles.geojson'
giveboxFile = 'giveboxes.geojson'
bookcasesFile = 'bookcases.geojson'

def newGeojsonStruct():
    return {
        'type': 'FeatureCollection',
        'features': []
    }

def convertJsonToGeoJson():
    print('Read source file data.json in folder: ' + dirData)
    with open(dirData + '/data.json') as file:
        data = json.load(file)

    attrs = []
    types = []

    bookcases = newGeojsonStruct()
    giveboxes = newGeojsonStruct()
    edibles = newGeojsonStruct()

    for d in data:
        attrs.extend(list(d.keys()))
        type = d['type']
        types.append(type)
        feature = {
            'type': 'Feature',
                    'properties': {
                        'title': d['title'],
                        'type': d['type'],
                        'observation': d['observation'],
                        'picture': d['picture']
                    },
            'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            float(d['lon']),
                            float(d['lat'])
                        ]
                    }
        }
        if 'INE' in type:
            edibles['features'].append(feature)
        if 'DSB' in type:
            giveboxes['features'].append(feature)
        if 'BSB' in type:
            bookcases['features'].append(feature)

    attrs = set(attrs)
    types = set(types)
    print('Dataset attributes: ' + ', '.join(attrs))
    print('Dataset types: ' + ', '.join(types))
    print('Objects found :')
    print('- ' + str(len(edibles['features'])) + ' INE: Incredible Edible')
    print('- ' + str(len(giveboxes['features'])) + ' DSB: give box (not only books)')
    print('- ' + str(len(bookcases['features'])) + ' BSB: public bookcase')

    dumpGeojsonToFile(edibles, os.path.join(dirData, edibleFile))
    dumpGeojsonToFile(giveboxes, os.path.join(dirData, giveboxFile))
    dumpGeojsonToFile(bookcases, os.path.join(dirData, bookcasesFile))

    print('Geojson files created in folder: ' + dirData)

def dumpGeojsonToFile(data, path):
    with open(path, 'w') as out:
        json.dump(data, out, indent=2, ensure_ascii=True)

def filterBookcasesByArea():
    print('Start of filtering bookcases by region')
    pathRegion = os.path.join(dirAsset, dirRegion)
    pathBookcase = os.path.join(dirData, bookcasesFile)
    areaFilename = os.listdir(pathRegion)

    print('Filter bookcases by region:')
    for areaName in areaFilename:
        areaFile = os.path.join(dirAsset, dirRegion, areaName)
        if os.path.isfile(areaFile):
            region = gpd.read_file(areaFile)
            regionName = os.path.basename(areaName)
            bookcases_filtered = gpd.read_file(pathBookcase, mask=region)
            print(' - ' + str(bookcases_filtered.size) + ' bookcases in ' + regionName)
            bookcases_filtered.to_file(os.path.join(dirData, dirRegion, areaName), driver='GeoJSON')
            bookcases_filtered.to_file(os.path.join(dirData, dirRegion, regionName + ".gpx"), driver='GPX', GPX_USE_EXTENSIONS=True)

    print('End of filtering bookcases by region')


print('Start parsing data.json from folder: ' + dirData)

pathRegion = os.path.join(dirData, dirRegion)
if not os.path.exists(pathRegion):
    print('Create folder: ' + pathRegion)
    os.makedirs(pathRegion)

convertJsonToGeoJson()
filterBookcasesByArea()

print('End of parsing')