#!/usr/bin/env python3
"""
london_venues.py — Parse London.md and Google Takeout CSVs for venue names,
fetch details from Google Maps Places API, and cache results in SQLite.

Usage:
    python3 london_venues.py                       # parse + fetch new venues + print summary
    python3 london_venues.py --refetch "Name"      # re-fetch a specific venue
    python3 london_venues.py --dump                 # dump all cached data as JSON
    python3 london_venues.py --parse-only           # just show what venues were parsed (no API calls)

    python3 london_venues.py --set-booking "Venue" --price "£10" --booking-required yes \
        --booking-url "https://..." --booking-notes "Notes" --member-required no

    python3 london_venues.py --add-event --title "Event" --venue "Venue" \
        --date "2026-02-15" --time "8pm" --price "£25" --url "https://..." \
        --category "concert" --source "halibuts" --notes "Notes"

    python3 london_venues.py --report              # full research report
    python3 london_venues.py --events              # list all events during trip

    python3 london_venues.py --import-reservations reservations.csv
    python3 london_venues.py --reservations        # list all reservations
    python3 london_venues.py --add-reservation "Duck & Waffle" --date 2026-02-17 \
        --time 19:15 --end-time 21:00 --confirmation ABC123 --party-size 2

Requires GOOGLE_MAPS_API_KEY env var for API calls.
"""

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "london_venues.db"
MD_PATH = SCRIPT_DIR / "London.md"

PLACES_API_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.regularOpeningHours,places.googleMapsUri"

# Sections in London.md that contain venues
VENUE_SECTIONS = {
    "Food/Pubs",
    "Museums",
    "Destinations",
    "Random / Low priority",
}

# Sections to skip entirely
SKIP_SECTIONS = {
    "Prep",
    "Stuff going on",
}


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def init_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            source TEXT,
            section TEXT,
            search_query TEXT,
            google_place_id TEXT,
            google_display_name TEXT,
            address TEXT,
            regular_hours_json TEXT,
            regular_hours_text TEXT,
            google_maps_uri TEXT,
            raw_response TEXT,
            fetched_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            venue_name TEXT,
            date TEXT,
            time TEXT,
            price TEXT,
            url TEXT,
            category TEXT,
            notes TEXT,
            source TEXT,
            fetched_at TEXT,
            UNIQUE(title, venue_name, date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venue_name TEXT NOT NULL,
            matched_venue TEXT,
            date TEXT NOT NULL,
            time TEXT,
            end_time TEXT,
            confirmation TEXT,
            party_size INTEGER,
            notes TEXT,
            created_at TEXT,
            UNIQUE(venue_name, date, time)
        )
    """)
    # Migrate: add booking columns if they don't exist yet
    _migrate_booking_columns(conn)
    conn.commit()
    return conn


def _migrate_booking_columns(conn: sqlite3.Connection):
    """Add booking/research columns to venues table if missing."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(venues)").fetchall()}
    new_cols = {
        "ticket_price": "TEXT",
        "booking_required": "TEXT",
        "booking_url": "TEXT",
        "booking_notes": "TEXT",
        "member_required": "TEXT",
    }
    for col, col_type in new_cols.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE venues ADD COLUMN {col} {col_type}")


def get_cached_names(conn: sqlite3.Connection) -> set:
    rows = conn.execute("SELECT name FROM venues").fetchall()
    return {row["name"] for row in rows}


def upsert_venue(conn: sqlite3.Connection, venue: dict):
    conn.execute("""
        INSERT INTO venues (name, source, section, search_query, google_place_id,
                            google_display_name, address, regular_hours_json,
                            regular_hours_text, google_maps_uri, raw_response, fetched_at)
        VALUES (:name, :source, :section, :search_query, :google_place_id,
                :google_display_name, :address, :regular_hours_json,
                :regular_hours_text, :google_maps_uri, :raw_response, :fetched_at)
        ON CONFLICT(name) DO UPDATE SET
            source = :source,
            section = :section,
            search_query = :search_query,
            google_place_id = :google_place_id,
            google_display_name = :google_display_name,
            address = :address,
            regular_hours_json = :regular_hours_json,
            regular_hours_text = :regular_hours_text,
            google_maps_uri = :google_maps_uri,
            raw_response = :raw_response,
            fetched_at = :fetched_at
    """, venue)
    conn.commit()


def _find_venue_name(conn: sqlite3.Connection, name: str) -> Optional[str]:
    """Find the actual venue name in the DB, handling apostrophe variants."""
    # Try exact match first
    row = conn.execute("SELECT name FROM venues WHERE name = ?", (name,)).fetchone()
    if row:
        return row["name"]
    # Try with apostrophe normalization (straight ↔ curly)
    for variant in [name.replace("'", "\u2019"), name.replace("\u2019", "'")]:
        row = conn.execute("SELECT name FROM venues WHERE name = ?", (variant,)).fetchone()
        if row:
            return row["name"]
    return None


def set_booking(conn: sqlite3.Connection, name: str, price: Optional[str],
                required: Optional[str], url: Optional[str],
                notes: Optional[str], member: Optional[str]):
    """Update booking info for an existing venue."""
    db_name = _find_venue_name(conn, name)
    if not db_name:
        print(f"Error: Venue '{name}' not found in database.")
        print("Available venues:")
        for row in conn.execute("SELECT name FROM venues ORDER BY name").fetchall():
            print(f"  {row['name']}")
        sys.exit(1)

    updates = []
    params = []
    if price is not None:
        updates.append("ticket_price = ?")
        params.append(price)
    if required is not None:
        updates.append("booking_required = ?")
        params.append(required)
    if url is not None:
        updates.append("booking_url = ?")
        params.append(url)
    if notes is not None:
        updates.append("booking_notes = ?")
        params.append(notes)
    if member is not None:
        updates.append("member_required = ?")
        params.append(member)

    if not updates:
        print("No booking fields provided.")
        return

    params.append(db_name)
    conn.execute(f"UPDATE venues SET {', '.join(updates)} WHERE name = ?", params)
    conn.commit()
    print(f"Updated booking info for '{db_name}'.")


def add_event(conn: sqlite3.Connection, title: str, venue_name: Optional[str],
              date: Optional[str], time: Optional[str], price: Optional[str],
              url: Optional[str], category: Optional[str], notes: Optional[str],
              source: Optional[str]):
    """Add an event to the events table."""
    now = datetime.utcnow().isoformat()
    try:
        conn.execute("""
            INSERT INTO events (title, venue_name, date, time, price, url, category, notes, source, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(title, venue_name, date) DO UPDATE SET
                time = excluded.time,
                price = excluded.price,
                url = excluded.url,
                category = excluded.category,
                notes = excluded.notes,
                source = excluded.source,
                fetched_at = excluded.fetched_at
        """, (title, venue_name, date, time, price, url, category, notes, source, now))
        conn.commit()
        print(f"Added event: '{title}'" + (f" at {venue_name}" if venue_name else "") +
              (f" on {date}" if date else ""))
    except sqlite3.IntegrityError as e:
        print(f"Error adding event: {e}")


def delete_venue(conn: sqlite3.Connection, name: str):
    conn.execute("DELETE FROM venues WHERE name = ?", (name,))
    conn.commit()


def fuzzy_match_venue(conn: sqlite3.Connection, name: str) -> Optional[str]:
    """Find the best matching venue name in the DB using fuzzy matching."""
    # Try exact match first
    exact = _find_venue_name(conn, name)
    if exact:
        return exact

    # Normalize for comparison
    target = normalize_name(name)
    all_venues = conn.execute("SELECT name FROM venues").fetchall()

    best_match = None
    best_score = 0

    for row in all_venues:
        venue_name = row["name"]
        normalized = normalize_name(venue_name)

        # Exact normalized match
        if normalized == target:
            return venue_name

        # Check if one contains the other
        if target in normalized or normalized in target:
            score = len(target) / max(len(normalized), len(target))
            if score > best_score:
                best_score = score
                best_match = venue_name

    # Return match if it's reasonably close (> 60% overlap)
    if best_score > 0.6:
        return best_match

    return None


def add_reservation(conn: sqlite3.Connection, venue_name: str, date: str,
                    time: Optional[str] = None, end_time: Optional[str] = None,
                    confirmation: Optional[str] = None, party_size: Optional[int] = None,
                    notes: Optional[str] = None) -> bool:
    """Add a reservation to the database."""
    now = datetime.utcnow().isoformat()

    # Try to match to an existing venue
    matched = fuzzy_match_venue(conn, venue_name)
    if matched:
        print(f"  Matched '{venue_name}' → '{matched}'")
    else:
        print(f"  Warning: '{venue_name}' not found in venues database (saving anyway)")

    try:
        conn.execute("""
            INSERT INTO reservations (venue_name, matched_venue, date, time, end_time,
                                      confirmation, party_size, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(venue_name, date, time) DO UPDATE SET
                matched_venue = excluded.matched_venue,
                end_time = excluded.end_time,
                confirmation = excluded.confirmation,
                party_size = excluded.party_size,
                notes = excluded.notes,
                created_at = excluded.created_at
        """, (venue_name, matched, date, time, end_time, confirmation, party_size, notes, now))
        conn.commit()
        print(f"Added reservation: {venue_name} on {date}" + (f" at {time}" if time else ""))
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error adding reservation: {e}")
        return False


def import_reservations_csv(conn: sqlite3.Connection, csv_path: Path):
    """Import reservations from a CSV file."""
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        sys.exit(1)

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            venue = row.get("venue", "").strip()
            date = row.get("date", "").strip()
            if not venue or not date:
                continue

            add_reservation(
                conn,
                venue_name=venue,
                date=date,
                time=row.get("time", "").strip() or None,
                end_time=row.get("end_time", "").strip() or None,
                confirmation=row.get("confirmation", "").strip() or None,
                party_size=int(row["party_size"]) if row.get("party_size", "").strip() else None,
                notes=row.get("notes", "").strip() or None,
            )
            count += 1

    print(f"\nImported {count} reservation(s) from {csv_path.name}")


def print_reservations(conn: sqlite3.Connection):
    """Print all reservations, sorted by date."""
    rows = conn.execute(
        "SELECT * FROM reservations ORDER BY date, time"
    ).fetchall()

    if not rows:
        print("No reservations in database.")
        return

    print("\n=== RESERVATIONS ===\n")
    current_date = None
    for row in rows:
        if row["date"] != current_date:
            current_date = row["date"]
            # Format date nicely
            try:
                dt = datetime.strptime(current_date, "%Y-%m-%d")
                date_str = dt.strftime("%a %b %d, %Y")
            except ValueError:
                date_str = current_date
            print(f"--- {date_str} ---")

        parts = [f"  {row['venue_name']}"]
        if row["time"]:
            time_str = row["time"]
            if row["end_time"]:
                time_str += f" - {row['end_time']}"
            parts.append(f"at {time_str}")
        print(" ".join(parts))

        if row["matched_venue"] and row["matched_venue"] != row["venue_name"]:
            print(f"    (matched to: {row['matched_venue']})")
        if row["party_size"]:
            print(f"    Party size: {row['party_size']}")
        if row["confirmation"]:
            print(f"    Confirmation: {row['confirmation']}")
        if row["notes"]:
            print(f"    Notes: {row['notes']}")
        print()


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_markdown(md_path: Path) -> list:
    """Parse London.md and return a list of {name, section, source}."""
    if not md_path.exists():
        print(f"Warning: {md_path} not found, skipping markdown parsing.")
        return []

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    venues = []
    current_section = None
    in_venue_section = False

    for line in lines:
        # Detect section headers
        header_match = re.match(r"^(#{1,3})\s+(.*?)$", line.strip())
        if header_match:
            section_name = header_match.group(2).strip()
            if section_name in VENUE_SECTIONS:
                current_section = section_name
                in_venue_section = True
            elif section_name in SKIP_SECTIONS or section_name == "":
                in_venue_section = False
            elif section_name and header_match.group(1) in ("##", "###"):
                # Any other named section resets
                in_venue_section = False
            continue

        if not in_venue_section:
            continue

        # Only process bullet points
        bullet_match = re.match(r"^\*\s+(.+)$", line.strip())
        if not bullet_match:
            continue

        content = bullet_match.group(1).strip()
        venue_name = extract_venue_name(content)
        if venue_name:
            venues.append({
                "name": venue_name,
                "section": current_section,
                "source": "markdown",
            })

    return venues


def extract_venue_name(content: str) -> Optional[str]:
    """Extract a venue name from a markdown bullet point content."""

    # Skip sub-bullets (indented items like notes)
    if content.startswith("  ") or content.startswith("\t"):
        return None

    # Pattern 1: Line starts with plain text followed by a parenthetical or link
    # e.g., "Victoria & Albert Museum ([link text](url))"
    # e.g., "Natural History Museum. [Dinosaurs](url)"
    plain_prefix_match = re.match(r"^([A-Za-z][A-Za-z &\'']+?)[\.\s]*[\(\[]", content)
    if plain_prefix_match:
        name = plain_prefix_match.group(1).strip().rstrip(".")
        # Check if this is "Royal Shakespeare Company [Ghost & Gore tour](...)" style
        # where the prefix is the org and the link is the specific thing
        if len(name) > 3:
            return name

    # Pattern 2: Line starts with [Venue Name](url) possibly followed by more stuff
    # e.g., "[Lost Souls Pizza](url) (vampire-themed pizza bar)"
    # e.g., "[Darwin's](url) (sky garden)"
    link_match = re.match(r"^\[([^\]]+)\]\([^\)]+\)(.*)", content)
    if link_match:
        link_text = link_match.group(1).strip()
        remainder = link_match.group(2).strip()

        # Special case: if remainder has a parenthetical that looks like a subtitle,
        # include it. e.g., "[Darwin's](url) (sky garden)" -> "Darwin's Sky Garden"
        paren_match = re.match(r"^\(([a-zA-Z\s]+)\)", remainder)
        if paren_match:
            subtitle = paren_match.group(1).strip()
            # Only append if it looks like a place qualifier, not a description
            qualifier_words = {"sky garden", "soho", "shoreditch", "covent garden",
                               "camden", "brixton", "mayfair", "kensington"}
            if subtitle.lower() in qualifier_words:
                return f"{link_text} {subtitle.title()}"

        return link_text

    # Pattern 3: Plain text with a link somewhere in it
    # e.g., "Read [Time Out London](url)" — but we skip "Stuff going on" section
    # This shouldn't normally fire since we filter sections, but just in case
    link_anywhere = re.search(r"\[([^\]]+)\]\([^\)]+\)", content)
    if link_anywhere:
        return link_anywhere.group(1).strip()

    # Pattern 4: Plain text only (no links)
    clean = content.strip()
    if clean and len(clean) > 2:
        return clean

    return None


# ---------------------------------------------------------------------------
# Google Takeout CSV parsing
# ---------------------------------------------------------------------------

def parse_takeout_csvs(directory: Path) -> list:
    """Find and parse any CSV files in the directory (Google Takeout format).

    Google Takeout "Saved" CSVs may have a title line and blank line before the
    actual header row (Title,Note,URL,Tags,Comment). We scan for the header row
    and parse from there.
    """
    venues = []
    csv_files = list(directory.glob("*.csv"))

    for csv_path in csv_files:
        try:
            with open(csv_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Find the actual header row containing "Title"
            header_idx = None
            for i, line in enumerate(lines):
                if line.strip().lower().startswith("title,") or line.strip().lower() == "title":
                    header_idx = i
                    break

            if header_idx is None:
                print(f"Warning: No 'Title' header found in {csv_path.name}, skipping.")
                continue

            # Parse from the header row onward
            csv_text = "".join(lines[header_idx:])
            reader = csv.DictReader(csv_text.splitlines())

            for row in reader:
                name = row.get("Title") or row.get("Name") or row.get("title") or row.get("name")
                if name and name.strip():
                    # Use tags as section hint if available
                    tags = row.get("Tags", "").strip()
                    section = _tags_to_section(tags) if tags else "Google Maps List"
                    venues.append({
                        "name": name.strip(),
                        "section": section,
                        "source": "google_maps",
                    })
        except (csv.Error, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {csv_path}: {e}")

    if csv_files:
        print(f"Found {len(csv_files)} CSV file(s), parsed {len(venues)} venues from Google Takeout.")
    return venues


def _tags_to_section(tags: str) -> str:
    """Map Google Maps tags to a section name."""
    t = tags.lower()
    if "shopping" in t:
        return "Shopping"
    if "art" in t:
        return "Museums"
    if "site" in t:
        return "Destinations"
    if "food" in t or "restaurant" in t or "pub" in t:
        return "Food/Pubs"
    return "Google Maps List"


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def normalize_name(name: str) -> str:
    """Normalize a venue name for dedup comparison."""
    n = name.lower()
    n = re.sub(r"[''`]s?\b", "", n)  # strip possessives
    n = re.sub(r"[^a-z0-9\s]", "", n)  # strip punctuation
    n = re.sub(r"\s+", " ", n).strip()
    # Strip common trailing words that vary between sources
    n = re.sub(r"\s+(tours?|visit|tickets?|experience)$", "", n)
    # Common misspellings
    n = n.replace("cemetary", "cemetery")
    return n


def deduplicate_venues(venues: list) -> list:
    """Deduplicate venue list, preferring markdown source over google_maps."""
    seen = {}
    for v in venues:
        key = normalize_name(v["name"])
        if key in seen:
            existing = seen[key]
            if existing["source"] == "google_maps" and v["source"] == "markdown":
                # Prefer markdown entry
                v["source"] = "both"
                seen[key] = v
            elif existing["source"] == "markdown" and v["source"] == "google_maps":
                existing["source"] = "both"
        else:
            seen[key] = v
    return list(seen.values())


# ---------------------------------------------------------------------------
# Google Maps Places API
# ---------------------------------------------------------------------------

def fetch_place(venue_name: str, api_key: str) -> Optional[dict]:
    """Fetch place details from Google Maps Places API."""
    query = f"{venue_name} London"
    payload = json.dumps({
        "textQuery": query,
        "maxResultCount": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        PLACES_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  API error for '{venue_name}': {e.code} — {body[:200]}")
        return None
    except urllib.error.URLError as e:
        print(f"  Network error for '{venue_name}': {e}")
        return None

    places = data.get("places", [])
    if not places:
        print(f"  No results for '{venue_name}'")
        return None

    return places[0]


def format_hours(hours_data: Optional[dict]) -> str:
    """Format regularOpeningHours into a readable string."""
    if not hours_data:
        return "Hours not available"

    # Use weekdayDescriptions if available (human-readable)
    descriptions = hours_data.get("weekdayDescriptions", [])
    if descriptions:
        return " | ".join(descriptions)

    return "Hours not available"


def build_venue_record(name: str, source: str, section: str, api_result: Optional[dict]) -> dict:
    """Build a venue dict suitable for DB insertion."""
    now = datetime.utcnow().isoformat()

    if api_result is None:
        return {
            "name": name,
            "source": source,
            "section": section,
            "search_query": f"{name} London",
            "google_place_id": None,
            "google_display_name": None,
            "address": None,
            "regular_hours_json": None,
            "regular_hours_text": "Could not fetch",
            "google_maps_uri": None,
            "raw_response": None,
            "fetched_at": now,
        }

    hours_data = api_result.get("regularOpeningHours")
    return {
        "name": name,
        "source": source,
        "section": section,
        "search_query": f"{name} London",
        "google_place_id": api_result.get("id"),
        "google_display_name": api_result.get("displayName", {}).get("text"),
        "address": api_result.get("formattedAddress"),
        "regular_hours_json": json.dumps(hours_data) if hours_data else None,
        "regular_hours_text": format_hours(hours_data),
        "google_maps_uri": api_result.get("googleMapsUri"),
        "raw_response": json.dumps(api_result),
        "fetched_at": now,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_summary(conn: sqlite3.Connection):
    """Print a formatted summary of all cached venues grouped by section."""
    rows = conn.execute(
        "SELECT * FROM venues ORDER BY section, name"
    ).fetchall()

    if not rows:
        print("No venues in database.")
        return

    current_section = None
    for row in rows:
        if row["section"] != current_section:
            current_section = row["section"]
            print(f"\n{'=' * 60}")
            print(f"  {current_section}")
            print(f"{'=' * 60}")

        print(f"\n  {row['name']}")
        if row["google_display_name"] and row["google_display_name"] != row["name"]:
            print(f"    Google name: {row['google_display_name']}")
        if row["address"]:
            print(f"    Address: {row['address']}")
        if row["regular_hours_text"]:
            hours = row["regular_hours_text"]
            if " | " in hours:
                print("    Hours:")
                for day_hours in hours.split(" | "):
                    print(f"      {day_hours}")
            else:
                print(f"    Hours: {hours}")
        if row["google_maps_uri"]:
            print(f"    Maps: {row['google_maps_uri']}")
        print(f"    Source: {row['source']}")


def print_report(conn: sqlite3.Connection):
    """Print full research report: hours + booking + events per venue."""
    rows = conn.execute(
        "SELECT * FROM venues ORDER BY section, name"
    ).fetchall()

    if not rows:
        print("No venues in database.")
        return

    current_section = None
    for row in rows:
        if row["section"] != current_section:
            current_section = row["section"]
            print(f"\n{'=' * 60}")
            print(f"  {current_section}")
            print(f"{'=' * 60}")

        print(f"\n  {row['name']}")
        if row["google_display_name"] and row["google_display_name"] != row["name"]:
            print(f"    Google name: {row['google_display_name']}")
        if row["address"]:
            print(f"    Address: {row['address']}")

        # Hours
        if row["regular_hours_text"]:
            hours = row["regular_hours_text"]
            if " | " in hours:
                print("    Hours:")
                for day_hours in hours.split(" | "):
                    print(f"      {day_hours}")
            else:
                print(f"    Hours: {hours}")

        # Booking info
        has_booking = any([row["ticket_price"], row["booking_required"],
                          row["booking_url"], row["booking_notes"],
                          row["member_required"]])
        if has_booking:
            print("    --- Booking ---")
            if row["ticket_price"]:
                print(f"    Price: {row['ticket_price']}")
            if row["booking_required"]:
                print(f"    Booking required: {row['booking_required']}")
            if row["booking_url"]:
                print(f"    Book here: {row['booking_url']}")
            if row["member_required"]:
                print(f"    Membership: {row['member_required']}")
            if row["booking_notes"]:
                print(f"    Notes: {row['booking_notes']}")

        # Events at this venue
        events = conn.execute(
            "SELECT * FROM events WHERE venue_name = ? ORDER BY date, time",
            (row["name"],)
        ).fetchall()
        if events:
            print("    --- Events ---")
            for evt in events:
                parts = [f"    * {evt['title']}"]
                if evt["date"]:
                    parts.append(f"({evt['date']})")
                if evt["time"]:
                    parts.append(f"at {evt['time']}")
                if evt["price"]:
                    parts.append(f"- {evt['price']}")
                print(" ".join(parts))
                if evt["notes"]:
                    print(f"      {evt['notes']}")
                if evt["url"]:
                    print(f"      {evt['url']}")

        if row["google_maps_uri"]:
            print(f"    Maps: {row['google_maps_uri']}")

    # Events not tied to a specific venue
    general_events = conn.execute(
        "SELECT * FROM events WHERE venue_name IS NULL OR venue_name = '' ORDER BY date, time"
    ).fetchall()
    if general_events:
        print(f"\n{'=' * 60}")
        print(f"  General Events (not venue-specific)")
        print(f"{'=' * 60}")
        for evt in general_events:
            parts = [f"\n  * {evt['title']}"]
            if evt["date"]:
                parts.append(f"({evt['date']})")
            if evt["time"]:
                parts.append(f"at {evt['time']}")
            if evt["price"]:
                parts.append(f"- {evt['price']}")
            print(" ".join(parts))
            if evt["venue_name"]:
                print(f"    Venue: {evt['venue_name']}")
            if evt["notes"]:
                print(f"    {evt['notes']}")
            if evt["url"]:
                print(f"    {evt['url']}")


def print_events(conn: sqlite3.Connection):
    """Print all events, grouped by date."""
    events = conn.execute(
        "SELECT * FROM events ORDER BY date, time, venue_name"
    ).fetchall()

    if not events:
        print("No events in database.")
        return

    current_date = None
    for evt in events:
        if evt["date"] != current_date:
            current_date = evt["date"]
            print(f"\n--- {current_date or 'No date'} ---")

        parts = [f"  {evt['title']}"]
        if evt["venue_name"]:
            parts.append(f"@ {evt['venue_name']}")
        if evt["time"]:
            parts.append(f"at {evt['time']}")
        if evt["price"]:
            parts.append(f"({evt['price']})")
        print(" ".join(parts))
        if evt["category"]:
            print(f"    Category: {evt['category']}")
        if evt["notes"]:
            print(f"    {evt['notes']}")
        if evt["url"]:
            print(f"    {evt['url']}")


def dump_json(conn: sqlite3.Connection):
    """Dump all venue and event data as JSON."""
    venues = conn.execute("SELECT * FROM venues ORDER BY section, name").fetchall()
    events = conn.execute("SELECT * FROM events ORDER BY date, time").fetchall()
    data = {
        "venues": [dict(row) for row in venues],
        "events": [dict(row) for row in events],
    }
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="London venue research tool")

    # Basic commands
    parser.add_argument("--refetch", metavar="NAME", help="Re-fetch a specific venue by name")
    parser.add_argument("--dump", action="store_true", help="Dump all cached data as JSON")
    parser.add_argument("--parse-only", action="store_true", help="Show parsed venues without fetching")
    parser.add_argument("--report", action="store_true", help="Full research report (hours + booking + events)")
    parser.add_argument("--events", action="store_true", help="List all events by date")

    # Booking commands
    parser.add_argument("--set-booking", metavar="VENUE", help="Set booking info for a venue")
    parser.add_argument("--price", help="Ticket/meal price (used with --set-booking)")
    parser.add_argument("--booking-required", choices=["yes", "no", "recommended", "free"],
                        help="Whether booking is required")
    parser.add_argument("--booking-url", help="URL to book")
    parser.add_argument("--booking-notes", help="Free-form booking notes")
    parser.add_argument("--member-required", help="Membership requirement (e.g., 'no', 'soho house')")

    # Event commands
    parser.add_argument("--add-event", action="store_true", help="Add an event")
    parser.add_argument("--title", help="Event title (used with --add-event)")
    parser.add_argument("--venue", help="Venue name for event (used with --add-event)")
    parser.add_argument("--date", help="Event date YYYY-MM-DD (used with --add-event or --add-reservation)")
    parser.add_argument("--time", help="Event/reservation time (used with --add-event or --add-reservation)")
    parser.add_argument("--url", help="Event URL (used with --add-event)")
    parser.add_argument("--category", help="Event category (used with --add-event)")
    parser.add_argument("--notes", help="Event/reservation notes (used with --add-event or --add-reservation)")
    parser.add_argument("--source", help="Where this info came from (used with --add-event)")

    # Reservation commands
    parser.add_argument("--reservations", action="store_true", help="List all reservations")
    parser.add_argument("--import-reservations", metavar="CSV", help="Import reservations from CSV file")
    parser.add_argument("--add-reservation", metavar="VENUE", help="Add a reservation for a venue")
    parser.add_argument("--end-time", help="Reservation end time (used with --add-reservation)")
    parser.add_argument("--confirmation", help="Confirmation number (used with --add-reservation)")
    parser.add_argument("--party-size", type=int, help="Party size (used with --add-reservation)")

    # Paths
    parser.add_argument("--md", default=str(MD_PATH), help="Path to London.md")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to SQLite database")
    args = parser.parse_args()

    db_path = Path(args.db)
    md_path = Path(args.md)
    conn = init_db(db_path)

    # Handle --dump
    if args.dump:
        dump_json(conn)
        return

    # Handle --report
    if args.report:
        print_report(conn)
        return

    # Handle --events
    if args.events:
        print_events(conn)
        return

    # Handle --set-booking
    if args.set_booking:
        set_booking(conn, args.set_booking, args.price, args.booking_required,
                    args.booking_url, args.booking_notes, args.member_required)
        return

    # Handle --add-event
    if args.add_event:
        if not args.title:
            print("Error: --title is required with --add-event")
            sys.exit(1)
        add_event(conn, args.title, args.venue, args.date, args.time,
                  args.price, args.url, args.category, args.notes, args.source)
        return

    # Handle --reservations
    if args.reservations:
        print_reservations(conn)
        return

    # Handle --import-reservations
    if args.import_reservations:
        import_reservations_csv(conn, Path(args.import_reservations))
        return

    # Handle --add-reservation
    if args.add_reservation:
        if not args.date:
            print("Error: --date is required with --add-reservation")
            sys.exit(1)
        add_reservation(conn, args.add_reservation, args.date, args.time,
                        args.end_time, args.confirmation, args.party_size, args.notes)
        return

    # Handle --refetch
    if args.refetch:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            print("Error: Set GOOGLE_MAPS_API_KEY environment variable.")
            sys.exit(1)

        print(f"Re-fetching: {args.refetch}")
        result = fetch_place(args.refetch, api_key)
        # Look up existing record for source/section
        existing = conn.execute("SELECT source, section FROM venues WHERE name = ?",
                                (args.refetch,)).fetchone()
        source = existing["source"] if existing else "manual"
        section = existing["section"] if existing else "Unknown"

        record = build_venue_record(args.refetch, source, section, result)
        upsert_venue(conn, record)
        print("Done. Updated record:")
        print_summary(conn)
        return

    # Parse venues from both sources
    print(f"Parsing {md_path}...")
    md_venues = parse_markdown(md_path)
    print(f"  Found {len(md_venues)} venues in markdown.\n")

    csv_venues = parse_takeout_csvs(SCRIPT_DIR)
    all_venues = md_venues + csv_venues
    all_venues = deduplicate_venues(all_venues)
    print(f"\nTotal unique venues after dedup: {len(all_venues)}")

    # Handle --parse-only
    if args.parse_only:
        for v in all_venues:
            print(f"  [{v['section']}] {v['name']} (source: {v['source']})")
        return

    # Determine what needs fetching
    cached = get_cached_names(conn)
    to_fetch = [v for v in all_venues if v["name"] not in cached]

    if not to_fetch:
        print("All venues already cached. No API calls needed.")
        print_summary(conn)
        return

    # Fetch from API
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_MAPS_API_KEY environment variable.")
        print(f"  {len(to_fetch)} venues need fetching but no API key provided.")
        sys.exit(1)

    print(f"\nFetching {len(to_fetch)} new venue(s) from Google Maps Places API...\n")

    for v in to_fetch:
        print(f"  Fetching: {v['name']}...")
        result = fetch_place(v["name"], api_key)
        record = build_venue_record(v["name"], v["source"], v["section"], result)
        upsert_venue(conn, record)

    print(f"\nDone. {len(to_fetch)} venue(s) fetched and cached.\n")
    print_summary(conn)


if __name__ == "__main__":
    main()
