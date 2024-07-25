import subprocess
import pyautogui
import time
import shutil
import os
import sys

# Path to the template Flutter project directory
template_project_dir = '/app'

# Path to the main.dart file in the template project
template_main_dart_path = os.path.join(template_project_dir, 'lib', 'main.dart')

# Path to save the screenshots
screenshot_save_dir = '/app/screenshots'

# Full path to the Flutter executable
flutter_executable = '/usr/local/bin/flutter'

# Ensure the screenshot save directory exists
os.makedirs(screenshot_save_dir, exist_ok=True)

def get_window_geometry(window_id):
    output = subprocess.check_output(['xdotool', 'getwindowgeometry', window_id]).decode()
    print(f"Window geometry output: {output}")
    lines = output.split('\n')
    geometry = {}
    for line in lines:
        if 'Position' in line:
            position = line.split(':')[1].strip().split(' ')
            geometry['x'], geometry['y'] = map(int, position[0].split(','))
        if 'Geometry' in line:
            size = line.split(':')[1].strip()
            geometry['width'], geometry['height'] = map(int, size.split('x'))
    print(f"Window geometry: {geometry}")
    return geometry

def run_flutter_and_screenshot(main_dart_file, screenshot_path):
    try:
        # Copy the main.dart file to the template project
        shutil.copy(main_dart_file, template_main_dart_path)
        print(f"Copied {main_dart_file} to {template_main_dart_path}")

        # Run the Flutter project using the terminal command, specifying Chrome as the target device
        flutter_process = subprocess.Popen([flutter_executable, 'run', '-d', 'chrome'], cwd=template_project_dir)
        print("Started Flutter process")

        # Wait for the app to start (adjust the sleep time if necessary)
        time.sleep(30)

        # Ensure Chrome is the active window before taking the screenshot
        window_id = None
        for _ in range(10):
            try:
                output = subprocess.check_output(['xdotool', 'search', '--name', 'Container Example']).decode().strip().split('\n')
                if output:
                    window_id = output[0]
                    print(f"Found Chrome window with title 'Container Example': {window_id}")
                    break
            except subprocess.CalledProcessError:
                pass
            time.sleep(1)

        if window_id is None:
            raise Exception("Chrome tab with the title 'Container Example' is not found.")

        # Activate and maximize the specific Chrome window
        subprocess.call(['xdotool', 'windowactivate', window_id])
        subprocess.call(['xdotool', 'windowsize', window_id, '100%', '100%'])
        print(f"Activated and maximized Chrome window: {window_id}")

        # Get the window geometry to capture the specific window
        geometry = get_window_geometry(window_id)
        x, y, width, height = geometry['x'], geometry['y'], geometry['width'], geometry['height']
        print(f"Capturing screenshot with region: x={x}, y={y}, width={width}, height={height}")

        # Take a screenshot of the specific window area
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # Save the screenshot
        screenshot.save(screenshot_path)
        print(f"Screenshot for {main_dart_file} taken and saved to {screenshot_path}.")

        # Terminate the Flutter process
        flutter_process.terminate()
        print("Terminated Flutter process")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Get the main.dart file path from the command line arguments
    main_dart_file = sys.argv[1]

    # Define the path to save the screenshot, using a fixed name or based on the input file name
    screenshot_path = os.path.join(screenshot_save_dir, 'screenshot.png')

    # Run the Flutter app with the given main.dart and take a screenshot
    run_flutter_and_screenshot(main_dart_file, screenshot_path)
