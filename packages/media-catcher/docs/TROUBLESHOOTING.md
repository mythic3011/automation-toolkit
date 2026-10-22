# 🔧 Troubleshooting Guide - Panopto XHR Catcher

## Quick Debug Steps

### Step 1: Check if Script is Loaded

1. Open browser console (F12)
2. Look for this message:

```
═══════════════════════════════════════
🎯 Panopto XHR Catcher Loaded!
═══════════════════════════════════════
```

**If you DON'T see this:**

- Check if Tampermonkey/Violentmonkey is enabled
- Check if the script is enabled in the extension
- Verify you're on a matching URL (`*.panopto.com/*`)
- Try refreshing the page (Ctrl+R or F5)

### Step 2: Check Script Status

In the browser console, type:

```javascript
panoptoCatcher.status();
```

You should see:

```
═══════════════════════════════════════
📊 Panopto XHR Catcher Status
═══════════════════════════════════════
✅ Script loaded: true
✅ XHR interceptors installed: true
📦 GUI button exists: true
📦 GUI panel exists: true
🔄 Auto-download enabled: true
📥 Requests captured: 0
💾 Requests downloaded: 0
```

**If GUI button/panel shows false:**

- Wait 3-5 seconds for initialization
- Try running: `panoptoCatcher.showPanel()`
- Check console for error messages

### Step 3: Look for the GUI Button

Look in the **bottom-right corner** of the page for a purple floating button with 📥

**If you DON'T see the button:**

1. Check console for errors
2. Try running in console:

```javascript
panoptoCatcher.showPanel();
```

3. Check if another element is overlapping it
4. Try scrolling the page

### Step 4: Test XHR Interception

1. Play the Panopto video
2. Watch the browser console
3. Look for messages like:

```
[Panopto XHR Catcher] POST request detected: ...
[Panopto XHR Catcher] 🎯 TARGET REQUEST INTERCEPTED!
[Panopto XHR Catcher] ✅ Response captured successfully!
```

**If you DON'T see these messages:**

- The video might not be making DeliveryInfo requests yet
- Try seeking to different parts of the video
- Check the Network tab (F12 → Network) for DeliveryInfo.aspx requests
- The script might be looking for the wrong URL pattern

## Common Issues & Solutions

### Issue 1: Script Not Loading

**Symptoms:** No console messages, no GUI

**Solutions:**

1. **Reinstall the script:**

   - Open Tampermonkey dashboard
   - Delete the old script
   - Create new script and paste code again
   - Save (Ctrl+S)

2. **Check @match patterns:**

   ```javascript
   // Should include:
   // @match        https://polyu.ap.panopto.com/*
   // @match        https://*.panopto.com/*
   ```

3. **Try different @run-at:**
   - Currently set to `document-end`
   - If not working, try `document-idle`

### Issue 2: GUI Not Appearing

**Symptoms:** Script loads but no button visible

**Solutions:**

1. **Check for conflicts:**

   - Disable other UserScripts temporarily
   - Disable browser extensions that modify the page

2. **Force create GUI:**

   ```javascript
   // In console:
   document.body.innerHTML +=
     '<button id="panopto-catcher-toggle-btn" style="position:fixed;bottom:20px;right:20px;width:60px;height:60px;z-index:999999;background:purple;color:white;border:none;border-radius:50%;font-size:24px;">📥</button>';
   ```

3. **Check CSS:**
   - Open DevTools → Elements
   - Search for `panopto-catcher-styles`
   - If missing, styles weren't injected

### Issue 3: No Requests Being Captured

**Symptoms:** GUI works but no captures

**Solutions:**

1. **Verify the URL pattern:**

   - Open DevTools → Network tab
   - Filter for "DeliveryInfo"
   - Check if requests are being made
   - Note the exact URL format

2. **Check request method:**

   - In Network tab, verify it's a POST request
   - Verify the URL contains "/Panopto/Pages/Viewer/DeliveryInfo.aspx"

3. **Manual test:**

   ```javascript
   // In console, force trigger:
   window.panoptoCatcher.status();
   ```

4. **Check if interceptor is working:**
   - Play the video
   - Look for "POST request detected" messages in console
   - If you see many POST requests but no "TARGET REQUEST INTERCEPTED", the URL pattern might be different

### Issue 4: Downloads Not Working

**Symptoms:** Requests captured but files not downloading

**Solutions:**

1. **Check browser settings:**

   - Settings → Downloads
   - Ensure downloads are enabled
   - Check "Ask where to save each file" setting

2. **Check popup blocker:**

   - Allow popups for Panopto
   - Some browsers block automatic downloads

3. **Test manual download:**

   ```javascript
   // In console:
   panoptoCatcher.download(0);
   ```

4. **Check download location:**
   - Files go to your default Downloads folder
   - Look for files starting with the video title

### Issue 5: Script Works But Wrong Data

**Symptoms:** Files download but content is wrong/empty

**Solutions:**

1. **Check response format:**

   ```javascript
   // In console:
   panoptoCatcher.view(0);
   ```

2. **Verify JSON structure:**
   - Open downloaded file in text editor
   - Should be valid JSON
   - Should contain video/caption data

## Advanced Debugging

### Enable Verbose Logging

The script already logs extensively. Check console for:

- `[Panopto XHR Catcher]` messages
- Any error messages in red
- Network requests in Network tab

### Check URL Pattern Matching

If requests aren't being caught, the URL might be different:

1. Open Network tab
2. Play video
3. Look for requests to "DeliveryInfo"
4. Right-click → Copy → Copy URL
5. Compare with script's URL pattern:
   ```javascript
   xhr._url.includes("/Panopto/Pages/Viewer/DeliveryInfo.aspx");
   ```

If different, modify the script at line ~680:

```javascript
// Change this line to match your URL:
xhr._url.includes("/YOUR_ACTUAL_PATH/DeliveryInfo.aspx");
```

### Test XHR Interception Manually

```javascript
// In console:
var xhr = new XMLHttpRequest();
xhr.open("POST", "/Panopto/Pages/Viewer/DeliveryInfo.aspx", true);
xhr.onload = function () {
  console.log("Test XHR complete");
};
xhr.send("test=data");
```

You should see: `[Panopto XHR Catcher] POST request detected`

### Check for JavaScript Errors

1. Open Console (F12)
2. Look for red error messages
3. Common errors:
   - `Uncaught ReferenceError`: Variable not defined
   - `Uncaught TypeError`: Wrong type used
   - `SecurityError`: CORS or security issue

## Still Not Working?

### Collect Debug Information

Run this in console and share the output:

```javascript
console.log("URL:", window.location.href);
console.log("UserAgent:", navigator.userAgent);
panoptoCatcher.status();
console.log("Body exists:", !!document.body);
console.log("Tampermonkey version:", GM_info);
```

### Alternative: Simple Version

If the GUI version isn't working, you can use a simpler non-GUI version:

```javascript
// Simple version without GUI
(function () {
  const original = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function (data) {
    this.addEventListener("load", function () {
      if (this.responseURL.includes("DeliveryInfo")) {
        console.log("CAPTURED:", this.responseText);
        const blob = new Blob([this.responseText], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "panopto-" + Date.now() + ".json";
        a.click();
      }
    });
    return original.apply(this, arguments);
  };
})();
```

### Contact & Support

If none of the above work:

1. Note which step failed
2. Copy any error messages from console
3. Check if you're using the latest version (v2.1)
4. Verify Panopto hasn't changed their API structure

## Success Checklist

When everything is working, you should see:

- ✅ Console shows "Panopto XHR Catcher Loaded!"
- ✅ Purple 📥 button in bottom-right corner
- ✅ Button shows when hovering
- ✅ Clicking button opens panel with stats
- ✅ Playing video shows "TARGET REQUEST INTERCEPTED" in console
- ✅ JSON files automatically download to Downloads folder
- ✅ Panel shows captured request count increasing

## Tips

- Keep console open (F12) while testing
- Use `panoptoCatcher.help()` for command list
- Use `panoptoCatcher.status()` to check state
- Files are named: `PageTitle_YYYY-MM-DD...json`
- Auto-download can be toggled in the GUI panel
