# Setup Database for AAC Shelter Data

This repository includes an automated script, `AutomaticSetup.bat`, that helps you quickly set up the MongoDB database. However, you need to install a few prerequisites manually before running the script.

## Prerequisites

Before you can run the script, ensure that the following software is installed on your system:

### 1. **Install Python**

You will need Python 3.6 or higher. You can download it from the [official Python website](https://www.python.org/downloads/).

### 2. **Install MongoDB**

MongoDB is required to store and query the shelter data. You can download it from the [official MongoDB website](https://www.mongodb.com/try/download/community). Be sure to follow the installation instructions for your platform.

## Running the Script

After installing Python and MongoDB, you can run the automated script to set up the database. Here’s what the script does:

1. **Create and Activate a Python Virtual Environment**

   The script will create a virtual environment and activate it to isolate dependencies.

2. **Install Python Dependencies**

   The required Python packages will be automatically installed. This includes dependencies like `pymongo`, `pandas`, and others necessary to interact with MongoDB and process the data.

3. **Set Up the MongoDB Database**

   The script connects to MongoDB, clears any existing data, and imports shelter data from the CSV file into the database. It also creates indexes for efficient querying.

4. **Verify the Data**

   Once the script completes, you can verify the data using MongoDB Compass or the MongoDB shell. The data will be imported into the `AAC` database, and you can inspect it to ensure everything is in place.
