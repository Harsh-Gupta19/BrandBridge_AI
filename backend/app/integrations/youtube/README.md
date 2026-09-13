# YouTube Integration

Current responsibility:

- Local development data collection through `youtubedatacollector.py`
- Public YouTube creator/channel/video metadata collection
- JSON output for analysis under `data/raw/youtube/`

Future responsibility:

- OAuth connection
- Channel verification
- Permitted channel statistics
- Analytics where authorized

The platform must continue working when YouTube APIs are unavailable. YouTube data should enrich matching, not become a mandatory dependency for base marketplace workflows.

## API Key

Use the `YOUTUBE_API_KEY` environment variable.

Do not commit the real API key. `.env` is ignored by Git, while `.env.example` only contains placeholders.

Relevant environment variables:

```text
YOUTUBE_API_KEY=
YOUTUBE_REGION_CODE=IN
YOUTUBE_LANGUAGE_CODE=en
YOUTUBE_MAX_CREATORS=100
YOUTUBE_MAX_VIDEOS_PER_CREATOR=20
YOUTUBE_SEARCH_PAGES_PER_QUERY=1
YOUTUBE_REQUEST_DELAY_SECONDS=0.1
YOUTUBE_SEARCH_QUERIES=fitness India,nutrition India,gym India
```

## Run The Collector

From `backend/`:

```bash
python -m app.integrations.youtube.youtubedatacollector --max-creators 100
```

Default JSON output path:

```text
data/raw/youtube/
```

## Data Collected

The collector stores normalized creator records plus raw public API payloads.

Creator-level data includes:

- Channel ID, title, description, URL, custom URL, country, creation date, thumbnail
- Public subscriber count when visible
- Total channel views
- Total video count
- Channel branding keywords when available
- Topic categories when available
- Discovery query signals
- Recent-video metrics
- Derived BrandBridge matching fields

Video-level data includes:

- Video ID, title, description, publish date, thumbnail
- Tags, category ID, language
- Duration, definition, caption status
- Views, likes, comments
- Topic categories when available

## Data Not Available With API Key Alone

The public YouTube Data API key flow does not provide:

- Audience age range
- Audience gender split
- Watch time
- Revenue
- Private analytics
- Creator business email
- Creator rate card

Those require YouTube Analytics OAuth permission, creator-entered data, or later enrichment.
