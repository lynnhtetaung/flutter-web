from flask import Flask, request, jsonify
import subprocess
import time
import os
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Define a fixed port number for the Flutter web server
FIXED_FLUTTER_PORT = 8080

# Path to the template Flutter project directory
template_project_dir = '/home/lynnhtetaung/Documents/develop/PLAS/flutter_app'

# Path to the main.dart file in the template project
template_main_dart_path = os.path.join(template_project_dir, 'lib', 'main.dart')

# Path to save the screenshots
screenshot_save_dir = os.path.join(template_project_dir, 'screenshots')
flutter_executable = '/home/lynnhtetaung/flutter/bin/flutter'

# Ensure the screenshot save directory exists
os.makedirs(screenshot_save_dir, exist_ok=True)

def run_flutter_and_screenshot(main_dart_file, screenshot_path):
    try:
        # Write the uploaded main.dart file to the project directory
        with open(template_main_dart_path, 'w') as f:
            f.write(main_dart_file)

        # Run the Flutter project on the fixed port
        print(f"Starting Flutter process with executable {flutter_executable}")
        flutter_process = subprocess.Popen([
            flutter_executable, 'run', '-d', 'chrome',
            '--web-port', str(FIXED_FLUTTER_PORT)
        ], cwd=template_project_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Capture logs for debugging
        stdout, stderr = flutter_process.communicate()
        print(f"Flutter stdout: {stdout.decode()}")
        print(f"Flutter stderr: {stderr.decode()}")

        print(f"Started Flutter process on port {FIXED_FLUTTER_PORT}")

        # Wait for the app to start
        time.sleep(60)  # Increase this time if needed

        # Use Playwright to take a screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Retry accessing the page if it fails initially
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    page.goto(f"http://localhost:{FIXED_FLUTTER_PORT}", wait_until="networkidle")
                    print("Page loaded successfully")
                    time.sleep(30)  # Ensure the page is fully rendered

                    # Take a screenshot
                    page.screenshot(path=screenshot_path)
                    print(f"Screenshot saved at {screenshot_path}")
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(10)  # Wait before retrying

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
    app.run(port=5000)  # Update the port
