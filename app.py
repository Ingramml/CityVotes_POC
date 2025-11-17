#!/usr/bin/env python3
"""
CityVotes POC - Main Application Entry Point
Flask application implementing the Two-City Vote Analysis Platform PRD
"""

import sys
import os
from app import create_app

# Add current directory to path for sub-agents
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Main application entry point"""
    print("🏛️  CityVotes POC - Starting Application")
    print("="*50)

    try:
        # Create Flask app
        app = create_app()
        print("✓ Flask application created")
        print("✓ Sub-agents initialized:")
        print("  - DataValidationAgent: Active")
        print("  - CityConfigAgent: Active")
        print("  - FileProcessingAgent: Active")

        # Get supported cities
        cities = app.city_config.get_supported_cities()
        print(f"✓ Cities configured: {cities}")

        print("\n🚀 Starting server...")
        print("📱 Open in browser:")
        print("   - http://localhost:5000")
        print("   - http://127.0.0.1:5000")

        print("\n📊 Dashboard Features:")
        print("   - Vote Summary Dashboard")
        print("   - Council Member Analysis")
        print("   - City Comparison View")

        print("\n🔌 API Endpoints:")
        print("   - GET /api/cities")
        print("   - GET /api/city/<name>")
        print("   - GET /api/session/data")
        print("   - POST /api/validate")

        print("\n" + "="*50)

        # Try multiple ports if 5000 is busy
        ports_to_try = [5000, 5001, 8000, 8080]

        for port in ports_to_try:
            try:
                print(f"🚀 Attempting to start on port {port}...")
                app.run(
                    debug=True,
                    host='0.0.0.0',
                    port=port,
                    threaded=True
                )
                break
            except OSError as e:
                if "Address already in use" in str(e):
                    print(f"Port {port} is busy, trying next port...")
                    continue
                else:
                    raise e
        else:
            print("❌ Could not start on any available port")

    except ImportError as e:
        print(f"✗ Import Error: {e}")
        print("Make sure you're running from the CityVotes_POC directory")
        return 1
    except Exception as e:
        print(f"✗ Application Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())