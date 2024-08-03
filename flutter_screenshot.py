import os
import time
import subprocess
from playwright.sync_api import sync_playwright

# Path configurations
template_project_dir = '/home/lynnhtetaung/Documents/develop/PLAS/flutter_app'
template_main_dart_path = os.path.join(template_project_dir, 'lib', 'main.dart')
flutter_executable = '/home/lynnhtetaung/flutter/bin/flutter'
FIXED_FLUTTER_PORT = 8080

def run_flutter_and_screenshot(main_dart_file, screenshot_path):
    try:
        with open(template_main_dart_path, 'w') as f:
            f.write(main_dart_file)

        flutter_process = subprocess.Popen([
            flutter_executable, 'run', '-d', 'chrome',
            '--web-port', str(FIXED_FLUTTER_PORT)
        ], cwd=template_project_dir)

        time.sleep(60)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"http://localhost:{FIXED_FLUTTER_PORT}")
            time.sleep(30)
            page.screenshot(path=screenshot_path)
            browser.close()

        flutter_process.terminate()
    except Exception as e:
        print(f"Error: {e}")
