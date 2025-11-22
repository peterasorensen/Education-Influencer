# Custom Photo and Audio Upload Feature

This feature allows users to upload their own photos and audio clips instead of using preset celebrities (Drake, Sydney Sweeney) for educational video generation.

## Overview

Users can now:
- Upload custom photos (JPEG, PNG, WebP) to use as the celebrity face
- Upload custom audio clips (MP3, WAV, WebM) for voice cloning
- Use these custom media files in video generation instead of presets

## API Endpoints

### 1. Upload Photo

**POST** `/api/upload/photo`

Upload a custom photo for use as celebrity image.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `photo`: File (JPEG, PNG, WebP)
  - `user_id`: string (default: "default")

**Response:**
```json
{
  "photo_id": "uuid",
  "photo_url": "/api/media/photos/{user_id}/{photo_id}.jpg",
  "thumbnail_url": "/api/media/photos/{user_id}/{photo_id}_thumb.jpg",
  "filename": "sanitized_filename.jpg",
  "size": 1024000,
  "dimensions": [1024, 1024],
  "created_at": "2025-11-21T10:30:00"
}
```

**Validation Rules:**
- Max size: 10 MB
- Min dimensions: 512x512
- Max dimensions: 4096x4096
- Allowed formats: JPEG, PNG, WebP
- Security: File signature verification, EXIF stripping

---

### 2. Upload Audio

**POST** `/api/upload/audio`

Upload a custom audio clip for voice cloning.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `audio`: File (MP3, WAV, WebM)
  - `user_id`: string (default: "default")

**Response:**
```json
{
  "audio_id": "uuid",
  "audio_url": "/api/media/audio/{user_id}/{audio_id}.mp3",
  "filename": "sanitized_filename.mp3",
  "size": 102400,
  "duration": 4.5,
  "sample_rate": 24000,
  "created_at": "2025-11-21T10:30:00"
}
```

**Validation Rules:**
- Max size: 2 MB
- Duration: 2-5 seconds
- Allowed formats: MP3, WAV, WebM
- Processing: Converted to mono MP3 at 24kHz
- Security: File signature verification

---

### 3. Get User Media

**GET** `/api/media/user/{user_id}`

Get all uploaded media for a user.

**Response:**
```json
{
  "photos": [
    {
      "photo_id": "uuid",
      "photo_url": "/api/media/photos/...",
      "thumbnail_url": "/api/media/photos/...",
      "filename": "photo.jpg",
      "size": 1024000,
      "dimensions": [1024, 1024],
      "created_at": "2025-11-21T10:30:00"
    }
  ],
  "audio": [
    {
      "audio_id": "uuid",
      "audio_url": "/api/media/audio/...",
      "filename": "audio.mp3",
      "size": 102400,
      "duration": 4.5,
      "sample_rate": 24000,
      "created_at": "2025-11-21T10:30:00"
    }
  ]
}
```

---

### 4. Get Photo File

**GET** `/api/media/photos/{user_id}/{filename}`

Download a photo file.

**Response:** JPEG image file

---

### 5. Get Audio File

**GET** `/api/media/audio/{user_id}/{filename}`

Download an audio file.

**Response:** MP3 audio file

---

### 6. Delete Photo

**DELETE** `/api/media/photos/{user_id}/{photo_id}`

Delete a photo and its thumbnail.

**Response:**
```json
{
  "message": "Photo {photo_id} deleted successfully"
}
```

---

### 7. Delete Audio

**DELETE** `/api/media/audio/{user_id}/{audio_id}`

Delete an audio file.

**Response:**
```json
{
  "message": "Audio {audio_id} deleted successfully"
}
```

---

## Video Generation with Custom Media

The `/api/generate` endpoint has been extended with new fields:

```json
{
  "topic": "Quantum Physics",
  "duration_seconds": 60,
  "quality": "medium_quality",
  "enable_subtitles": true,
  "celebrity": "drake",
  "renderer": "manim",

  // NEW FIELDS for custom celebrity
  "celebrity_mode": "custom",  // "preset" or "custom"
  "custom_photo_id": "uuid-of-uploaded-photo",
  "custom_audio_id": "uuid-of-uploaded-audio",
  "user_id": "default"
}
```

**Celebrity Modes:**

1. **Preset Mode** (default):
   ```json
   {
     "celebrity_mode": "preset",
     "celebrity": "drake"  // or "sydney_sweeney"
   }
   ```

2. **Custom Mode**:
   ```json
   {
     "celebrity_mode": "custom",
     "custom_photo_id": "uuid-from-upload-photo-response",
     "custom_audio_id": "uuid-from-upload-audio-response",
     "user_id": "default"
   }
   ```

---

## File Structure

```
backend/
├── models/
│   ├── __init__.py
│   └── media_models.py          # Pydantic models for media
├── pipeline/
│   ├── media_validator.py       # File validation and security
│   ├── media_processor.py       # Image/audio processing
│   └── media_storage.py         # Storage management
├── uploads/                     # User uploads directory
│   ├── photos/
│   │   └── {user_id}/
│   │       ├── {photo_id}.jpg
│   │       └── {photo_id}_thumb.jpg
│   ├── audio/
│   │   └── {user_id}/
│   │       └── {audio_id}.mp3
│   └── metadata/
│       └── {user_id}.json
└── main.py                      # Updated with new endpoints
```

---

## Security Features

### Photo Upload Security:
1. **File Signature Verification**: Checks magic bytes to prevent file spoofing
2. **EXIF Stripping**: Removes metadata for privacy
3. **Dimension Validation**: Ensures reasonable image sizes
4. **Format Conversion**: All images converted to JPEG
5. **Filename Sanitization**: Removes special characters and path components

### Audio Upload Security:
1. **File Signature Verification**: Validates audio format via magic bytes
2. **Duration Validation**: Enforces 2-5 second limit
3. **Format Conversion**: Converts to standard mono MP3 at 24kHz
4. **Size Limits**: Maximum 2MB to prevent abuse
5. **Filename Sanitization**: Removes special characters

---

## Processing Pipeline

### Photo Processing:
1. Validate file type and size
2. Check image dimensions
3. Strip EXIF metadata
4. Convert to JPEG format
5. Create 256x256 thumbnail
6. Save to user directory
7. Generate metadata

### Audio Processing:
1. Validate file type and size
2. Check audio duration
3. Convert to mono MP3 at 24kHz
4. Trim to max 5 seconds
5. Save to user directory
6. Generate metadata

---

## Example Usage

### 1. Upload Custom Photo
```bash
curl -X POST http://localhost:8000/api/upload/photo \
  -F "photo=@my_photo.jpg" \
  -F "user_id=user123"
```

### 2. Upload Custom Audio
```bash
curl -X POST http://localhost:8000/api/upload/audio \
  -F "audio=@my_voice.mp3" \
  -F "user_id=user123"
```

### 3. Generate Video with Custom Celebrity
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Quantum Physics",
    "duration_seconds": 60,
    "celebrity_mode": "custom",
    "custom_photo_id": "9dacb15e-bc64-4f9c-ad8f-6ca1c3bc58e2",
    "custom_audio_id": "4605cf1c-1a9d-4894-ad35-3ab2dd6bf76d",
    "user_id": "user123"
  }'
```

---

## Dependencies

Added to `requirements.txt`:
```
Pillow>=10.0.0        # Image processing
mutagen>=1.47.0       # Audio metadata extraction
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Testing

Run the test suite:
```bash
python test_media_upload.py
```

This tests:
- Photo upload, processing, storage, and deletion
- Audio upload, processing, storage, and deletion
- Validation error handling
- File security checks

---

## Storage Limits

**Recommended Limits (implement in production):**
- Per-user photo limit: 10 photos
- Per-user audio limit: 10 clips
- Storage cleanup: Delete uploads after 30 days of inactivity
- Rate limiting: 10 uploads per hour per user

**Current Implementation:**
- No hard limits (add rate limiting for production)
- Files persist until manually deleted
- Organized by user_id for easy cleanup

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Validation error (file too large, wrong format, etc.)
- `404 Not Found`: Media not found
- `500 Internal Server Error`: Processing error

Error responses include detailed messages:
```json
{
  "detail": "Photo size exceeds maximum allowed size of 10.0MB"
}
```

---

## Future Enhancements

1. **Voice Cloning Integration**: Use custom audio for actual voice synthesis
2. **Face Detection**: Automatically crop/center faces in photos
3. **Image Upscaling**: Enhance low-resolution photos
4. **Audio Quality Enhancement**: Denoise and normalize audio
5. **Batch Upload**: Upload multiple files at once
6. **Preview Generation**: Show preview before video generation
7. **Storage Management**: Automatic cleanup of old files
8. **User Quotas**: Enforce per-user storage limits

---

## Notes

- Custom audio is currently stored but not used for voice cloning (requires integration with voice synthesis models)
- All images are converted to JPEG to maintain consistency
- Audio is normalized to mono 24kHz MP3 for compatibility
- Metadata is stored in JSON files for easy querying
- UUIDs are used for file IDs to prevent collisions
