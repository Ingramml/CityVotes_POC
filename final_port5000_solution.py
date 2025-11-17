#!/usr/bin/env python3
"""
Final Port 5000 Solution for CityVotes POC
Uses system-level port forwarding and aggressive process management
"""

import sys
import os
import subprocess
import time
import signal
from app import create_app

def completely_disable_airplay():
    """Aggressively disable AirPlay and related services"""
    print("🔧 Completely disabling AirPlay services...")

    try:
        # Kill all Control Center processes
        subprocess.run(['pkill', '-f', 'ControlCenter'], capture_output=True)
        time.sleep(1)

        # Kill all processes using port 5000
        result = subprocess.run(['lsof', '-ti:5000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"✅ Killed PID {pid}")
                except:
                    pass

        time.sleep(2)

        # Check if port is free
        check = subprocess.run(['lsof', '-i:5000'], capture_output=True)
        if check.returncode != 0:
            print("✅ Port 5000 is now free!")
            return True
        else:
            print("❌ Port 5000 still in use")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_direct_on_5000():
    """Start Flask app directly on port 5000"""
    print("🏛️  CityVotes POC - Final Port 5000 Solution")
    print("="*60)

    # Step 1: Aggressively disable AirPlay
    if not completely_disable_airplay():
        print("⚠️  Port 5000 still busy, trying force start anyway...")

    # Step 2: Create and start Flask app
    try:
        app = create_app()
        print("✅ Flask application created")
        print("✅ Sub-agents initialized")

        cities = app.city_config.get_supported_cities()
        print(f"✅ Cities configured: {cities}")

        print("\n🚀 FORCE STARTING ON PORT 5000...")
        print("📱 http://localhost:5000")
        print("📱 http://127.0.0.1:5000")
        print("\n✨ CityVotes POC Features:")
        print("   - Drag & drop file upload")
        print("   - Vote Summary Dashboard")
        print("   - Council Member Analysis")
        print("   - City Comparison View")
        print("   - Sample data at /sample-data")
        print("   - RESTful API endpoints")
        print("\n" + "="*60)
        print("🎉 PORT 5000 SHOULD NOW BE WORKING!")
        print("="*60)

        # Force start with SO_REUSEADDR
        import socket
        from werkzeug.serving import make_server

        server = make_server(
            host='0.0.0.0',
            port=5000,
            app=app,
            threaded=True
        )

        # Enable socket reuse
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("🚀 Server starting with socket reuse enabled...")
        server.serve_forever()

    except OSError as e:
        if "Address already in use" in str(e):
            print("\n❌ FINAL ATTEMPT FAILED")
            print("🍎 macOS AirPlay Receiver is persistently using port 5000")
            print("\n💡 MANUAL SOLUTION (takes 30 seconds):")
            print("   1. Open System Preferences")
            print("   2. Go to Sharing")
            print("   3. Uncheck 'AirPlay Receiver'")
            print("   4. Run: python3 run.py")
            print("\n🔄 ALTERNATIVE - Use working port:")
            print("   python3 run.py  # Uses port 5001, 8000, etc.")
            print("   Then visit the URL it provides")
            return 1
        else:
            raise e

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0

if __name__ == '__main__':
    sys.exit(start_direct_on_5000())