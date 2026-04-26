# Setup
## Docker (recommended)

1.  Install Docker Desktop for macOS or Windows/Linux from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2.  Open a terminal.
3.  Navigate to the project directory.
4.  Run `make run` to build and start the application.

## Manual (Not Recommended)

1. Ensure you have Python 3.11 installed.
2. Create a virtual environment (optional but recommended):
   `python -m venv .venv`
   `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
3. Install the dependencies:
   `pip install -r requirements.txt`
4. Run the application:
   `python main.py`