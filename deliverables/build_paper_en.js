// English conference paper (A4, two columns, Times New Roman), same layout as the interim paper.
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, ImageRun, BorderStyle, Footer, PageNumber, SectionType } = require("docx");

const F = "Times New Roman", SZ = 20; // 10 pt
const run = (t) => typeof t === "string" ? new TextRun({ text: t, font: F, size: SZ }) : new TextRun({ font: F, size: SZ, ...t });
const P = (text, o = {}) => new Paragraph({ spacing: { before: 60, after: 100, line: 240 }, alignment: o.align || AlignmentType.JUSTIFIED, children: (Array.isArray(text) ? text : [text]).map(run) });
const H = t => new Paragraph({ spacing: { before: 160, after: 80 }, keepNext: true, children: [new TextRun({ text: t, font: F, size: 22, bold: true })] });
const H2 = t => new Paragraph({ spacing: { before: 100, after: 60 }, keepNext: true, children: [new TextRun({ text: t, font: F, size: SZ, bold: true, italics: true })] });
const TCAP = t => new Paragraph({ spacing: { before: 100, after: 60 }, keepNext: true, alignment: AlignmentType.CENTER, children: [new TextRun({ text: t, font: F, size: 18, bold: true })] });
const FCAP = t => new Paragraph({ spacing: { before: 40, after: 120 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: t, font: F, size: 18, bold: true })] });
const b = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
function table(head, rows, widths, fs = 16) {
  const W = widths.reduce((a, c) => a + c, 0);
  const cell = (t, i, hdr) => new TableCell({ width: { size: widths[i], type: WidthType.DXA }, margins: { top: 20, bottom: 20, left: 60, right: 60 },
    borders: { top: b, bottom: b, left: b, right: b }, shading: hdr ? { type: ShadingType.CLEAR, fill: "F2F2F2", color: "auto" } : undefined,
    children: [new Paragraph({ keepNext: true, keepLines: true, alignment: AlignmentType.LEFT, children: [new TextRun({ text: String(t), font: F, size: fs, bold: !!hdr })] })] });
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, cantSplit: true, children: head.map((t, i) => cell(t, i, true)) }), ...rows.map(r => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, i, false)) }))] });
}
const COL = 4663;

const title = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Which Station-Space Experiences Go with Passenger Ratings? Evidence from Google Maps Reviews of Singapore’s North-South Line MRT Stations", font: F, size: 30, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [new TextRun({ text: "Wang Yulu", font: F, size: 22 }), new TextRun({ text: "1", font: F, size: 22, superScript: true }), new TextRun({ text: ", Zhang Xinyue", font: F, size: 22 }), new TextRun({ text: "1", font: F, size: 22, superScript: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "1", font: F, size: 20, superScript: true }), new TextRun({ text: "National University of Singapore, Singapore", font: F, size: 20 })] }),
];

const body = [
  H("Abstract"),
  P("Aim: MRT stations are daily-use public spaces, and online reviews describe how passengers experience them. This study asks which station-space experiences in Google Maps reviews of Singapore’s 27 North-South Line (NSL) stations are associated with overall star ratings, whether the most-mentioned aspects are also the most predictive, and how recurring complaints can ground station-level proposals. Methods: We collected 21,796 ratings; 3,884 text reviews mention at least one of nine spatial aspects flagged by a fixed bilingual dictionary. Models were evaluated with station-grouped cross-validation, and permutation importance with station bootstrap gave importance and rank stability. Two authors independently coded 100 reviews in two rounds; a rule-based aspect-polarity coder was compared with mention-only features and an overall-sentiment control, and a frozen pipeline was checked on newly posted reviews at one held-out station. Results: Inter-coder κ rose from 0.26 (scope) and 0.47 (aspect mention) to 0.77 and 0.67 after the codebook was revised. Mention-only spatial models reached AUC 0.61–0.63 against a 0.48 baseline; adding aspect polarity raised AUC to 0.74, matched by the overall-sentiment control. Connectivity and amenities ranked in the top three under every model, while vertical access, mentioned in 4% of reviews, ranked second only in the mention-only logistic model. Negative mentions of vertical access and cleanliness came with 1–3-star ratings 68% and 61% of the time, against 20% overall. Conclusions: Spatial mentions carry modest rating information, mention frequency differs from predictive importance, and evidence cards on an interactive map turn recurring complaints into small, testable station changes."),
  H("Keywords"),
  P("MRT stations; online reviews; aspect-based sentiment; permutation importance; inter-coder agreement"),
  P([{ text: "Topic: ", bold: true }, "Modeling for the digital world – Big data & machine learning; Human-centered simulation/design."]),

  H("1. Introduction"),
  P("MRT stations are not only places to board trains but also spaces where passengers walk, transfer, wait and linger. Station–city connections, walking routes and signage, lifts and escalators, crowding, heat and ventilation, cleanliness, and shops and toilets all shape the experience. Satisfaction surveys are costly and slow to update, whereas Google Maps reviews cover every station and carry both text and a star rating, offering another view of station space from the passenger’s side [1, 2, 3]."),
  P("Mentioning an issue, however, is not the same as the issue affecting the rating. A frequently mentioned aspect may simply be salient, while a rarely mentioned one may be strongly tied to low ratings when it does appear. We therefore ask three questions: (RQ1) which station-space experiences in reviews are associated with the overall rating; (RQ2) whether the most-mentioned aspects also contribute most to rating prediction; and (RQ3) whether recurring complaints can ground small, station-specific improvement proposals."),
  P("The paper contributes a review dataset and reproducible station-grouped evaluation for the whole NSL, two rounds of independent human coding with a frozen codebook, and an interactive map that links model results to station-level evidence cards."),

  H("2. Related Work"),
  P("Aspect-based sentiment analysis splits reviews into specific aspects and judges their polarity [2, 4]; studies of transit service quality likewise find that satisfaction depends on several distinguishable service and environment attributes [3], and review-based work on urban public space has linked experiential factors to subjective evaluations [1]. Permutation importance measures how much a fitted model relies on a feature by shuffling it and observing the drop in performance [5, 6]; this reliance depends on correlated features and model type and is not the benefit of changing the factor [6, 7]. When automatic coding is checked against human labels, Cohen’s κ is the usual agreement measure [8, 9]; because κ is unstable for sparse categories, we also report raw agreement and class counts."),

  H("3. Data"),
  P("On 4 October 2026 we collected all Google Maps ratings for the 27 NSL stations, sorted newest-first: 21,796 records. Collected counts match the displayed totals at 26 stations; Yew Tee shows 146 and yielded 145. Of these, 7,636 have text. Table 1 shows the screening: rating-only records, records without analysable text and normalised duplicates were removed, and reviews mentioning at least one spatial aspect were retained, giving 3,884 reviews from all 27 stations."),
  TCAP("Table 1 Data screening"),
  table(["Step", "Records"], [["All rating records", "21,796"], ["Rating only, no text", "14,160"], ["No analysable text", "71"], ["Duplicate after normalisation", "1,153"], ["No spatial aspect mentioned", "2,528"], ["In the model", "3,884"]], [3263, 1400], 17),
  P("In the model set, 80.25% of reviews (3,117) are rated 4–5 stars and 19.75% (767) 1–3 stars. The target is 4–5 versus 1–3 stars. Because a model that always predicts “high” is 80% accurate, AUC and macro F1 are the main metrics, with balanced accuracy and accuracy also shown. Reviewers are self-selected, so the data describe reviewers’ experiences rather than all passengers."),

  H("4. Methods"),
  H2("4.1 Nine station-space aspects"),
  P("We define nine aspects: C station–city connectivity; M walking and transfer paths; F wayfinding and signage; V vertical circulation and accessibility; D crowding and pedestrian flow; T thermal comfort, air and shelter; Q cleanliness and maintenance; A amenities and dwell support; L lighting and spatial ambience. Each has a fixed set of English and Chinese keywords, set before the expanded corpus was tested, which flags whether a review mentions the aspect."),
  H2("4.2 Independent human coding"),
  P("Both authors coded the same reviews with a web tool that hides star ratings, dictionary flags and AI suggestions. Each review receives a scope (station space, operations only, train interior, surroundings only, off topic, generic, unclear) and, for each aspect, absent, positive, negative, neutral, mixed or uncertain. Each author exported original answers before any discussion."),
  P("Round 1 coded 60 stratified reviews never used in development, covering dictionary matches and non-matches, rarer aspects and short, easily confused reviews. From its disagreements we added five rules and froze codebook v2: any coded aspect implies station-space scope; “near” or “convenient to” a destination is C; shops and food inside the station are A; long walks to outside destinations are C, with M reserved for walking and transfer inside the station; movable temporary supplies are operations only, and ageing fixed facilities are Q. Round 2 coded 40 new reviews, disjoint from all 260 earlier ones, with v2 and a Chinese reading aid. The authors then adjudicated all 100 reviews, keeping original and adjudicated labels separately, and used the adjudicated labels to check the dictionary and the polarity rules."),
  H2("4.3 Models and station-grouped evaluation"),
  P("We compare a majority baseline; logistic regression and random forest on the nine mention flags; and TF-IDF logistic regression on the text, used only as a comparator because it also draws on general sentiment words. All models use station-grouped 5-fold cross-validation, so a station’s reviews are only in training or only in testing, repeated with three seeds that form two distinct station partitions [10]."),
  P("For a prospective check, we froze the codebook, dictionary, polarity rules and model settings with file fingerprints, trained final models on the other 26 stations, then collected reviews posted at Woodlands (NS9) after the 4 October capture and evaluated them once. Woodlands was chosen by a rule fixed in advance (most reviews in the month before capture, excluding the case-card stations); its earlier reviews were seen during development."),
  H2("4.4 Aspect polarity (option C)"),
  P("To separate mentioning from experiencing, a fixed rule set scores the clauses that contain each mentioned aspect with a small sentiment lexicon, handles negation within three words, and treats requests or absences (“would be good if”, “no shelter”) as negative. The rules never see ratings; they were checked only on a 200-review AI-annotated development set, frozen, and compared once with the human labels. Each aspect becomes positive, negative and neutral indicators. A control model adds whole-review counts of positive and negative clauses to the mention flags, to test whether polarity adds information beyond overall tone. All models use the same station splits."),
  H2("4.5 Importance and rank stability"),
  P("Permutation importance shuffles an aspect within each station in each test fold (the three option-C indicators together) and records the AUC drop. 300 station-bootstrap resamples of the first-seed out-of-fold predictions give 95% intervals and the share of resamples in which each aspect ranks in the top three. The resamples reuse fixed predictions and do not refit coding or models."),

  H("5. Results"),
  H2("5.1 Coding agreement and automatic labels"),
  P("Table 2 reports agreement. Round 1 disagreements centred on scope: one coder labelled 39 reviews as station space and the other 17, mainly over generic versus station-space comments, connectivity versus surroundings, and whether in-station shops are amenities. After the revision, scope κ on new reviews rose to 0.77 and the station-space counts converged (22 and 21). The two rounds used different reviews and round 2 added a reading aid, so the rise is not attributed to the codebook alone. Per-aspect κ is unstable for sparse aspects (M had 2 and 0 mentions in round 2); full results are in the repository. When both coders marked an aspect, polarity almost always agreed."),
  TCAP("Table 2 Independent coding agreement"),
  table(["Measure", "Round 1 (60, v1)", "Round 2 (40, v2)"], [
    ["Scope, 7 classes: raw / κ", "0.43 / 0.26", "0.85 / 0.77"],
    ["Station space vs other: raw / κ", "0.60 / 0.29", "0.93 / 0.85"],
    ["Aspect mention (9 × n): raw / κ", "0.92 / 0.47", "0.95 / 0.67"],
    ["Station space (coder 1 / 2)", "17 / 39", "22 / 21"],
    ["Aspects marked (coder 1 / 2)", "37 / 56", "30 / 30"]], [2263, 1200, 1200], 16),
  P("Against the 100 adjudicated labels (Table 3), the dictionary is fairly reliable at deciding whether a review concerns station space (precision 0.77, recall 0.82) but much coarser at deciding which aspect (precision 0.49, recall 0.61). Amenities (15) and walking paths (11) are most often over-flagged; connectivity and amenities (9 each) are most often missed. Results based on mention flags are therefore more trustworthy at the level of “station space or not” than for individual aspects."),
  TCAP("Table 3 Dictionary labels vs adjudicated human labels"),
  table(["Dictionary vs human (100)", "Both", "Dict. only", "Human only", "Prec.", "Rec.", "κ"], [
    ["Station space or not", "49", "15", "11", "0.77", "0.82", "0.45"],
    ["Aspect mention (9 × 100)", "54", "56", "35", "0.49", "0.61", "0.49"]], [1463, 500, 600, 650, 480, 480, 490], 15),
  H2("5.2 Model performance"),
  P("Table 4 shows station-grouped results. Mention-only spatial models beat the baseline (AUC 0.61–0.63 vs 0.48): spatial mentions carry some rating information, but on their own explain little. Excluding 3-star reviews, the mention-only logistic AUC is 0.68 (n = 3,429). Adding aspect polarity lifts both models to AUC 0.74, a gain of 0.13 (logistic; station-bootstrap interval 0.09–0.17) and 0.11 (forest; 0.08–0.14). The overall-sentiment control, however, is slightly higher than option C (differences −0.016 and −0.022, intervals below zero): the gain is explained by the review’s overall tone, and with these rules we cannot show that knowing which aspect was praised or criticised adds information."),
  TCAP("Table 4 Station-grouped 5-fold CV (mean of 3 seeds)"),
  table(["Model", "AUC", "Macro F1", "Bal. acc.", "Acc."], [
    ["Majority baseline", "0.482", "0.445", "0.500", "0.803"],
    ["B mentions, logistic", "0.609", "0.551", "0.586", "0.640"],
    ["B mentions, forest", "0.634", "0.580", "0.607", "0.681"],
    ["C aspect + polarity, logistic", "0.739", "0.648", "0.692", "0.729"],
    ["C aspect + polarity, forest", "0.739", "0.638", "0.684", "0.718"],
    ["Control: mentions + overall tone, logistic", "0.755", "0.669", "0.703", "0.757"],
    ["Control: mentions + overall tone, forest", "0.761", "0.680", "0.708", "0.771"],
    ["TF-IDF text, logistic", "0.796", "0.701", "0.729", "0.787"]], [2063, 650, 650, 650, 650], 15),
  P("Against the adjudicated labels (54 review–aspect pairs marked by both), the polarity rules agree 63% of the time (κ = 0.34); they recover 84% of human negative labels but only 25% of positive ones, labelling most praise as neutral. Option C therefore mainly captures complaints."),
  P("In the prospective check, Woodlands received 36 new ratings after capture (27 five-star, 5 four-star, 4 three-star). 26 had no text, 2 duplicated existing texts and 4 mentioned no spatial aspect, so only 4 entered the model, all rated 4–5 stars. Each frozen model classified 3 of the 4 correctly; with no low ratings, AUC is undefined. The frozen pipeline runs unchanged on new reviews, but six weeks of reviews are too few to estimate performance."),
  H2("5.3 Mentioned most is not predictive most"),
  P("Fig. 1 compares mention share with permutation importance. Amenities (42%) and connectivity (38%) are mentioned most; vertical access is mentioned in only 4% of reviews yet ranks second in the mention-only logistic model, while cleanliness (19%) ranks last. A negative or near-zero importance only means that shuffling did not hurt this model; it does not mean the issue is unimportant for station operation."),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80 }, keepNext: true, children: [new ImageRun({ type: "png", data: fs.readFileSync("fig_importance_en_col.png"), transformation: { width: 300, height: 406 }, altText: { title: "Figure 1", description: "Mention share and permutation importance of nine aspects", name: "fig1" } })] }),
  FCAP("Fig. 1 Mention share and permutation importance (mention-only logistic, 95% station-bootstrap interval)"),
  P("Table 5 tests whether these ranks hold. Connectivity and amenities almost always rank in the top three under all four models. Vertical access is stable only in the mention-only logistic model (13% of resamples in the top three for the forest), and cleanliness rises to first once polarity is added, because “clean” and “dirty” carry sentiment. Negative mentions of vertical access and cleanliness come with 1–3 stars 68% and 61% of the time, against 20% for all reviews; crowding only 33%."),
  TCAP("Table 5 Share of 300 station resamples ranking each aspect in the top three (T, L ≤ 0.04 in all models)"),
  table(["Aspect", "Ment.", "1–3★ if negative", "B log.", "B for.", "C log.", "C for."], [
    ["V vertical", "4%", "68% (40/59)", "1.00", "0.13", "0.05", "0.00"],
    ["Q clean", "19%", "61% (70/114)", "0.00", "0.95", "1.00", "1.00"],
    ["M walking", "12%", "52% (58/112)", "0.02", "0.00", "0.00", "0.00"],
    ["F wayfinding", "12%", "45% (80/176)", "0.01", "0.00", "0.00", "0.00"],
    ["C connect.", "38%", "41% (72/177)", "1.00", "0.92", "1.00", "1.00"],
    ["A amenities", "42%", "38% (77/201)", "0.92", "1.00", "0.95", "1.00"],
    ["D crowding", "23%", "33% (149/452)", "0.01", "0.00", "0.00", "0.00"]], [840, 560, 1023, 560, 560, 560, 560], 15),
  P("In the original 224-review pilot, removing the 13 operations-only reviews without spatial flags changed macro F1 from 0.634 to 0.623 and AUC from 0.736 to 0.712 under the matched five-repeat setting; the top three remained connectivity, amenities and vertical access."),
  H2("5.4 Station evidence cards"),
  P("To turn review patterns into proposals that can be discussed, we built evidence cards for three stations with many low-rated mentions of an aspect (Table 6). Each card gives aspect mentions against the station’s model reviews, the 1–2-star share against the station share, the review period, supporting and contradicting quotations with review IDs, a candidate small change and a way to test it. Cards are labelled “review claim / needs site check”."),
  TCAP("Table 6 Evidence-card summary (full cards on the website)"),
  table(["Station", "Aspect", "Mentions / station (1–2★, station)", "Candidate change"], [
    ["Dhoby Ghaut", "F/V wayfinding", "87 / 252 (14%, 8%)", "Add exit numbers or destinations to transfer signs"],
    ["Jurong East", "F/D/M crowding, wayfinding", "226 / 399 (14%, 11%)", "Show the arriving platform earlier; large signs to malls during construction"],
    ["Kranji", "Q cleanliness, odour", "56 / 270 (16%, 10%)", "Check cleaning rota and supplies; confirm who manages the bin area"]], [900, 950, 1113, 1700], 15),

  H("6. Discussion"),
  P("First, spatial mentions relate to ratings but have limited predictive power on their own, as expected: a star rating also reflects service, trains, personal circumstances and overall mood. Second, mention frequency and predictive importance do differ, but the ranking depends on model and features. Connectivity and amenities are stable across all settings and are the most reliable finding; vertical access and cleanliness move with the model. For planning, priorities should combine mention counts, the low-rating share among negative mentions and rank stability rather than a single importance ranking; vertical access and cleanliness, whose negative mentions are most strongly tied to low ratings, deserve early checks."),
  P("Third, polarity improves prediction, but no more than overall tone. Judging how much a specific aspect’s experience matters requires better aspect-level polarity, especially for praise, compared on the same station splits; the frozen codebook and 100 adjudicated labels are a starting point for training and testing it. Fourth, evidence cards give users what a model cannot: who complained about what and when, whether others disagreed, a small change to try first and how to test it. Importance reflects model reliance, not the benefit of a change, so candidate changes should be checked on site and evaluated before and after at a fixed station with newly collected reviews or observation."),

  H("7. Conclusion"),
  P("Across 3,884 space-related reviews of the 27 NSL stations, spatial mentions relate to passenger ratings but explain little on their own; mention frequency differs from predictive importance, with connectivity and amenities the most stable contributors; and the gain from aspect polarity comes mainly from overall tone. Two rounds of independent coding reached κ = 0.77 (scope) and 0.67 (aspect mention) after the codebook was revised. Code, processing, coding records and the interactive website are available at github.com/mokscreate/assignment-5231."),

  H("References"),
  ...[
    "[1] Wang, K., Zhang, X., Yang, H., Tang, L., Xie, D., & Yuan, C. (2026). Experiential factors associated with subjective well-being in urban waterfront environments: Evidence from social media data in Wuhan, China. Ecological Indicators, 190, 115367. https://doi.org/10.1016/j.ecolind.2026.115367",
    "[2] Hu, M., & Liu, B. (2004). Mining and summarizing customer reviews. Proceedings of the 10th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 168–177.",
    "[3] Eboli, L., & Mazzulla, G. (2007). Service quality attributes affecting customer satisfaction for bus transit. Journal of Public Transportation, 10(3), 21–34.",
    "[4] Pontiki, M., et al. (2014). SemEval-2014 Task 4: Aspect based sentiment analysis. Proceedings of the 8th International Workshop on Semantic Evaluation, 27–35.",
    "[5] Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.",
    "[6] Fisher, A., Rudin, C., & Dominici, F. (2019). All models are wrong, but many are useful. Journal of Machine Learning Research, 20(177), 1–81.",
    "[7] Strobl, C., Boulesteix, A.-L., Zeileis, A., & Hothorn, T. (2007). Bias in random forest variable importance measures. BMC Bioinformatics, 8, 25.",
    "[8] Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, 20(1), 37–46.",
    "[9] Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159–174.",
    "[10] Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
  ].map(t => new Paragraph({ spacing: { after: 60 }, indent: { left: 340, hanging: 340 }, alignment: AlignmentType.LEFT, children: [new TextRun({ text: t, font: F, size: 18 })] })),
  H("AI Tool Declaration"),
  P("We used GPT-5.6 (interim stage) and Claude (Anthropic) to assist with data-processing scripts, the polarity rules, the coding and adjudication tools, the website and the drafting of this paper. All human coding was done independently by the two authors; AI annotations were used only for development and never as human labels. The results were reviewed and interpreted by our group, and we are responsible for the content and quality of the submitted work."),
];

const page = { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1077, right: 1077 } };
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18 })] })] });
const doc = new Document({
  creator: "Wang Yulu, Zhang Xinyue", title: "NSL MRT station-space experiences and passenger ratings",
  styles: { default: { document: { run: { font: F, size: SZ } } } },
  sections: [
    { properties: { page }, footers: { default: footer }, children: title },
    { properties: { page, type: SectionType.CONTINUOUS, column: { count: 2, space: 425 } }, footers: { default: footer }, children: body },
  ],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync("NSL_MRT_paper_en.docx", buf); console.log("ok"); });
