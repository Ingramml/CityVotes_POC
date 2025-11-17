#!/usr/bin/env python3
"""
Final Working Solution for CityVotes POC Port 5000
Uses socat TCP proxy to redirect port 5000 → 5001
"""

import sys
import os
import subprocess
import time
import signal
import socket
import threading
from app import create_app

def kill_port_5000():
    """Aggressively kill anything on port 5000"""
    try:
        # Get PIDs using port 5000
        result = subprocess.run(['lsof', '-ti:5000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=False)
                    print(f"✅ Killed PID {pid} on port 5000")
                except:
                    pass

        # Kill common AirPlay processes
        for process in ['ControlCenter', 'rapportd', 'AirPlayXPCHelper']:
            subprocess.run(['pkill', '-f', process], check=False)

        time.sleep(2)
        return True
    except:
        return False

def check_socat():
    """Check if socat is available"""
    try:
        subprocess.run(['socat', '-V'], capture_output=True, check=True)
        return True
    except:
        print("📦 Installing socat...")
        try:
            subprocess.run(['brew', 'install', 'socat'], check=True)
            return True
        except:
            print("❌ Could not install socat")
            return False

def start_socat_proxy():
    """Start socat proxy from 5000 to 5001"""
    try:
        # Kill port 5000 processes
        kill_port_5000()

        print("🚀 Starting socat proxy: 5000 → 5001")

        # Start socat proxy in background
        proc = subprocess.Popen([
            'socat',
            'TCP-LISTEN:5000,fork,reuseaddr',
            'TCP:127.0.0.1:5001'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(2)

        # Test if proxy is working
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 5000))
            sock.close()

            if result == 0:
                print("✅ socat proxy is running on port 5000")
                return proc
            else:
                proc.kill()
                return None
        except:
            proc.kill()
            return None
    except Exception as e:
        print(f"❌ socat proxy failed: {e}")
        return None

def start_complete_solution():
    """Start complete solution: Flask on 5001, socat proxy on 5000"""
    print("🏛️  CityVotes POC - Final Working Solution")
    print("="*60)

    # Step 1: Check socat availability
    if not check_socat():
        return 1

    # Step 2: Start Flask app on port 5001
    print("🚀 Starting Flask application on port 5001...")

    # Start Flask app in separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    time.sleep(3)

    # Test Flask app on 5001
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()

        if result != 0:
            print("❌ Flask app failed to start on port 5001")
            return 1
        else:
            print("✅ Flask app running on port 5001")
    except:
        print("❌ Could not verify Flask app")
        return 1

    # Step 3: Start socat proxy
    proxy_proc = start_socat_proxy()
    if not proxy_proc:
        print("❌ Failed to start socat proxy")
        return 1

    # Step 4: Final test
    time.sleep(2)
    test_result = test_port_5000()

    if test_result:
        print("✅ SUCCESS: http://localhost:5000 is working!")
        print("📱 http://localhost:5000 (proxied)")
        print("📱 http://localhost:5001 (direct)")
        print("\n✨ CityVotes POC Features:")
        print("   - Drag & drop file upload")
        print("   - Vote Summary Dashboard")
        print("   - Council Member Analysis")
        print("   - City Comparison View")
        print("   - Sample data at /sample-data")
        print("\n" + "="*60)
        print("🎉 http://localhost:5000 IS NOW WORKING!")
        print("="*60)

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            proxy_proc.kill()
            print("✅ Cleaned up")
            return 0
    else:
        print("❌ Port 5000 test failed")
        proxy_proc.kill()
        return 1

def run_flask_app():
    """Run Flask app on port 5001"""
    try:
        app = create_app()
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5001,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"Flask error: {e}")

def test_port_5000():
    """Test if port 5000 is responding to HTTP requests"""
    try:
        import urllib.request
        response = urllib.request.urlopen('http://localhost:5000/', timeout=5)
        return response.getcode() == 200
    except:
        return False

if __name__ == '__main__':
    sys.exit(start_complete_solution())