# Use the base Flutter image from Docker Hub
FROM cirrusci/flutter:stable

# Set the working directory in the container
WORKDIR /app

# Copy the Flutter project files into the container
COPY . .

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y xdg-utils python3 python3-pip xdotool xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install pyautogui

# Enable Flutter web
RUN flutter config --enable-web

# Get Flutter dependencies
RUN flutter pub get

# Copy the Python script into the container
COPY run_flutter_and_screenshot.py /usr/local/bin/run_flutter_and_screenshot.py

# Make the script executable
RUN chmod +x /usr/local/bin/run_flutter_and_screenshot.py

# Expose the port for the web server (default is 8080)
EXPOSE 8080

# Command to run the Python script with xvfb-run
CMD ["xvfb-run", "-a", "python3", "/usr/local/bin/run_flutter_and_screenshot.py", "/app/lib/main.dart"]
