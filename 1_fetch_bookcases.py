import os
import geojson
import requests
import shutil

SSL_VERIFY = False

# Constants
PICTURE_PREFIX = 'https://delivrez.fr/public/posts/'
TYPES = {
    'INE': {'folder': 'edibles', 'name': 'INE: Incredible Edible'},
    'DSB': {'folder': 'giveboxes', 'name': 'DSB: give boxes'},
    'BSB': {'folder': 'bookcases', 'name': 'BSB: public bookcases'},
    'SES': {'folder': 'seedboxes', 'name': 'SES: seedboxes'}
}

# URL to fetch data from
DATA_URL = 'https://delivrez.fr/boundary/json?east=180&west=-180&north=90&south=-90'

# Delete and recreate folders
for type_info in TYPES.values():
    folder = type_info['folder']
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

# Fetch data from URL
response = requests.get(DATA_URL, verify=SSL_VERIFY)
data = response.json()

# Check if there are any bookcases
if not data:
    print('Error: No bookcases found.')
    exit(1)

# Initialize GeoJSON collections
geojson_collections = {type_code: geojson.FeatureCollection([]) for type_code in TYPES}
unknown_types = set()

# Process each data entry
for d in data:
    # Create feature with all properties copied, removing null or "-" values
    feature_properties = {k: v for k, v in d.items() if v and v != "-"}

    # Prefix the picture property if it exists
    if 'picture' in feature_properties:
        feature_properties['picture'] = PICTURE_PREFIX + feature_properties['picture']
    
    feature = geojson.Feature(
        geometry=geojson.Point((float(d['lon']), float(d['lat']))),
        properties=feature_properties
    )

    type_code = next((key for key in TYPES if key in d['type']), None)
    if type_code:
        geojson_collections[type_code].features.append(feature)
    else:
        unknown_types.add(d['type'])

# Dump GeoJSON files to respective folders
for type_code, collection in geojson_collections.items():
    folder = TYPES[type_code]['folder']
    geojson_file_path = os.path.join(folder, f"{folder}.geojson")
    with open(geojson_file_path, 'w', encoding='utf-8') as file:
        geojson.dump(collection, file, indent=2, ensure_ascii=False)

# Print unknown types if any
if unknown_types:
    print(f"Unknown types found: {', '.join(unknown_types)}")

# Print summary
print('Objects found:')
for type_code, type_info in TYPES.items():
    folder = type_info['folder']
    name = type_info['name']
    count = len(geojson_collections[type_code].features)
    print(f'- {count} {name}')
print('Geojson files created in respective folders')
