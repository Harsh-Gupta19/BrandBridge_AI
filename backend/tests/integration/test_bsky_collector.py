"""
Quick test script for BlueSky data collector.

This script demonstrates how to use the BlueSky integration programmatically.
"""

import json
from pathlib import Path
from app.integrations.bsky import BlueSkyCollectorConfig, collect_bsky_creator_data


def test_bsky_collector_small():
    """Test the BlueSky collector with a small dataset."""
    print("Testing BlueSky Data Collector...")
    print("-" * 50)

    # Configure with minimal parameters for quick testing
    config = BlueSkyCollectorConfig(
        output_dir=Path("data/raw/bsky"),
        search_queries=("fitness India", "technology creator"),  # Minimal queries
        max_creators=5,  # Only collect 5 creators for quick test
        max_posts_per_creator=10,  # Only 10 posts per creator
        request_delay_seconds=0.2,  # Slightly longer delay to be respectful
        include_raw_api_payloads=False,  # Exclude raw data for smaller output
    )

    print(f"Configuration:")
    print(f"  Search Queries: {config.search_queries}")
    print(f"  Max Creators: {config.max_creators}")
    print(f"  Max Posts per Creator: {config.max_posts_per_creator}")
    print(f"  Output Directory: {config.output_dir}")
    print()

    try:
        print("Starting data collection...")
        dataset = collect_bsky_creator_data(config)

        metadata = dataset.get("metadata", {})
        print()
        print("Collection Complete!")
        print(f"  Duration: {metadata.get('duration_seconds')}s")
        print(f"  Creators Found: {metadata.get('creator_count')}")
        print(f"  Posts Collected: {metadata.get('post_count')}")
        print()

        # Print sample creator data
        creators = dataset.get("creators", [])
        if creators:
            print("Sample Creator Data:")
            creator = creators[0]
            print(f"  Handle: {creator['profile']['handle']}")
            print(f"  Display Name: {creator['profile']['display_name']}")
            print(f"  Followers: {creator['public_statistics']['followers_count']}")
            print(f"  Posts Count: {creator['public_statistics']['posts_count']}")
            print(f"  Avg Engagement: {creator['recent_post_metrics']['average_engagement']}")
            print()

        # Print sample post data
        posts = dataset.get("posts", [])
        if posts:
            print("Sample Post Data:")
            post = posts[0]
            print(f"  Handle: {post['creator_handle']}")
            print(f"  Text: {post['text'][:50]}...")
            print(f"  Likes: {post['likes']}, Reposts: {post['reposts']}")
            print(f"  Total Engagement: {post['total_engagement']}")
            print()

        return True

    except Exception as error:
        print(f"Error during collection: {error}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_bsky_collector_small()
    exit(0 if success else 1)
