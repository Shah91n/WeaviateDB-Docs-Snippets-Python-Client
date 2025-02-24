import weaviate
import csv
from weaviate.classes.config import Configure, Property, DataType, Tokenization

# Global Weavaiate credentials and variables
WEAVIATE_URL = "<URL>"
WEAVIATE_API_KEY = "KEY"
OPENAI_API_KEY = "KEY"

def initialize_client():
    """
    Initialize the Weaviate client.
    """
    client = weaviate.connect_to_wcs(
        cluster_url=WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
    )
    # Check client readiness and server versions
    ready = client.is_ready()
    server_version = client.get_meta()["version"]
    client_version = weaviate.__version__

    if not ready:
        raise Exception("Weaviate client is not ready.")
    print(f"Weaviate client is ready: {ready}")
    print(f"Weaviate Client Version: {client_version}")
    print(f"Weaviate Server Version: {server_version}")

    return client

def create_collection(client, collection_name):
    """
    Define the schema and create the collection
    """
    coll = client.collections.create(
        collection_name,
        vectorizer_config=Configure.Vectorizer.text2vec_openai(),
        properties=[
            Property(name="company_id", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="last_name", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="first_name", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="job_title", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="email_address", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="country", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="interaction_notes", data_type=DataType.TEXT, tokenization=Tokenization.WORD)
        ],
        replication_config=Configure.replication(3)
    )
    print(f"Collection '{collection_name}' created successfully.")

def batch_upload(client, file_path, collection_name, batch_size=10):
    """
    Batch upload data from a CSV file into the specified collection.
    """
    if not client.collections.exists(collection_name):
        raise Exception(f"Collection '{collection_name}' does not exist. Cannot insert data.")

    failed_objects = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Normalize column headers
            csv_reader.fieldnames = [header.strip().lower() for header in csv_reader.fieldnames]

            with client.batch.fixed_size(batch_size=100, concurrent_requests=2) as batch:
                for i, row in enumerate(csv_reader):
                    # Prepare object properties
                    obj_properties = {
                        "company_id": row.get("company_id", ""),
                        "last_name": row.get("last_name", ""),
                        "first_name": row.get("first_name", ""),
                        "job_title": row.get("job_title", ""),
                        "email_address": row.get("email_address", ""),
                        "country": row.get("country", ""),
                        "interaction_notes": row.get("interaction_notes", ""),
                    }
                    batch.add_object(
                        properties=obj_properties,
                        collection=collection_name
                    )
                print(f"Batch processing completed. {i + 1} objects added.")
    except Exception as e:
        raise Exception(f"Batch insertion failed: {e}")

    # Check for failed objects and reason behind to be printed out
    failed_objects = client.batch.failed_objects
    if failed_objects:
        print(f"Number of failed objects: {len(failed_objects)}")
        for i, failed_obj in enumerate(failed_objects, 1):
            print(f"Failed object {i}: {failed_obj}")
    else:
        print(f"All objects successfully inserted into '{collection_name}'.")

if __name__ == "__main__":
    collection_name = "<COLLECTION_NAME>"  # Update the collection name
    CSV_FILE_PATH = "<PATH>.csv"  # Update this path when requires
    # Initialize the client
    client = initialize_client()
    # Create the collection
    create_collection(client, collection_name)
    # Perform batch upload
    batch_upload(client, CSV_FILE_PATH, collection_name)