"""Canonical story copy and illustration metadata for Tyson's seventh adventure."""

STORY = {
    "slug": "the-tooth-that-took-a-bounce",
    "title": "Tyson and the Tooth That Took a Bounce",
    "accent": "Tooth That Took a Bounce",
    "icon": "🦷",
    "badge": "🦷 A First Loose Tooth Adventure",
    "subtitle": "A stubborn tooth, a trampoline, and a little note full of hope.",
    "preview": "His tooth bounced away. Could a note save the day?",
    "menu_blurb": "Loose tooth • a bounce and a wish",
    "theme_meta": "✨ Family & Tooth Fairy Magic",
    "chant": "Wiggle, wobble, bounce away! A little note can save the day!",
    "chant_scene": 4,
    "footer_theme": "A Rhyming First Loose Tooth Adventure with Mom and Dad",
    "images": [
        ("", "wiggle-wobble.webp", "A tiny wiggle. A very big first!",
         "Tyson shows his first loose tooth while Alex and Theresa encourage him with gentle smiles."),
        ("", "trampoline-bounce.webp", "Boing! His tooth takes a tiny trip of its own.",
         "Tyson bounces inside an enclosed backyard trampoline, unaware that his tiny tooth has fallen into the grass."),
        ("", "fairy-note.webp", "No tooth to leave? A little note will do.",
         "Tyson writes a note to the Tooth Fairy at his bedroom desk, with Theresa and Alex reassuring him."),
        ("", "morning-dollar.webp", "One missing tooth. One wonderful dollar.",
         "Tyson wakes with a gap-toothed smile and finds a one-dollar bill under his pillow as Mom and Dad smile beside his bed."),
    ],
    "scenes": [
        ("Wiggle, wobble, not quite yet", [
            "Tyson brushed and stopped to stare;\nA tiny tooth was wobbling there.\n\u201cMy first loose tooth!\u201d he cried with glee.\n\u201cA wiggly tooth belongs to me!\u201d",
            "Dad, Alex, said, \u201cLet's see it go\u2014\nJust gentle wiggles, nice and slow.\u201d\nTheresa smiled, her eyes so bright:\n\u201cWe'll let it go when time is right.\u201d",
            "With clean hands, Tyson gently tried;\nThat little tooth went side to side.\nHe nudged it with his tongue once more;\nIt held on tighter than before.",
            "\u201cWiggle, wobble! Won't you fall?\u201d\nIt would not budge much more at all.\n\u201cLet's take a break,\u201d he heard Dad say.\nSo Tyson dashed outside to play.",
        ]),
        ("The bounce he didn't notice", [
            "The trampoline was round and green,\nThe bounciest thing he'd ever seen.\nIts net zipped shut; Mom watched nearby,\nWhile Tyson bounced beneath the sky.",
            "A little hop! A happy spin!\nA breeze tickled his cheek and chin.\nHe laughed and bounced above the ground;\nHis tooth slipped out without a sound.",
            "It tumbled past the padded side\nAnd in the grass it went to hide.\nNo tiny tap. No shout of \u201cHey!\u201d\nHe never felt it slip away.",
            "When play was done, he touched his chin.\nHis tongue explored his toothy grin.\nHe found a gap! His eyes grew round:\n\u201cMy tooth is gone\u2014but can't be found!\u201d",
        ]),
        ("A note instead of a tooth", [
            "They searched the grass; they checked each shoe.\nThey looked beneath the trampoline, too.\nBut not a speck of tooth was there.\nTyson sniffled in the evening air.",
            "\u201cNo tooth beneath my pillow tonight!\nThe fairy won't come on her flight!\u201d\nMom hugged him close. Dad held him tight.\n\u201cLet's leave a note,\u201d said Mom. \u201cWe'll write.\u201d",
            "Dear Tooth Fairy, my tooth came free\nWhile I was bouncing happily.\nI didn't notice it fall that day;\nIt landed somewhere far away.",
            "We searched and searched, but couldn't see\nThe little tooth that came from me.\nPlease visit even though it's gone.\nLove, Tyson. Then he gave a yawn.",
        ]),
        ("A dollar and a brand-new grin", [
            "He tucked the note, then climbed in bed.\nMom kissed his cheek; Dad stroked his head.\nThe moon shone softly, silver-white;\nHis little room grew still that night.",
            "On whisper-wings, a fairy flew\nAnd read the note that told her true.\n\u201cA missing tooth? That's quite all right.\nYour note has brought me here tonight.\u201d",
            "She left a dollar, crisp and green,\nBeneath his pillow, quite unseen.\nAt dawn he peeked\u2014then gave a shout:\n\u201cShe came! She came! It all worked out!\u201d",
            "Theresa laughed; Dad grinned along.\nHis tooth was lost, but hope stayed strong.\nOne dollar! One new gap to show!\nAnd one more way for him to grow.",
        ]),
    ],
}


def narration_sections():
    """One recorded section per illustrated scene, without headings or captions."""
    return ["\n\n".join(paragraphs) for _, paragraphs in STORY["scenes"]]
