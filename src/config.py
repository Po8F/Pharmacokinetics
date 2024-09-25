import os

TEMP_FOLDER_PATH = os.path.join(os.getcwd(), "PharmacokineticAnalysis")
if not os.path.exists(TEMP_FOLDER_PATH):
    os.makedirs(TEMP_FOLDER_PATH)
