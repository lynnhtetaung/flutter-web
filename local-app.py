from flask import Flask, request, jsonify
import subprocess
import time
import shutil
import os
import random
import sys
from playwright.sync_api import sync_playwright

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

def run_flutter_and_screenshot(main_dart_file, screenshot_path):
    try:
        # Write the uploaded main.dart file to the project directory
        with open(template_main_dart_path, 'w') as f:
            f.write(main_dart_file)

        print(f"Starting Flutter process with executable {flutter_executable}")
        flutter_process = subprocess.Popen([
            flutter_executable, 'run', '-d', 'chrome',
            '--web-port', str(FIXED_FLUTTER_PORT)
        ], cwd=template_project_dir)

        print(f"Started Flutter process on port {FIXED_FLUTTER_PORT}")

        # Wait for the app to start
        time.sleep(60)  # Increase this time if needed

        # Use Playwright to take a screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"http://localhost:{FIXED_FLUTTER_PORT}")

            # Wait for the page to fully render
            time.sleep(30)  # Adjust if necessary

            # Take a screenshot
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved at {screenshot_path}")

            browser.close()

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
    app.run(port=5000)
