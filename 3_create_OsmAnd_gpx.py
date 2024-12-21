import json
import os

# Constants for each type
TYPES = {
    'bookcases': {'folder': 'bookcases', 'color': '#ff5020', 'icon': 'public_bookcase', 'type_name': 'Delivrez bookcases'},
    'edibles': {'folder': 'edibles', 'color': '#00ff00', 'icon': 'shop_greengrocer', 'type_name': 'Delivrez edibles'},
    'giveboxes': {'folder': 'giveboxes', 'color': '#0000ff', 'icon': 'outpost', 'type_name': 'Delivrez giveboxes'},
    'seedboxes': {'folder': 'seedboxes', 'color': '#ffa500', 'icon': 'club_nature', 'type_name': 'Delivrez seedboxes'}
}

REGIONS_FOLDER = 'Régions Françaises/'

def save_file(filepath, content):
    try:
        with open(filepath, 'w+', encoding='utf-8') as f:
            f.write(content)
        print(f'OK {filepath}')
    except Exception as err:
        print(f'KO {filepath} {err}')

def generate_gpx(features, color, icon, type_name):
    header = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<gpx version="1.1" creator="Binnette" xmlns="http://www.topografix.com/GPX/1/1" xmlns:osmand="https://osmand.net" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">"""
    footer = f"""  <extensions>
    <osmand:points_groups>
      <group name="{type_name}" color="{color}" icon="{icon}" background="square" />
    </osmand:points_groups>
  </extensions>
</gpx>"""
    content = [header]
    
    for feature in features:
        lat = feature['geometry']['coordinates'][1]
        lon = feature['geometry']['coordinates'][0]
        props = feature['properties']
        name = ""
        if 'title' in props:
            name = props['title'].replace('&', ' et ')
        desc = ""
        if 'observation' in props:
            desc = props['observation'].replace('&', ' et ')
        
        wpt = f"""  <wpt lat="{lat}" lon="{lon}">
    <name>{name}</name>
    <desc>{desc}</desc>
    <type>{type_name}</type>
    <extensions>
      <osmand:color>{color}</osmand:color>
      <osmand:background>square</osmand:background>
      <osmand:icon>{icon}</osmand:icon>
    </extensions>
  </wpt>"""
        content.append(wpt)
    
    content.append(footer)
    return '\n'.join(content)

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as err:
        print(err)
        return None

def process_files(folder, color, icon, type_name):
    main_files = [f for f in os.listdir(folder) if f.endswith('.geojson')]
    region_files = [f for f in os.listdir(os.path.join(folder, REGIONS_FOLDER)) if f.endswith('.geojson')]

    for file in main_files:
        path = os.path.join(folder, file)
        data = read_file(path)
        if data:
            converted = generate_gpx(data['features'], color, icon, type_name)
            gpx_path = os.path.join(folder, f'{os.path.splitext(file)[0]}.gpx')
            save_file(gpx_path, converted)

    for file in region_files:
        path = os.path.join(folder, REGIONS_FOLDER, file)
        data = read_file(path)
        if data:
            converted = generate_gpx(data['features'], color, icon, type_name)
            gpx_path = os.path.join(folder, REGIONS_FOLDER, f'{os.path.splitext(file)[0]}.gpx')
            save_file(gpx_path, converted)

for type_name, type_info in TYPES.items():
    process_files(type_info['folder'], type_info['color'], type_info['icon'], type_info['type_name'])

print("Done.")
