-- Appends to an EXISTING note (change "London" to match your note name)
tell application "Notes"
	activate

	set noteContent to "

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UPDATED SCHEDULE - " & (current date) as string & "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 SATURDAY FEB 14 (TODAY) - North London + Valentine's Dinner

10:00 - Highgate Cemetery (£10, book online)
12:00 - Camden Town
12:30 - Abbey Road (optional)
13:00 - Lost Souls Pizza
14:30 - Camden Market
16:30 - Return to South Ken
19:15 - La Terrazza Kensington ✓ CONFIRMED (Conf: 24901)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 WEDNESDAY FEB 18 - Covent Garden & Niece's Birthday

Morning - Royal Ballet School area
11:00 - Covent Garden Market
12:00 - Royal Opera House tour (£15) OR Somerset House
13:00 - Casual lunch (Dishoom/Petersham/market)
Afternoon - National Portrait Gallery OR Transport Museum
15:00 - Theatre district shopping
Evening - BIRTHDAY DINNER

🍽️ Birthday Dinner Options:
⭐ Clos Maggiore (020 7379 9696) - fairy lights & cherry blossoms
🏛️ Rules (020 7836 5314) - historic, Edwardian
🌿 Spring at Somerset House (020 3011 0115) - skylit atrium
🍛 Dishoom (casual Indian)
"

	try
		-- Change "London" to match your existing note name
		tell account "iCloud"
			set targetNote to note "London" of folder "Notes"
			set body of targetNote to (body of targetNote) & noteContent
		end tell
		display dialog "✓ Updated note: 'London'" buttons {"OK"} default button "OK"
	on error errMsg
		display dialog "❌ Error: Could not find note 'London'.

Error: " & errMsg buttons {"OK"} default button "OK" with icon stop
	end try
end tell
