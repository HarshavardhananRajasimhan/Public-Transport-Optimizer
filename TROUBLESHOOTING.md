# Troubleshooting - SmartTransit AI

## ✅ Servers Status

Both servers should be running:
- **Backend**: http://localhost:5000 ✓
- **Frontend**: http://localhost:5173 ✓ (Vite dev server)

## 🔍 Step-by-Step Debugging

### Step 1: Verify Backend is Working
```bash
curl -s http://localhost:5000/api/health | python3 -m json.tool
```

**Expected output**:
```json
{
  "status": "healthy",
  "buses_tracked": 2400+,
  "routes_active": 600+
}
```

### Step 2: Test Route Planning API
```bash
curl -X POST http://localhost:5000/api/plan-route \
  -H "Content-Type: application/json" \
  -d '{"start":{"lat":28.6315,"lon":77.2167,"name":"CP"},"end":{"lat":28.5494,"lon":77.2501,"name":"NP"},"preference":"fastest"}' \
  | python3 -m json.tool | head -50
```

**Expected**: Should return 3 routes with DTC route numbers

### Step 3: Open Frontend
1. Go to: http://localhost:5173
2. You should see "SmartTransit AI" header
3. Left side: Route planner form
4. Right side: "Your Journey Awaits" message

### Step 4: Test Route Planning in Browser
1. Enter "Connaught Place" in Start Location
2. Enter "Nehru Place" in End Location
3. Select "Fastest" preference
4. Click "Find Routes" button

### Step 5: Check Browser Console
Press F12 to open Developer Tools, go to Console tab.

**Look for**:
- "Backend response:" log with route data
- "Returning routes:" log with array of routes
- Any red error messages

### Step 6: Check Network Tab
In Developer Tools, go to Network tab:
1. Click "Find Routes" again
2. Look for "plan-route" request
3. Click on it
4. Check "Response" tab - should show JSON with routes

## 🐛 Common Issues & Fixes

### Issue 1: "Failed to plan route"
**Cause**: Backend not running or wrong URL
**Fix**:
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# If not, start it
cd backend
source venv/bin/activate
python3 route_planning_server.py
```

### Issue 2: Loading Forever
**Cause**: Frontend can't reach backend
**Check**:
1. Is backend on port 5000? `lsof -i :5000`
2. Is VITE_BACKEND_URL correct in `.env`?
3. Any CORS errors in console?

### Issue 3: No Routes Displayed
**Cause**: Data returned but not rendering
**Debug**:
1. Open console (F12)
2. Type: `localStorage.clear()` and press Enter
3. Refresh page (Cmd+R or Ctrl+R)
4. Try again

### Issue 4: Blank Screen
**Cause**: JavaScript error
**Fix**:
1. Check console for red errors
2. Look for TypeScript compilation errors
3. Try: `cd smarttransit-ai && npm install`

### Issue 5: "No routes found"
**Cause**: No buses near those locations
**Try different locations**:
- Connaught Place → Nehru Place
- India Gate → Rajiv Chowk
- Kashmere Gate → Red Fort

## 🧪 Manual Test in Browser Console

Open browser console (F12) and paste:

```javascript
// Test 1: Check if fetch works
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(d => console.log('✓ Backend reachable:', d))
  .catch(e => console.error('✗ Backend error:', e))

// Test 2: Test route planning
fetch('http://localhost:5000/api/plan-route', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    start: {lat: 28.6315, lon: 77.2167, name: "Connaught Place"},
    end: {lat: 28.5494, lon: 77.2501, name: "Nehru Place"},
    preference: "fastest"
  })
})
.then(r => r.json())
.then(d => {
  console.log('✓ Routes found:', d.routes.length);
  console.log('✓ First route:', d.routes[0].routeName);
  console.log('✓ Full data:', d);
})
.catch(e => console.error('✗ Error:', e))
```

## 📊 Expected Behavior

### When Working Correctly:
1. Click "Find Routes"
2. See loading spinner for 1-2 seconds
3. See 3 route cards appear
4. Each card shows:
   - "DTC Route XXXX" (e.g., "DTC Route 1938")
   - Duration (e.g., "80 minutes")
   - Cost (e.g., "₹58")
   - "✓ X buses tracked live on this route"
   - Segments (Walk → Bus → Walk)

### Example Route Card:
```
DTC Route 1938
80 min | ₹58 | Comfort: 7/10

✓ 3 buses tracked live on this route

Take DTC bus route 1938 - 9.7 km journey with 3 buses currently running

Segments:
• Walk to bus stop (1.59 km) - 19 min
• DTC Bus Route 1938 - 29 min
  ✓ Live tracking: 3 buses on this route
• Walk to destination (2.25 km) - 27 min
```

## 🔄 Full Reset

If nothing works, try a full reset:

```bash
# Stop all servers
# Press Ctrl+C in both terminal windows

# Backend
cd backend
source venv/bin/activate
python3 route_planning_server.py

# Frontend (new terminal)
cd smarttransit-ai
rm -rf node_modules/.vite
npm run dev
```

Then:
1. Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)
2. Go to http://localhost:3000
3. Open console (F12)
4. Try route planning again

## 📝 What to Report

If still not working, check:
1. What do you see on the screen?
2. What's in the browser console? (copy/paste errors)
3. What's in the Network tab for "plan-route" request?
4. Does the curl command work?

## ✅ Success Indicators

You'll know it's working when:
- ✓ Backend shows "✓ Loaded 2403 bus routes"
- ✓ Frontend loads without errors
- ✓ Clicking "Find Routes" shows loading spinner
- ✓ After 1-2 seconds, 3 route cards appear
- ✓ Each card shows "DTC Route XXXX"
- ✓ Console shows "Backend response:" and "Returning routes:"

---

**Current Status**: Both servers are running. Backend is returning data correctly. If frontend isn't showing routes, it's likely a rendering or state management issue.
