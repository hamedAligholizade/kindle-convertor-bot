#!/bin/bash

# Start the Python FastAPI service in the background
python src/bot_service.py &

# Start the Node.js service
npm start 