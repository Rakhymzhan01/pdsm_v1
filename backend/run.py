import uvicorn
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()