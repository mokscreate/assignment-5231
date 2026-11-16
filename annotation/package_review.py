from pathlib import Path
import json,html,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/NSL_Annotation_Review'
A=json.loads((OUT/'annotations.json').read_text(encoding='utf-8'));S=json.loads((OUT/'audit_summary.json').read_text())
codebook='''NSL MRT — 200-REVIEW ANNOTATION CHECK
Wang Yulu | Zhang Xinyue | BPS5231 | 5 October 2026

WHAT WAS COMPLETED
One AI read and initially annotated all 200 sampled reviews across 27 stations.
Each record has a scope decision, aspect-level polarity, exact evidence excerpts,
a rationale and a human-adjudication flag. These are NOT human-verified labels.
40 records need priority adjudication. All other records still need independent review.
90 were provisionally classified as station-spatial, 22 as unclear, and 88 as other
content (generic, staff/service, wider neighbourhood, unrelated place or train interior).
This deliberately stratified diagnostic sample is NOT a representative estimate of
the fraction of useful reviews in the complete corpus.

OPEN review.html
The local review tool contains all 200 texts. It makes no network requests.
Original star ratings, original dictionary labels and old model predictions are hidden.
AI suggestions are also hidden by default to reduce anchoring. Enter your own scope
and labels first, then optionally reveal AI suggestions and discuss disagreements.
Start with the Priority only filter for the 40 ambiguous records.
Enter a reviewer ID; use separate IDs/files for two independent reviewers.
Unanswered fields mean unreviewed, not absent or neutral. Mark all nine aspect fields
explicitly for each fully reviewed record. Use absent when a factor is not discussed.
Save progress with Export human review JSON before closing or sharing the file.
The browser also attempts local autosave, but the exported JSON is the reliable copy.
Do not share only the HTML expecting it to contain your saved browser edits.

SAMPLING
Seed 5231200. Nonempty text was normalised and deduplicated, then sampled round-robin
from station x original-rating-band (1-2, 3, 4-5) x old dictionary-hit strata until 200.
Stars were used for sample coverage, NOT to generate the labels. The private sampling
key stayed separate while annotation was performed. Two comments (R133 and R176)
contained residual in-text rating language missed by the initial mask; this was noted,
masked in the review tool, and those records were excluded from agreement calculations.
R073 is numeric-only and is masked in the review tool. No synthetic reviews were added.

SCOPE FIRST
station_spatial: Station interior, immediate station entrance/interface, or an explicit
pedestrian/multimodal connection between the station and a destination.
station_operations_only: Staff attitude, fare/payment policy, service delays, security
procedures or ticket-office service without a distinct physical-space assessment.
train_interior: Seats, temperature/noise or other conditions inside a vehicle.
surroundings_only: A neighbourhood, street or landmark described without an explicit
station access or station-space experience.
off_topic: Another business/place or unrelated text.
generic: Great, okay, check-ins or other statements without a specific spatial factor.
unclear: The evaluated object cannot be located confidently; retain for adjudication.
Spatial reviews may also contain operational content. Code only supported spatial
claims. A factual spatial inventory may be relevant even without positive/negative tone.

ASPECTS (MULTI-LABEL)
C  Station-city connectivity: location/proximity and actual connections to destinations
   or other transport. Missing a bus because a train is late is operational, not C.
M  Walking and transfer paths: actual walking distance, detours, passageways, gates and
   pedestrian routes. Inter-station rail distance is not station walking distance.
F  Wayfinding and signage: orientation, signs/maps, misleading naming and concrete
   route/exit guidance. An incidental exit word is insufficient. Reviewer route advice
   can be neutral; it does not prove that station signage is good.
V  Vertical circulation/accessibility: lift/escalator/stair availability, operation,
   arrangement or mobility access. Mentioning an escalator only to locate litter is not V.
D  Crowding/pedestrian flow: actual pedestrian density, capacity and movement/queue
   constraints. Vehicle parking jams and hypothetical future crowds are not D.
   Ticket-service queues alone are operational unless a spatial bottleneck is identified.
T  Thermal comfort/air/shelter: station or immediate access-route heat, ventilation,
   cooling and rain/sun protection. Cold food is not T; train temperature is out of scope.
Q  Cleanliness/maintenance: physical station condition, hygiene and upkeep/construction.
   Ticket-machine payment problems are operational. Age alone does not prove disrepair.
A  Amenities/dwell support: station food/retail, toilets, seating, charging or rest
   provision. A restaurant menu/taste complaint is not automatically a station amenity
   assessment. A nearby mall connection belongs to C unless station amenities are clear.
L  Lighting/spatial ambience: lighting, aesthetics, murals, station views/visual character.
   The word design alone does not establish L; generic usability criticism may be unmapped.
General station size or unspecific usability feedback may be station_spatial with no
resolved aspect. Keep it; do not invent a category just to fill every row.

POLARITY, FOR EACH ASPECT
positive: Text explicitly favours the experience, including not as crowded.
negative: Explicit discomfort, deficiency or burden, including too hot or confusing.
neutral: A factual feature/absence/procedure with no clear valenced judgement.
mixed: BOTH positive and negative CURRENT experiences of the SAME aspect.
uncertain: Aspect or sentiment cannot be resolved confidently.
absent: Aspect is not discussed. This is different from saying a facility is absent.
Missing AC alone can be neutral; missing AC plus hot/stuffy is negative.
Busy can be neutral; too busy or crowding that impedes movement is negative.
Old praise and future hopes must not be treated as positive current experience.
Positive connectivity plus negative heat is two differently valenced aspects, not
mixed sentiment for both. No clearly supported same-aspect mixed label was forced
into this sample just to populate the category.
Physical problems can legitimately receive multiple labels (e.g. broken lift: V and Q;
dirty toilet: A and Q). Correlation must be considered in later importance analysis.

AUDIT FINDINGS
Among 160 records not flagged as ambiguous, the old dictionary and the AI scope labels
agree on 61 spatial matches and 68 nonspatial cases; 17 old matches were judged nonspatial
by AI, and 14 AI-spatial cases were missed by the old dictionary. This is diagnostic
AI agreement, NOT human precision/recall or a population error estimate.
The weakest-looking boundaries include destination proximity (C), generic design/view
words (L), shops/food outside the station (A), and incidental route words (M/F).
Concrete examples: R032 is a durian vendor complaint despite mentioning a footbridge;
R071 uses cold for food; R090 says not as crowded; R193 praises connectivity while
criticising shelter, toilet condition and walking distance.

WHAT CHANGES NEXT
1. Independently verify scope, polarity and evidence, starting with the flagged 40.
2. Resolve disagreements and freeze the codebook. If both reviewers independently
   label an overlapping subset, agreement can then be measured; no such statistic is
   claimed for this single-AI pass.
3. Apply the checked scheme to a larger training corpus. Keep a separately annotated,
   untouched test set and maintain station-grouped splits.
4. Compare mention-only inputs against aspect-plus-polarity inputs on identical splits.
   Fit any learned extractor on training stations only, or externally freeze it before
   evaluation; never let test ratings generate aspect labels.
The 200 diagnostic records are now codebook-development data, NOT a final test set.
Do not infer that this audit improves model AUC. No new polarity-rating model was
trained in this step; the previous fitted models and files have been preserved.

FILES
review.html          Rating-blind reading/review interface, with optional AI suggestions.
annotations.json     200 complete AI initial annotations and blank human-review fields.
audit_summary.json   Diagnostic counts and dictionary-versus-AI agreement only.
README.txt           Scope rules, interpretation and next modelling steps.
'''
(OUT/'README.txt').write_text(codebook,encoding='utf-8')
template=r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NSL MRT — 200-review check</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#203348;font:16px/1.5 system-ui,sans-serif}header{background:#164c7c;color:white;padding:24px max(24px,calc((100% - 1100px)/2))}h1{font-size:27px;margin:0}header p{margin:8px 0}main{max-width:1100px;margin:24px auto;padding:0 20px}.panel,article{background:white;padding:22px;border:1px solid #dbe4ed;border-radius:10px;margin:16px 0}.stats{display:flex;gap:22px;flex-wrap:wrap}.stats strong{font-size:25px;display:block}button,input,select,textarea{font:inherit;padding:8px;border:1px solid #a7b9ca;border-radius:5px}button{cursor:pointer;background:#edf4fa;color:#164c7c}button.primary{background:#164c7c;color:white}label{display:inline-block;margin:6px 12px 6px 0}input[type=checkbox]{margin-right:8px}.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.review{white-space:pre-wrap;background:#f7f9fc;padding:16px;border-left:4px solid #378cc6;overflow-wrap:anywhere}.tag{font-size:13px;color:#77561b;background:#fff4d9;border-radius:12px;padding:3px 10px}.aspects{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.aspects label{margin:0;font-size:14px}.aspects select{width:100%}textarea{width:100%;min-height:80px}.muted{color:#5b6d7e;font-size:14px}summary{cursor:pointer;font-weight:600;color:#164c7c}.ai{margin-top:12px;border-top:1px solid #ddd;padding-top:10px}.ai p{margin:6px 0}footer{padding:20px 0;color:#5b6d7e}a{color:#1467a2}@media(max-width:700px){.aspects{grid-template-columns:1fr}h1{font-size:22px}}</style>
<header><h1>NSL MRT · Review the evidence</h1><p>200 comments · 27 stations · Single-AI initial annotations</p></header><main>
<section class="panel"><div class="stats"><div><strong>200</strong>comments reviewed by AI</div><div><strong>90</strong>provisionally station-spatial</div><div><strong>40</strong>priority adjudications</div></div><p>This is a diagnostic sample, not a representative survey. AI labels are not human ground truth. Original ratings and prior model outputs are hidden. Read the text and enter your judgement before revealing AI suggestions.</p><p class="muted">No new polarity model has been trained. <a href="README.txt">Read scope and polarity rules</a>. Two residual in-text rating disclosures were detected in the first AI pass and are documented.</p></section>
<section class="panel"><div class="bar"><label>Reviewer ID <input id="reviewer" placeholder="Reviewer A" size="14"></label><button class="primary" id="export">Export human review JSON</button></div><p class="muted">Edits autosave locally when supported. Export your JSON before closing. Use separate reviewer IDs for independent annotations. Do not equate a blank field with absent.</p><div class="bar"><label><input id="priority" type="checkbox">Priority only</label><label><input id="unfinished" type="checkbox">Incomplete only</label><input id="search" placeholder="Search station, ID or text" aria-label="Search reviews"><span id="progress"></span></div></section>
<div class="bar"><button id="prev">Previous</button><span id="page"></span><button id="next">Next</button></div><div id="cards"></div><footer>Source: collected Google Maps station reviews. No API calls or external scripts. AI suggestions and evidence remain distinct from your judgements.</footer></main>
<script id="dataset" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('dataset').textContent);
const names={C:'Station-city connectivity',M:'Walking / transfer paths',F:'Wayfinding / signage',V:'Vertical access',D:'Crowding / flow',T:'Thermal / air / shelter',Q:'Cleanliness / maintenance',A:'Amenities / dwell',L:'Lighting / ambience'};
const scopes=['station_spatial','station_operations_only','train_interior','surroundings_only','off_topic','generic','unclear'];const vals=['absent','positive','negative','neutral','mixed','uncertain'];
let edits={},page=0;const el=id=>document.getElementById(id);const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function key(){return 'nsl-review-200-v1-'+(el('reviewer').value.trim()||'anonymous')}
function save(){try{localStorage.setItem(key(),JSON.stringify(edits))}catch(e){el('progress').textContent='Autosave unavailable; export your JSON.'}}
function load(){try{edits=JSON.parse(localStorage.getItem(key())||'{}')}catch(e){edits={}}page=0;render()}
function complete(id){let e=edits[id];return e&&e.scope&&Object.keys(names).every(k=>e.aspects&&e.aspects[k])}
function options(items,selected){return '<option value="">Unreviewed</option>'+items.map(v=>`<option value="${v}" ${v===selected?'selected':''}>${v.replaceAll('_',' ')}</option>`).join('')}
function filtered(){let q=el('search').value.toLowerCase();return data.filter(a=>(!el('priority').checked||a.needs_adjudication)&&(!el('unfinished').checked||!complete(a.audit_id))&&(!q||(a.audit_id+' '+a.station+' '+a.review_text_blinded).toLowerCase().includes(q)))}
function render(){let all=filtered();page=Math.min(page,Math.max(0,Math.ceil(all.length/10)-1));el('page').textContent=`Page ${page+1} / ${Math.max(1,Math.ceil(all.length/10))} · ${all.length} matching reviews`;el('progress').textContent=data.filter(a=>complete(a.audit_id)).length+' / 200 fully reviewed';el('prev').disabled=page===0;el('next').disabled=(page+1)*10>=all.length;
el('cards').innerHTML=all.slice(page*10,page*10+10).map(a=>{let e=edits[a.audit_id]||{aspects:{}};return `<article data-id="${a.audit_id}"><h2>${a.audit_id} · ${esc(a.station)} ${a.needs_adjudication?'<span class="tag">Priority check</span>':''}</h2><div class="review">${esc(a.review_text_blinded)}</div><h3>Your independent judgement</h3><label>Scope <select data-field="scope">${options(scopes,e.scope)}</select></label><div class="aspects">${Object.keys(names).map(k=>`<label>${k} · ${names[k]}<select data-aspect="${k}">${options(vals,e.aspects[k])}</select></label>`).join('')}</div><label style="width:100%">Evidence / disagreement notes<textarea data-field="notes">${esc(e.notes||'')}</textarea></label><details class="ai"><summary>Reveal AI suggestion and evidence</summary><p><b>Scope:</b> ${esc(a.scope_ai)}</p><p><b>Aspects:</b> ${esc(Object.entries(a.aspects_ai).filter(([k,v])=>v!=='absent').map(([k,v])=>k+': '+v).join('; ')||'No resolved specific aspect')}</p><p><b>Evidence:</b> ${esc(a.evidence_ai.join(' | '))}</p><p>${esc(a.rationale_ai)}</p><p class="muted">${esc(a.blinding_note)} All labels remain AI initial annotations.</p></details></article>`}).join('')||'<p>No matching reviews.</p>'}
el('cards').addEventListener('input',ev=>{let a=ev.target.closest('article');if(!a)return;let e=edits[a.dataset.id]||{scope:'',aspects:{},notes:''};if(ev.target.dataset.aspect)e.aspects[ev.target.dataset.aspect]=ev.target.value;else if(ev.target.dataset.field)e[ev.target.dataset.field]=ev.target.value;else return;edits[a.dataset.id]=e;save();el('progress').textContent=data.filter(a=>complete(a.audit_id)).length+' / 200 fully reviewed'});
el('reviewer').addEventListener('input',load);['priority','unfinished','search'].forEach(id=>el(id).addEventListener('input',()=>{page=0;render()}));el('prev').onclick=()=>{page--;render()};el('next').onclick=()=>{page++;render()};
el('export').onclick=()=>{let payload={reviewer_id:el('reviewer').value.trim()||'anonymous',exported_at:new Date().toISOString(),schema:'nsl-human-review-v1',reviews:data.filter(a=>edits[a.audit_id]).map(a=>({audit_id:a.audit_id,review_id:a.review_id,complete:!!complete(a.audit_id),...edits[a.audit_id]}))};let url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));let a=document.createElement('a');a.href=url;a.download='NSL_human_review_'+payload.reviewer_id.replace(/[^a-z0-9_-]/gi,'_')+'.json';a.click();URL.revokeObjectURL(url)};load();
</script></html>'''
payload=json.dumps(A,ensure_ascii=False).replace('<','\\u003c')
(OUT/'review.html').write_text(template.replace('__DATA__',payload),encoding='utf-8')
with zipfile.ZipFile(ROOT/'output/NSL_Annotation_Review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['review.html','annotations.json','audit_summary.json','README.txt']:z.write(OUT/n,n)
print('Packaged 200 annotations, four files. HTML bytes:',(OUT/'review.html').stat().st_size)
