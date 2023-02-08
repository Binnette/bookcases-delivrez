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
baseUrl = 'https://delivrez.fr/public/posts/'

gpxNs = 'osmand'
gpxNsUrl = 'https://osmand.net'

edibleFile = 'edibles'
giveboxFile = 'giveboxes'
bookcasesFile = 'bookcases'


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
                'name': d['title'],
                'codetype': d['type'],
                'type': 'Delivrez',
                'desc': d['observation'],
                'color': '#00842b',
                'background': 'square'
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    float(d['lon']),
                    float(d['lat'])
                ]
            }
        }
        if d['picture'] is not None:
            feature['properties']['website'] = baseUrl + d['picture']
        if 'INE' in type:
            feature['properties']['type'] += ' edible'
            edibles['features'].append(feature)
        if 'DSB' in type:
            feature['properties']['type'] += ' givebox'
            giveboxes['features'].append(feature)
        if 'BSB' in type:
            feature['properties']['type'] += ' bookcase'
            feature['properties']['amenity_subtype'] = 'public_bookcase'
            feature['properties']['icon'] = 'public_bookcase'
            bookcases['features'].append(feature)

    attrs = set(attrs)
    types = set(types)
    print('Dataset attributes: ' + ', '.join(attrs))
    print('Dataset types: ' + ', '.join(types))
    print('Objects found :')
    print('- ' + str(len(edibles['features'])) + ' INE: Incredible Edible')
    print('- ' + str(len(giveboxes['features'])) + ' DSB: give box (not only books)')
    print('- ' + str(len(bookcases['features'])) + ' BSB: public bookcase')

    dumpGeojsonToFile(edibles, os.path.join(dirData, edibleFile + '.geojson'))
    dumpGeojsonToFile(giveboxes, os.path.join(dirData, giveboxFile + '.geojson'))
    dumpGeojsonToFile(bookcases, os.path.join(dirData, bookcasesFile + '.geojson'))

    print('Geojson files created in folder: ' + dirData)


def dumpGeojsonToFile(data, path):
    with open(path, 'w') as out:
        json.dump(data, out, indent=2, ensure_ascii=True)


def dumpToGpx(data, path):
    data.to_file(path, driver='GPX', GPX_USE_EXTENSIONS=True, GPX_EXTENSIONS_NS=gpxNs, GPX_EXTENSIONS_NS_URL=gpxNsUrl)


def convertGeojsonToGpx(file):
    print('Convert ' + file + ' from geojson to GPX')
    path = os.path.join(dirData, file + '.geojson')
    bookcases = gpd.read_file(path)
    path = os.path.join(dirData, file + '.gpx')
    dumpToGpx(bookcases, path)


def filterBookcasesByArea():
    print('Start of filtering bookcases by region')
    pathRegion = os.path.join(dirAsset, dirRegion)
    pathBookcase = os.path.join(dirData, bookcasesFile + '.geojson')
    areaFilename = os.listdir(pathRegion)

    print('Filter bookcases by region:')
    for areaName in areaFilename:
        areaFile = os.path.join(dirAsset, dirRegion, areaName)
        if os.path.isfile(areaFile):
            region = gpd.read_file(areaFile)
            regionName = os.path.basename(areaName)
            regionName = os.path.splitext(regionName)[0]
            bookcases_filtered = gpd.read_file(pathBookcase, mask=region)
            bookcases_filtered['type'] += ' ' + regionName
            print(' - ' + str(bookcases_filtered.size) + ' bookcases in ' + regionName)
            bookcases_filtered.to_file(os.path.join(dirData, dirRegion, areaName), driver='GeoJSON')
            filepath = os.path.join(dirData, dirRegion, regionName + '.gpx')
            dumpToGpx(bookcases_filtered, filepath)

    print('End of filtering bookcases by region')


print('Start parsing data.json from folder: ' + dirData)

pathRegion = os.path.join(dirData, dirRegion)
if not os.path.exists(pathRegion):
    print('Create folder: ' + pathRegion)
    os.makedirs(pathRegion)

convertJsonToGeoJson()
convertGeojsonToGpx(bookcasesFile)
convertGeojsonToGpx(edibleFile)
convertGeojsonToGpx(giveboxFile)
filterBookcasesByArea()

print('End of parsing')
