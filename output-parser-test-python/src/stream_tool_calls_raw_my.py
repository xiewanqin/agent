"""练习入口：极简见 stream_tool_calls_raw.py；加长版见 stream_tool_calls_raw_verbose.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stream_tool_calls_raw import main

if __name__ == "__main__":
    main()
