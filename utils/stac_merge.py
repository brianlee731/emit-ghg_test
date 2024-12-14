import json
import logging
import os
import sys


from pystac import ItemCollection, Catalog, get_stac_version
from pystac.errors import STACTypeError


def read_stac(stac_file):
    root_catalog = None
    try:
      root_catalog = Catalog.from_file(stac_file)
      id = root_catalog.id
      items = root_catalog.get_all_items()
    except STACTypeError as e:
      pass
    # attempt to read as a feature collection

    # ItemCollection
    if root_catalog is None:
       with open(stac_file, 'r') as f:
          data = json.load(f)
          ic = ItemCollection.from_dict(data)
          try:
             id = data['features'][0]['collection']
          except:
             pass
       
          items = ic.items
    return items


#from unity_sds_client.resources.dataset import Dataset
#from unity_sds_client.resources.data_file import DataFile

# stage_in packages
#from unity_sds_client.resources.collection import Collection

if len(sys.argv) < 2:
    print("stac_merge requires at least 2 arguments:")
    print("stac_merge.py output_dir stac_file1 ... <stac_filen>")
    sys.exit(0)
    
# inputs
#"/unity/ads/input_collections/SBG-L2-RSRFL/catalog.json", "/unity/ads/input_collections/SBG-L1B-PRE/catalog.json"]
stac_files = sys.argv[2:]

#"/unity/ads/input_collections/REFLECT_CORRECT_MERGE"
output_location = sys.argv[1]

if len(stac_files) == 0:
    print("Not enough stac files given, nothing to do")
    sys.exit()

items = []
for x in stac_files:
    stac_items = read_stac(x)
    items = items + stac_items 
#master_collection = Collection.from_stac(stac_files[0])
#
#for file in stac_files[1:]:
#  temp_collection = Collection.from_stac(file)
#  for ds in temp_collection.datasets:
#    master_collection.add_dataset(d)s
#Collection.to_stac(master_collection, output_location)
ItemCollection(items).save_object(dest_href=output_location+'/catalog.json')

