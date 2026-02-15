-- Creates a NEW note with the updated schedule
tell application "Notes"
	activate

	set noteContent to "UPDATED LONDON SCHEDULE

📅 SATURDAY FEB 14 (TODAY) - North London + Valentine's Dinner

10:00 - Highgate Cemetery
        £10 combined East+West, timed entry
        Book: highgatecemetery.org

12:00 - Tube to Camden Town (Northern line)

12:30 - Abbey Road Studios (optional detour)
        St John's Wood tube, photo at the crossing

13:00 - Lost Souls Pizza (lunch)
        Vampire-themed, Valentine's specials?

14:30 - Camden Market
        Street food, vintage stalls

16:30 - Return to South Kensington
        Freshen up for dinner

19:15 - La Terrazza Kensington ✓ CONFIRMED
        Conf: 24901
        Table for 2, name: Ezra Ball

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 WEDNESDAY FEB 18 - Covent Garden & Niece's Birthday

Morning - Meet niece at Royal Ballet School
          Upper School, Floral St, Covent Garden

11:00 - Covent Garden Market
        Street performers, shops, historic building

12:00 - Royal Opera House tour (optional)
        £15, 1 hour, book at roh.org.uk
        OR Somerset House (free courtyard)

13:00 - Casual lunch
        • Dishoom Covent Garden (Indian)
        • Petersham Nurseries (botanical cafe)
        • Market hall options

Afternoon - National Portrait Gallery (free)
            Lucian Freud exhibition
            OR London Transport Museum (£20.50)

15:00 - Theatre district shopping
        Seven Dials, Neal's Yard, vintage shops

Evening - SPECIAL BIRTHDAY DINNER

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🍽️ BIRTHDAY DINNER OPTIONS (book ASAP!)

⭐ TOP PICK: Clos Maggiore
   33 King St, WC2E 8JD
   • London's most romantic restaurant
   • Conservatory with fairy lights & cherry blossoms
   • French cuisine, mains ~£30-40
   • Book: 020 7379 9696 or OpenTable

🏛️ Rules Restaurant
   35 Maiden Ln, WC2E 7LB
   • London's oldest restaurant (est. 1798)
   • Edwardian glamour, theatrical history
   • Traditional British, mains ~£25-35
   • Book: 020 7836 5314 or rules.co.uk

🌿 Spring at Somerset House
   Somerset House, Lancaster Pl, WC2R 1LA
   • Beautiful skylit atrium
   • Seasonal British, set lunch £29
   • Book: springrestaurant.co.uk or 020 3011 0115

🍛 Dishoom Covent Garden (casual)
   12 Upper St Martin's Ln, WC2H 9FB
   • Theatrical Indian, ~£25pp
   • Walk-ins or book ahead"

	-- Create new note in default account
	tell account "iCloud"
		make new note at folder "Notes" with properties {name:"London Trip - Updated Schedule", body:noteContent}
	end tell

	display dialog "✓ New note created: 'London Trip - Updated Schedule'" buttons {"OK"} default button "OK"
end tell
