"""练习入口：见 xml_output_parser.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from xml_output_parser import main

if __name__ == "__main__":
    main()
