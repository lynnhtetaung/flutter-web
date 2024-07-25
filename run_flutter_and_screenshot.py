import subprocess
import time
import shutil
import os
import random
from playwright.sync_api import sync_playwright

# Path to the template Flutter project directory
template_project_dir = '/home/lynnhtetaung/Documents/develop/PLAS/flutter_app'

# Path to the main.dart file in the template project
template_main_dart_path = os.path.join(template_project_dir, 'lib', 'main.dart')

# Path to save the screenshots
screenshot_save_dir = os.path.join(template_project_dir, 'screenshots')

# Full path to the Flutter executable
flutter_executable = '/home/lynnhtetaung/flutter/bin/flutter'

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

def run_flutter_and_screenshot(main_dart_file, screenshot_path):
    try:
        # Check if the source and destination paths are the same
        if os.path.abspath(main_dart_file) != os.path.abspath(template_main_dart_path):
            # Copy the main.dart file to the template project if the paths are different
            shutil.copy(main_dart_file, template_main_dart_path)
            print(f"Copied {main_dart_file} to {template_main_dart_path}")
        else:
            print("Source and destination are the same. No need to copy.")

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
    # Hardcoded path to the main.dart file
    main_dart_file = template_main_dart_path  # Replace with your actual path

    # Define the path to save the screenshot
    screenshot_path = os.path.join(screenshot_save_dir, 'screenshot.png')

    # Run the Flutter app with the given main.dart and take a screenshot
    run_flutter_and_screenshot(main_dart_file, screenshot_path)
