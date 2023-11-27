from pymongo import MongoClient, WriteConcern
from pymongo.errors import ConnectionFailure, OperationFailure
from threading import Thread
import random

# Connect to the MongoDB replica set
client = MongoClient('mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=myReplicaSet')
db = client['streaming_dds']

# Collections involved in the transaction
playlists_collection = db.playlists
user_collection = db.users

def execute_transaction(session, playlists_collection, user_collection, playlist_id, user_id):
    try:
        with session.start_transaction(write_concern=WriteConcern('majority')):
            playlists_collection.update_one({'_id': playlist_id}, {'$set': {'status': 'active'}}, session=session)
            user_collection.update_one({'_id': user_id}, {'$inc': {'playlist_count': 1}}, session=session)
            session.commit_transaction()
            print(f"Transaction committed successfully for playlist_id {playlist_id} and user_id {user_id}.")
    except (OperationFailure, ConnectionFailure) as e:
        print("Transaction aborted due to error:", e)
        session.abort_transaction()

def simulate_concurrent_transactions(playlist_id, user_id):
    with client.start_session() as session:
        execute_transaction(session, playlists_collection, user_collection, playlist_id, user_id)

# Simulating concurrent transactions
threads = []
for _ in range(5):  # Number of concurrent transactions
    playlist_id = random.randint(1, 5)  # Adjust based on your data
    user_id = random.randint(1, 5)      # Adjust based on your data
    thread = Thread(target=simulate_concurrent_transactions, args=(playlist_id, user_id))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
