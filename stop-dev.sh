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

# Stop backend server (multiple patterns to catch all variations)
echo "🔍 Looking for backend processes..."
kill_processes "python3 main.py" "Backend Server (Python)"
kill_processes "python main.py" "Backend Server (Python)"
kill_processes "uvicorn.*src.api" "Backend Server (Uvicorn)"
kill_processes "uvicorn.*main" "Backend Server (Uvicorn)"

# Stop frontend server
echo "🔍 Looking for frontend processes..."
kill_processes "vite.*dev" "Frontend Server (Vite)"
kill_processes "npm.*dev" "Frontend Server (NPM)"
kill_processes "node.*vite" "Frontend Server (Node)"

# Stop any remaining Python processes that might be our backend
echo "🔍 Looking for remaining Python processes..."
if pgrep -f "main.py" > /dev/null; then
    echo "⚠️  Found remaining main.py processes, force stopping..."
    pkill -9 -f "main.py"
    sleep 1
fi

# Check for any remaining processes on common ports
echo "🔍 Checking for remaining processes on ports..."

for port in 8000 5173 5174 5175 5176 5177; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  Port $port is still in use:"
        lsof -i :$port
        echo "   Force killing processes on port $port..."
        lsof -ti :$port | xargs kill -9 2>/dev/null
        sleep 1
        
        # Check again
        if lsof -i :$port >/dev/null 2>&1; then
            echo "❌ Port $port is still in use after force kill"
        else
            echo "✅ Port $port is now free"
        fi
    else
        echo "✅ Port $port is free"
    fi
done

# Final cleanup - kill any remaining processes that might be related
echo "🔍 Final cleanup..."
if pgrep -f "ai-job-apply" > /dev/null; then
    echo "⚠️  Found remaining ai-job-apply related processes, force stopping..."
    pkill -9 -f "ai-job-apply"
fi

if pgrep -f "backend" > /dev/null; then
    echo "⚠️  Found remaining backend related processes, force stopping..."
    pkill -9 -f "backend"
fi

# Wait a moment for processes to fully terminate
sleep 2

# Final status check
echo ""
echo "📊 Final Status Check:"
echo "======================"

# Check if any of our processes are still running
backend_running=false
frontend_running=false

if pgrep -f "main.py" > /dev/null; then
    echo "❌ Backend still running (main.py)"
    backend_running=true
fi

if pgrep -f "vite" > /dev/null; then
    echo "❌ Frontend still running (vite)"
    frontend_running=true
fi

# Check ports
if lsof -i :8000 >/dev/null 2>&1; then
    echo "❌ Port 8000 still in use"
    backend_running=true
fi

if lsof -i :5173 >/dev/null 2>&1; then
    echo "❌ Port 5173 still in use"
    frontend_running=true
fi

if [ "$backend_running" = false ] && [ "$frontend_running" = false ]; then
    echo "✅ All services stopped successfully"
else
    echo "⚠️  Some services may still be running"
    echo "   You may need to manually kill remaining processes:"
    echo "   - Backend: pkill -9 -f 'main.py'"
    echo "   - Frontend: pkill -9 -f 'vite'"
    echo "   - Port 8000: lsof -ti :8000 | xargs kill -9"
    echo "   - Port 5173: lsof -ti :5173 | xargs kill -9"
fi

echo ""
echo "🎉 Development environment stopped!"
echo ""
echo "To start again, run: ./start-dev.sh"
