from pymongo import MongoClient, ASCENDING
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

# Set up MongoDB connection string and other settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')

# Logging Setup
def log(message):
    print(f"[INFO] {message}")

def error_log(message):
    print(f"[ERROR] {message}")

def success_log(message):
    print(f"[SUCCESS] {message}")

# Main Setup
def main():
    log("Starting database setup...")
    
    try:
        # Connect to MongoDB
        log(f"Connecting to MongoDB at {MONGO_URI}...")
        client = MongoClient(MONGO_URI)
        
        # Create or access the AAC database
        db = client['AAC']
        
        # Create or access the 'animals' collection
        collection = db['animals']
        
        # Clear existing data from collection
        log("Clearing existing data from the 'animals' collection...")
        collection.delete_many({})
        
        # Read CSV file
        log("Reading CSV file 'aac_shelter_outcomes.csv'...")
        if not os.path.exists('aac_shelter_outcomes.csv'):
            error_log("CSV file 'aac_shelter_outcomes.csv' not found!")
            return
        
        df = pd.read_csv('aac_shelter_outcomes.csv')
        
        # Import data into MongoDB
        log("Importing data to MongoDB...")
        records = df.to_dict('records')
        collection.insert_many(records)
        
        # Create indexes
        log("Creating indexes on 'breed', 'sex_upon_outcome', and 'age_upon_outcome_in_weeks'...")
        collection.create_index([('breed', ASCENDING)])
        collection.create_index([('sex_upon_outcome', ASCENDING)])
        collection.create_index([('age_upon_outcome_in_weeks', ASCENDING)])
        
        success_log("Database setup completed successfully!")
        success_log(f"Imported {len(records)} records into the 'animals' collection.")
        
        # Get and display a sample document from the collection
        log("\nFetching a sample document from the 'animals' collection...")
        sample = db.animals.find_one()
        if sample:
            print("\nSample document:")
            print(sample)
        else:
            error_log("No documents found in the 'animals' collection.")
    
    except Exception as e:
        error_log(f"An error occurred: {str(e)}")
    
    finally:
        # Close the MongoDB connection
        if 'client' in locals():
            client.close()
            log("MongoDB connection closed.")

# Run the script
if __name__ == "__main__":
    main()
