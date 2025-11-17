#!/usr/bin/env python3
"""
CityVotes POC Flask Startup Script with Troubleshooting
Comprehensive script to diagnose and fix common Flask startup issues
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("🏛️  CITYVOTES POC - FLASK STARTUP SCRIPT")
    print("="*60)

def check_environment():
    """Check and report environment status"""
    print("\n🔍 ENVIRONMENT CHECK")
    print("-" * 30)

    # Check working directory
    current_dir = os.getcwd()
    print(f"✓ Working Directory: {current_dir}")

    # Check if we're in the right place
    expected_files = ['agents', 'flask_example.py', 'test_agents.py']
    missing_files = []

    for file in expected_files:
        if os.path.exists(file):
            print(f"✓ Found: {file}")
        else:
            print(f"✗ Missing: {file}")
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️  WARNING: Missing files: {missing_files}")
        print("   Make sure you're running from the CityVotes_POC directory")
        return False

    return True

def check_python_requirements():
    """Check Python and required packages"""
    print("\n🐍 PYTHON REQUIREMENTS CHECK")
    print("-" * 30)

    # Check Python version
    python_version = sys.version.split()[0]
    print(f"✓ Python Version: {python_version}")

    # Check required packages
    required_packages = {
        'flask': 'Flask',
        'json': 'json (built-in)',
        'pathlib': 'pathlib (built-in)'
    }

    missing_packages = []

    for package, display_name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {display_name}: Available")
        except ImportError:
            print(f"✗ {display_name}: MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        if 'flask' in missing_packages:
            print("   Install Flask: pip3 install Flask")
        return False

    return True

def test_sub_agents():
    """Test if sub-agents can be imported"""
    print("\n🤖 SUB-AGENTS CHECK")
    print("-" * 30)

    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())

        from agents import DataValidationAgent, CityConfigAgent
        print("✓ DataValidationAgent: Imported successfully")
        print("✓ CityConfigAgent: Imported successfully")

        # Test initialization
        validator = DataValidationAgent()
        city_config = CityConfigAgent()
        print("✓ Sub-agents: Initialized successfully")

        # Test basic functionality
        cities = city_config.get_supported_cities()
        print(f"✓ Configured cities: {cities}")

        return True

    except ImportError as e:
        print(f"✗ Import Error: {e}")
        print("   Sub-agents will run in fallback mode")
        return False
    except Exception as e:
        print(f"✗ Initialization Error: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print("\n🧪 RUNNING TESTS")
    print("-" * 30)

    try:
        # Test agents if available
        result = subprocess.run([sys.executable, 'test_agents.py'],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✓ Agent integration tests: PASSED")
            return True
        else:
            print("✗ Agent integration tests: FAILED")
            print(f"   Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Tests timed out")
        return False
    except FileNotFoundError:
        print("✗ test_agents.py not found")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def start_flask_app(test_mode=False):
    """Start the Flask application"""
    print(f"\n🚀 STARTING FLASK APP {'(TEST MODE)' if test_mode else ''}")
    print("-" * 30)

    script_name = 'minimal_flask_test.py' if test_mode else 'flask_example.py'

    if not os.path.exists(script_name):
        print(f"✗ {script_name} not found")
        return False

    try:
        print(f"Starting {script_name}...")
        print("Press Ctrl+C to stop the server")
        print("\nAvailable URLs:")
        print("  - http://localhost:5000")
        print("  - http://127.0.0.1:5000")
        print("  - Check console for alternative ports if 5000 is busy")

        # Run the Flask app
        subprocess.run([sys.executable, script_name])
        return True

    except KeyboardInterrupt:
        print("\n\n✓ Server stopped by user")
        return True
    except Exception as e:
        print(f"✗ Error starting Flask app: {e}")
        return False

def show_troubleshooting():
    """Show troubleshooting guide"""
    print("\n🔧 TROUBLESHOOTING GUIDE")
    print("-" * 30)
    print("If you're having issues:")
    print("")
    print("1. IMPORT ERRORS:")
    print("   - Make sure you're in the CityVotes_POC directory")
    print("   - Try: cd /path/to/CityVotes_POC")
    print("   - Check that 'agents' folder exists")
    print("")
    print("2. FLASK NOT STARTING:")
    print("   - Install Flask: pip3 install Flask")
    print("   - Try test mode: python3 run_flask.py --test")
    print("")
    print("3. PORT ISSUES:")
    print("   - Script tries multiple ports (5000, 5001, 8000, 8080)")
    print("   - Check for port conflicts with other apps")
    print("")
    print("4. PERMISSION ISSUES:")
    print("   - Try: chmod +x *.py")
    print("   - Check file permissions")
    print("")
    print("5. BROWSER ACCESS DENIED:")
    print("   - Try http://localhost:PORT instead of 127.0.0.1:PORT")
    print("   - Check firewall settings")
    print("   - Try different browser")

def main():
    """Main startup routine"""
    print_banner()

    # Parse command line arguments
    test_mode = '--test' in sys.argv
    skip_checks = '--skip-checks' in sys.argv

    if not skip_checks:
        # Run environment checks
        env_ok = check_environment()
        python_ok = check_python_requirements()
        agents_ok = test_sub_agents()

        if not env_ok or not python_ok:
            print("\n❌ CRITICAL ISSUES FOUND")
            show_troubleshooting()
            return 1

        if not agents_ok:
            print("\n⚠️  Sub-agents not available - will run in fallback mode")

        # Run tests
        if agents_ok:
            tests_ok = run_tests()
            if not tests_ok:
                print("\n⚠️  Tests failed but continuing anyway...")

    # Start Flask app
    print("\n" + "="*60)
    success = start_flask_app(test_mode)

    if not success:
        print("\n❌ FAILED TO START FLASK APP")
        show_troubleshooting()
        return 1

    print("\n✓ Session completed successfully")
    return 0

if __name__ == '__main__':
    if '--help' in sys.argv:
        print("CityVotes POC Flask Startup Script")
        print("\nUsage:")
        print("  python3 run_flask.py              # Normal mode")
        print("  python3 run_flask.py --test       # Test mode (minimal Flask)")
        print("  python3 run_flask.py --skip-checks # Skip environment checks")
        print("  python3 run_flask.py --help       # Show this help")
    else:
        exit(main())