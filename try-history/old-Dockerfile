# Use the base Flutter image from Docker Hub
FROM cirrusci/flutter:stable

# Set the working directory in the container
WORKDIR /app

# Copy the Flutter project files into the container
COPY . .

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y xdg-utils python3 python3-pip xdotool xvfb unzip wget gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Download and install Chrome browser
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Download and install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && chmod +x chromedriver \
    && mv -f chromedriver /usr/local/bin/chromedriver

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
