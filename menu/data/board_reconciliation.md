# Trifold brochure vs. the reference menu board

Reference sheet #2 is a board for the same restaurant — the section names and
prices line up with the trifold (فحم عادي 16/22/40.00, تكا دجاج 18.00,
ملاي تكا 20.00, سلطة تكا دجاج 12.00, روبيان مقلي 20.00, فول 10.00, دوسا سبت 6.00).
Where the two disagree, the board is the newer artwork, but the trifold is the
file we were given, so `menu.json` still follows the trifold. Decisions needed:

## Naming differences

| Trifold | Board | Note |
|---|---|---|
| فحم فلفل أخضر حار | فحم فاهيتا أخضر حار | "pepper" vs "fajita" — the board photo shows a fajita-style grill with peppers and tomato |
| فحم فلفل أسود | فحم فاهيتا أسود | same distinction |
| فحم إيري بوري | فحم أبري بوري | spelling |
| ملاي تكا | ملي تكا | spelling |
| دوسا سيت | دوسا سبت | spelling |

## Price / item differences

| Item | Trifold | Board |
|---|---|---|
| سلطة خضراء | 2/5/10.00 | 5.00 |
| سلطة عربية | 10.00 **and** a second entry at 5.00 | one entry, 10.00 |

The board carries three salads, not four. That supports reading the trifold's
second `سلطة عربية 5.00` as a typo for `سلطة خضراء 5.00`.

## Dishes on the board that are missing from the trifold

- **زبادية** (yoghurt dip) — breakfast, 6/8/12.00
- **جبن** (white cheese plate) — breakfast, 6/8/12.00

Not added to `menu.json` yet — confirm whether the trifold or the board is the
current menu.

## Dishes in the trifold that the board does not show

هامور فحم (APS) and روبيان ماسالا (20.00) appear only in the trifold's fish
section.

## Caveat

A couple of board tiles look loosely matched to their captions — the
`دوسا سبت` tile shows a cheese-and-olive plate, not a dosa. Treat the board
photos as style reference, not as proof of what each dish is plated like.
