"""练习入口：见 stream_tool_calls_parser.py"""
from stream_tool_calls_parser import main
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


if __name__ == "__main__":
  main()
