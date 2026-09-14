# BlueSky Integration

Data collection module for BlueSky public creators using the BlueSky Public API.

## Overview

The BlueSky integration collects public creator data from BlueSky (https://bsky.app/) using the public API endpoint at `https://public.api.bsky.app/xrpc`. 

No authentication is required for public data collection, making this integration straightforward and accessible.

## Features

- **Creator Search**: Search for creators by keywords (e.g., "fitness India", "technology creator")
- **Profile Data**: Collect public profile information (handle, display name, description, follower count, etc.)
- **Feed Collection**: Fetch recent posts from creators with engagement metrics (likes, reposts, replies, quotes)
- **Metrics Calculation**: Compute engagement rates, average interactions per post
- **Data Normalization**: Standardized output format consistent with other platform integrations
- **Raw API Payloads**: Optional inclusion of complete API responses for detailed analysis

## BlueSky API Endpoints Used

- **`app.bsky.actor.searchActors`**: Search for creators by query string
- **`app.bsky.actor.getProfile`**: Fetch detailed profile information for a creator
- **`app.bsky.feed.getAuthorFeed`**: Retrieve recent posts from a creator's feed

## Configuration

### Environment Variables

```bash
# Optional: Override default search queries (comma-separated or JSON array)
BSKY_SEARCH_QUERIES=fitness,technology,beauty

# Optional: Maximum number of creators to collect (default: 100)
BSKY_MAX_CREATORS=100

# Optional: Maximum posts per creator (default: 50)
BSKY_MAX_POSTS_PER_CREATOR=50

# Optional: Delay between API requests in seconds (default: 0.1)
BSKY_REQUEST_DELAY_SECONDS=0.1
```

### Programmatic Configuration

```python
from pathlib import Path
from app.integrations.bsky import BlueSkyCollectorConfig, collect_bsky_creator_data

config = BlueSkyCollectorConfig(
    output_dir=Path("data/raw/bsky"),
    search_queries=("fitness", "technology", "beauty"),
    max_creators=50,
    max_posts_per_creator=30,
    request_delay_seconds=0.15,
    include_raw_api_payloads=True
)

dataset = collect_bsky_creator_data(config)
```

## Command Line Usage

```bash
# Collect with defaults
python -m app.integrations.bsky.bskydatacollector

# Custom search queries
python -m app.integrations.bsky.bskydatacollector --search-query "fitness" --search-query "technology"

# Collect more creators and posts
python -m app.integrations.bsky.bskydatacollector \
  --max-creators 200 \
  --max-posts-per-creator 100

# Exclude raw API payloads
python -m app.integrations.bsky.bskydatacollector --no-raw

# Custom output directory
python -m app.integrations.bsky.bskydatacollector --output-dir /path/to/output
```

## Output Format

The collector generates the following JSON files:

### 1. Full Dataset
**File**: `brandbridge_bsky_dataset_{timestamp}.json`

Contains complete collection metadata, configuration, creator records, posts, and raw search results.

```json
{
  "metadata": {
    "project": "BrandBridge AI",
    "source": "BlueSky Public API",
    "data_classification": "public_api_data",
    "started_at": "2024-01-15T10:30:00+00:00",
    "finished_at": "2024-01-15T10:45:30+00:00",
    "duration_seconds": 915.2,
    "creator_count": 50,
    "post_count": 2500
  },
  "collection_config": {...},
  "creators": [...],
  "posts": [...],
  "raw_search_pages": [...]
}
```

### 2. Creators
**File**: `brandbridge_bsky_creators_{timestamp}.json`

Array of normalized creator records.

```json
[
  {
    "creator_id": "bsky:did:plc:...",
    "platform": "bsky",
    "profile": {
      "did": "did:plc:...",
      "handle": "creator.bsky",
      "display_name": "Example Creator",
      "description": "Content creator focused on technology and lifestyle",
      "avatar": "https://...",
      "creator_url": "https://bsky.app/profile/creator.bsky",
      "created_at": "2023-01-15T10:30:00.000Z",
      "indexed_at": "2024-01-15T10:30:00.000Z"
    },
    "public_statistics": {
      "followers_count": 5000,
      "follows_count": 500,
      "posts_count": 250,
      "follower_to_following_ratio": 10.0
    },
    "viewer_state": {
      "muted": false,
      "blocked_by": false
    },
    "recent_post_metrics": {
      "posts_analyzed": 50,
      "average_likes": 45.5,
      "average_replies": 8.2,
      "average_reposts": 12.3,
      "average_quotes": 3.1,
      "average_engagement": 69.1,
      "total_engagement": 3455,
      "engagement_per_follower": 0.0138,
      "top_words": ["technology", "web3", "decentralized", ...]
    },
    "brandbridge_fields": {
      "creator_categories": ["technology", "web3", "social"],
      "platforms": {
        "bsky": {
          "did": "did:plc:...",
          "handle": "creator.bsky",
          "followers": 5000,
          "average_engagement": 69.1
        }
      },
      "matching_features": {...}
    },
    "recent_posts": [...]
  }
]
```

### 3. Posts
**File**: `brandbridge_bsky_posts_{timestamp}.json`

Array of normalized post records.

```json
[
  {
    "post_uri": "at://did:plc:.../app.bsky.feed.post/...",
    "post_cid": "bafy...",
    "did": "did:plc:...",
    "creator_handle": "creator.bsky",
    "created_at": "2024-01-15T10:30:00.000Z",
    "text": "This is a sample BlueSky post with engagement",
    "likes": 120,
    "replies": 15,
    "reposts": 45,
    "quotes": 8,
    "total_engagement": 188,
    "engagement_rate": 188.0,
    "langs": ["en"],
    "facets": [],
    "reply_ref": null
  }
]
```

### 4. Latest Links
Symbolic links to the latest collection run:
- `brandbridge_bsky_dataset.latest.json`
- `brandbridge_bsky_creators.latest.json`
- `brandbridge_bsky_posts.latest.json`

## Data Schema Reference

### Creator Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `creator_id` | string | Platform-prefixed DID (format: `bsky:did:plc:...`) |
| `platform` | string | Always "bsky" |
| `profile.did` | string | BlueSky decentralized identifier |
| `profile.handle` | string | BlueSky handle (e.g., creator.bsky) |
| `profile.display_name` | string | Display name as set by user |
| `profile.description` | string | Bio/description text |
| `public_statistics.followers_count` | int | Number of followers |
| `public_statistics.follows_count` | int | Number of accounts followed |
| `public_statistics.posts_count` | int | Total posts ever made |
| `recent_post_metrics` | object | Aggregate stats from recent posts |

### Post Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `post_uri` | string | BlueSky AT URI for the post |
| `post_cid` | string | Content identifier hash |
| `created_at` | string | ISO 8601 timestamp |
| `text` | string | Post content text |
| `likes` | int | Number of likes received |
| `replies` | int | Number of replies |
| `reposts` | int | Number of reposts |
| `quotes` | int | Number of quote posts |
| `total_engagement` | int | Sum of all engagement metrics |
| `langs` | array | Languages detected in post |

## Limitations

1. **Public Data Only**: Only publicly visible creator profiles and posts are collected
2. **No Authentication**: Cannot access private profiles or direct messages
3. **Rate Limiting**: BlueSky API has rate limits; use `--request-delay-seconds` to avoid throttling
4. **Limited Historical Data**: Only recent posts are typically available via the API
5. **No Private Metrics**: Audience demographics, analytics, and rate card data unavailable from public API
6. **DID vs Handle Stability**: DIDs are permanent but handles can change; store DIDs as primary identifier

## API Response Codes and Error Handling

The collector gracefully handles API errors:

- **HTTP 429 (Too Many Requests)**: Exceeded rate limit; increase `request_delay_seconds`
- **HTTP 404 (Not Found)**: Creator or post not found (skipped)
- **HTTP 500 (Server Error)**: Temporary API issue; retrying may help
- **Connection Timeout**: Network issue; check internet connection

Failed requests for individual creators or posts are logged as warnings and collection continues for other items.

## Performance Considerations

- **Typical Speed**: ~1-2 creators per second with default delay (0.1s between requests)
- **For 100 creators with 50 posts each**: ~15-20 minutes
- **Bandwidth**: Relatively low; most posts are < 1KB each
- **Storage**: ~10-15MB for 100 creators with 50 posts each (including raw payloads)

To speed up collection:
```bash
python -m app.integrations.bsky.bskydatacollector \
  --request-delay-seconds 0.05 \
  --no-raw
```

## Integration with BrandBridge Backend

The collected data can be loaded and processed in the backend:

```python
from pathlib import Path
import json

# Load the latest dataset
dataset_path = Path("data/raw/bsky/brandbridge_bsky_dataset.latest.json")
dataset = json.loads(dataset_path.read_text())

# Access creators
creators = dataset["creators"]

# Access posts
posts = dataset["posts"]

# Use in matching algorithms
for creator in creators:
    categories = creator["brandbridge_fields"]["creator_categories"]
    engagement = creator["recent_post_metrics"]["average_engagement"]
    followers = creator["public_statistics"]["followers_count"]
```

## Comparison with Other Platforms

| Feature | YouTube | BlueSky | Instagram |
|---------|---------|---------|-----------|
| API Requirement | API Key Required | Public (no auth) | OAuth Required |
| Search Method | Channel search | Actor search | Graph Search (deprecated) |
| Engagement Metrics | Views, Likes, Comments | Likes, Reposts, Replies, Quotes | Likes, Comments |
| Historical Posts | Configurable via playlists | Recent feed | Last ~30 posts |
| Audience Data | Limited to public | Follower count only | Restricted (OAuth needed) |

## Resources

- **BlueSky API Documentation**: https://docs.bsky.app/
- **ATProto Reference**: https://atproto.com/
- **Public API Endpoint**: https://public.api.bsky.app/xrpc
- **BlueSky GitHub**: https://github.com/bluesky-social/atproto

## Troubleshooting

### No results found
- Check search queries are valid
- Try broader search terms
- Verify internet connection

### API Request Failed
- Check BlueSky API status
- Increase `--request-delay-seconds`
- Retry after a few minutes

### Incomplete creator data
- Some creators may have private profiles
- Not all creators have recent posts
- Check logs for individual failure messages

## Future Enhancements

- [ ] Add support for authenticated endpoints (when available)
- [ ] Implement recursive post thread collection
- [ ] Add support for post search/trending data
- [ ] Implement list and feed collection
- [ ] Add support for reply chain analysis
- [ ] Integrate with ML features for content classification

## License

Part of the BrandBridge AI project.
