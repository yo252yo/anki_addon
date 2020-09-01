# anki_addon
Anki add on to transform lists of words into cards.

Sorry it's not in the most shareable state, but you can tweak it to your likings. 

My setup takes as input two text files: "in_review.txt" and "in_new.txt" which contain list of words that I notice I don't know well (review for the ones I want bumped up, new is for the ones I really don't know).

It makes cards with them talking to jisho.org, and imports them into my decks (importer.py) or reschedules them if they already exist. At the same time, it outputs a bunch of stats for my own monitoring.

It also depends on a file that contains the list of kanjis I know, so that I can distinguish between words I'm supposed to know how to read or not. 

Let me know if you have an idea about how to make it more generic/shareable, or if you need things like cards models...
