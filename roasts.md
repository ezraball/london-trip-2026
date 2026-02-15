# Sunday Roast Research Session - Feb 15, 2026

## Context
- User wanted Sunday roast recommendations for TODAY (Feb 15)
- Doing East London itinerary: God's Own Junkyard (Walthamstow) → Viktor Wynd Museum (Hackney)
- Wanted to reverse engineer the rdldn.co.uk map to get full venue list (363 restaurants)

## Research Path & Blocks

### ✅ What Worked

1. **League of Roasts JSON-LD Data**
   - Successfully extracted top 20 rated venues from https://www.rdldn.co.uk/league-of-roasts/
   - Found structured JSON-LD data in `<script type="application/ld+json">` tag
   - Top venues relevant to itinerary:
     - #1: Blacklock, Shoreditch (9.29)
     - #2: Madame Pigg, Dalston (9.14) - perfect for today!
     - #18: The Raglan, Walthamstow

2. **Web Search for Area-Specific Recommendations**
   - Searched for Hackney/Dalston, Camden, South Kensington Sunday roasts
   - Got detailed recommendations with prices, addresses, hours:
     - Jones & Sons, Dalston (3 Gillett Street, N16 8JH) - £18-22
     - The Nelson's, Hackney (32 Horatio Street, E2 7SB) - 12-6pm
     - Barge East, Hackney Wick
     - The Marksman, Hackney Road (Michelin pub, £40)

3. **WebArchive Extraction**
   - User saved https://www.rdldn.co.uk/maps as ~/Downloads/RoastMaps.webarchive (3.9MB)
   - Converted to XML: `plutil -convert xml1 -o /tmp/roastmaps.xml`
   - Extracted base64-encoded HTML: 124KB main document
   - Found 86 data elements total

### ❌ Where I Got Blocked

**The Map Data Problem:**

The rdldn.co.uk/maps page uses **modern JavaScript framework (Astro)** that loads data asynchronously:

1. **Initial HTML has no venue data**
   - WebArchive captured the page shell/framework code
   - No embedded JSON with restaurant coordinates
   - No inline markers array

2. **Data loaded via JavaScript after page render**
   - Map likely fetches from API endpoint like `/api/restaurants.json`
   - JavaScript makes async request: `fetch('/api/restaurants.json').then(data => renderMap(data))`
   - WebArchive can't capture JavaScript-executed network requests

3. **Attempts that failed:**
   - Searched for `lat`/`lng` coordinates: None in HTML
   - Looked for `markers` arrays: None
   - Searched for iframes (Google My Maps embed): None
   - Looked for Google Maps API URLs: None in source
   - Tried to find external JS files (`/_astro/page.DogxaioH.js`): Not captured in archive
   - Searched for JSON data structures: Only found framework code

4. **What the archive contained:**
   - Astro framework JavaScript (hydration, component loading)
   - Partytown library code (for web workers)
   - CSS stylesheets
   - Page structure with `<astro-island>` components
   - BUT: No actual restaurant/map data

**Why This Happened:**

Safari's WebArchive captures the **initial page state** when you hit Save. But modern SPAs/frameworks:
- Render minimal HTML shell first
- Execute JavaScript to fetch data
- Update DOM with fetched content

The map data loads in step 2-3, which happens AFTER the webarchive snapshot.

**What Would Work:**

1. **Headless browser with network capture**
   ```bash
   # Puppeteer/Selenium script to:
   # - Load page and wait for map to render
   # - Intercept network requests
   # - Capture the API response
   ```

2. **Find the API endpoint directly**
   - Check browser DevTools Network tab
   - Look for `/api/` or `.json` requests
   - Call endpoint directly

3. **Use the data we already have**
   - Top 20 from League of Roasts (structured data)
   - Area-specific recommendations from web search
   - Focus on venues near the itinerary

## Recommendations for Today (Sunday Feb 15)

### Best Options:

**Between God's Own Junkyard (Walthamstow) and Viktor Wynd (Hackney):**

1. **Madame Pigg, Dalston** ⭐ #2 on League (9.14/10)
   - Perfect location between Walthamstow & Hackney
   - Featured in North London best roasts

2. **Jones & Sons, Dalston**
   - 3 Gillett Street, N16 8JH
   - Hidden courtyard, huge Yorkshire puddings
   - Veggie £18, meat from £22

3. **The Nelson's, Hackney**
   - 32 Horatio Street, E2 7SB (near Viktor Wynd at 11 Mare St)
   - Beef rump, pork belly, lamb shoulder, fried chicken
   - Sundays 12-6pm

4. **The Raglan, Walthamstow** - #18 on League
   - Right in Walthamstow near God's Own Junkyard

**Timing Recommendation:**
- 1-2pm lunch at Jones & Sons or Madame Pigg in Dalston
- Perfect between God's Own Junkyard (close 6pm) and Viktor Wynd (2:30pm entry)

**Alternative:**
- Keep The Troubadour Jazz Sunday (7:30pm, near hotel in South Ken) for dinner

## Sources
- [London's 24 Best Sunday Lunch Roasts [Updated February 2026]](https://www.timeout.com/london/food-and-drink/londons-best-sunday-lunches)
- [The 15 Best Sunday Roasts In London](https://www.theinfatuation.com/london/guides/best-sunday-roasts-london)
- [Best Sunday Roast in Camden: Top 5 Places](https://www.hometainment.com/uk/blog/best-sunday-roast-in-camden)
- [5 Best Sunday Roasts in Hackney](https://www.culturecalling.com/london/food-and-drink/features/5-best-sunday-roasts-in-hackney)
- [The Best Sunday Roasts in Kensington](https://www.silverdoor.com/blog/the-best-sunday-roasts-in-kensington-our-top-5-places-)
- [Roast Dinners In London - League of Roasts](https://www.rdldn.co.uk/league-of-roasts/)

## Technical Notes

### Commands Used:
```bash
# Convert webarchive to XML
plutil -convert xml1 ~/Downloads/RoastMaps.webarchive -o /tmp/roastmaps.xml

# Extract base64-encoded HTML from XML
python3 << 'EOF'
import xml.etree.ElementTree as ET
import base64

tree = ET.parse('/tmp/roastmaps.xml')
root = tree.getroot()
data_elements = root.findall('.//data')

for idx, data_elem in enumerate(data_elements):
    if data_elem.text and len(data_elem.text) > 100:
        decoded = base64.b64decode(data_elem.text).decode('utf-8', errors='ignore')
        if 'marker' in decoded.lower() or 'restaurant' in decoded.lower():
            with open(f'/tmp/decoded_{idx}.html', 'w') as f:
                f.write(decoded)
EOF

# Search for map data
grep -i 'marker\|latitude\|longitude' /tmp/decoded_0.html
grep -o '"lat":[^,]*,"lng":[^,]*' /tmp/decoded_0.html
```

### File Locations:
- WebArchive: `~/Downloads/RoastMaps.webarchive`
- XML version: `/tmp/roastmaps.xml`
- Decoded HTML: `/tmp/decoded_0.html`
- League data: Extracted from rdldn.co.uk/league-of-roasts/
