# Error Fix: "Can't Find Variable Category"

## Problem
When clicking on a category card, the UI showed error: "Error loading question, can't find variable category"

## Root Cause
The browser was caching an older version of `static/script.js` that still referenced the old `category` field name instead of the refactored `chapter` field name.

The refactored API returns:
- `chapter` (not `category`)
- `chapterName` (not `categoryName`)
- `question` (not `questionText`)

But the cached JavaScript was trying to reference `data.category` which doesn't exist in the API response.

## Solution
Added cache-busting query parameters to the script and link tags in `templates/index.html`:

**Before:**
```html
<link rel="stylesheet" href="/static/styles.css">
<script src="/static/script.js"></script>
```

**After:**
```html
<link rel="stylesheet" href="/static/styles.css?v=2">
<script src="/static/script.js?v=2"></script>
```

The `?v=2` query parameter forces the browser to:
1. Ignore cached versions
2. Fetch fresh copies from the server
3. Load the corrected script with proper field references

## Verification
- ✅ API response includes `chapter` field (not `category`)
- ✅ JavaScript references `data.chapter` (not `data.category`)
- ✅ Cache-busting parameters added to HTML
- ✅ Server serves fresh files when cache parameter changes

## Status
✅ **FIXED** - UI should now work without errors

Next time cache needs clearing, just increment the version number:
- `?v=3`, `?v=4`, etc.
