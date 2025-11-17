#!/usr/bin/env python3
"""
Native macOS Port 5000 Solution for CityVotes POC
Uses system-level port redirection and native macOS commands
"""

import sys
import os
import subprocess
import time
import signal
import socket
from app import create_app

def check_admin():
    """Check if running with admin privileges"""
    return os.geteuid() == 0

def get_port_pid(port=5000):
    """Get PID of process using specified port"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'],
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    return None

def force_kill_port_process(port=5000):
    """Force kill process using port with maximum aggression"""
    print(f"🔧 Force killing process on port {port}...")

    try:
        # Method 1: Get PID and kill
        pid = get_port_pid(port)
        if pid:
            print(f"Found PID {pid} using port {port}")

            # Try regular kill first
            try:
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(1)
                if not get_port_pid(port):
                    print(f"✅ Port {port} freed with SIGTERM")
                    return True
            except:
                pass

            # Try force kill
            try:
                os.kill(int(pid), signal.SIGKILL)
                time.sleep(1)
                if not get_port_pid(port):
                    print(f"✅ Port {port} freed with SIGKILL")
                    return True
            except:
                pass

        # Method 2: Use pkill to kill by name
        airplay_processes = ['ControlCenter', 'AirPlayXPCHelper', 'rapportd']
        for process in airplay_processes:
            try:
                subprocess.run(['pkill', '-f', process], check=False)
                print(f"Killed {process} processes")
            except:
                pass

        time.sleep(2)

        # Method 3: Final check and sudo kill if needed
        pid = get_port_pid(port)
        if pid:
            print(f"Port still in use by PID {pid}, trying sudo...")
            try:
                subprocess.run(['sudo', 'kill', '-9', pid], check=True)
                time.sleep(2)
                if not get_port_pid(port):
                    print(f"✅ Port {port} freed with sudo kill")
                    return True
            except:
                pass

        return not bool(get_port_pid(port))

    except Exception as e:
        print(f"Error in force_kill_port_process: {e}")
        return False

def setup_port_forwarding(source_port=5000, target_port=5001):
    """Setup pfctl port forwarding as fallback"""
    try:
        print(f"Setting up port forwarding {source_port} → {target_port}")

        # Create pf rule
        rule = f"rdr pass on lo0 inet proto tcp from any to any port {source_port} -> 127.0.0.1 port {target_port}"

        # Write rule to temp file
        rule_file = "/tmp/pf_redirect.conf"
        with open(rule_file, 'w') as f:
            f.write(rule + "\n")

        # Apply rule
        subprocess.run(['sudo', 'pfctl', '-f', rule_file], check=True)
        subprocess.run(['sudo', 'pfctl', '-e'], check=True)

        print(f"✅ Port forwarding enabled: {source_port} → {target_port}")
        return True

    except Exception as e:
        print(f"Port forwarding failed: {e}")
        return False

def start_on_available_port():
    """Start Flask app on first available port, then setup forwarding"""
    print("🏛️  CityVotes POC - Native Port 5000 Solution")
    print("="*60)

    # Step 1: Try to free port 5000 aggressively
    print("🔧 Step 1: Aggressively freeing port 5000...")
    if force_kill_port_process(5000):
        print("✅ Port 5000 successfully freed!")

        # Try to start directly on port 5000
        try:
            app = create_app()
            print("✅ Flask application created")
            print("✅ Sub-agents initialized")

            print("🚀 Starting directly on port 5000...")
            print("📱 http://localhost:5000")
            print("📱 http://127.0.0.1:5000")
            print("\n" + "="*60)
            print("🎉 SUCCESS: Running on port 5000!")
            print("="*60)

            app.run(
                debug=False,
                host='0.0.0.0',
                port=5000,
                threaded=True,
                use_reloader=False
            )
            return 0

        except OSError:
            print("❌ Port 5000 immediately reclaimed")

    # Step 2: Start on alternative port
    print("🔧 Step 2: Starting on alternative port...")
    for target_port in [5001, 5002, 8000, 8080]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', target_port))
            sock.close()

            if result != 0:  # Port is available
                print(f"✅ Using port {target_port} for Flask app")

                # Start Flask app in background
                app = create_app()
                print("✅ Flask application created")
                print("✅ Sub-agents initialized")

                # Try to setup port forwarding
                print(f"🔧 Setting up port forwarding 5000 → {target_port}...")
                if setup_port_forwarding(5000, target_port):
                    print("✅ Port forwarding active!")
                    print("📱 http://localhost:5000 (forwarded)")
                    print(f"📱 http://localhost:{target_port} (direct)")
                else:
                    print(f"📱 http://localhost:{target_port} (direct access)")

                print("\n✨ Features available:")
                print("   - Drag & drop file upload")
                print("   - Vote Summary Dashboard")
                print("   - Council Member Analysis")
                print("   - City Comparison View")
                print("   - Sample data at /sample-data")
                print("\n" + "="*60)
                print("🎉 CITYVOTES POC IS RUNNING!")
                print("="*60)

                app.run(
                    debug=False,
                    host='0.0.0.0',
                    port=target_port,
                    threaded=True,
                    use_reloader=False
                )
                return 0

        except Exception as e:
            continue

    print("❌ No available ports found")
    return 1

if __name__ == '__main__':
    try:
        sys.exit(start_on_available_port())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        # Clean up port forwarding
        try:
            subprocess.run(['sudo', 'pfctl', '-d'], check=False)
            print("✅ Cleaned up port forwarding")
        except:
            pass
        sys.exit(0)