#!/bin/bash
# nginx Port 5000 Proxy Solution for CityVotes POC
# Sets up nginx to proxy port 5000 to the running Flask app

echo "🏛️  CityVotes POC - nginx Port 5000 Proxy Solution"
echo "=================================================="

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing nginx..."
    if command -v brew &> /dev/null; then
        brew install nginx
    else
        echo "❌ Please install nginx first:"
        echo "   brew install nginx"
        exit 1
    fi
fi

# Create nginx config for port 5000 proxy
NGINX_CONFIG="/opt/homebrew/etc/nginx/servers/cityvotes.conf"

echo "🔧 Creating nginx configuration..."
sudo mkdir -p "$(dirname "$NGINX_CONFIG")"

cat > /tmp/cityvotes.conf << 'EOF'
server {
    listen 5000;
    server_name localhost 127.0.0.1;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Handle static files
    location /static/ {
        proxy_pass http://127.0.0.1:5001;
    }

    # Handle API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
    }
}
EOF

echo "📝 Installing nginx configuration..."
sudo cp /tmp/cityvotes.conf "$NGINX_CONFIG"

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ nginx configuration is valid"
else
    echo "❌ nginx configuration error"
    exit 1
fi

# Stop any existing nginx processes
echo "🔧 Stopping existing nginx..."
sudo nginx -s stop 2>/dev/null || true
sudo pkill nginx 2>/dev/null || true

# Kill any process using port 5000
echo "🔧 Freeing port 5000..."
PIDS=$(lsof -ti:5000 2>/dev/null || true)
if [ ! -z "$PIDS" ]; then
    echo "Killing processes: $PIDS"
    sudo kill -9 $PIDS 2>/dev/null || true
fi

sleep 2

# Start nginx
echo "🚀 Starting nginx proxy..."
sudo nginx

# Check if nginx started successfully
sleep 2
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ | grep -q "200\|302"; then
    echo "✅ SUCCESS: nginx proxy is running!"
    echo "📱 http://localhost:5000 (nginx → Flask on 5001)"
    echo "📱 http://127.0.0.1:5000"
    echo ""
    echo "✨ Features available:"
    echo "   - Drag & drop file upload"
    echo "   - Vote Summary Dashboard"
    echo "   - Council Member Analysis"
    echo "   - City Comparison View"
    echo "   - Sample data at /sample-data"
    echo ""
    echo "=================================================="
    echo "🎉 PORT 5000 IS NOW WORKING VIA nginx PROXY!"
    echo "=================================================="

    # Show nginx status
    echo ""
    echo "nginx status:"
    ps aux | grep nginx | grep -v grep
else
    echo "❌ nginx proxy failed to start"
    sudo nginx -s stop 2>/dev/null
fi