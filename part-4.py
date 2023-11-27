from pymongo import MongoClient, WriteConcern, ReadConcern, ReadPreference
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import transaction_options

def execute_transaction(session, playlists_collection, user_collection, playlist_id, user_id):
    try:
        # Transaction operations
        with session.start_transaction(
            read_concern=ReadConcern('local'),
            write_concern=WriteConcern('majority'),
            read_preference=ReadPreference.PRIMARY
        ):
            # Sample update operation on playlists_collection
            playlists_collection.update_one(
                {'_id': playlist_id},
                {'$set': {'status': 'active'}},
                session=session
            )
            
            # Sample update operation on user_collection
            user_collection.update_one(
                {'_id': user_id},
                {'$inc': {'playlist_count': 1}},
                session=session
            )
            
            # Commit the transaction
            session.commit_transaction()
            print("Transaction committed successfully.")

    except (OperationFailure, ConnectionFailure) as e:
        # Handle transaction failure
        print("Transaction aborted due to error:", e)
        session.abort_transaction()

# Connect to the MongoDB database
client = MongoClient('localhost', 27017)
db = client['streaming_dds']

# Collections involved in the transaction
playlists_collection = db.playlists
user_collection = db.users

# Start a session for transaction
with client.start_session() as session:
    # Example usage of the transaction function
    execute_transaction(session, playlists_collection, user_collection, playlist_id=1, user_id=123)
