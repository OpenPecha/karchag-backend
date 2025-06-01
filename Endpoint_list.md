# Complete API Endpoints List

## Frontend (Public) Endpoints

### 1. Karchag Page Endpoints

#### Categories
```
GET /api/karchag/categories
- Returns: All active main categories with their sub-categories
- Query params: ?lang=en|tb (language preference)
- Response: Hierarchical category structure
```

#### Sub-categories
```
GET /api/karchag/categories/{category_id}/subcategories
- Returns: All active sub-categories under a specific main category
- Query params: ?lang=en|tb
- Response: List of sub-categories with their basic info
```

#### Texts
```
GET /api/karchag/categories/{category_id}/subcategories/{sub_category_id}/texts
- Returns: All texts under a specific sub-category
- Query params: ?page=1&limit=20&lang=en|tb
- Response: Paginated list of texts with basic info

GET /api/karchag/categories/{category_id}/subcategories/{sub_category_id}/texts/{text_id}
- Returns: Detailed information about a specific text
- Query params: ?lang=en|tb
- Response: Complete text details including summary, volumes, and audio files
```

#### Audio
```
GET /api/karchag/categories/{category_id}/subcategories/{sub_category_id}/texts/{text_id}/audio
- Returns: All audio files for a specific text
- Query params: ?lang=en|tb&quality=128kbps|320kbps
- Response: List of audio files with metadata

GET /api/karchag/audio/{audio_id}
- Returns: Specific audio file details and streaming URL
- Query params: ?lang=en|tb
- Response: Audio metadata and streaming information
```

#### Search & Filter
```
GET /api/karchag/search
- Query params: ?q=search_term&category_id=1&sermon_id=2&yana_id=3&translation_type_id=4&page=1&limit=20&lang=en|tb
- Returns: Filtered and searched texts

GET /api/karchag/filters
- Returns: All available filter options (sermons, yanas, translation_types)
- Query params: ?lang=en|tb
```

### 2. News Page Endpoints

```
GET /api/news
- Returns: Published news articles
- Query params: ?page=1&limit=10&lang=en|tb
- Response: Paginated news list ordered by published_date

GET /api/news/{news_id}
- Returns: Specific news article details
- Query params: ?lang=en|tb
- Response: Complete news article content

GET /api/news/latest
- Returns: Latest 5 published news articles
- Query params: ?lang=en|tb
```

### 3. Audio Page Endpoints

#### Categories & Navigation
```
GET /api/audio/categories
- Returns: All active main categories that have audio content
- Query params: ?lang=en|tb
- Response: Hierarchical category structure with audio counts

GET /api/audio/categories/{category_id}/subcategories
- Returns: Sub-categories under specific category that have audio content
- Query params: ?lang=en|tb
- Response: Sub-categories with audio counts
```

#### Audio by Category/Sub-category
```
GET /api/audio/categories/{category_id}/subcategories/{sub_category_id}/audio
- Returns: All audio files under a specific sub-category
- Query params: ?page=1&limit=20&narrator=&quality=&language=tibetan|english&lang=en|tb
- Response: Audio files with metadata and text information

GET /api/audio/categories/{category_id}/subcategories/{sub_category_id}/audio/{audio_id}
- Returns: Specific audio details and streaming URL
- Query params: ?lang=en|tb
- Response: Audio metadata and streaming information
```

### 4. Video Page Endpoints

```
GET /api/video
- Returns: All available video content
- Query params: ?page=1&limit=20&lang=en|tb
- Response: Video files with metadata

GET /api/video/{video_id}
- Returns: Specific video details and streaming URL
- Query params: ?lang=en|tb
- Response: Video metadata and streaming information

GET /api/video/latest
- Returns: Latest 5 published videos
- Query params: ?lang=en|tb
```

### 5. Edition Page Endpoints

```
GET /api/editions
- Returns: All available Kangyur editions
- Query params: ?page=1&limit=20&lang=en|tb
- Response: Edition information

GET /api/editions/{edition_id}
- Returns: Specific edition details
- Query params: ?lang=en|tb
```

---

## CMS Dashboard (Admin) Endpoints

### 1. Authentication

```
POST /api/auth/login
- Body: {"username": "admin", "password": "password"}
- Returns: JWT token

POST /api/auth/refresh
- Headers: Authorization: Bearer {token}
- Returns: New JWT token

POST /api/auth/logout
- Headers: Authorization: Bearer {token}
- Returns: Success message
```

### 2. User Management

```
GET /api/admin/users
- Returns: List of all users
- Query params: ?page=1&limit=20

POST /api/admin/users
- Body: User creation data
- Returns: Created user

PUT /api/admin/users/{user_id}
- Body: User update data
- Returns: Updated user

DELETE /api/admin/users/{user_id}
- Returns: Success message
```

### 3. Karchag Management

#### Categories Management
```
GET /api/admin/categories
- Returns: All main categories (including inactive)

POST /api/admin/categories
- Body: {"name_english": "...", "name_tibetan": "...", "order_index": 1}
- Returns: Created main category

PUT /api/admin/categories/{category_id}
- Body: Updated category data
- Returns: Updated category

DELETE /api/admin/categories/{category_id}
- Returns: Success message

GET /api/admin/categories/{category_id}/subcategories
- Returns: Sub-categories under specific main category

POST /api/admin/categories/{category_id}/subcategories
- Body: Sub-category data
- Returns: Created sub-category

PUT /api/admin/categories/{category_id}/subcategories/{sub_category_id}
- Body: Updated sub-category data
- Returns: Updated sub-category

DELETE /api/admin/categories/{category_id}/subcategories/{sub_category_id}
- Returns: Success message
```

#### Text Management
```
GET /api/admin/texts
- Query params: ?page=1&limit=20&category_id=1&sub_category_id=1&search=
- Returns: Paginated texts with full details

GET /api/admin/categories/{category_id}/subcategories/{sub_category_id}/texts
- Query params: ?page=1&limit=20&search=
- Returns: Texts within specific sub-category

GET /api/admin/texts/{text_id}
- Returns: Complete text data for editing

POST /api/admin/categories/{category_id}/subcategories/{sub_category_id}/texts
- Body: Complete text data including summary and volumes
- Returns: Created text

PUT /api/admin/texts/{text_id}
- Body: Updated text data
- Returns: Updated text

DELETE /api/admin/texts/{text_id}
- Returns: Success message

POST /api/admin/texts/bulk-import
- Body: CSV/JSON data for bulk text import
- Returns: Import results
```

#### Audio Management
```
GET /api/admin/audio
- Query params: ?page=1&limit=20&text_id=&narrator=&language=&search=
- Returns: All audio files with text information

GET /api/admin/texts/{text_id}/audio
- Returns: Audio files for specific text

GET /api/admin/audio/{audio_id}
- Returns: Specific audio details for editing

POST /api/admin/texts/{text_id}/audio
- Body: FormData with audio file and metadata
- Returns: Created audio record

PUT /api/admin/audio/{audio_id}
- Body: Updated audio metadata (without file)
- Returns: Updated audio

PUT /api/admin/audio/{audio_id}/file
- Body: FormData with new audio file
- Returns: Updated audio with new file

DELETE /api/admin/audio/{audio_id}
- Returns: Success message
```

#### Lookup Tables Management
```
GET /api/admin/sermons
- Returns: All sermons (active and inactive)

POST /api/admin/sermons
- Body: {"name_english": "...", "name_tibetan": "...", "order_index": 1}
- Returns: Created sermon

PUT /api/admin/sermons/{sermon_id}
- Body: Updated sermon data
- Returns: Updated sermon

DELETE /api/admin/sermons/{sermon_id}
- Returns: Success message

# Similar endpoints for Yanas and Translation Types
GET /api/admin/yanas
POST /api/admin/yanas
PUT /api/admin/yanas/{yana_id}
DELETE /api/admin/yanas/{yana_id}

GET /api/admin/translation-types
POST /api/admin/translation-types
PUT /api/admin/translation-types/{translation_type_id}
DELETE /api/admin/translation-types/{translation_type_id}
```

### 4. News Management

```
GET /api/admin/news
- Query params: ?page=1&limit=20&status=all|published|draft&search=
- Returns: All news articles with filters

GET /api/admin/news/{news_id}
- Returns: Specific news article for editing

POST /api/admin/news
- Body: Complete news article data
- Returns: Created news article

PUT /api/admin/news/{news_id}
- Body: Updated news data
- Returns: Updated news

DELETE /api/admin/news/{news_id}
- Returns: Success message

POST /api/admin/news/{news_id}/publish
- Body: {"published_date": "2024-01-01T10:00:00Z"}
- Returns: Published news article

POST /api/admin/news/{news_id}/unpublish
- Returns: Unpublished news article
```

### 5. Audio Management

```
GET /api/admin/audio
- Query params: ?page=1&limit=20&text_id=&narrator=&language=&search=
- Returns: All audio files with text information

GET /api/admin/texts/{text_id}/audio
- Returns: Audio files for specific text

GET /api/admin/audio/{audio_id}
- Returns: Specific audio details for editing

POST /api/admin/texts/{text_id}/audio
- Body: FormData with audio file and metadata
- Returns: Created audio record

PUT /api/admin/audio/{audio_id}
- Body: Updated audio metadata (without file)
- Returns: Updated audio

PUT /api/admin/audio/{audio_id}/file
- Body: FormData with new audio file
- Returns: Updated audio with new file

DELETE /api/admin/audio/{audio_id}
- Returns: Success message
```

### 6. Video Management

```
GET /api/admin/video
- Query params: ?page=1&limit=20&search=
- Returns: All video files

GET /api/admin/video/{video_id}
- Returns: Specific video details for editing

POST /api/admin/video
- Body: Complete video data with metadata
- Returns: Created video record

PUT /api/admin/video/{video_id}
- Body: Updated video metadata
- Returns: Updated video

DELETE /api/admin/video/{video_id}
- Returns: Success message

POST /api/admin/video/{video_id}/publish
- Body: {"published_date": "2024-01-01T10:00:00Z"}
- Returns: Published video

POST /api/admin/video/{video_id}/unpublish
- Returns: Unpublished video
```

### 7. Edition Management

```
GET /api/admin/editions
- Query params: ?page=1&limit=20&search=
- Returns: All editions

POST /api/admin/editions
- Body: Edition data
- Returns: Created edition

PUT /api/admin/editions/{edition_id}
- Body: Updated edition data
- Returns: Updated edition

DELETE /api/admin/editions/{edition_id}
- Returns: Success message
```

### 8. Dashboard & Analytics

```
GET /api/admin/dashboard/stats
- Returns: Overall statistics (total texts, categories, news, etc.)

GET /api/admin/dashboard/recent-activity
- Returns: Recent changes/activities

GET /api/admin/audit-logs
- Query params: ?page=1&limit=50&table_name=&action=&date_from=&date_to=
- Returns: Audit trail of all changes
```

---

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {...}
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Authentication Headers

All CMS endpoints require:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

File upload endpoints use:
```
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data
```
