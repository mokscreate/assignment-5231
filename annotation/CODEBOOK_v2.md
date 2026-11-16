# Annotation codebook v2 (frozen 2026-11-15)

Frozen by Wang Yulu after adjudicating the 60-record round-1 overlap (round-1 agreement was computed on the original pre-discussion labels under v1).
v2 = the v1 rules in `docs/Annotation_Codebook_README.txt` (SCOPE FIRST / ASPECTS / POLARITY) plus the following rules, which take precedence:

1. If any aspect is not `absent`, scope must be `station_spatial`.
2. Statements that the station is near / convenient for reaching a destination, connected to a mall, or convenient for transferring to buses or other transport are coded **C**, with scope `station_spatial`.
3. Shops, food outlets and supermarkets inside the station are coded **A**.
4. Long or indirect walks from the station to an outside destination are **C**. **M** is reserved for walking and transfer inside the station (passageways, between platforms or lines, gates).
5. Presence or absence of movable, temporary supplies (e.g. umbrella bags) is `station_operations_only` with no aspect. Ageing or worn fixed facilities, including "the station is old", are **Q**, with polarity from the tone. This replaces the v1 note that age alone does not prove disrepair.

Round 2 (40 new records, `round2_blind.json`) is coded independently under v2 with `review_round2_zh.html`.
