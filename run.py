import os
import argparse
from collections import defaultdict

def read_file(file_path):
    """Reads the contents of a file and returns a list of lines."""
    with open(file_path, 'r') as file:
        return file.readlines()

def split_cmdb_eon_map(file_data):
    """Splits the CMDB EON map data into a dictionary."""
    cmdb_eon_map = {}
    for data in file_data:
        if data.strip() and not data.startswith('#'):
            cm_id, eon_id = data.split(":")[:2]
            cmdb_eon_map[cm_id] = eon_id.strip()
    return cmdb_eon_map

def split_asset_map(line):
    """Splits the asset map line and returns a tuple of relevant parts."""
    parts = line.strip().split(':')
    if len(parts) >= 7:  # Ensure at least 7 parts exist
        return tuple(parts[i] for i in [0, 3, 4, 5])

def process_deployment_file(file_data):
    """Processes the deployment file data and constructs a deployment map."""
    deployment_map = defaultdict(lambda: defaultdict(set))
    for data in file_data:
        if data.strip() and not data.startswith("#"):
            split_data = data.split(":")
            if len(split_data) >= 5:
                e, a, s, i, host = split_data[:5]
                key = f"{a}_{s}_{i}"
                deployment_map[key][e].add(host)
    return deployment_map

def main(args):
    """Main function to process files in the specified directory."""
    directory = args.directory
    assetmep_path = os.path.join(directory, 'assetmap.txt')
    deployments_path = os.path.join(directory, 'deployments.txt')
    cmdb_eon_map_path = os.path.join(directory, 'cmdb_eon_map.txt')

    # Read contents of each file
    assetmep_path_data = read_file(assetmep_path)
    deployments_path_data = read_file(deployments_path)
    cmdb_eon_map_path_data = read_file(cmdb_eon_map_path)

    # Process CMDB EON map data
    cmdb_eon_map = split_cmdb_eon_map(cmdb_eon_map_path_data)

    # Process deployment file data
    deployment_map = process_deployment_file(deployments_path_data)

    # Generate output
    output = ""
    for asset in assetmep_path_data:
        if not asset.strip() and asset.startswith('#'):
            continue
        assets_tuple = split_asset_map(asset)
        if assets_tuple:  # Check if split_asset_map() returned a tuple
            id, a, s, i = assets_tuple
            if id in cmdb_eon_map:
                cmdb_id = cmdb_eon_map[id]
            else:
                continue
            key = f"{a}_{s}_{i}"
            if key in deployment_map:
                for value in deployment_map[key]:
                    output += f'{cmdb_id}:{value}:{a}:{s}:{i}:{",".join(list(deployment_map[key][value]))}\n'
    print(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files in a directory.")
    parser.add_argument("-d", "--directory", type=str, required=True, help="Path to the directory containing the files.")
    args = parser.parse_args()
    main(args)
