#!/usr/bin/env python3
"""
Quick web viewer for london_venues.db
Run: python3 web_viewer.py
Open: http://localhost:8080
"""

import html
import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DB_PATH = Path(__file__).parent / "london_venues.db"

STYLE = """
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
  h1 { color: #333; }
  h2 { color: #555; margin-top: 30px; }
  a { color: #0066cc; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .nav { background: #333; padding: 10px 20px; margin: -20px -20px 20px; }
  .nav a { color: white; margin-right: 20px; }
  table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f8f8f8; font-weight: 600; }
  tr:hover { background: #fafafa; }
  .card { background: white; padding: 20px; margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 4px; }
  .card h3 { margin-top: 0; }
  .label { font-weight: 600; color: #666; min-width: 150px; display: inline-block; }
  .field { margin: 8px 0; }
  .tag { display: inline-block; background: #e0e0e0; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }
  .tag.confirmed { background: #c8e6c9; color: #2e7d32; }
  .section { margin: 30px 0; }
  pre { background: #f0f0f0; padding: 10px; overflow-x: auto; font-size: 12px; }
</style>
"""

def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Ensure UTF-8 encoding
    conn.execute("PRAGMA encoding='UTF-8'")
    return conn

def escape(s):
    if s is None:
        return ""
    try:
        # Handle bytes that might be UTF-8 encoded
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return html.escape(str(s), quote=True)
    except Exception as e:
        return html.escape(repr(s), quote=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/" or path == "/venues":
            content = self.list_venues()
        elif path == "/venue":
            venue_id = params.get("id", [None])[0]
            content = self.show_venue(venue_id)
        elif path == "/events":
            content = self.list_events()
        elif path == "/event":
            event_id = params.get("id", [None])[0]
            content = self.show_event(event_id)
        elif path == "/reservations":
            content = self.list_reservations()
        else:
            content = "<h1>404 Not Found</h1>"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>London Trip DB</title>
{STYLE}
</head>
<body>
<div class="nav">
    <a href="/venues">Venues</a>
    <a href="/events">Events</a>
    <a href="/reservations">Reservations</a>
</div>
{content}
</body>
</html>"""
        self.send_header("charset", "utf-8")
        self.wfile.write(page.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Suppress logging

    def list_venues(self):
        conn = get_db()
        rows = conn.execute("SELECT id, name, section, address, booking_required FROM venues ORDER BY section, name").fetchall()
        conn.close()

        html_rows = ""
        for r in rows:
            html_rows += f"""<tr>
                <td><a href="/venue?id={r['id']}">{escape(r['name'])}</a></td>
                <td>{escape(r['section'])}</td>
                <td>{escape(r['address'] or '')[:50]}</td>
                <td>{escape(r['booking_required'] or '')}</td>
            </tr>"""

        return f"""
        <h1>Venues ({len(rows)})</h1>
        <table>
            <tr><th>Name</th><th>Section</th><th>Address</th><th>Booking</th></tr>
            {html_rows}
        </table>
        """

    def show_venue(self, venue_id):
        if not venue_id:
            return "<p>No venue ID</p>"

        conn = get_db()
        row = conn.execute("SELECT * FROM venues WHERE id = ?", (venue_id,)).fetchone()
        events = conn.execute("SELECT * FROM events WHERE venue_name = ?", (row['name'] if row else '',)).fetchall()
        reservations = conn.execute("SELECT * FROM reservations WHERE matched_venue = ? OR venue_name = ?",
                                    (row['name'] if row else '', row['name'] if row else '')).fetchall()
        conn.close()

        if not row:
            return "<p>Venue not found</p>"

        fields = [
            ("Name", row['name']),
            ("Section", row['section']),
            ("Source", row['source']),
            ("Address", row['address']),
            ("Hours", row['regular_hours_text']),
            ("Google Maps", f"<a href='{row['google_maps_uri']}' target='_blank'>Open in Maps</a>" if row['google_maps_uri'] else None),
            ("", ""),  # spacer
            ("Price", row['ticket_price']),
            ("Booking Required", row['booking_required']),
            ("Booking URL", f"<a href='{row['booking_url']}' target='_blank'>{row['booking_url']}</a>" if row['booking_url'] else None),
            ("Booking Notes", row['booking_notes']),
            ("Membership", row['member_required']),
        ]

        fields_html = ""
        for label, value in fields:
            if label == "" and value == "":
                fields_html += "<hr style='margin: 15px 0; border: none; border-top: 1px solid #eee;'>"
            elif value:
                fields_html += f"<div class='field'><span class='label'>{label}:</span> {value if '<a' in str(value) else escape(value)}</div>"

        events_html = ""
        if events:
            events_html = "<h3>Events at this venue</h3><ul>"
            for e in events:
                events_html += f"<li><a href='/event?id={e['id']}'>{escape(e['title'])}</a> ({escape(e['date'] or 'ongoing')})</li>"
            events_html += "</ul>"

        res_html = ""
        if reservations:
            res_html = "<h3>Reservations</h3>"
            for r in reservations:
                res_html += f"<div class='tag confirmed'>CONFIRMED: {escape(r['date'])} {escape(r['time'] or '')} - {escape(r['confirmation'] or 'no conf#')}</div>"

        return f"""
        <h1>{escape(row['name'])}</h1>
        {res_html}
        <div class="card">
            {fields_html}
        </div>
        {events_html}
        <p><a href="/venues">&larr; Back to venues</a></p>
        """

    def list_events(self):
        conn = get_db()
        rows = conn.execute("SELECT id, title, venue_name, date, time, category FROM events ORDER BY date, time").fetchall()
        conn.close()

        html_rows = ""
        for r in rows:
            html_rows += f"""<tr>
                <td><a href="/event?id={r['id']}">{escape(r['title'])}</a></td>
                <td>{escape(r['venue_name'] or '')}</td>
                <td>{escape(r['date'] or '')}</td>
                <td>{escape(r['time'] or '')}</td>
                <td>{escape(r['category'] or '')}</td>
            </tr>"""

        return f"""
        <h1>Events ({len(rows)})</h1>
        <table>
            <tr><th>Title</th><th>Venue</th><th>Date</th><th>Time</th><th>Category</th></tr>
            {html_rows}
        </table>
        """

    def show_event(self, event_id):
        if not event_id:
            return "<p>No event ID</p>"

        conn = get_db()
        row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        conn.close()

        if not row:
            return "<p>Event not found</p>"

        fields = [
            ("Title", row['title']),
            ("Venue", row['venue_name']),
            ("Date", row['date']),
            ("Time", row['time']),
            ("Price", row['price']),
            ("Category", row['category']),
            ("Notes", row['notes']),
            ("URL", f"<a href='{row['url']}' target='_blank'>{row['url']}</a>" if row['url'] else None),
            ("Source", row['source']),
        ]

        fields_html = ""
        for label, value in fields:
            if value:
                fields_html += f"<div class='field'><span class='label'>{label}:</span> {value if '<a' in str(value) else escape(value)}</div>"

        return f"""
        <h1>{escape(row['title'])}</h1>
        <div class="card">
            {fields_html}
        </div>
        <p><a href="/events">&larr; Back to events</a></p>
        """

    def list_reservations(self):
        conn = get_db()
        rows = conn.execute("SELECT * FROM reservations ORDER BY date, time").fetchall()
        conn.close()

        html_rows = ""
        for r in rows:
            html_rows += f"""<tr>
                <td>{escape(r['venue_name'])}</td>
                <td>{escape(r['date'])}</td>
                <td>{escape(r['time'] or '')} - {escape(r['end_time'] or '')}</td>
                <td><code>{escape(r['confirmation'] or '')}</code></td>
                <td>{escape(r['party_size'] or '')}</td>
                <td>{escape(r['notes'] or '')}</td>
            </tr>"""

        return f"""
        <h1>Reservations ({len(rows)})</h1>
        <table>
            <tr><th>Venue</th><th>Date</th><th>Time</th><th>Confirmation</th><th>Party</th><th>Notes</th></tr>
            {html_rows}
        </table>
        """

if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("localhost", port), Handler)
    print(f"Server running at http://localhost:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
