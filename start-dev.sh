#!/bin/bash

# AI Job Application Assistant - Development Startup Script
# This script starts both backend and frontend development servers

set -e

echo "🚀 Starting AI Job Application Assistant Development Environment..."

# Function to check if a process is running on a port
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill existing processes
kill_existing_processes() {
    echo "🔄 Checking for existing processes..."
    
    # Kill existing backend processes
    if pgrep -f "uvicorn.*src.api" > /dev/null; then
        echo "🛑 Stopping existing backend server..."
        pkill -f "uvicorn.*src.api"
        sleep 2
    fi
    
    # Kill existing frontend processes
    if pgrep -f "vite.*dev" > /dev/null; then
        echo "🛑 Stopping existing frontend server..."
        pkill -f "vite.*dev"
        sleep 2
    fi
}

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "✅ Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✅ Frontend server stopped"
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Kill any existing processes first
kill_existing_processes

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected structure: ai-job-apply/"
    echo "   ├── frontend/"
    echo "   └── backend/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
echo "🐍 Python version: $PYTHON_VERSION"

# Check Node.js version
NODE_VERSION=$(node --version 2>&1 | grep -o 'v[0-9]\+\.[0-9]\+' | head -1)
echo "📦 Node.js version: $NODE_VERSION"

# Start Backend Server
echo "🔧 Starting Backend Server (Port 8000)..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing/updating Python dependencies..."
pip install -r requirements.txt

# Setup database (SQLite by default)
echo "🗄️ Setting up database..."
cd backend && python3 setup-database.py && cd ..

# Check if backend port is already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is still in use, waiting for it to be free..."
    sleep 3
    if check_port 8000; then
        echo "❌ Port 8000 is still in use after cleanup. Please check manually:"
        echo "   lsof -i :8000"
        exit 1
    fi
fi

# Start backend server in background
echo "🚀 Starting FastAPI server..."
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend server failed to start"
    echo "🔍 Checking backend process..."
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died. Check logs above for errors."
    fi
    exit 1
fi

echo "✅ Backend server started successfully (PID: $BACKEND_PID)"
echo "   Health check: http://localhost:8000/health"
echo "   API docs: http://localhost:8000/docs"

# Go back to root and start Frontend
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check available ports for frontend (Vite auto-selects if 5173 is busy)
FRONTEND_PORT=5173
if check_port $FRONTEND_PORT; then
    echo "⚠️  Port $FRONTEND_PORT is in use, Vite will auto-select another port..."
fi

# Start frontend server in background
echo "🎨 Starting Frontend Server..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Find the actual port Vite is using (it might auto-select a different one)
ACTUAL_PORT=$(lsof -ti :5173,5174,5175,5176,5177 2>/dev/null | head -1)
if [ ! -z "$ACTUAL_PORT" ]; then
    FRONTEND_URL=$(lsof -Pan -p $ACTUAL_PORT -i | grep LISTEN | awk '{print $9}' | head -1)
    if [ ! -z "$FRONTEND_URL" ]; then
        FRONTEND_PORT=$(echo $FRONTEND_URL | cut -d: -f2)
    fi
fi

# Check if frontend is running
if ! curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    # Try common Vite ports
    for port in 5173 5174 5175 5176 5177; do
        if curl -s http://localhost:$port > /dev/null 2>&1; then
            FRONTEND_PORT=$port
            break
        fi
    done
    
    if ! curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "❌ Frontend server failed to start"
        echo "🔍 Checking frontend process..."
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "❌ Frontend process died. Check logs above for errors."
        fi
        exit 1
    fi
fi

echo "✅ Frontend server started successfully (PID: $FRONTEND_PID)"
echo "   Frontend: http://localhost:$FRONTEND_PORT"

# Go back to root
cd ..

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📱 Frontend: http://localhost:$FRONTEND_PORT"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running and monitor processes
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend server stopped unexpectedly"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend server stopped unexpectedly"
        break
    fi
    
    sleep 5
done

echo "🔄 One or more servers stopped. Use './start-dev.sh' to restart."
