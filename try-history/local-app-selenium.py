from flask import Flask, request, jsonify
import subprocess
import time
import shutil
import os
import random
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Use environment variables to get paths

# Path to the template Flutter project directory
template_project_dir = '/home/lynnhtetaung/Documents/develop/PLAS/flutter_app'

# Path to the main.dart file in the template project
template_main_dart_path = os.path.join(template_project_dir, 'lib', 'main.dart')

# Path to save the screenshots
screenshot_save_dir = os.path.join(template_project_dir, 'screenshots')
flutter_executable = '/home/lynnhtetaung/flutter/bin/flutter'

# Ensure the screenshot save directory exists
os.makedirs(screenshot_save_dir, exist_ok=True)

# Define a fixed port number for the Flutter web server
FIXED_FLUTTER_PORT = 8080

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
        # Write the uploaded main.dart file to the project directory
        with open(template_main_dart_path, 'w') as f:
            f.write(main_dart_file)

        # Generate a random port and run the Flutter project
        # flutter_port = find_available_port()
        print(f"Starting Flutter process with executable {flutter_executable}")
        flutter_process = subprocess.Popen([
            flutter_executable, 'run', '-d', 'chrome',
            '--web-port', str(FIXED_FLUTTER_PORT)
        ], cwd=template_project_dir)

        print(f"Started Flutter process on port {FIXED_FLUTTER_PORT}")

        # Wait for the app to start
        time.sleep(60)  # Increase this time if needed

        # Use Selenium to take a screenshot
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Path to the ChromeDriver executable
        service = Service('/usr/local/bin/chromedriver')

        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.get(f"http://localhost:{FIXED_FLUTTER_PORT}")

            # Wait for the page to fully render
            time.sleep(30)  # Adjust if necessary

            # Take a screenshot
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved at {screenshot_path}")
        finally:
            driver.quit()

        # Terminate the Flutter process
        flutter_process.terminate()
        print("Terminated Flutter process")
    except Exception as e:
        print(f"Error: {e}")


@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()

    main_dart_file_content = data.get('sourceCode')
    student_id = data.get('studentId')

    if not main_dart_file_content or not student_id:
        return jsonify({"status": "error", "message": "Missing sourceCode or student_id"}), 400

    # Save the uploaded file content to the Flutter project's main.dart
    screenshot_path = os.path.join(screenshot_save_dir, f'{student_id}_screenshot.png')

    # Run the Flutter app with the given main.dart and take a screenshot
    run_flutter_and_screenshot(main_dart_file_content, screenshot_path)

    return jsonify({"status": "success", "screenshot_path": screenshot_path}), 200

if __name__ == '__main__':
    app.run(port=5000)  # Update the port
