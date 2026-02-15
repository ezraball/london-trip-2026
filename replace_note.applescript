-- Completely REPLACES the content of an existing note
tell application "Notes"
	activate

	set noteContent to "<html><head><style>
body { font-family: -apple-system, SF Pro Text; font-size: 15px; line-height: 1.6; color: #333; }
h1 { font-size: 22px; font-weight: 600; margin: 0 0 20px 0; color: #000; }
h2 { font-size: 18px; font-weight: 600; margin: 24px 0 12px 0; color: #007AFF; border-bottom: 2px solid #007AFF; padding-bottom: 4px; }
h3 { font-size: 16px; font-weight: 600; margin: 12px 0 6px 0; color: #5856D6; }
.time { font-weight: 600; color: #FF9500; }
.confirmed { background: #34C759; color: white; padding: 2px 6px; border-radius: 3px; font-size: 13px; font-weight: 600; }
.venue { font-weight: 600; color: #000; }
.theme { font-style: italic; color: #666; margin-bottom: 12px; }
.details { color: #666; margin-left: 20px; font-size: 14px; line-height: 1.5; }
.note { background: #F2F2F7; padding: 10px; border-radius: 6px; margin: 10px 0; font-size: 14px; }
ul { margin: 6px 0; padding-left: 20px; }
li { margin: 3px 0; }
.restaurant { background: #F9F9F9; padding: 10px; border-radius: 6px; margin: 10px 0; border-left: 3px solid #ddd; }
.top-pick { border-left-color: #FF9500; }
</style></head><body>

<h1>London Trip Schedule</h1>

<h2>Friday Feb 13 — Arrival Night</h2>
<p class='theme'>Arrive late evening. Settle into hotel (South Kensington).</p>

<div class='note'>
<strong>If arriving by 6pm:</strong><br>
• Saatchi Lates: The Long Now (6:30-9pm, Chelsea, from £10)<br>
• Or: Lost Souls Pizza Friday the 13th Special (Camden, £13 pizzas + 2-for-£13 cocktails)<br><br>
<strong>If arriving later:</strong> Rest up, jet lag recovery, grab food near hotel.
</div>

<h2>Saturday Feb 14 — Valentine's Day: North London Adventure</h2>
<p class='theme'>Gothic cemetery, punk markets, vampire pizza, then Valentine's dinner.</p>

<p><span class='time'>10:00</span> — <span class='venue'>Highgate Cemetery</span><br>
<span class='details'>£10 combined East+West, timed entry (book at highgatecemetery.org)<br>Winter hours 10am-4pm, last entry 3:30pm. Card only. Allow 1.5-2 hours.</span></p>

<p><span class='time'>12:00</span> — Tube to Camden Town (Northern line, ~15min)</p>

<p><span class='time'>12:30</span> — <span class='venue'>Abbey Road Studios</span> (optional)<br>
<span class='details'>St John's Wood tube (Jubilee line from Baker Street). ~30min round trip for photo at crossing.</span></p>

<p><span class='time'>13:00</span> — <span class='venue'>Lost Souls Pizza</span> (lunch)<br>
<span class='details'>Vampire-themed. Valentine's special? Book via TheFork if possible.</span></p>

<p><span class='time'>14:30</span> — <span class='venue'>Camden Market</span><br>
<span class='details'>Free. Explore stalls, street food, vintage. Saturday = busier but good energy.</span></p>

<p><span class='time'>16:30</span> — Return to South Kensington<br>
<span class='details'>Allow time to freshen up for dinner.</span></p>

<p><span class='time'>19:15</span> — <span class='venue'>La Terrazza Kensington</span> <span class='confirmed'>✓ CONFIRMED</span><br>
<span class='details'>Conf: 24901 • Table for 2, name: Ezra Ball</span></p>

<h2>Sunday Feb 15 — East London + Sunday Roast</h2>
<p class='theme'>Neon art, curiosities, Sunday roast, and jazz. The \"weird &amp; wonderful\" day.</p>

<p><span class='time'>10:30</span> — Head to Walthamstow (Victoria line, ~30min)</p>

<p><span class='time'>11:00</span> — <span class='venue'>God's Own Junkyard</span><br>
<span class='details'>Free entry. Rolling Scones Cafe for brunch. Phone photos only (no DSLRs). Closes 6pm Sun.</span></p>

<p><span class='time'>13:00</span> — Head to Dalston (~15min by Overground from Walthamstow Central)</p>

<p><span class='time'>13:30</span> — <span class='venue'>Sunday Roast: Madame Pigg or Jones &amp; Sons, Dalston</span><br>
<span class='details'><strong>Madame Pigg</strong> (#2 on League of Roasts, 9.14/10) OR <strong>Jones &amp; Sons</strong> (3 Gillett St, N16 8JH, veggie £18, meat £22+, hidden courtyard, huge Yorkshires). Both perfect between Walthamstow &amp; Hackney.</span></p>

<p><span class='time'>14:30</span> — Walk to <span class='venue'>Viktor Wynd Museum</span> (~10min walk to 11 Mare St, E8 4RP)<br>
<span class='details'>£12 (opens noon Sun). Dark Fairy Tales exhibition. Absinthe Parlour bar (free entry to bar).</span></p>

<p><span class='time'>17:00</span> — Head back west</p>

<p><span class='time'>19:30</span> — <span class='venue'>The Troubadour — Jazz Sunday</span><br>
<span class='details'>Live jazz, dinner + drinks. Old Brompton Rd (near hotel). Romantic evening.</span></p>

<div class='note'>
<strong>Sunday Roast Alternatives:</strong><br>
• The Raglan, Walthamstow (#18 on League) - if eating earlier<br>
• The Nelson's, Hackney (32 Horatio St, E2 7SB) - near Viktor Wynd, 12-6pm<br><br>
<strong>Backup if weather is bad:</strong> Skip Walthamstow, do V&amp;A instead (free, near hotel). Viktor Wynd can move to Thursday (£4 walk-in!).
</div>

<h2>Monday Feb 16 — Southbank + Soho</h2>
<p class='theme'>Modern art, street art, vinyl shopping, Soho dining. Borough Market is closed Monday.</p>

<p><span class='time'>10:00</span> — <span class='venue'>Tate Modern</span><br>
<span class='details'>Free. Theatre Picasso, Nigerian Modernism, Turbine Hall commission.</span></p>

<p><span class='time'>12:30</span> — Walk along South Bank toward Waterloo</p>

<p><span class='time'>13:00</span> — <span class='venue'>Leake Street Graffiti Tunnel</span><br>
<span class='details'>Free, open 24/7. Quick stop for photos. Near Waterloo.</span></p>

<p><span class='time'>13:30</span> — Lunch on South Bank or head to Soho</p>

<p><span class='time'>14:30</span> — <span class='venue'>Soho circuit</span><br>
<span class='details'>Outernet London (free screens) → Sister Ray (vinyl, Berwick St) → Dr. Martens (Oxford Circus)<br>All walkable within Soho/West End.</span></p>

<p><span class='time'>18:00</span> — Dinner: <span class='venue'>Ducksoup</span> (Dean St) or <span class='venue'>Kettner's</span> (Romilly St)<br>
<span class='details'>Ducksoup: natural wine + small plates. Kettner's: French bistro + champagne bar.</span></p>

<div class='note'>
<strong>Optional add-ons:</strong><br>
• SEA LIFE London Aquarium (1:30pm slot after Graffiti Tunnel, from £23)<br>
• The National Gallery (free, Trafalgar Square, on route to Soho)<br>
• Churchill War Rooms (£33, £25 after 3:30pm, 15min from Waterloo)
</div>

<h2>Tuesday Feb 17 — The City (Meesh's Birthday!)</h2>
<p class='theme'>Brutalist architecture, history, panoramic views. The \"iconic London\" day.</p>

<p><span class='time'>09:00</span> — <span class='venue'>Breakfast: Barbie Green</span><br>
<span class='details'>Australian brunch spot at London Wall Place (5min from Barbican). Opens 7am weekdays. Banana bread sandwich, shakshuka, good coffee. No booking needed.</span></p>

<p><span class='time'>10:00</span> — <span class='venue'>Walk the Barbican Centre</span><br>
<span class='details'>Free. Explore Brutalist terraces, lakeside, highwalks. The Curve gallery opens at 11am if time allows.</span></p>

<p><span class='time'>11:30</span> — <span class='venue'>Tower of London</span> <span class='confirmed'>✓ CONFIRMED</span><br>
<span class='details'>Conf: DVOTK7G16KVZY • ~20min walk from Barbican. Yeoman Warder tour every 30min. Crown Jewels, White Tower. Allow 2.5 hours.</span></p>

<p><span class='time'>14:00</span> — Walk to <span class='venue'>Sky Garden</span> (~15min along river)<br>
<span class='details'>Free. Book timed entry at tickets.skygarden.london. Panoramic views, gardens.</span></p>

<p><span class='time'>15:00</span> — Free afternoon — explore the City<br>
<span class='details'>Tower Bridge glass walkway (£12.30), St Paul's exterior, or just wander.</span></p>

<p><span class='time'>19:15</span> — <span class='venue'>Duck &amp; Waffle dinner</span> <span class='confirmed'>✓ CONFIRMED</span><br>
<span class='details'>Conf: CXSNF933JR88 • 40th floor, smart casual.</span></p>

<h2>Wednesday Feb 18 — Covent Garden &amp; Niece's Birthday</h2>
<p class='theme'>Royal Ballet School area, theatre district, special birthday celebration.</p>

<p><span class='time'>Morning</span> — Meet niece near <span class='venue'>Royal Ballet School</span><br>
<span class='details'>Upper School, Floral St, right in Covent Garden!</span></p>

<p><span class='time'>11:00</span> — <span class='venue'>Covent Garden Market</span><br>
<span class='details'>Free. Beautiful historic market building, street performers, shops. Very theatrical atmosphere.</span></p>

<p><span class='time'>12:00</span> — <span class='venue'>Royal Opera House tour</span> (optional)<br>
<span class='details'>£15, ~1 hour. Perfect for a ballet student! Book ahead at roh.org.uk.<br>OR Somerset House (free courtyard, exhibitions).</span></p>

<p><span class='time'>13:00</span> — Casual lunch<br>
<span class='details'>Dishoom Covent Garden (Indian) • Petersham Nurseries (botanical cafe) • Market hall options.</span></p>

<p><span class='time'>Afternoon</span> — <span class='venue'>National Portrait Gallery</span> (free, 10 min walk)<br>
<span class='details'>Lucian Freud exhibition. OR London Transport Museum (£20.50).</span></p>

<p><span class='time'>15:00</span> — Explore theatre district / shopping<br>
<span class='details'>Seven Dials, Neal's Yard (colorful courtyard), vintage shops.</span></p>

<p><span class='time'>Evening</span> — <span class='venue'>Special Birthday Dinner</span></p>

<h3>Birthday Dinner Recommendations</h3>

<div class='restaurant top-pick'>
<strong>⭐ Top Pick: Clos Maggiore</strong> (33 King St, WC2E 8JD)<br>
London's most romantic restaurant. Conservatory with fairy lights &amp; cherry blossoms.<br>
French cuisine, mains ~£30-40. Book: 020 7379 9696 or OpenTable.
</div>

<div class='restaurant'>
<strong>Rules Restaurant</strong> (35 Maiden Ln, WC2E 7LB)<br>
London's oldest restaurant (est. 1798). Edwardian glamour, theatrical history. Traditional British.<br>
Mains ~£25-35. Book: 020 7836 5314 or rules.co.uk.
</div>

<div class='restaurant'>
<strong>Spring at Somerset House</strong> (Somerset House, Lancaster Pl, WC2R 1LA)<br>
Beautiful skylit atrium, seasonal British cuisine.<br>
Set lunch £29, mains ~£30. Book: springrestaurant.co.uk or 020 3011 0115.
</div>

<div class='restaurant'>
<strong>Dishoom Covent Garden</strong> (12 Upper St Martin's Ln, WC2H 9FB)<br>
Theatrical Indian, house black daal, chai. ~£25pp. Walk-ins or book ahead.
</div>

<h2>Thursday Feb 19 — Museums + London Fashion Week</h2>
<p class='theme'>World-class museums and fashion week atmosphere.</p>

<p><span class='time'>10:00</span> — <span class='venue'>British Museum</span><br>
<span class='details'>Free general, timed entry recommended. Samurai (£23, Room 30) — 280 objects. Hawai'i (£16, Room 35) — feathered cloaks. Allow 3 hours.</span></p>

<p><span class='time'>13:00</span> — Tube to London Bridge (~15min)</p>

<p><span class='time'>13:30</span> — <span class='venue'>Borough Market — street food lunch</span><br>
<span class='details'>Open Thu 10am-5pm. Graze the stalls: Kappacasein raclette, Bread Ahead doughnuts, Padella (fresh pasta), Ethiopian/Turkish/Thai street food.</span></p>

<p><span class='time'>15:00</span> — Tube to South Kensington (~20min)</p>

<p><span class='time'>15:30</span> — <span class='venue'>Natural History Museum</span><br>
<span class='details'>Free general. Space: Could Life Exist Beyond Earth? (£14) — closes Feb 22, last chance! Wildlife Photographer (£15.50). Attenborough (£20). Family Festival (free).</span></p>

<p><span class='time'>17:00</span> — London Fashion Week atmosphere<br>
<span class='details'>Day 1 of LFW. Check BFC City Wide Celebration for public events: designer pop-ups, panel discussions. Shows at 180 Strand (invite-only).</span></p>

<p><span class='time'>Evening</span> — Final big dinner (Kettner's, or revisit a favorite)</p>

<h2>Friday Feb 20 — Departure Day</h2>
<p class='theme'>Quick hit near hotel before heading to airport.</p>

<p><span class='time'>10:00</span> — <span class='venue'>V&amp;A Museum</span><br>
<span class='details'>Free, opens 10am, right next to hotel in South Ken. Hit the highlights: Fashion galleries, Jewellery, Medieval &amp; Renaissance, Cast Courts.</span></p>

<p><span class='time'>12:00</span> — Pack up, check out</p>

<p><span class='time'>Early PM</span> — Head to airport</p>

<h2>Advance Booking Checklist</h2>

<div class='note'>
<strong>Confirmed:</strong><br>
✓ La Terrazza Valentine's dinner (Sat Feb 14, 19:15) — Conf: 24901<br>
✓ Tower of London (Tue Feb 17, 11:30) — Conf: DVOTK7G16KVZY<br>
✓ Duck &amp; Waffle (Tue Feb 17, 19:15) — Conf: CXSNF933JR88<br><br>

<strong>Still need to book:</strong><br>
• Highgate Cemetery (Sat Feb 14) — timed entry at highgatecemetery.org<br>
• Sky Garden free tickets (Tue Feb 17) — tickets.skygarden.london<br>
• British Museum timed entry (Thu Feb 19) — britishmuseum.org<br>
• Birthday dinner (Wed Feb 18) — Clos Maggiore, Rules, or Spring<br>
• Ducksoup or Kettner's (Mon Feb 16) — OpenTable<br>
• Viktor Wynd Museum (Sun Feb 15) — eventbrite.co.uk, £12<br>
• Optional: NHM exhibitions, British Museum Samurai
</div>

</body></html>"

	try
		-- Note name: "London Trip Research & Schedule Plan (Claude output)"
		set noteName to "London Trip Research & Schedule Plan (Claude output)"
		set foundNote to false

		repeat with acc in accounts
			repeat with fld in folders of acc
				try
					set targetNote to note noteName of fld
					set body of targetNote to noteContent
					set foundNote to true
					exit repeat
				end try
			end repeat
			if foundNote then exit repeat
		end repeat

		if foundNote then
			display dialog "✓ Note 'London Trip Research & Schedule Plan (Claude output)' has been updated" buttons {"OK"} default button "OK"
		else
			error "Note not found"
		end if
	on error errMsg
		display dialog "❌ Error: Could not find note 'London Trip Research & Schedule Plan (Claude output)'.

Make sure:
1. The note exists in iCloud Notes
2. The note name matches exactly (case-sensitive)

Error: " & errMsg buttons {"OK"} default button "OK" with icon stop
	end try
end tell
