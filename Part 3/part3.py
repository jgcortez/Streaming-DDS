from pymongo import MongoClient
import time

# Connect to the MongoDB cluster
client = MongoClient('mongodb://localhost:27017/')
db = client['streaming_dds']
playlists_collection = db['playlists']

# Function to measure query execution time
def measure_query_time(collection, query):
    start_time = time.time()
    list(collection.find(query))  # Execute the query
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert to milliseconds

# Measure query time before indexing
query = {"name": "Sample Playlist Name"}  # Replace with your query
time_before_indexing = measure_query_time(playlists_collection, query)
print(f"Time before indexing: {time_before_indexing:.2f} milliseconds")

playlists_collection.create_index([('name', 1)])

# Measure query time after indexing
time_after_indexing = measure_query_time(playlists_collection, query)
print(f"Time after indexing: {time_after_indexing:.2f} milliseconds")
