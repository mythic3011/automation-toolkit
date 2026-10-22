# 📹 Zoom VTT Transcript Support

## Overview

**Version 2.3** adds support for capturing Zoom transcript VTT files alongside existing Panopto JSON capture functionality.

---

## ✨ What's New

### Dual Platform Support

The script now supports **two platforms**:

1. **📹 Panopto** - JSON delivery info (captions, streams, metadata)
2. **📹 Zoom** - VTT transcript files (WebVTT subtitles)

---

## 🎯 Zoom VTT Format

### What is VTT?

VTT (WebVTT) is a standard subtitle/caption format used by Zoom for transcripts:

```vtt
WEBVTT

00:00:00.000 --> 00:00:05.120
Then OS will create process. I have to tell you
that actually, you are very lucky about now.

00:00:05.120 --> 00:00:08.450
Because the operating system concept is quite stable.
```

### Zoom URL Pattern

The script intercepts requests to:

```
https://polyu.zoom.us/rec/play/vtt?type=transcript&fid=...&action=play
```

**Parameters:**

- `type=transcript` - Specifies transcript type
- `fid=...` - File ID
- `action=play` - Play action

---

## 🚀 How It Works

### 1. **Automatic Detection**

The script automatically detects when you're on:

- Panopto pages (JSON capture)
- Zoom pages (VTT capture)

### 2. **XHR/Fetch Interception**

Both GET (Zoom) and POST (Panopto) requests are intercepted:

```javascript
// Zoom VTT - GET request
GET /rec/play/vtt?type=transcript...

// Panopto JSON - POST request
POST /Panopto/Pages/Viewer/DeliveryInfo.aspx
```

### 3. **Content Type Detection**

The script checks if content is VTT format:

```javascript
function isVTTFormat(data) {
  return data.trim().startsWith("WEBVTT") || data.includes("-->");
}
```

### 4. **Appropriate File Extension**

- **Zoom**: Saves as `.vtt` files
- **Panopto**: Saves as `.json` files

---

## 📋 Features

### All Existing Features Work

✅ **Auto Download** - Works for both JSON and VTT  
✅ **Deduplication** - Prevents duplicate VTT/JSON captures  
✅ **Size Filtering** - Min size reduced to 100 bytes for VTT  
✅ **Manual Download** - Download any captured file later  
✅ **View Data** - Inspect VTT or JSON in console

### VTT-Specific Features

📝 **Plain Text** - VTT saved as-is (no cleaning needed)  
📝 **Proper MIME Type** - `text/vtt` for compatibility  
📝 **Timestamp Preserved** - ISO format in filename

### JSON-Specific Features

🧹 **Data Cleaning** - Remove null/empty fields (JSON only)  
📦 **Pretty Print** - Formatted JSON output

---

## 🎮 Usage

### On Zoom

1. Navigate to a Zoom recording with transcript:

   ```
   https://polyu.zoom.us/rec/play/...
   ```

2. Play the recording

3. The script will intercept the VTT request:

   ```
   [Media Catcher] 🎯 Zoom VTT REQUEST INTERCEPTED!
   [Media Catcher] ✅ Response is meaningful!
   ```

4. VTT file downloads automatically (if auto-download enabled):
   ```
   Zoom-Recording_2025-10-25T12-30-45-123.vtt
   ```

### On Panopto

Works exactly as before:

1. Navigate to Panopto video
2. Play video
3. JSON files captured and downloaded

---

## 📊 GUI Updates

### New Display Format

Captured items now show content type:

```
⏰ 25/10/2025, 6:30:15 pm
✅ 📝 VTT #1
Size: 12.45 KB
[💾 Download] [👁️ View]

⏰ 25/10/2025, 6:28:10 pm
✅ 📋 JSON #2
Size: 28.30 KB
[💾 Download] [👁️ View]
```

**Icons:**

- 📝 = VTT file
- 📋 = JSON file

### Panel Title

Updated to show dual support:

```
🎯 Media Catcher (Panopto + Zoom)
```

---

## 🔧 Technical Details

### Configuration Changes

```javascript
const CONFIG = {
  MIN_SIZE_BYTES: 100, // Reduced from 1000 for VTT
  PANOPTO_URL_PATTERN: "/Panopto/Pages/Viewer/DeliveryInfo.aspx",
  ZOOM_VTT_PATTERN: "/rec/play/vtt", // NEW
};
```

### New Functions

```javascript
// Download VTT as plain text
downloadVTT(data, filename);

// Detect VTT format
isVTTFormat(data);

// Updated to accept extension
createFilename((extension = "json"));

// Updated handler with content type
handleCapturedResponse(responseData, (contentType = "json"));
```

### Request Structure

Captured VTT requests are stored with type:

```javascript
{
  timestamp: Date,
  data: "WEBVTT\n\n00:00:00.000 --> ...",
  hash: "abc123",
  size: 12450,
  contentType: "vtt", // NEW
  downloaded: false
}
```

---

## 🎯 Example Use Case

### Scenario: Capture Zoom Lecture Transcript

1. **Open Zoom Recording**

   ```
   https://polyu.zoom.us/rec/play/vtt?type=transcript&fid=...
   ```

2. **Play Video**

   - Transcript loads automatically

3. **Check Console**

   ```
   [Media Catcher] 🎯 Zoom VTT REQUEST INTERCEPTED!
   [Media Catcher] Content type: vtt
   [Media Catcher] ✅ Response is meaningful!
   [Media Catcher] Size: 12.45 KB
   ```

4. **File Downloaded**

   ```
   Lecture-01-Introduction_2025-10-25T18-30-45-123.vtt
   ```

5. **Use VTT File**
   - Import into video editors
   - Use with media players
   - Convert to other subtitle formats
   - Search/analyze transcript content

---

## 📝 VTT File Format Details

### Header

```vtt
WEBVTT
```

### Cue Format

```vtt
[start time] --> [end time]
[text content]
```

### Example

```vtt
WEBVTT

00:00:00.000 --> 00:00:05.120
Then OS will create process.

00:00:05.120 --> 00:00:08.450
I have to tell you that actually,
you are very lucky about now.

00:00:08.450 --> 00:00:12.300
Because the operating system
concept is quite stable.
```

---

## 🔍 Comparison

| Feature          | Panopto (JSON)                   | Zoom (VTT)                 |
| ---------------- | -------------------------------- | -------------------------- |
| **Request Type** | POST                             | GET                        |
| **Format**       | JSON                             | Plain Text                 |
| **Extension**    | `.json`                          | `.vtt`                     |
| **Cleaning**     | ✅ Yes                           | ❌ No (plain text)         |
| **Content**      | Delivery info, captions, streams | Transcript with timestamps |
| **Size**         | ~20-50KB                         | ~5-20KB                    |
| **Use Case**     | Video metadata                   | Subtitles/transcripts      |

---

## 🎓 Benefits

### For Students

✅ **Offline Access** - Save transcripts for offline study  
✅ **Search & Review** - Search through lecture content  
✅ **Accessibility** - Subtitles for hearing-impaired  
✅ **Note Taking** - Reference exact quotes with timestamps

### For Content Creators

✅ **Subtitle Files** - Use in video editing  
✅ **Translation** - Translate to other languages  
✅ **SEO** - Transcripts for video SEO  
✅ **Archival** - Backup important content

---

## 🚀 Future Enhancements

### Potential Features

1. **SRT Conversion** - Convert VTT to SRT format
2. **Timestamp Search** - Search by time in GUI
3. **Multi-language** - Detect and handle different languages
4. **Merge Cues** - Combine short cues for readability
5. **Export Options** - TXT, SRT, JSON formats

---

## 🐛 Troubleshooting

### VTT Not Capturing?

1. **Check URL Pattern**

   - Look for `/rec/play/vtt` in URL
   - Console should show: `GET Zoom VTT request detected`

2. **Check Response**

   - Open Network tab (F12)
   - Look for requests to `vtt?type=transcript`
   - Check if response contains `WEBVTT`

3. **Enable Console Logging**
   ```javascript
   panoptoCatcher.status();
   ```

### File Not Downloading?

1. **Check Auto-Download**

   - Toggle in GUI panel
   - Or manually download from list

2. **Check Browser Settings**

   - Allow multiple downloads
   - Check download location

3. **Check File Size**
   - Min size: 100 bytes
   - Check if file is too small

---

## 📚 Resources

### VTT Specification

- [W3C WebVTT Standard](https://www.w3.org/TR/webvtt1/)
- [MDN WebVTT Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API)

### Tools for VTT Files

- **Players**: VLC, MPV, most modern browsers
- **Editors**: Subtitle Edit, Aegisub
- **Converters**: FFmpeg, HandBrake

---

## 🎉 Summary

**Version 2.3** brings:

- ✅ **Zoom VTT Support** - Capture transcript files
- ✅ **Dual Platform** - Panopto + Zoom in one script
- ✅ **Smart Detection** - Automatic format recognition
- ✅ **Same Great Features** - All existing features work
- ✅ **Better UI** - Shows file types (VTT/JSON)
- ✅ **Zero Breaking Changes** - Backward compatible

**Type `panoptoCatcher.help()` to see all features!** 🚀
