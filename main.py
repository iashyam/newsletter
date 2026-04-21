import os
from dotenv import load_dotenv

# Tell python exactly where your .env file is located
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.newsletter_mcp import mcp
def main():
    mcp.run()

if __name__ == "__main__":
    main()
