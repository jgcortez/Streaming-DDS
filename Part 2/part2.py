from pymongo import MongoClient
import string

client = MongoClient('localhost', 27017)
db = client['streaming_dds']

# Access the collection
playlists_collection = db.playlists

# Function to categorize playlist names
def categorize_playlist(name):
    first_char = name[0].lower()
    return first_char if first_char in string.ascii_lowercase else 'others'

# Create a dictionary to store categorized playlists
categorized_playlists = {char: [] for char in string.ascii_lowercase}
categorized_playlists['others'] = []

# Fetch and categorize all playlist documents
for playlist in playlists_collection.find():
    category = categorize_playlist(playlist['name'])
    categorized_playlists[category].append(playlist)

# Print the names of playlists along with their categories
for category, playlists in categorized_playlists.items():
    if playlists:
        print(f"\nCategory '{category}':", end=" ")
        for playlist in playlists:
            print(playlist['name'], end=", ")  # Prints only the name of the playlist