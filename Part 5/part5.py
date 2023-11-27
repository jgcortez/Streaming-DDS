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
            print("Omitting data: 'searchTime' is missing or empty.")
            return
        
        if collection.find_one({'searchTime': data['searchTime']}):
            print(f"Omitting data: Search query at '{data['searchTime']}' already exists.")
            return
        
        collection.insert_one(data)


    def create_streaming_history(data):
        required_fields = ['endTime', 'artistName', 'trackName', 'msPlayed']
        if not all(field in data and data[field] for field in required_fields):
            print(f"Omitting data: Required fields {required_fields} must be present and non-empty.")
            return

        query = {field: data[field] for field in required_fields}
        if collection.find_one(query):
            print(f"Omitting data: Streaming history for '{data['trackName']}' by '{data['artistName']}' at '{data['endTime']}' with duration {data['msPlayed']}ms already exists.")
            return
        
        collection.insert_one(data)


    def create_playlist(data):
        # Validate playlist name
        if 'name' not in data or not data['name']:
            print("Omitting data: Playlist name is missing or empty.")
            return

        # Check for unique playlist name
        if collection.find_one({'name': data['name']}):
            print(f"Omitting data: Playlist '{data['name']}' already exists.")
            return

        # Validate items
        if 'items' not in data or not isinstance(data['items'], list):
            print("Omitting data: 'items' is missing or not a list.")
            return
        
        # Validate track names and check for duplicate items within the same playlist
        track_names = [item['track']['trackName'] for item in data['items'] if item.get('track') and 'trackName' in item['track']]
        if len(track_names) != len(set(track_names)):
            print(f"Omitting data: Duplicate tracks found in playlist '{data['name']}'.")
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
    db = client['spotify_clone_db']

    # Use CRUD Operations
    sample_playlist = {
        "name": "Chill Vibes",
        "lastModifiedDate": "2023-03-15",
        "items": [
            {   
                "track": {
                    "trackName": "COPYCAT",
                    "artistName": "Billie Eilish",
                    "albumName": "dont smile at me",
                    "trackUri": "spotify:track:5w7wuzMzsDer96KqxafeRK"
                }
            },
            {
                "track": {
                    "trackName": "bloodline",
                    "artistName": "Ariana Grande",
                    "albumName": "thank u, next",
                    "trackUri": "spotify:track:2hloaUoRonYssMuqLCBLTX"
                }
            },
            {
                "track": {
                    "trackName": "Boyfriend",
                    "artistName": "Dove Cameron",
                    "albumName": "Boyfriend",
                    "trackUri": "spotify:track:59CfNbkERJ3NoTXDvoURjj"
                }
            },
            {
                "track": {
                    "trackName": "needy",
                    "artistName": "Ariana Grande",
                    "albumName": "thank u, next",
                    "trackUri": "spotify:track:1TEL6MlSSVLSdhOSddidlJ"
                }
            }   
        ],
        "description": "A playlist for relaxing and unwinding.",
        "numberOfFollowers": 5
    }
    print("\nCREATE:")
    print("\nData to be Inserted:\n", sample_playlist)
    create(db.playlists, sample_playlist)

    # Query entire playlist "Chill Vibes"
    chill_vibes_playlist = list(read(db.playlists, {"name": "Chill Vibes"}, limit=1))
    print("\nQuery Data Inserted:\n", chill_vibes_playlist)


    print("\nREAD:")
    # Get first track from playlist "Chill Vibes"
    first_track = db.playlists.find_one({"name": "Chill Vibes"}, {"items": {"$slice": 1}})
    print("\nQuery First Track in Playlist:\n", first_track)

    # Get all tracks in playlist "Chill Vibes" where the artistName is Ariana Grande
    ariana_tracks = db.playlists.aggregate([
        {"$match": {"name": "Chill Vibes"}},
        {"$project": {
            "items": {
                "$filter": {
                    "input": "$items",
                    "as": "item",
                    "cond": {"$eq": ["$$item.track.artistName", "Ariana Grande"]}
                }
            }
        }}
    ])
    ariana_tracks_list = list(ariana_tracks)
    print("\nQuery All Ariana Grande Tracks:\n", ariana_tracks_list)


    print("\nUPDATE:")
    # Find the track with trackName COPYCAT in playlist "Chill Vibes" and update it to have trackName "bellyache" and trackUri "spotify:track:51NFxnQvaosfDDutk0tams"
    db.playlists.update_one({"name": "Chill Vibes", "items.track.trackName": "COPYCAT"}, {"$set": {"items.$.track.trackName": "bellyache", "items.$.track.albumName": "Bellyache", "items.$.track.trackUri": "spotify:track:51NFxnQvaosfDDutk0tams"}})
    chill_vibes_playlist = list(read(db.playlists, {"name": "Chill Vibes"}, limit=1))
    print("\nUpdate \"COPYCAT\" to \"bellyache\" with trackUri \"spotify:track:51NFxnQvaosfDDutk0tams\":\n", chill_vibes_playlist)


    # Update the description of playlist "Chill Vibes" to say "My favorite songs."
    update(db.playlists, {"name": "Chill Vibes"}, {"$set": {"description": "My favorite songs."}})
    chill_vibes_playlist = list(read(db.playlists, {"name": "Chill Vibes"}, limit=1))
    print("\nUpdate the description of the playlist to say \"My favorite songs.\":\n", chill_vibes_playlist)


    print("\nDELETE:")
    # Delete track with trackName "needy" from playlist "Chill Vibes"
    db.playlists.update_one({"name": "Chill Vibes"}, {"$pull": {"items": {"track.trackName": "needy"}}})
    chill_vibes_playlist = list(read(db.playlists, {"name": "Chill Vibes"}, limit=1))
    print("\nDelete \"needy\":\n", chill_vibes_playlist)

    # Delete entire playlist "Chill Vibes"
    print("\nDelete playlist \"Chill Vibes\":")
    delete(db.playlists, {"name": "Chill Vibes"})
    deleted_playlist = list(read(db.playlists, {"name": "Chill Vibes"}, limit=1))
    if not deleted_playlist:
        print("Playlist not found")
    else:
        print("Playlist found:", deleted_playlist)


    # Other sample queries

    # Read
    # print("\nSample Playlist Document:\n", list(read(db.playlists)))
    # print("\nSample Search Query Document:\n", list(read(db.search_queries)))
    # print("\nSample Streaming History Document:\n", list(read(db.streaming_history)))
    # print("\nFirst Document in Playlist Collection:\n", list(read(db.playlists, limit=1))) # Fetching the first document found in the playlists collection
    # print("\nPlaylists with the name \"promise\":\n", list(read(db.playlists, {"name": "promise"}, limit=1))) # Fetching playlists with a specific name
    # print("\nFirst 5 docuents from Search Queries Collection:\n", list(read(db.search_queries, limit=5))) # Fetching the first 5 documents from the search_queries collection
    # print(list(read(db.streaming_history, {"$or": [{"track.trackName": "Scary Love"}, {"track.artistName": "The Neighbourhood"}]}, limit=5))) # Fetching streaming history records for a specific track or artist

    # Update
    # update(db.playlists, {'name': 'promise'}, {'$set': {'numberOfFollowers': 10}})
    # update(db.search_queries, {}, {'$set': {'new_field': 'value'}}, update_many=True)

    # Delete
    # delete(db.streaming_history, {'track.trackName': 'Scary Love'})
    
except Exception as e:
    import traceback
    print("An error occurred: ", e)
    traceback.print_exc()
finally:
    # Close the connection
    client.close()

