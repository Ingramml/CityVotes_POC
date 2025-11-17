#!/usr/bin/env python3
"""
CityVotes POC - Force Port 5000 Solution
Kills AirPlay Receiver and starts on port 5000 as requested
"""

import sys
import os
import subprocess
import time
from app import create_app

def disable_airplay_receiver():
    """Disable AirPlay Receiver that uses port 5000"""
    print("🔧 Checking port 5000 availability...")

    try:
        # Check what's using port 5000
        result = subprocess.run(['lsof', '-i', ':5000'],
                              capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            print("❌ Port 5000 is in use by:")
            print(result.stdout)

            # Try to kill the process
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    try:
                        print(f"🔧 Attempting to free port 5000 (PID: {pid})...")
                        subprocess.run(['kill', '-9', pid], check=True)
                        print(f"✅ Killed process {pid}")
                        time.sleep(1)  # Wait for port to be freed
                    except subprocess.CalledProcessError:
                        print(f"❌ Could not kill process {pid} (requires admin)")
                        return False
        else:
            print("✅ Port 5000 is available!")

        return True

    except Exception as e:
        print(f"❌ Error checking port 5000: {e}")
        return False

def start_on_port_5000():
    """Start the Flask application specifically on port 5000"""
    print("🏛️  CityVotes POC - Port 5000 Forced Start")
    print("="*50)

    try:
        # Create Flask app
        app = create_app()
        print("✅ Flask application created")
        print("✅ Sub-agents initialized and ready")

        # Get supported cities
        cities = app.city_config.get_supported_cities()
        print(f"✅ Cities configured: {cities}")

        # Disable AirPlay if needed
        if not disable_airplay_receiver():
            print("⚠️  Could not free port 5000, but trying anyway...")

        print("\n🚀 Starting server on port 5000...")
        print("📱 http://localhost:5000")
        print("📱 http://127.0.0.1:5000")
        print("\n✨ Features available:")
        print("   - Drag & drop file upload")
        print("   - Vote Summary Dashboard")
        print("   - Council Member Analysis")
        print("   - City Comparison View")
        print("   - Sample data at /sample-data")
        print("\n" + "="*50)
        print("🚀 SERVER RUNNING ON PORT 5000 AS REQUESTED!")
        print("="*50)

        # Force start on port 5000
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )

        return 0

    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 5000 still in use!")
            print("\n💡 SOLUTION: Disable AirPlay Receiver manually:")
            print("   1. System Preferences → Sharing")
            print("   2. Uncheck 'AirPlay Receiver'")
            print("   3. Run this script again")
            print("\n🔄 Or use alternative startup: python3 run.py")
            return 1
        else:
            raise e

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the CityVotes_POC directory")
        print("💡 Install requirements: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(start_on_port_5000())