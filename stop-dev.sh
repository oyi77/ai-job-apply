#!/bin/bash

# AI Job Application Assistant - Stop Development Servers Script

echo "🛑 Stopping AI Job Application Assistant Development Environment..."

# Function to kill processes by pattern
kill_processes() {
    local pattern=$1
    local name=$2
    
    if pgrep -f "$pattern" > /dev/null; then
        echo "🔄 Stopping $name..."
        pkill -f "$pattern"
        sleep 2
        
        # Check if processes are still running
        if pgrep -f "$pattern" > /dev/null; then
            echo "⚠️  Force stopping $name..."
            pkill -9 -f "$pattern"
            sleep 1
        fi
        
        if ! pgrep -f "$pattern" > /dev/null; then
            echo "✅ $name stopped successfully"
        else
            echo "❌ Failed to stop $name"
        fi
    else
        echo "ℹ️  $name is not running"
    fi
}

# Stop backend server
kill_processes "uvicorn.*src.api" "Backend Server"

# Stop frontend server
kill_processes "vite.*dev" "Frontend Server"

# Check for any remaining processes on common ports
echo "🔍 Checking for remaining processes on ports..."

for port in 8000 5173 5174 5175 5176 5177; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  Port $port is still in use:"
        lsof -i :$port
        echo "   You may need to kill manually: lsof -ti :$port | xargs kill"
    fi
done

echo ""
echo "🎉 Development environment stopped!"
echo ""
echo "To start again, run: ./start-dev.sh"
