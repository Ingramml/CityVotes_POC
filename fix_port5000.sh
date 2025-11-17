#!/bin/bash
# Fix Port 5000 for CityVotes POC
# This script disables AirPlay Receiver and starts the app on port 5000

echo "🏛️  CityVotes POC - Port 5000 Fix Script"
echo "=========================================="

# Function to check if port is free
check_port() {
    lsof -i:5000 >/dev/null 2>&1
    return $?
}

# Step 1: Kill AirPlay processes
echo "🔧 Disabling AirPlay Receiver..."
pkill -f "ControlCenter" 2>/dev/null
sudo pkill -f "airplay" 2>/dev/null
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.AirPlayXPCHelper.plist 2>/dev/null

# Step 2: Kill processes using port 5000
echo "🔧 Freeing port 5000..."
PIDS=$(lsof -ti:5000 2>/dev/null)
if [ ! -z "$PIDS" ]; then
    echo "Killing processes: $PIDS"
    sudo kill -9 $PIDS 2>/dev/null
fi

# Wait a moment
sleep 2

# Step 3: Check if port is now free
if check_port; then
    echo "❌ Port 5000 still in use. Manual intervention required:"
    echo "   1. Open System Preferences → Sharing"
    echo "   2. Uncheck 'AirPlay Receiver'"
    echo "   3. Run: python3 run.py"
    exit 1
else
    echo "✅ Port 5000 is now free!"
fi

# Step 4: Start the application
echo "🚀 Starting CityVotes POC on port 5000..."
echo "📱 http://localhost:5000"
echo "=========================================="

# Start with forced port 5000
python3 -c "
from app import create_app
import socket
from werkzeug.serving import make_server

app = create_app()
print('✅ Flask app created')
print('✅ Sub-agents ready')

try:
    server = make_server('0.0.0.0', 5000, app, threaded=True)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('🎉 SUCCESS: Server running on http://localhost:5000')
    server.serve_forever()
except Exception as e:
    print(f'❌ Failed: {e}')
    print('💡 Alternative: python3 run.py')
"