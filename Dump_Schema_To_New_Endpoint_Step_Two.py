import os
import json
import weaviate
import sys
import json

weaviate_url = "<CLOUD_URL>"
weaviate_key = "<API_KEY>"
weaviate_port = "<Port>" # Port is only required for local instances

# weaviate_url = os.environ.get("WEAVIATE_URL", "localhost")
# weaviate_key = os.environ.get("WEAVIATE_API_KEY", "")
# weaviate_port = os.environ.get("WEAVIATE_PORT", "8080")

if weaviate_url != "localhost":
    # Setting up client for cloud
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

# Pass the path to the JSON file DumpSchema.json as an argument
file = str(sys.argv[1])

if not file:
    print("Please provide the path to the JSON file as an argument")
    sys.exit(1)

# Get the path of the current script
script_path = os.path.dirname(os.path.abspath(__file__))
# Create a file path for the dump file in the same directory as the script
file_path = os.path.join(script_path, file)

if not os.path.exists(file_path):
    print(f"File {file_path} does not exist")
    sys.exit(1)

# Load the JSON file
with open(file_path) as file:
    data = json.load(file)

# Iterate over each collection in the JSON data
for collection_name, values in data.items():

    if not client.collections.exists(collection_name):
        print(
            f"Collection {collection_name} does not exist. Creating its schema first."
        )
        collection = client.collections.create_from_dict(values)
    else:
        collection = client.collections.get(collection_name)

    print(f"Collection {collection_name} loaded.")

client.close()