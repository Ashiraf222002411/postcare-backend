import subprocess
import threading
import time
import os

def run_flask():
    print("Starting Flask...")
    subprocess.run(["python", "run.py"])

def run_tunnel():
    print("Starting LocalTunnel...")
    try:
        # Use npm to run localtunnel
        subprocess.run(["npm", "exec", "--", "localtunnel", "--port", "5001"])
    except Exception as e:
        print(f"Error: {e}")
        print("Installing LocalTunnel...")
        subprocess.run(["npm", "install", "-g", "localtunnel"])
        print("Retrying LocalTunnel...")
        subprocess.run(["npm", "exec", "--", "localtunnel", "--port", "5001"])

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Give Flask time to start
time.sleep(5)

# Start LocalTunnel
run_tunnel()
