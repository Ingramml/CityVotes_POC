# Flask "Access Not Allowed" - Troubleshooting Guide

## 🚀 Quick Fix (Try This First)

1. **Use the startup script:**
   ```bash
   python3 run_flask.py
   ```

2. **If that fails, try test mode:**
   ```bash
   python3 run_flask.py --test
   ```

3. **Check if basic Flask works:**
   ```bash
   python3 minimal_flask_test.py
   ```

## 🔍 Step-by-Step Diagnosis

### Step 1: Environment Check
```bash
# Make sure you're in the right directory
pwd
# Should show: /path/to/CityVotes_POC

# Check required files exist
ls -la
# Should see: agents/ flask_example.py test_agents.py
```

### Step 2: Test Sub-Agents
```bash
# Test if sub-agents work independently
python3 test_agents.py
```

**Expected Output:**
```
✓ Data Validation Agent: Working
✓ City Configuration Agent: Working
✓ Agent Communication: Working
✓ Error Handling: Working
```

### Step 3: Test Basic Flask
```bash
# Test minimal Flask functionality
python3 minimal_flask_test.py
```

### Step 4: Try Main App
```bash
# Run the full Flask app
python3 flask_example.py
```

## 🔧 Common Issues & Solutions

### Issue 1: "Module 'agents' not found"
**Symptoms:** ImportError when starting Flask
**Solution:**
```bash
# Make sure you're in the CityVotes_POC directory
cd /path/to/CityVotes_POC
python3 flask_example.py
```

### Issue 2: "Address already in use"
**Symptoms:** Port 5000 is busy
**Solution:** The app will automatically try ports 5001, 8000, 8080

### Issue 3: "Access Not Allowed" in Browser
**Solutions to try:**
1. Use `localhost` instead of `127.0.0.1`:
   - Try: http://localhost:5000
   - Instead of: http://127.0.0.1:5000

2. Check the console output for the actual port:
   ```
   Starting server on port 5001...  # Use this port
   ```

3. Try different browsers (Chrome, Firefox, Safari)

4. Check firewall settings

### Issue 4: Flask Not Installed
**Symptoms:** "No module named 'flask'"
**Solution:**
```bash
pip3 install Flask
# or
python3 -m pip install Flask
```

### Issue 5: Permission Denied
**Solution:**
```bash
chmod +x *.py
python3 flask_example.py
```

## 🧪 Testing Strategy

### Level 1: Basic Python
```bash
python3 --version
# Should show Python 3.x
```

### Level 2: Flask Installation
```bash
python3 -c "import flask; print('Flask OK')"
# Should print: Flask OK
```

### Level 3: Sub-Agents
```bash
python3 -c "from agents import DataValidationAgent; print('Agents OK')"
# Should print: Agents OK
```

### Level 4: Integration
```bash
python3 test_agents.py
# Should show all tests passing
```

### Level 5: Web Server
```bash
python3 minimal_flask_test.py
# Should start server and be accessible in browser
```

## 🌐 Browser Troubleshooting

### If browser shows "Access Denied" or "Can't connect":

1. **Check the exact URL from console output:**
   ```
   URL: http://127.0.0.1:5001  # Use this exact URL
   ALT: http://localhost:5001  # Or try this alternative
   ```

2. **Try curl instead of browser:**
   ```bash
   curl http://localhost:5000
   # Should return HTML content
   ```

3. **Check if server is actually running:**
   ```bash
   # In another terminal:
   netstat -an | grep 5000
   # Should show something like: tcp4  0  0  *.5000  *.*  LISTEN
   ```

## 📝 API Testing (Alternative to Browser)

If browser access doesn't work, test with curl:

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test cities API
curl http://localhost:5000/api/cities

# Expected response:
{
  "success": true,
  "cities": {
    "santa_ana": "Santa Ana, CA",
    "pomona": "Pomona, CA"
  },
  "total_cities": 2
}
```

## 🆘 Last Resort Options

### Option 1: Different Port Manually
```bash
# Edit flask_example.py, change port to 8080:
# app.run(debug=True, host='0.0.0.0', port=8080)
```

### Option 2: Run Without Sub-Agents
```bash
# The app has fallback mode if sub-agents fail to load
# It will still show a basic interface
```

### Option 3: Use Different Host
```bash
# Change host in flask_example.py:
# app.run(debug=True, host='localhost', port=5000)
```

## ✅ Success Indicators

**You'll know it's working when:**
1. Console shows: "Starting server..."
2. Console shows: "✓ Sub-agents initialized successfully"
3. No error messages in console
4. Browser loads the page with "CityVotes POC" title
5. You can see the upload form and city information

**Example successful console output:**
```
==================================================
CityVotes POC - Sub-Agent Flask Demo
==================================================
✓ Sub-agents imported successfully
✓ Sub-agents initialized successfully
✓ Current directory: /path/to/CityVotes_POC
✓ Python path includes: /path/to/CityVotes_POC

🚀 Starting server...
   URL: http://127.0.0.1:5000
   ALT: http://localhost:5000

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

## 📞 Still Having Issues?

If none of these solutions work:

1. Run the comprehensive diagnostic:
   ```bash
   python3 run_flask.py
   ```

2. Copy the console output and error messages

3. The issue might be system-specific (firewall, network configuration, etc.)

The sub-agents work independently of the web interface, so you can still use them directly with:
```bash
python3 test_agents.py  # Test the core functionality
```