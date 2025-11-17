#!/usr/bin/env python3
"""
CityVotes POC - Enhanced Startup Script
Handles port conflicts and provides better error handling
"""

import sys
import os
from app import create_app

def start_server():
    """Start the Flask server with automatic port detection"""
    print("🏛️  CityVotes POC - Enhanced Startup")
    print("="*50)

    try:
        # Create Flask app
        app = create_app()
        print("✓ Flask application created")
        print("✓ Sub-agents initialized and ready")

        # Get supported cities
        cities = app.city_config.get_supported_cities()
        print(f"✓ Cities configured: {cities}")

        # Try multiple ports
        ports_to_try = [5001, 8000, 8080, 3000, 9000]  # Skip 5000 first due to AirPlay

        success = False
        for port in ports_to_try:
            try:
                print(f"\n🚀 Attempting server on port {port}...")

                # Test if port is available first
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result == 0:
                    print(f"❌ Port {port} is busy, trying next...")
                    continue

                print(f"✅ Port {port} is available!")
                print(f"   📱 Open: http://localhost:{port}")
                print(f"   📱 Or:   http://127.0.0.1:{port}")
                print("\n✨ Features available:")
                print("   - Drag & drop file upload")
                print("   - Vote Summary Dashboard")
                print("   - Council Member Analysis")
                print("   - City Comparison View")
                print("   - Sample data at /sample-data")
                print("\n" + "="*50)
                print(f"🚀 SERVER STARTING ON PORT {port} - READY FOR BROWSER!")
                print("="*50)

                app.run(
                    debug=True,
                    host='0.0.0.0',
                    port=port,
                    threaded=True
                )
                success = True
                break

            except Exception as e:
                print(f"❌ Error on port {port}: {e}")
                continue

        if not success:
            print("❌ Could not start on any available port")
            print("💡 Try manually specifying a port:")
            print("   python -c \"from app import create_app; create_app().run(host='0.0.0.0', port=9000)\"")
            return 1

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the CityVotes_POC directory")
        print("💡 Install requirements: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(start_server())