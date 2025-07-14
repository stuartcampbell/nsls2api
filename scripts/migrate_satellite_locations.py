#!/usr/bin/env python3
"""
migrate_satellite_locations.py

One-time migration to convert any string-valued
nsls2_redhat_satellite_location_name into a single-element array.
Requires MongoDB 4.2+ for the aggregation‐style update.

Usage:
    python3 migrate_satellite_locations.py \
        --mongo-uri "mongodb://user:pass@host:port/?authSource=admin" \
        --db your_database_name \
        --collection beamlines \
        [--dry-run]
"""

import argparse
from pymongo import MongoClient


def migrate(uri: str, db_name: str, collection_name: str, dry_run: bool) -> None:
    client = MongoClient(uri)
    db = client[db_name]
    coll = db[collection_name]

    # Select docs where the field is currently a string
    query = { "nsls2_redhat_satellite_location_name": { "$type": "string" } }

    # Aggregation‐style update to wrap the string in an array
    pipeline = [
        {
            "$set": {
                "nsls2_redhat_satellite_location_name": [
                    "$nsls2_redhat_satellite_location_name"
                ]
            }
        }
    ]

    if dry_run:
        count = coll.count_documents(query)
        print(f"[DRY RUN] {count} document(s) WOULD be updated.")
        return

    result = coll.update_many(query, pipeline)
    print(f"Matched   : {result.matched_count} document(s)")
    print(f"Modified  : {result.modified_count} document(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate nsls2_redhat_satellite_location_name from string → array"
    )
    parser.add_argument(
        "--mongo-uri",
        required=True,
        help="MongoDB URI (e.g. mongodb://user:pass@host:port/?authSource=admin)",
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Name of the database containing the beamlines collection",
    )
    parser.add_argument(
        "--collection",
        default="beamlines",
        help="Name of the collection to migrate (default: beamlines)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show how many docs would change, without modifying anything",
    )

    args = parser.parse_args()
    migrate(args.mongo_uri, args.db, args.collection, args.dry_run)


if __name__ == "__main__":
    main()