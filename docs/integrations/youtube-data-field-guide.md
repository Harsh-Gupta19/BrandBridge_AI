# YouTube Data Field Guide

This guide explains the generated YouTube JSON data using one creator example and ranks fields by project priority.

Example file:

```text
data/raw/youtube/brandbridge_youtube_creators.latest.json
```

Example creator used in this guide:

```text
Rohit Khatri Fitness
creator_id: youtube:UChXRi2xTPZ8J5lznBNuMCOw
country: IN
subscribers: 5,220,000
average recent views: 227,847.45
engagement rate: 2.9516%
videos analyzed: 20
```

## Dataset Files

The collector creates three useful JSON files:

```text
brandbridge_youtube_creators.latest.json
brandbridge_youtube_videos.latest.json
brandbridge_youtube_dataset.latest.json
```

Use them like this:

- `creators.latest.json`: best file for creator profile and matching work.
- `videos.latest.json`: best file for video-level analysis and feature engineering.
- `dataset.latest.json`: combined file with metadata, creators, videos, and raw search pages.

## Top-Level Creator Shape

Each creator record has this structure:

```text
creator_id
platform
channel
public_statistics
branding
status
topics
discovery
recent_video_metrics
brandbridge_fields
recent_videos
raw
```

## Priority Levels

Use these levels while building the project:

- P0: Required for MVP creator-brand matching.
- P1: Important for better ranking and explanations.
- P2: Useful for UI, analytics, and future enrichment.
- P3: Raw/debug data. Keep for research, but do not expose directly in the product UI.

## P0 Fields: Required For MVP

These are the most important fields for the first working BrandBridge recommendation flow.

### Creator Identity

```json
{
  "creator_id": "youtube:UChXRi2xTPZ8J5lznBNuMCOw",
  "platform": "youtube"
}
```

Why it matters:

- Unique creator ID for the platform.
- Allows future multi-platform profiles such as YouTube plus Instagram.

Database destination later:

```text
CreatorProfile
SocialAccount
```

### Channel Basics

```json
{
  "channel_id": "UChXRi2xTPZ8J5lznBNuMCOw",
  "title": "Rohit Khatri Fitness",
  "description": "...",
  "custom_url": "@rohitkhatrifitness",
  "channel_url": "https://www.youtube.com/channel/UChXRi2xTPZ8J5lznBNuMCOw",
  "country": "IN",
  "thumbnail_url": "..."
}
```

Why it matters:

- Shows creator profile details in UI.
- Helps brand users inspect the creator.
- Country helps campaign-country matching.
- Description helps semantic search and embeddings.

Database destination later:

```text
CreatorProfile
SocialAccount
```

### Public Reach

```json
{
  "subscriber_count": 5220000,
  "total_view_count": 430661645,
  "video_count": 839
}
```

Why it matters:

- Subscriber count is the basic reach signal.
- Total views and video count show scale and maturity.

ML feature candidates:

```text
follower_score
creator_reliability
```

### Recent Performance Metrics

```json
{
  "videos_analyzed": 20,
  "average_views": 227847.45,
  "average_likes": 6502.9,
  "average_comments": 222.2,
  "engagement_rate_percent": 2.9516,
  "average_views_to_subscriber_ratio": 0.0436
}
```

Why it matters:

- Average views are often more useful than subscriber count.
- Engagement rate helps compare creators of different sizes.
- Views-to-subscriber ratio shows how active/reachable the audience is.

ML feature candidates:

```text
engagement_rate
follower_score
creator_reliability
```

### Creator Categories

```json
{
  "creator_categories": [
    "fitness",
    "weight gain",
    "how to lose weight",
    "diet plan"
  ]
}
```

Why it matters:

- Used to match campaign category with creator niche.
- For example, a protein snack campaign should prefer fitness/nutrition creators.

ML feature candidates:

```text
category_similarity
semantic_similarity
```

### Platform Summary

```json
{
  "platforms": {
    "youtube": {
      "channel_id": "...",
      "channel_url": "...",
      "subscribers": 5220000,
      "average_views": 227847.45,
      "engagement_rate_percent": 2.9516
    }
  }
}
```

Why it matters:

- This is close to the final creator profile shape needed by BrandBridge.
- It supports multi-platform matching later.

ML feature candidates:

```text
platform_match
follower_score
engagement_rate
```

### Semantic Similarity Text

```json
{
  "semantic_similarity_text": "Rohit Khatri Fitness ... how to weight gain ..."
}
```

Why it matters:

- This text can be embedded using `sentence-transformers`.
- Later, campaign briefs can be compared against this text using pgvector.

AI/RAG destination later:

```text
backend/app/ai/embeddings/
PostgreSQL pgvector
```

ML feature candidate:

```text
semantic_similarity
```

## P1 Fields: Important For Better Matching

These should be used after the first matching flow works.

### Top Tags

```json
{
  "top_tags": [
    "how to",
    "weight gain",
    "how to gain weight fast",
    "how to lose weight",
    "belly fat"
  ]
}
```

Why it matters:

- Tags reveal creator topic focus.
- Helpful for campaign-category matching.
- Helpful for embeddings and explanations.

### Content Formats Observed

```json
{
  "content_formats_observed": ["long_form", "mid_form"]
}
```

Why it matters:

- Brands may ask for Shorts, long videos, Reels, or tutorials.
- This creator mostly has mid/long-form content in the recent sample.

ML feature candidate:

```text
platform_match
content_format_match
```

### Recent Videos

Each creator has up to 20 recent videos.

Useful video fields:

```text
video_id
title
description
published_at
tags
duration_seconds
views
likes
comments
topic_categories
```

Why it matters:

- Recent videos show what the creator is currently making.
- Recent views help avoid relying only on lifetime subscriber count.
- Video tags and titles improve semantic understanding.

## P2 Fields: Useful For UI And Future Analytics

These are useful, but not essential for the first recommender.

### Thumbnail URL

Use for creator profile cards.

```text
channel.thumbnail_url
```

### Channel Created Date

Use for profile completeness or trust signals.

```text
channel.published_at
```

### Branding Keywords

Use for enrichment, but do not trust blindly.

```text
branding.channel_keywords
```

### Topic Categories

Useful when available, but not always present.

```text
topics.topic_categories
recent_videos[].topic_categories
```

## P3 Fields: Raw Or Debug Only

These fields are useful for development and research, but should not be exposed directly in frontend screens.

```text
raw
discovery.search_results[].raw
recent_videos[].raw
```

Why keep them:

- Debugging API responses.
- Rebuilding derived fields later.
- Feature engineering experiments.

Why not expose them:

- Too large.
- Too noisy.
- Not designed for product UI.

## Missing Fields Needed For Full BrandBridge

The YouTube API key gives only public YouTube data. It does not provide all fields needed for the full project.

### Missing Creator Fields

These should come from creator registration forms, OAuth, or manual enrichment:

```text
creator user account
creator email
creator location beyond channel country
creator languages
creator rate card
creator preferred collaboration types
creator availability
creator audience age range
creator audience gender split
creator audience country distribution
creator brand safety preferences
creator past collaboration history
```

### Missing Brand/Campaign Fields

These should come from brand registration and campaign creation:

```text
brand name
brand industry
brand website
campaign title
campaign brief
campaign budget
campaign country
target audience age range
target audience country
preferred platforms
required content formats
creator categories
campaign goals
brand guidelines
approval status
```

## Recommended MVP Matching Inputs

For the first working recommender, use only these fields.

### Creator Side

```text
creator_id
channel.title
channel.description
channel.country
channel.channel_url
channel.thumbnail_url
public_statistics.subscriber_count
public_statistics.total_view_count
public_statistics.video_count
recent_video_metrics.average_views
recent_video_metrics.engagement_rate_percent
recent_video_metrics.top_tags
recent_video_metrics.content_formats_observed
brandbridge_fields.creator_categories
brandbridge_fields.matching_features.semantic_similarity_text
```

### Campaign Side

```text
campaign title
campaign brief
campaign category
campaign budget
campaign country
target age range
preferred platforms
required content formats
creator categories
```

### First Matching Features

```text
category_similarity
country_match
platform_match
content_format_match
engagement_rate
follower_score
semantic_similarity
```

## Example Interpretation

For the example creator:

```text
Creator: Rohit Khatri Fitness
Category fit: fitness, weight loss, diet, exercise
Country fit: India
Platform fit: YouTube
Reach: very high subscriber count
Recent performance: strong average views
Engagement: around 2.95% on recent videos
Content style: mid-form and long-form fitness videos
Missing data: audience demographics, rate card, direct verified collaboration info
```

Good campaign match:

```text
Protein snack launch in India
Fitness-focused young adults
YouTube video or Shorts campaign
Health, nutrition, gym, or weight-loss positioning
```

Weak campaign match:

```text
Luxury fashion
Finance app
Travel hotel campaign
Instagram-only Reel campaign unless Instagram data is added
```

## Practical Development Plan

Recommended order:

1. Build `CreatorProfile` and `SocialAccount` storage using P0 fields.
2. Build campaign creation using campaign-side P0 fields.
3. Implement simple rule-based matching with category, country, platform, and content format.
4. Add ML features using average views, engagement rate, subscribers, and reliability.
5. Add embeddings using `semantic_similarity_text`.
6. Add creator-entered missing fields like rate card and audience.
7. Add OAuth later if private analytics become necessary.
