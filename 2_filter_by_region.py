import os
import geojson
from shapely.geometry import shape, Point, Polygon
from datetime import datetime
import csv

# Constants
bookcases_folder = "bookcases"
edibles_folder = "edibles"
giveboxes_folder = "giveboxes"
seedboxes_folder = "seedboxes"

# Define the order of the columns
column_order = ['date', 'total', 'out_of_region', 'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Bretagne', 'Centre-Val de Loire', 'Corse', 'Grand Est', 'Hauts-de-France', 'Île-de-France', 'Normandie', 'Nouvelle-Aquitaine', 'Occitanie', 'Pays de la Loire', 'Provence-Alpes-Côte d\'Azur']

# Paths to the input files
regions_file_path = 'assets/georef-france-region-custom.geojson'

# CSV output paths for each type
csv_output_paths = {
    'bookcases': 'assets/bookcase_count_history.csv',
    'edibles': 'assets/edibles_count_history.csv',
    'giveboxes': 'assets/giveboxes_count_history.csv',
    'seedboxes': 'assets/seedboxes_count_history.csv'
}

# Load the regions data
with open(regions_file_path, 'r', encoding='utf-8') as f:
    regions_data = geojson.load(f)

# Function to check if a point is inside a region
def is_point_in_region(point, region_shape):
    return region_shape.contains(point)

# Preprocess regions to convert geometries to shapes
regions_shapes = [
    (region['properties']['reg_name'], shape(region['geometry']) if region['geometry']['type'] != 'LineString' else Polygon(region['geometry']['coordinates']))
    for region in regions_data['features']
]

# Function to filter by region and write to GeoJSON
def filter_and_write_to_geojson(folder):
    # Paths to the input files
    geojson_file_path = f'{folder}/{folder}.geojson'
    output_dir = f'{folder}/Régions Françaises'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the data
    with open(geojson_file_path, 'r', encoding='utf-8') as f:
        data = geojson.load(f)
    
    # Initialize GeoJSON structures
    out_of_region = geojson.FeatureCollection([])
    
    total = len(data['features'])
    
    # Dictionary to hold features for each region
    region_features = {region_name: geojson.FeatureCollection([]) for region_name, _ in regions_shapes}
    
    # Process each feature
    for feature in data['features']:
        point = Point(feature['geometry']['coordinates'])
        in_any_region = False
        for region_name, region_shape in regions_shapes:
            if is_point_in_region(point, region_shape):
                region_features[region_name].features.append(feature)
                in_any_region = True
                break
        if not in_any_region:
            out_of_region.features.append(feature)
    
    # Export features to .geojson files for each region
    for region_name, features in region_features.items():
        geojson_output_path = os.path.join(output_dir, f'{region_name}.geojson')
        with open(geojson_output_path, 'w', encoding='utf-8') as f:
            geojson.dump(features, f, indent=2, ensure_ascii=False)
    
    # Export out-of-region features to .geojson
    out_geojson_output_path = f'{folder}/out-france-metro.geojson'
    with open(out_geojson_output_path, 'w', encoding='utf-8') as f:
        geojson.dump(out_of_region, f, indent=2, ensure_ascii=False)
    
    # Return the results for CSV
    return total, len(out_of_region['features']), {region_name: len(features['features']) for region_name, features in region_features.items()}

# Filter and process each folder
total_bookcases, out_of_region_bookcases, region_bookcases_counts = filter_and_write_to_geojson(bookcases_folder)
total_edibles, out_of_region_edibles, region_edibles_counts = filter_and_write_to_geojson(edibles_folder)
total_giveboxes, out_of_region_giveboxes, region_giveboxes_counts = filter_and_write_to_geojson(giveboxes_folder)
total_seedboxes, out_of_region_seedboxes, region_seedboxes_counts = filter_and_write_to_geojson(seedboxes_folder)

# Get the current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Prepare data for CSV
def prepare_csv_data(total, out_of_region, region_counts):
    return [
        current_date,
        total,
        out_of_region
    ] + [
        region_counts.get(region_name, 0)
        for region_name in column_order[3:]
    ]

bookcases_csv_row = prepare_csv_data(total_bookcases, out_of_region_bookcases, region_bookcases_counts)
edibles_csv_row = prepare_csv_data(total_edibles, out_of_region_edibles, region_edibles_counts)
giveboxes_csv_row = prepare_csv_data(total_giveboxes, out_of_region_giveboxes, region_giveboxes_counts)
seedboxes_csv_row = prepare_csv_data(total_seedboxes, out_of_region_seedboxes, region_seedboxes_counts)

# Write data to respective CSV files
for type_name, csv_row in zip(['bookcases', 'edibles', 'giveboxes', 'seedboxes'], [bookcases_csv_row, edibles_csv_row, giveboxes_csv_row, seedboxes_csv_row]):
    csv_output_path = csv_output_paths[type_name]
    
    # Create CSV header if the file doesn't exist
    if not os.path.exists(csv_output_path):
        with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_order)
    
    # Write the data row to the CSV
    with open(csv_output_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_row)

# Print completion message
for type_name in ['bookcases', 'edibles', 'giveboxes', 'seedboxes']:
    print(f"CSV file for {type_name} updated at {csv_output_paths[type_name]}")

print("Processing complete!")
