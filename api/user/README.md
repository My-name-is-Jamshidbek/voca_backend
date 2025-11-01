# User APIs - Comprehensive Documentation

Professional User APIs for Flutter app with Bearer token authentication, comprehensive documentation, examples, and default values.

## 📁 Directory Structure

```
api/user/
├── __init__.py                 # Module exports
├── urls.py                     # URL routing
├── README.md                   # This documentation
├── common/                     # Shared utilities
│   ├── __init__.py
│   └── base.py                # Base classes, permissions, helpers
├── profile/                    # User Profile Management
│   ├── __init__.py
│   ├── views.py               # Profile ViewSet with comprehensive endpoints
│   └── serializers.py         # Profile serializers with examples
├── learning/                   # Vocabulary Learning & Progress
│   ├── __init__.py
│   ├── views.py               # Learning ViewSets
│   └── serializers.py         # Learning serializers
└── analytics/                  # Learning Analytics & Reports
    ├── __init__.py
    ├── views.py               # Analytics ViewSet
    └── serializers.py         # Analytics serializers
```

## 🔐 Authentication

All User API endpoints require **Bearer Token Authentication** using JWT tokens obtained from the authentication endpoint.

### Getting JWT Token

**Request:**
```bash
POST /api/base/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        },
        "user": {
            "id": "user-123",
            "email": "user@example.com"
        }
    }
}
```

### Using Bearer Token

Include the JWT access token in all requests:

```bash
GET /api/user/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Token Expiry:**
- Access Token: 15 minutes
- Refresh Token: 7 days

### Refreshing Token

When access token expires:

```bash
POST /api/base/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 📋 API Endpoints Overview

### Profile Management
- `GET /api/user/profile/` - Get current user profile
- `PUT /api/user/profile/update/` - Update profile
- `POST /api/user/profile/change_password/` - Change password
- `DELETE /api/user/profile/` - Delete account
- `GET /api/user/profile/statistics/` - Get learning statistics
- `POST /api/user/profile/avatar/` - Upload avatar
- `GET /api/user/profile/devices/` - List devices
- `POST /api/user/profile/devices/` - Register device
- `DELETE /api/user/profile/devices/{id}/` - Remove device
- `POST /api/user/profile/logout_all/` - Logout all devices

### Learning
- `GET /api/user/learning/words/` - List words (paginated)
- `GET /api/user/learning/words/{id}/` - Get word details
- `GET /api/user/learning/words/by_difficulty/` - Filter by difficulty
- `GET /api/user/learning/words/due_for_review/` - Words for review
- `GET /api/user/learning/words/random/` - Random words
- `POST /api/user/learning/words/{id}/mark_progress/` - Mark progress
- `GET /api/user/learning/collections/` - List collections
- `POST /api/user/learning/collections/` - Create collection
- `GET /api/user/learning/collections/{id}/` - Get collection
- `PUT /api/user/learning/collections/{id}/` - Update collection
- `DELETE /api/user/learning/collections/{id}/` - Delete collection
- `POST /api/user/learning/collections/{id}/add_word/` - Add word
- `DELETE /api/user/learning/collections/{id}/remove_word/` - Remove word

### Analytics
- `GET /api/user/analytics/overview/` - Learning overview
- `GET /api/user/analytics/progress/` - Progress details
- `GET /api/user/analytics/daily/` - Daily statistics
- `GET /api/user/analytics/weekly/` - Weekly statistics
- `GET /api/user/analytics/monthly/` - Monthly statistics
- `GET /api/user/analytics/difficulty/` - By difficulty level
- `GET /api/user/analytics/sessions/` - Sessions history
- `GET /api/user/analytics/performance/` - Performance metrics

---

## 🎯 Profile Management APIs

### 1. Get Current User Profile

**Endpoint:** `GET /api/user/profile/`

**Authentication:** Bearer Token (Required)

**Response:**
```json
{
    "success": true,
    "message": "Profile retrieved successfully",
    "data": {
        "id": "user-123",
        "email": "user@example.com",
        "is_staff": false,
        "is_active": true,
        "role": "user",
        "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "bio": "Language enthusiast",
            "avatar_url": "https://example.com/avatars/user-123.jpg",
            "birth_date": "1990-01-15",
            "preferred_language": "English",
            "secondary_languages": "German,Spanish",
            "timezone": "America/New_York",
            "theme": "dark",
            "notifications_enabled": true,
            "email_verified": true,
            "phone_verified": false,
            "created_at": "2024-10-01T12:00:00Z",
            "updated_at": "2024-11-01T15:30:00Z"
        },
        "devices": [
            {
                "id": "device-123",
                "device_id": "hardware-id-xyz",
                "device_name": "iPhone 14 Pro",
                "platform": "ios",
                "os_version": "17.0",
                "app_version": "1.0.0",
                "is_active": true,
                "last_sync": "2024-11-01T10:30:00Z",
                "created_at": "2024-10-15T14:20:00Z"
            }
        ]
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 2. Update User Profile

**Endpoint:** `PUT /api/user/profile/update/`

**Authentication:** Bearer Token (Required)

**Request Body:**
```json
{
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+9876543210",
    "bio": "German language learner",
    "birth_date": "1992-05-20",
    "preferred_language": "German",
    "secondary_languages": "French,Spanish",
    "timezone": "Europe/Berlin",
    "theme": "dark",
    "notifications_enabled": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+9876543210",
        "bio": "German language learner",
        "birth_date": "1992-05-20",
        "preferred_language": "German",
        "secondary_languages": "French,Spanish",
        "timezone": "Europe/Berlin",
        "theme": "dark",
        "notifications_enabled": true
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 3. Change Password

**Endpoint:** `POST /api/user/profile/change_password/`

**Authentication:** Bearer Token (Required)

**Request Body:**
```json
{
    "old_password": "CurrentPassword123!",
    "new_password": "NewPassword456@",
    "confirm_password": "NewPassword456@"
}
```

**Validation Rules:**
- Old password must be correct
- New password minimum 8 characters
- New password must be different from old password
- Passwords must match

**Response:**
```json
{
    "success": true,
    "message": "Password changed successfully",
    "data": null,
    "timestamp": "2024-11-01T16:00:00Z"
}
```

**Error Response:**
```json
{
    "success": false,
    "error": true,
    "message": "Password change failed",
    "details": {
        "old_password": "Old password is incorrect"
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 4. Get Learning Statistics

**Endpoint:** `GET /api/user/profile/statistics/`

**Authentication:** Bearer Token (Required)

**Response:**
```json
{
    "success": true,
    "message": "Statistics retrieved successfully",
    "data": {
        "total_words_available": 5000,
        "words_learned": 250,
        "words_in_progress": 150,
        "words_not_started": 4600,
        "review_due": 15,
        "learning_percentage": 5.0,
        "current_streak": 7,
        "last_session_date": "2024-11-01T10:30:00Z",
        "max_streak": 15,
        "total_sessions": 42,
        "total_study_time": 1260
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

**Field Definitions:**
- `total_words_available`: Total vocabulary in the system
- `words_learned`: Words with mastery level ≥ 3 (fully learned)
- `words_in_progress`: Words with mastery level 1-2
- `words_not_started`: Words never reviewed
- `review_due`: Words due for review today
- `learning_percentage`: % of total words learned (0-100)
- `current_streak`: Consecutive days of learning
- `total_sessions`: Total learning sessions completed
- `total_study_time`: Total minutes spent learning

---

### 5. Upload Avatar

**Endpoint:** `POST /api/user/profile/avatar/`

**Authentication:** Bearer Token (Required)

**Request Body:** multipart/form-data
```
avatar: [image file] (JPG, PNG, max 5MB)
```

**Response:**
```json
{
    "success": true,
    "message": "Avatar uploaded successfully",
    "data": {
        "avatar_url": "https://example.com/media/avatars/user-123.jpg"
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 6. List User Devices

**Endpoint:** `GET /api/user/profile/devices/`

**Authentication:** Bearer Token (Required)

**Response:**
```json
{
    "success": true,
    "message": "Devices retrieved successfully",
    "data": [
        {
            "id": "device-123",
            "device_name": "iPhone 14 Pro",
            "platform": "ios",
            "os_version": "17.0",
            "app_version": "1.0.0",
            "is_active": true,
            "last_sync": "2024-11-01T10:30:00Z"
        },
        {
            "id": "device-456",
            "device_name": "Samsung Galaxy S23",
            "platform": "android",
            "os_version": "14",
            "app_version": "1.0.0",
            "is_active": true,
            "last_sync": "2024-10-31T15:20:00Z"
        }
    ],
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 7. Register New Device

**Endpoint:** `POST /api/user/profile/devices/`

**Authentication:** Bearer Token (Required)

**Request Body:**
```json
{
    "device_id": "hardware-id-xyz",
    "device_name": "iPhone 14 Pro",
    "platform": "ios",
    "os_version": "17.0",
    "app_version": "1.0.0"
}
```

**Platform Options:** ios, android, web, desktop

**Response:**
```json
{
    "success": true,
    "message": "Device registered successfully",
    "data": {
        "id": "device-123",
        "device_id": "hardware-id-xyz",
        "device_name": "iPhone 14 Pro",
        "platform": "ios",
        "os_version": "17.0",
        "app_version": "1.0.0",
        "is_active": true,
        "created_at": "2024-11-01T16:00:00Z"
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 8. Remove Device

**Endpoint:** `DELETE /api/user/profile/devices/{device_id}/`

**Authentication:** Bearer Token (Required)

**Path Parameters:**
- `device_id`: Device ID to remove (from device registration)

**Response:**
```json
{
    "success": true,
    "message": "Device removed successfully",
    "data": null,
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 9. Logout All Devices

**Endpoint:** `POST /api/user/profile/logout_all/`

**Authentication:** Bearer Token (Required)

**Description:** Deactivates all user devices and invalidates all sessions

**Response:**
```json
{
    "success": true,
    "message": "Logged out from all devices successfully",
    "data": null,
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

## 📚 Learning APIs

### 1. List Words

**Endpoint:** `GET /api/user/learning/words/`

**Authentication:** Bearer Token (Required)

**Query Parameters:**
```
page=1                    (default: 1)
page_size=20              (default: 20, max: 100)
difficulty=A1             (optional: A1, A2, B1, B2, C1, C2)
search=hello              (optional: search word)
collection_id=col-123     (optional: filter by collection)
```

**Response:**
```json
{
    "success": true,
    "message": "Words retrieved successfully",
    "data": {
        "data": [
            {
                "id": "word-1",
                "word": "Hello",
                "phonetic": "həˈloʊ",
                "difficulty_level_name": "A1",
                "frequency_rank": 100,
                "image_url": "https://example.com/images/hello.jpg"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_count": 5000,
            "total_pages": 250,
            "has_next": true,
            "has_previous": false
        }
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 2. Get Word Details

**Endpoint:** `GET /api/user/learning/words/{id}/`

**Authentication:** Bearer Token (Required)

**Path Parameters:**
- `id`: Word ID

**Response:**
```json
{
    "success": true,
    "message": "Word retrieved successfully",
    "data": {
        "id": "word-1",
        "word": "Hello",
        "phonetic": "həˈloʊ",
        "pronunciation_url": "https://example.com/audio/hello.mp3",
        "difficulty_level": {
            "id": "level-1",
            "level_name": "A1",
            "description": "Beginner",
            "cefr_level": "A1",
            "order": 1
        },
        "translations": [
            {
                "id": "trans-1",
                "language": "German",
                "translation": "Hallo"
            },
            {
                "id": "trans-2",
                "language": "Spanish",
                "translation": "Hola"
            }
        ],
        "definitions": [
            {
                "id": "def-1",
                "definition": "A greeting expression used when meeting someone",
                "example_sentence": "Hello, how are you doing today?",
                "part_of_speech": "interjection"
            }
        ],
        "image_url": "https://example.com/images/hello.jpg",
        "tags": "greeting,common,social",
        "frequency_rank": 100
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 3. Filter Words by Difficulty

**Endpoint:** `GET /api/user/learning/words/by_difficulty/`

**Authentication:** Bearer Token (Required)

**Query Parameters:**
```
level=A1              (required: A1, A2, B1, B2, C1, C2)
page=1                (default: 1)
page_size=20          (default: 20, max: 100)
```

**Response:** Same as List Words, but filtered by difficulty

---

### 4. Get Words Due for Review

**Endpoint:** `GET /api/user/learning/words/due_for_review/`

**Authentication:** Bearer Token (Required)

**Query Parameters:**
```
page=1           (default: 1)
page_size=20     (default: 20, max: 100)
```

**Response:**
```json
{
    "success": true,
    "message": "Words due for review retrieved successfully",
    "data": {
        "data": [
            {
                "id": "prog-1",
                "word": {
                    "id": "word-1",
                    "word": "Hello",
                    "difficulty_level": "A1"
                },
                "mastery_level": 2,
                "times_reviewed": 5,
                "correct_answers": 4,
                "incorrect_answers": 1,
                "last_reviewed": "2024-10-28T10:30:00Z",
                "next_review_date": "2024-11-02T10:30:00Z",
                "first_learned_date": "2024-10-20T14:15:00Z",
                "accuracy_percentage": 80.0
            }
        ],
        "pagination": {...}
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 5. Get Random Words

**Endpoint:** `GET /api/user/learning/words/random/`

**Authentication:** Bearer Token (Required)

**Query Parameters:**
```
count=5                 (default: 5, max: 20)
difficulty=A1           (optional: filter by difficulty)
```

**Response:**
```json
{
    "success": true,
    "message": "Random words retrieved successfully",
    "data": [
        {
            "id": "word-1",
            "word": "Hello",
            "phonetic": "həˈloʊ",
            "difficulty_level_name": "A1",
            "frequency_rank": 100,
            "image_url": "https://example.com/images/hello.jpg"
        }
    ],
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 6. Mark Word Progress

**Endpoint:** `POST /api/user/learning/words/{id}/mark_progress/`

**Authentication:** Bearer Token (Required)

**Path Parameters:**
- `id`: Word ID

**Request Body:**
```json
{
    "is_correct": true,
    "review_notes": "Easy to remember"
}
```

**Mastery Level Progression:**
- 0: Not started
- 1: Beginning (1-3 correct reviews)
- 2: Developing (4-7 correct reviews)
- 3: Competent (8-14 correct reviews) - Considered "learned"
- 4: Proficient (15-30 correct reviews)
- 5: Mastered (30+ correct reviews)

**Next Review Schedule:**
- Level 0 → 1 day
- Level 1 → 3 days
- Level 2 → 7 days
- Level 3 → 14 days
- Level 4 → 30 days
- Level 5 → 60 days

**Response:**
```json
{
    "success": true,
    "message": "Progress updated successfully",
    "data": {
        "mastery_level": 2,
        "next_review_date": "2024-11-02T10:30:00Z",
        "accuracy_percentage": 80.0
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 7. List Collections

**Endpoint:** `GET /api/user/learning/collections/`

**Authentication:** Bearer Token (Required)

**Response:**
```json
{
    "success": true,
    "message": "Collections retrieved successfully",
    "data": [
        {
            "id": "col-1",
            "name": "Daily Vocabulary",
            "description": "Words I learn daily",
            "words_count": 25,
            "created_at": "2024-10-20T14:15:00Z",
            "updated_at": "2024-11-01T15:30:00Z"
        }
    ],
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 8. Create Collection

**Endpoint:** `POST /api/user/learning/collections/`

**Authentication:** Bearer Token (Required)

**Request Body:**
```json
{
    "name": "Daily Vocabulary",
    "description": "Words I learn daily"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Collection created successfully",
    "data": {
        "id": "col-1",
        "name": "Daily Vocabulary",
        "description": "Words I learn daily",
        "words_count": 0,
        "created_at": "2024-11-01T16:00:00Z",
        "updated_at": "2024-11-01T16:00:00Z"
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 9. Add Word to Collection

**Endpoint:** `POST /api/user/learning/collections/{id}/add_word/`

**Authentication:** Bearer Token (Required)

**Path Parameters:**
- `id`: Collection ID

**Request Body:**
```json
{
    "word_id": "word-123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Word added to collection successfully",
    "data": null,
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 10. Remove Word from Collection

**Endpoint:** `DELETE /api/user/learning/collections/{id}/remove_word/`

**Authentication:** Bearer Token (Required)

**Path Parameters:**
- `id`: Collection ID

**Query Parameters:**
```
word_id=word-123  (required: Word ID to remove)
```

**Response:**
```json
{
    "success": true,
    "message": "Word removed from collection successfully",
    "data": null,
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

## 📊 Analytics APIs

### 1. Learning Overview

**Endpoint:** `GET /api/user/analytics/overview/`

**Authentication:** Bearer Token (Required)

**Response:**
```json
{
    "success": true,
    "message": "Overview retrieved successfully",
    "data": {
        "stats": {
            "total_words_available": 5000,
            "words_learned": 250,
            "words_in_progress": 150,
            "words_not_started": 4600,
            "learning_percentage": 5.0
        },
        "streak": {
            "current_streak": 7,
            "longest_streak": 15
        },
        "today_session": {
            "duration_minutes": 45,
            "words_reviewed": 15,
            "accuracy_percentage": 87.5
        }
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 2. Daily Statistics

**Endpoint:** `GET /api/user/analytics/daily/`

**Authentication:** Bearer Token (Required)

**Query Parameters:**
```
days=7   (default: 7, max: 90)
```

**Response:**
```json
{
    "success": true,
    "message": "Daily statistics retrieved successfully",
    "data": [
        {
            "date": "2024-11-01",
            "duration_minutes": 45,
            "words_reviewed": 15,
            "accuracy_percentage": 87.5,
            "words_added": 3
        },
        {
            "date": "2024-10-31",
            "duration_minutes": 30,
            "words_reviewed": 10,
            "accuracy_percentage": 85.0,
            "words_added": 2
        }
    ],
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 3. Weekly Statistics

**Endpoint:** `GET /api/user/analytics/weekly/`

**Authentication:** Bearer Token (Required)

**Query Parameters:**
```
weeks=4   (default: 4, max: 12)
```

**Response:**
```json
{
    "success": true,
    "message": "Weekly statistics retrieved successfully",
    "data": [
        {
            "week": "Week 1",
            "start_date": "2024-10-28",
            "end_date": "2024-11-03",
            "total_duration_minutes": 315,
            "total_words_reviewed": 105,
            "average_accuracy_percentage": 86.5,
            "days_active": 7
        }
    ],
    "timestamp": "2024-11-01T16:00:00Z"
}
```

---

### 4. Performance Metrics

**Endpoint:** `GET /api/user/analytics/performance/`

**Authentication:** Bearer Token (Required)

**Response:**
```json
{
    "success": true,
    "message": "Performance metrics retrieved successfully",
    "data": {
        "total_study_time_minutes": 1260,
        "average_daily_study_time": 45,
        "total_words_reviewed": 315,
        "overall_accuracy": 85.5,
        "consistency_score": 8.5,
        "learning_velocity": 2.5,
        "recommendations": [
            "Great job! Keep up the excellent work!"
        ]
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

**Metrics Explanation:**
- `total_study_time_minutes`: Total minutes spent learning
- `average_daily_study_time`: Average minutes per day
- `overall_accuracy`: Overall review accuracy (0-100%)
- `consistency_score`: Consistency rating (0-10)
- `learning_velocity`: Words learned per day
- `recommendations`: Personalized learning recommendations

---

## 🚀 Flutter Integration Examples

### Example 1: Get User Profile

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> getUserProfile(String token) async {
  final response = await http.get(
    Uri.parse('https://api.example.com/api/user/profile/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    print('Profile: ${data['data']}');
  } else {
    print('Error: ${response.statusCode}');
  }
}
```

### Example 2: Mark Word Progress

```dart
Future<void> markWordProgress(String token, String wordId, bool isCorrect) async {
  final response = await http.post(
    Uri.parse('https://api.example.com/api/user/learning/words/$wordId/mark_progress/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'is_correct': isCorrect,
      'review_notes': 'Easy to remember',
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    print('Progress updated: ${data['data']}');
  } else {
    print('Error: ${response.statusCode}');
  }
}
```

### Example 3: Get Learning Statistics

```dart
Future<void> getStatistics(String token) async {
  final response = await http.get(
    Uri.parse('https://api.example.com/api/user/profile/statistics/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    final stats = data['data'];
    print('Words Learned: ${stats['words_learned']}');
    print('Learning Percentage: ${stats['learning_percentage']}%');
    print('Current Streak: ${stats['current_streak']} days');
  } else {
    print('Error: ${response.statusCode}');
  }
}
```

### Example 4: List Words with Pagination

```dart
Future<void> listWords(String token, {int page = 1, String? difficulty}) async {
  String url = 'https://api.example.com/api/user/learning/words/?page=$page&page_size=20';
  
  if (difficulty != null) {
    url += '&difficulty=$difficulty';
  }

  final response = await http.get(
    Uri.parse(url),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    final words = data['data']['data'];
    final pagination = data['data']['pagination'];
    
    print('Words: $words');
    print('Total: ${pagination['total_count']}');
    print('Has Next: ${pagination['has_next']}');
  } else {
    print('Error: ${response.statusCode}');
  }
}
```

---

## ⚠️ Error Handling

All API endpoints return standardized error responses:

```json
{
    "success": false,
    "error": true,
    "message": "Error description",
    "details": {
        "field_name": "Error message"
    },
    "timestamp": "2024-11-01T16:00:00Z"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 🔒 Security Best Practices

1. **Always use HTTPS** - Never send tokens over HTTP
2. **Store tokens securely** - Use Secure Storage in Flutter
3. **Refresh tokens regularly** - Refresh access token before expiry
4. **Handle token expiry** - Implement automatic token refresh
5. **Clear tokens on logout** - Remove tokens from secure storage
6. **Validate SSL certificates** - Verify server certificates

---

## 📞 Support & Examples

For more examples and support:
- GitHub: https://github.com/myname/voca_backend
- API Documentation: https://api.example.com/docs/
- Swagger UI: https://api.example.com/api/base/docs/swagger/

---

## 📝 Changelog

### v1.0.0 - Initial Release
- ✅ Professional User APIs with comprehensive documentation
- ✅ Bearer token authentication support
- ✅ Complete profile management system
- ✅ Vocabulary learning endpoints
- ✅ Progress tracking with spaced repetition
- ✅ Advanced analytics and reporting
- ✅ Device management for multi-device support
- ✅ Pagination and filtering for all list endpoints
- ✅ Complete error handling and validation
- ✅ Flutter-ready examples and integration guide
