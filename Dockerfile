FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    calibre \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the start script first and set permissions
COPY start.sh .
RUN chmod +x start.sh

# Copy the rest of the application
COPY . .

# Ensure the script is still executable after copying all files
RUN chmod +x start.sh

# Expose ports for both services
EXPOSE 3000 8000

CMD ["./start.sh"] 