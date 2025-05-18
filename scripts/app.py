"""
CLI entrypoint to launch the Streamlit app locally.
Use: `poetry run app`
"""

import subprocess
from pathlib import Path

def main():
    streamlit_path = Path(__file__).parent.parent / "src" / "phdfinder" / "app" / "streamlit_app.py"
    subprocess.run(["streamlit", "run", str(streamlit_path)])
