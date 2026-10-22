# 🎯 Panopto XHR Catcher (GUI Version)

A powerful UserScript that intercepts and captures XHR POST requests to Panopto's DeliveryInfo API with a beautiful, modern GUI interface.

## ✨ Features

### 🎨 Modern GUI

- **Floating Button**: Easy-access toggle button in the bottom-right corner
- **Draggable Panel**: Move the panel anywhere on the screen
- **Beautiful Design**: Purple gradient theme with smooth animations
- **Badge Notifications**: See at a glance how many requests have been captured

### 📊 Real-time Statistics

- **Captured Count**: Total number of intercepted requests
- **Downloaded Count**: Number of requests you've downloaded
- **Request History**: View all captured requests with timestamps

### 🔧 Control Features

- **Auto Download Toggle**: Turn automatic downloading on/off
- **Manual Download**: Download any captured request individually
- **View Data**: Inspect request data in the browser console
- **Clear History**: Remove all captured requests with one click

### 💾 Smart Downloads

- **ISO Format Filenames**: `PageTitle_YYYY-MM-DDTHH-MM-SS-mmm.json`
- **Automatic Naming**: Uses video title + timestamp
- **JSON Formatting**: Pretty-printed JSON for easy reading

## 🚀 Installation

### 1. Install UserScript Manager

Install one of these browser extensions:

- **Tampermonkey** (Chrome, Edge, Firefox, Safari) - [Download](https://www.tampermonkey.net/)
- **Violentmonkey** (Chrome, Edge, Firefox) - [Download](https://violentmonkey.github.io/)
- **Greasemonkey** (Firefox only) - [Download](https://addons.mozilla.org/firefox/addon/greasemonkey/)

### 2. Install the Script

1. Open Tampermonkey/Violentmonkey dashboard
2. Click **"Create a new script"** or **"+"** button
3. Copy the entire contents of `panopto-xhr-catcher.user.js`
4. Paste into the editor
5. Save (Ctrl+S or File → Save)

### 3. Navigate to Panopto

Visit any Panopto video page at:

- `https://polyu.ap.panopto.com/Panopto/Pages/Viewer/*`
- Or any other Panopto subdomain

## 📖 Usage Guide

### Opening the GUI

1. Look for the **📥 floating button** in the bottom-right corner
2. Click it to open/close the control panel
3. A **red badge** shows the number of captured requests

### Using Auto Download

- **Toggle Switch**: Click to enable/disable auto-download
- **When ON** (purple): Requests are downloaded automatically
- **When OFF** (gray): Requests are captured but not downloaded

### Manual Operations

Each captured request shows:

- ⏰ **Timestamp**: When the request was captured
- 📦 **Size**: JSON data size in KB
- ✅ **Status**: Downloaded or pending

**Actions**:

- **💾 Download**: Save the JSON file manually
- **👁️ View**: Log data to browser console for inspection

### Clearing History

- Click **🗑️ Clear All** button at the bottom
- Confirms before clearing to prevent accidents

## 🎮 GUI Controls

### Keyboard Shortcuts

- **ESC**: Close the panel (when focused)
- **F12**: Open browser console to see logged data

### Mouse Actions

- **Click Badge/Button**: Toggle panel visibility
- **Drag Header**: Move panel to new position
- **Click × Button**: Close panel

## 📋 Example Workflow

1. **Open Panopto Video** → Script activates automatically
2. **Click Floating Button** → Panel opens
3. **Enable Auto Download** → Toggle switch to ON (purple)
4. **Play Video** → DeliveryInfo requests are captured automatically
5. **Check Downloads** → JSON files appear in your downloads folder
6. **Review Later** → Disable auto-download and manually select what to save

## 🔍 Captured Data Example

The script captures the complete DeliveryInfo response, including:

- Video delivery URLs
- Caption/subtitle information
- Stream quality options
- Timing information
- All metadata from the API

**Filename format**:

```
Video-Title_2025-10-24T17-29-49-123.json
```

## 🛠️ Troubleshooting

### Script Not Working?

1. **Check if script is enabled** in Tampermonkey
2. **Refresh the page** after installing
3. **Check browser console** (F12) for error messages
4. **Verify URL match** - ensure you're on a Panopto page

### Button Not Appearing?

1. Wait for page to fully load
2. Check if another script is conflicting
3. Try disabling other UserScripts temporarily

### No Requests Being Captured?

1. Open browser console (F12)
2. Look for `[Panopto XHR Catcher]` messages
3. Play the video to trigger API calls
4. Check Network tab for DeliveryInfo.aspx requests

### Downloads Not Working?

1. Check browser's download settings
2. Disable popup blockers for Panopto
3. Allow multiple file downloads if prompted

## 🎨 Customization

### Colors

Edit the CSS in the script to change colors:

- Main gradient: `#667eea` to `#764ba2`
- Accent color: `#667eea`
- Error/clear button: `#e53e3e`

### Position

Change the floating button position by editing:

```css
#panopto-catcher-toggle-btn {
  bottom: 20px; /* Change this */
  right: 20px; /* Change this */
}
```

## 📝 Console Messages

The script logs activity to the console:

```
[Panopto XHR Catcher] Script loaded
[Panopto XHR Catcher] XHR and Fetch interceptors installed
[Panopto XHR Catcher] GUI initialization scheduled
[Panopto XHR Catcher] Intercepted POST to DeliveryInfo.aspx
[Panopto XHR Catcher] Response received: {...}
[Panopto XHR Catcher] Downloaded: filename.json
```

## 🔒 Privacy & Security

- ✅ No data sent to external servers
- ✅ All processing happens locally in your browser
- ✅ Only captures DeliveryInfo.aspx requests
- ✅ Does not modify or interfere with video playback
- ✅ Open source - inspect the code yourself

## 📜 License

Free to use and modify for personal and educational purposes.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Open browser console for error messages
3. Verify the script matches the latest version
4. Try on a different Panopto page

## 🎉 Enjoy!

Happy capturing! 📥✨
