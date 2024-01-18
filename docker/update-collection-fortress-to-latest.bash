#!/bin/bash

if [ $# -eq 0 ]; then
    echo "No arguments provided for update"
    exit 0
fi


yaml_fixed="fixed-collection-fortress.yaml"
yaml_latest="latest-collection-fortress.yaml"

# Download latest collection-fortress yaml
wget https://raw.githubusercontent.com/ignition-tooling/gazebodistro/master/collection-fortress.yaml
mv collection-fortress.yaml $yaml_latest

# Generate fixed tags collection

# Components to update (e.g., "gz-sensors")
components_to_update=$@

for component in $components_to_update
do 
    latest_version=$(yq eval ".repositories.$component.version" "$yaml_latest")
    yq eval -i ".repositories.$component.version = \"$latest_version\"" "$yaml_fixed"
done