from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


# Function to initialize the replica set
def initialize_replica_set(client, members):
    config = {'_id': 'myreplset', 'members': members}
    try:
        client.admin.command('replSetInitiate', config)
        print("Replica set initiated successfully.")
    except OperationFailure as e:
        print("An error occurred during replica set initiation:", e)

# Function to get the status of the replica set
def get_replica_set_status(client):
    try:
        status = client.admin.command('replSetGetStatus')
        print("Current replica set status:")
        for member in status['members']:
            print(f"Member ID: {member['_id']}, Host: {member['name']}, State: {member['stateStr']}")
    except OperationFailure as e:
        print("An error occurred while getting replica set status:", e)

try:
    # Connect to the primary mongo instance (mongo1)
    client = MongoClient('mongodb://root:512project@localhost:27018/', serverSelectionTimeoutMS=5000)
    
    # Attempt to get the status of the replica set to see if it is already initialized
    try:
        get_replica_set_status(client)
        print("Replica set already initialized.")
    except OperationFailure:
        # Replica set not initialized, so we initialize it with the first member
        members = [
            {'_id': 0, 'host': 'mongo1:27018'},
            {'_id': 1, 'host': 'mongo2:27019'},
            {'_id': 2, 'host': 'mongo3:27020'}
        ]
        initialize_replica_set(client, members)

    # Finally, check the status again to confirm the setup
    get_replica_set_status(client)

except ConnectionFailure:
    print("Failed to connect to MongoDB server.")

finally:
    # Close the connection
    client.close()
