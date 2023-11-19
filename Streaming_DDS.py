import json

# Function to load JSON files
def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Load data
playlists = load_file('Data/Playlist1.json')
search_queries = load_file('Data/SearchQueries.json')
streaming_history = load_file('Data/StreamingHistory0.json')