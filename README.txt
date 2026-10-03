NSL MRT PILOT — CORE CODE AND DATA
Wang Yulv | Zhang Xinyue | BPS5231

FOUR FILES
model.py          Train and evaluate the core model.
data.csv          224 coded review records with stars and source identifiers.
requirements.txt  Python dependencies.
README.txt        This guide.

RUN
In this extracted folder, using Python 3.12 or a compatible version:
python -m pip install -r requirements.txt
python model.py
No API key is needed. Two output files are generated in results/:
summary.json and factor_ranking.csv.

METHOD
Nine binary mention flags predict 4–5 stars versus 1–3 stars.
Logistic regression uses C=1 and balanced class weights.
Stratified 5-fold validation is repeated 10 times.
Importance is the mean held-out AUC drop after shuffling a feature.
Expected macro F1: approximately 0.640; AUC: 0.738; accuracy: 0.704.
Majority baseline macro F1: 0.437; accuracy: 0.777.
This core version reproduces the slide metrics and factor rankings.
Additional sensitivity and leave-one-station-out analyses are omitted here.

DATA DICTIONARY
C: connections to transit, malls and destinations.
M: walking distances, passageways and transfer routes.
F: exit choices, signage, maps and getting lost.
V: lifts, escalators, stairs and wheelchair/pram access.
D: crowding, queues and pedestrian density.
T: thermal comfort, ventilation, air and weather protection.
Q: cleanliness, damage and maintenance.
A: shops, food, toilets, seating and resting/meeting facilities.
L: lighting, decoration and spatial ambience.
1 means mentioned; 0 means not mentioned, not a negative experience.
Stars are the review author's original rating, never an input feature.
record_id links to the pilot record; review_id and source_url support auditing.

SCOPE
Five stations; 211 spatial reviews plus 13 operations-only records.
Existing AI-assisted coding is supplied; it still needs human verification.
This script does not collect reviews or regenerate text annotations.
Full review text is not included; consult source links for original wording.
The taxonomy was developed on the pilot, so evaluation is exploratory.
Relevance sampling and high-rating bias limit generalization.
Predictive importance is not causal impact or retrofit effectiveness.
Negative importance does not establish that a spatial factor is unimportant.
Code was prepared with AI assistance; disclose this as required by the course.

METHOD REFERENCE
Wang et al. (2026), Ecological Indicators 190, 115367.
https://doi.org/10.1016/j.ecolind.2026.115367
