from pymongo import MongoClient  # For connecting to MongoDB
from bson.objectid import ObjectId  # For handling MongoDB ObjectIds

class AnimalShelter(object):
    """ CRUD operations for the Animal collection in MongoDB """

    def __init__(self):
        # MongoDB connection details
        USER = 'aacuser'  # MongoDB username
        PASS = 'SNHU1234'  # MongoDB password
        HOST = 'nv-desktop-services.apporto.com'  # MongoDB host address
        PORT = 31659  # MongoDB port
        DB = 'AAC'  # Database name
        COL = 'animals'  # Collection name
        
        # Initialize MongoDB client and access the specified collection
        self.client = MongoClient(f'mongodb://{USER}:{PASS}@{HOST}:{PORT}')
        self.database = self.client[DB]
        self.collection = self.database[COL]

    def create(self, data):
        """ Method to insert a new document into the collection """
        if data is not None:
            try:
                self.collection.insert_one(data)  # Insert the document into the collection
                return True  # Return True if insertion is successful
            except Exception as e:
                print(f"An error occurred while inserting data: {e}")  # Print error message if insertion fails
                return False  # Return False if insertion fails
        else:
            raise Exception("No data provided; the data parameter is empty")  # Raise an exception if no data is provided

    def read(self, query):
        """ Method to retrieve documents from the collection based on the query """
        if query is not None:
            try:
                results = list(self.collection.find(query))  # Find documents matching the query and convert to a list
                if results is None:
                    raise Exception("No results returned from the database.")  # Raise an exception if no results are found
                print(f"Read results: {results}")  # Print results for debugging purposes
                return results  # Return the retrieved documents
            except Exception as e:
                print(f"An error occurred while reading data: {e}")  # Print error message if reading fails
                return []  # Return an empty list if reading fails
        else:
            raise Exception("Query parameter is empty")  # Raise an exception if the query parameter is empty

    def update(self, query, update_data):
        """ Method to update existing documents in the collection based on the query """
        if query is not None and update_data is not None:
            try:
                result = self.collection.update_many(query, {'$set': update_data})  # Update documents matching the query
                return result.modified_count  # Return the number of documents that were updated
            except Exception as e:
                print(f"An error occurred while updating data: {e}")  # Print error message if updating fails
                return 0  # Return 0 if no documents were updated
        else:
            raise Exception("Query or update_data parameter is empty")  # Raise an exception if either parameter is empty

    def delete(self, query):
        """ Method to delete documents from the collection based on the query """
        if query is not None:
            try:
                result = self.collection.delete_many(query)  # Delete documents matching the query
                return result.deleted_count  # Return the number of documents that were deleted
            except Exception as e:
                print(f"An error occurred while deleting data: {e}")  # Print error message if deletion fails
                return 0  # Return 0 if no documents were deleted
        else:
            raise Exception("Query parameter is empty")  # Raise an exception if the query parameter is empty
