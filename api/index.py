import sys
import os

# 1. This line tells Python to look in the root dir for your code
# without this, 'import main' will fail on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Import your FastAPI instance from your main file
from main import app

# 3. Vercel looks for 'app' or 'handler' by default
handler = app
