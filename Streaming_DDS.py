import json
from pymongo import MongoClient

# Function to load JSON files
def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Load data
playlists = load_file('Data/Playlist1.json')
search_queries = load_file('Data/SearchQueries.json')
streaming_history = load_file('Data/StreamingHistory0.json')

# Function to create (insert) data
def create(collection, data):
    def create_search_query(data):
        if 'searchTime' not in data or not data['searchTime']:
            print("Invalid data: 'searchTime' is missing or empty.")
            return
        
        if collection.find_one({'searchTime': data['searchTime']}):
            print(f"Search query at '{data['searchTime']}' already exists.")
            return
        
        collection.insert_one(data)


    def create_streaming_history(data):
        required_fields = ['endTime', 'artistName', 'trackName', 'msPlayed']
        if not all(field in data and data[field] for field in required_fields):
            print(f"Invalid data: Required fields {required_fields} must be present and non-empty.")
            return

        query = {field: data[field] for field in required_fields}
        if collection.find_one(query):
            print(f"Streaming history for '{data['trackName']}' by '{data['artistName']}' at '{data['endTime']}' with duration {data['msPlayed']}ms already exists.")
            return
        
        collection.insert_one(data)


    def create_playlist(data):
        # Validate playlist name
        if 'name' not in data or not data['name']:
            print("Invalid data: Playlist name is missing or empty.")
            return

        # Check for unique playlist name
        if collection.find_one({'name': data['name']}):
            print(f"Playlist '{data['name']}' already exists.")
            return

        # Validate items
        if 'items' not in data or not isinstance(data['items'], list):
            print("Invalid data: 'items' is missing or not a list.")
            return
        
        # Validate track names and check for duplicate items within the same playlist
        # track_names = [item['track']['trackName'] for item in data['items'] if item['track'] is not None]
        track_names = [item['track']['trackName'] for item in data['items'] if item.get('track') and 'trackName' in item['track']]
        if len(track_names) != len(set(track_names)):
            print(f"Duplicate tracks found in playlist '{data['name']}'.")
            return

        collection.insert_one(data)


    # Main logic for choosing which specialized function to call
    if isinstance(data, list):
        if collection.name == "playlists":
            for playlist in data:
                create_playlist(playlist)
        elif collection.name == "search_queries":
            for queries in data:
                create_search_query(queries)
        elif collection.name == "streaming_history":
            for str_hist in data:
                create_streaming_history(str_hist)
        else:
            collection.insert_many(data)
    else:
        if collection.name == "playlists":
            create_playlist(data)
        elif collection.name == "search_queries":
            create_search_query(data)
        elif collection.name == "streaming_history":
            create_streaming_history(data)
        else:
            print("New Collection Created: ", collection.name)
            collection.insert_one(data)


# Function to read (query) data
def read(collection, query={}, limit=1):
    return collection.find(query).limit(limit)

# Function to update data
def update(collection, query, new_values, update_many=False):
    if update_many:
        collection.update_many(query, new_values)
    else:
        collection.update_one(query, new_values)

# Function to delete data
def delete(collection, query, delete_many=False):
    if delete_many:
        collection.delete_many(query)
    else:
        collection.delete_one(query)


try:
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client['streaming_dds']

    # Create (Insert initial data) 
    # (!!: Comment out after first run to avoid inserting duplicates)
    create(db.playlists, playlists['playlists'])
    create(db.search_queries, search_queries)
    create(db.streaming_history, streaming_history)

    # Verify Connection and Data Insertion
    print("\nCollections in spotify_clone_db:", db.list_collection_names())
    print("Number of documents in playlists:", db.playlists.count_documents({}))
    print("Number of documents in search_queries:", db.search_queries.count_documents({}))
    print("Number of documents in streaming_history:", db.streaming_history.count_documents({}))

    # Read (Query)
    print("\nSample Playlist Document:\n", list(read(db.playlists)))
    print("\nSample Search Query Document:\n", list(read(db.search_queries)))
    print("\nSample Streaming History Document:\n", list(read(db.streaming_history)))

    # Other sample queries
    print("\nFirst Document in Playlist Collection:\n", list(read(db.playlists, limit=1))) # Fetching the first document found in the playlists collection
    print("\nPlaylists with the name \"promise\":\n", list(read(db.playlists, {"name": "promise"}, limit=1))) # Fetching playlists with a specific name
    print("\nFirst 5 docuents from Search Queries Collection:\n", list(read(db.search_queries, limit=5))) # Fetching the first 5 documents from the search_queries collection
    # print(list(read(db.streaming_history, {"$or": [{"track.trackName": "Scary Love"}, {"track.artistName": "The Neighbourhood"}]}, limit=5))) # Fetching streaming history records for a specific track or artist

    # Update data (Do not use yet, to be used later)
    # update(db.playlists, {'name': 'promise'}, {'$set': {'numberOfFollowers': 10}})
    # update(db.search_queries, {}, {'$set': {'new_field': 'value'}}, update_many=True)

    # Delete data (Do not use yet, to be used later)
    # delete(db.streaming_history, {'track.trackName': 'Scary Love'})
    
except Exception as e:
    import traceback
    print("An error occurred: ", e)
    traceback.print_exc()
finally:
    # Close the connection
    client.close()

