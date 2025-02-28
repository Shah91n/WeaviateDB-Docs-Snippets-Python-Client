import os
import json
import weaviate

weaviate_url = "<CLOUD_URL>"
weaviate_key = "<API_KEY>"
weaviate_port = "<Port>" # Port is only required for local instances

# weaviate_url = os.environ.get("WEAVIATE_URL", "localhost")
# weaviate_key = os.environ.get("WEAVIATE_API_KEY", "")
# weaviate_port = os.environ.get("WEAVIATE_PORT", "8080")

if weaviate_url != "localhost":
    # Setting up client for wcs
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=weaviate.auth.AuthApiKey(api_key=weaviate_key),
        skip_init_checks=True,
    )
else:
    client = weaviate.connect_to_local(
        host=weaviate_url,
        port=weaviate_port,
        auth_credentials=(
            weaviate.auth.AuthApiKey(api_key=weaviate_key) if weaviate_key else None
        ),
    )

dumped_collections = {}

# Retrieve all collections from the cluster
collections = client.collections.list_all()
for collection_name in collections:
    collection = client.collections.get(collection_name)

    dumped_collections[collection_name] = {}
    dumped_collections[collection_name]["schema"] = client.collections.export_config(
        collection_name
    ).to_dict()

# Get the path of the current script
script_path = os.path.dirname(os.path.abspath(__file__))

# Create a file path for the dump file in the same directory as the script
dump_file_path = os.path.join(
    script_path, "DumpSchema" + ".json"
)

# Write the dumped collections to the dump file
with open(dump_file_path, "w") as dump_file:
    json.dump(dumped_collections, dump_file)

print(f"Dump file generated at {dump_file_path}")

client.close()