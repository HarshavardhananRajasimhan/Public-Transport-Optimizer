# Frontend Testing Guide

## Quick Test

Open your browser to: **http://localhost:3000**

Then open the browser console (F12 → Console tab) and try:

### Test 1: Check if backend is reachable
```javascript
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(d => console.log('Backend health:', d))
```

### Test 2: Test route planning directly
```javascript
fetch('http://localhost:5000/api/plan-route', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    start: {lat: 28.6315, lon: 77.2167, name: "CP"},
    end: {lat: 28.5494, lon: 77.2501, name: "NP"},
    preference: "fastest"
  })
})
.then(r => r.json())
.then(d => console.log('Routes:', d.routes.length, 'routes found'))
```

### Test 3: Check what happens when you click "Find Routes"
1. Enter "Connaught Place" as start
2. Enter "Nehru Place" as end
3. Click "Find Routes"
4. Watch the console for:
   - "Backend response:" log
   - "Returning routes:" log
   - Any errors

## Common Issues

### Issue 1: CORS Error
**Symptom**: Console shows "CORS policy" error
**Fix**: Backend should have CORS enabled (it does)

### Issue 2: Network Error
**Symptom**: Console shows "Failed to fetch"
**Fix**: Make sure backend is running on port 5000

### Issue 3: No Routes Displayed
**Symptom**: Backend returns data but UI shows nothing
**Possible causes**:
- Data format mismatch
- TypeScript type errors
- Component not re-rendering

### Issue 4: Loading Forever
**Symptom**: Spinner never stops
**Cause**: Error in try/catch not being handled

## What Should Happen

1. Click "Find Routes"
2. See loading spinner
3. After 1-2 seconds, see 3 route cards
4. Each card shows:
   - "DTC Route XXXX"
   - Duration
   - Cost
   - "✓ X buses tracked live"

## If Nothing Works

Try this in the browser console:
```javascript
// Force test the route planner service
import('./services/routePlannerService.js').then(module => {
  module.planRouteWithRealData('Connaught Place', 'Nehru Place', {priority: 'FASTEST'})
    .then(routes => console.log('SUCCESS:', routes))
    .catch(err => console.error('ERROR:', err))
})
```
