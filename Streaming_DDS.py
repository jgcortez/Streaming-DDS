import json

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