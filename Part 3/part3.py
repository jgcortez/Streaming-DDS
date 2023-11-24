from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client['streaming_dds']
playlists_collection = db.playlists

# Function to measure query execution time in milliseconds
def measure_query_time(query):
    start_time = time.time()
    list(playlists_collection.find(query))  # Execute the query and convert to list
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert seconds to milliseconds

# Measure time before indexing
time_before_indexing = measure_query_time({"name": {"$regex": "^S"}})
print(f"Time before indexing: {time_before_indexing:.2f} milliseconds")

# Creating an index on the 'name' field
playlists_collection.create_index([('name', 1)])

# Measure time after indexing
time_after_indexing = measure_query_time({"name": {"$regex": "^S"}})
print(f"Time after indexing: {time_after_indexing:.2f} milliseconds")

# Drop the index after testing (optional)
playlists_collection.drop_index([('name', 1)])
