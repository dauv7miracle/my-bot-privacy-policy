# Use an official Python runtime as a parent image
FROM python:3.10-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm (required for PM2)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install PM2 globally
RUN npm install pm2 -g

# Copy the ecosystem.config.js file
COPY ecosystem.config.js .

# Copy all Python scripts and their dependencies
# This is a broad copy, adjust if you have specific subdirectories you want to exclude
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose any ports your applications might be listening on (if any)
# For example, if a bot runs a web server on port 3000:
# EXPOSE 3000

# Command to run PM2 and start all applications
CMD ["pm2-runtime", "start", "ecosystem.config.js"]
