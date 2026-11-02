#!/usr/bin/env bash
# Download USDA FoodData Central SR Legacy (public domain) into a local cache for scripts/usda_lookup.py.
set -euo pipefail
CACHE="${USDA_CACHE:-$HOME/.cache/chef-usda}"
mkdir -p "$CACHE"
cd "$CACHE"
if [ ! -d FoodData_Central_sr_legacy_food_csv_2018-04 ]; then
  curl -sS -L -o sr_legacy.zip "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip"
  unzip -q -o sr_legacy.zip
fi
echo "USDA SR Legacy ready in $CACHE"
