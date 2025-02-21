@echo off
cls
echo ============================================================
echo                 Setting Up Your Environment
echo ============================================================

REM Activate virtual environment
echo [INFO] Activating virtual environment...
if not exist venv (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv venv
)
call venv\Scripts\activate

REM Install required Python packages
echo [INFO] Installing required Python packages...
pip install pymongo pandas dash dash-leaflet plotly jupyter-dash python-dotenv ipykernel notebook

echo [SUCCESS] Dependencies installed successfully!

echo ============================================================
echo                MongoDB Setup and Data Import
echo ============================================================

REM Connect to MongoDB and create database
echo [INFO] Connecting to MongoDB and creating the database...
set MONGO_URI=mongodb://localhost:27017
python -c "import pymongo; client = pymongo.MongoClient('%MONGO_URI%'); db = client['AAC']; print('Database connected!')"

echo [SUCCESS] MongoDB setup complete!

REM Import CSV Data
echo [INFO] Importing data from CSV into MongoDB...
python -c "import pandas as pd, pymongo; df = pd.read_csv('aac_shelter_outcomes.csv'); client = pymongo.MongoClient('%MONGO_URI%'); db = client['AAC']; collection = db['animals']; collection.insert_many(df.to_dict('records')); print('Data imported!')"

echo [SUCCESS] Data import complete!

echo ============================================================
echo                    Creating Indexes
echo ============================================================

REM Create Indexes
echo [INFO] Creating indexes on the 'animals' collection...
python -c "import pymongo; client = pymongo.MongoClient('%MONGO_URI%'); db = client['AAC']; collection = db['animals']; indexes = [('breed', 1), ('sex_upon_outcome', 1), ('age_upon_outcome_in_weeks', 1)]; [collection.create_index([index]) for index in indexes]; print('Indexes created!')"

echo [SUCCESS] Indexes created successfully!

echo ============================================================
echo              Running Setup and Verification Scripts
echo ============================================================

REM Run setup script
echo [INFO] Running setup_database.py script...
python setup_database.py > setup_output.log 2>&1 & type setup_output.log

echo [SUCCESS] Database setup scripts executed!

echo ============================================================
echo               Waiting to View Script Output
echo ============================================================

REM Sleep for 15 seconds to allow viewing of output
echo [INFO] Waiting for 15 seconds to review script output...
timeout /t 15

echo ============================================================
echo                     Launching Jupyter Notebook
echo ============================================================

REM Launch Jupyter Notebook
echo [INFO] Launching Jupyter Notebook...
start jupyter notebook dashboard.ipynb

echo [SUCCESS] Setup complete! Exiting...
