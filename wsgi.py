import os
import sys
from pathlib import Path

# Add the project directory to the python path
project_home = str(Path(__file__).parent)
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import your FastAPI app
from src.main import app as application

if __name__ == "__main__":
    application.run()
