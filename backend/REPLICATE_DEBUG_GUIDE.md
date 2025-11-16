# Replicate Output Debugging Guide

## Overview

This guide explains how to view and access Replicate-generated videos even when the backend crashes or fails, allowing you to debug and inspect the AI-generated content.

## Automatic URL Logging

Every Replicate API call now automatically logs URLs in **two places**:

### 1. Console Logs

All Replicate URLs are logged to the console with these prefixes:
- **Image-to-video**: `Replicate video URL: https://...`
- **Lip-sync**: `Replicate lipsync URL: https://...`

**Example log output:**
```
2025-11-15 18:45:23 - INFO - Replicate video URL: https://replicate.delivery/pbxt/abc123/segment_000.mp4
2025-11-15 18:45:45 - INFO - Replicate lipsync URL: https://replicate.delivery/pbxt/def456/lipsynced_000.mp4
```

### 2. Metadata Files

For each generated video, a `.txt` file is saved alongside it containing the Replicate URL:

**Location structure:**
```
output/{job_id}/
  celebrity_videos/
    segment_000.mp4
    segment_000_replicate_url.txt  ← URL file
    segment_001.mp4
    segment_001_replicate_url.txt  ← URL file
    ...
  lipsynced_videos/
    lipsynced_000.mp4
    lipsynced_000_replicate_url.txt  ← URL file
    lipsynced_001.mp4
    lipsynced_001_replicate_url.txt  ← URL file
    ...
```

**Metadata file content example:**
```
Replicate URL: https://replicate.delivery/pbxt/abc123def456/output.mp4
Generated: segment_000.mp4
```

## How to View Outputs After Backend Crash

### Method 1: Check Log Files

1. **Find the logs:**
   ```bash
   tail -f backend.log
   # or
   grep "Replicate.*URL" backend.log
   ```

2. **Copy the URLs** from log output

3. **Open in browser** - URLs are valid for 24 hours

### Method 2: Check Metadata Files

1. **Navigate to output directory:**
   ```bash
   cd output/{job_id}/celebrity_videos/
   ```

2. **View URL files:**
   ```bash
   cat segment_000_replicate_url.txt
   ```

3. **Copy and open the URL** in your browser

### Method 3: Use Replicate Dashboard

1. Go to https://replicate.com/predictions
2. View all your recent predictions
3. Click on any prediction to see:
   - Input parameters
   - Output video URL
   - Generation logs
   - Cost breakdown

## URL Availability

- **Replicate URLs are valid for 24 hours** after generation
- After 24 hours, videos are deleted from Replicate's CDN
- Download important videos within 24 hours if needed

## Debugging Workflow

### If Backend Crashes During Generation:

1. **Check which segments completed:**
   ```bash
   ls -la output/{job_id}/celebrity_videos/
   ls -la output/{job_id}/lipsynced_videos/
   ```

2. **Find the last successful segment:**
   ```bash
   ls -t output/{job_id}/celebrity_videos/*.txt | head -1
   ```

3. **View the URL:**
   ```bash
   cat output/{job_id}/celebrity_videos/segment_XXX_replicate_url.txt
   ```

4. **Download successful segments:**
   ```bash
   # Open URLs in browser and save, or use curl
   curl -o debug_segment.mp4 "https://replicate.delivery/pbxt/..."
   ```

### If You Want to Retry from a Specific Segment:

The metadata files let you:
1. Identify which segments succeeded
2. Download those segments manually
3. Skip re-generating those specific segments
4. Continue from where it failed

## Troubleshooting

### Problem: Can't find log files
**Solution:**
```bash
# Check if logging to file is enabled
grep "LOG_FILE" .env

# View recent logs
tail -100 backend.log

# Search all logs
grep -r "Replicate.*URL" .
```

### Problem: Metadata files not created
**Solution:**
- Check if the video generation reached the download phase
- Metadata files are only created after successful Replicate response
- If Replicate API fails before returning a URL, no metadata file exists

### Problem: URLs expired (404 error)
**Solution:**
- Replicate URLs expire after 24 hours
- Re-run the generation if needed
- Consider downloading important outputs immediately

### Problem: Need to see all URLs for a job
**Solution:**
```bash
# Find all metadata files for a job
find output/{job_id} -name "*_replicate_url.txt"

# View all URLs
find output/{job_id} -name "*_replicate_url.txt" -exec cat {} \;
```

## Development Tips

### Quick URL Extraction Script

Create `extract_urls.sh`:
```bash
#!/bin/bash
JOB_ID=$1
echo "Replicate URLs for job: $JOB_ID"
echo "================================"
echo ""
echo "Celebrity Videos:"
find output/$JOB_ID/celebrity_videos -name "*_replicate_url.txt" 2>/dev/null | sort | while read file; do
    cat "$file"
    echo ""
done
echo ""
echo "Lip-synced Videos:"
find output/$JOB_ID/lipsynced_videos -name "*_replicate_url.txt" 2>/dev/null | sort | while read file; do
    cat "$file"
    echo ""
done
```

Usage:
```bash
chmod +x extract_urls.sh
./extract_urls.sh abc-123-def-456
```

### Watch Replicate API Calls in Real-Time

```bash
# Terminal 1: Watch logs
tail -f backend.log | grep "Replicate"

# Terminal 2: Run backend
python main.py
```

## Cost Tracking

Each metadata file represents one Replicate API call:
- Count celebrity video files: ~$0.10-0.30 each
- Count lipsync files: ~$0.05-0.15 each

```bash
# Count total Replicate calls for a job
echo "Celebrity videos: $(find output/{job_id}/celebrity_videos -name "*_replicate_url.txt" | wc -l)"
echo "Lip-synced videos: $(find output/{job_id}/lipsynced_videos -name "*_replicate_url.txt" | wc -l)"
```

## Example Debug Session

```bash
# 1. Backend crashed, check what was generated
$ ls output/abc-123/celebrity_videos/
segment_000.mp4
segment_000_replicate_url.txt
segment_001.mp4
segment_001_replicate_url.txt

# 2. View the URLs
$ cat output/abc-123/celebrity_videos/segment_000_replicate_url.txt
Replicate URL: https://replicate.delivery/pbxt/xyz789/segment.mp4
Generated: segment_000.mp4

# 3. Open URL in browser to verify quality
# (Open the URL)

# 4. Check if lipsync started
$ ls output/abc-123/lipsynced_videos/
# Empty - crashed before lipsync

# Conclusion: Made it through 2 segments of celebrity video generation,
# then crashed before lip-sync. Can resume from segment 2.
```

## Summary

✅ Every Replicate call is logged in console
✅ Every generated video has a metadata file with URL
✅ URLs are valid for 24 hours
✅ Easy to find and debug partial generations
✅ Can download outputs directly from Replicate even if backend crashes

This system ensures you never lose access to expensive AI-generated content, even during development and debugging!
