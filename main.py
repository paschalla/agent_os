import sys
import os
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.interface.repl import run_repl

def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    run_repl()

if __name__ == "__main__":
    main()
