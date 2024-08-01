import subprocess
import time
import shutil
import os
import random
import sys

from playwright.sync_api import sync_playwright

# Use environment variables to get paths
template_project_dir = os.getenv('TEMPLATE_PROJECT_DIR', '/app')
template_main_dart_path = os.path.join(template_project_dir, 'lib', 'main.dart')
screenshot_save_dir = os.getenv('SCREENSHOT_SAVE_DIR', os.path.join(template_project_dir, 'screenshots'))
flutter_executable = os.getenv('FLUTTER_EXECUTABLE', '/usr/local/flutter/bin/flutter')

# Ensure the screenshot save directory exists
os.makedirs(screenshot_save_dir, exist_ok=True)

def find_available_port():
    """Find an available port for the Flutter app."""
    while True:
        port = random.randint(1024, 65535)
        # Check if the port is available
        with os.popen(f'netstat -an | grep {port}') as proc:
            if not proc.read():
                return port

def run_flutter_and_screenshot(screenshot_path):
    try:
        # Generate a random port and run the Flutter project
        flutter_port = find_available_port()
        flutter_process = subprocess.Popen([flutter_executable, 'run', '-d', 'chrome', '--web-port', str(flutter_port)], cwd=template_project_dir)
        print(f"Started Flutter process on port {flutter_port}")

        # Wait for the app to start
        time.sleep(30)

        # Use Playwright to take a screenshot
        with sync_playwright() as p:
            # Launch the browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Retry accessing the page if it fails initially
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    # Navigate to the Flutter app
                    page.goto(f"http://localhost:{flutter_port}", wait_until="load")
                    print("Page loaded successfully")
                    time.sleep(60)

                    # Take a screenshot
                    page.screenshot(path=screenshot_path)
                    print(f"Screenshot saved at {screenshot_path}")
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(10)  # Wait before retrying

            # Close the browser
            browser.close()

        # Terminate the Flutter process
        flutter_process.terminate()
        print("Terminated Flutter process")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python3 run_flutter_and_screenshot.py <student_id>")
        sys.exit(1)

    # Path to the main.dart file passed as an argument
    sid = sys.argv[1]

    # Define the path to save the screenshot
    screenshot_path = os.path.join(screenshot_save_dir, sid + '_screenshot.png')

    # Run the Flutter app with the given main.dart and take a screenshot
    run_flutter_and_screenshot(screenshot_path)
