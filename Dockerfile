# Use the base image from Ubuntu
FROM ubuntu:20.04

# Set environment variable to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y curl git vim wget unzip libgconf-2-4 gdb libstdc++6 libglu1-mesa fonts-droid-fallback \
    python3 python3-pip xdg-utils xdotool xvfb gnupg2 net-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

    # Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
apt-get update && \
apt-get install -y google-chrome-stable && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*
ENV CHROME_EXECUTABLE /usr/bin/google-chrome-stable

# Install Playwright for Python
RUN pip3 install playwright \
    && playwright install

# Set environment variables for Flutter
ENV DEBIAN_FRONTEND=dialog
ENV PUB_HOSTED_URL=https://pub.flutter-io.cn
ENV FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

# Download Flutter SDK from Flutter GitHub repo
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter

# Set Flutter environment path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Run Flutter doctor
RUN flutter doctor

# Enable Flutter web
RUN flutter channel master \
    && flutter upgrade \
    && flutter config --enable-web

# Set the working directory
WORKDIR /app/

# Copy files to container
COPY . /app/

# Build the Flutter web project
RUN flutter build web

# Install Flask and other Python dependencies
RUN pip3 install flask

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Expose the port for Flask
EXPOSE 5000

# Command to start Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
