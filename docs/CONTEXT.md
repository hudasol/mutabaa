# Context: the public commitments and who made them

This is the only prose document in the repository that names real entities. Everything here comes from public sources listed below. Nothing in this repository is endorsed by, produced with, or affiliated with any entity named here. Mutabaa is a student prototype and a proposal seed, not a deployment and not an official tool.

## Why these commitments are tracked

In 2025 and 2026 the UAE federal government and the Government of Abu Dhabi announced AI transformation targets that leaders will be assessed on:

- **Federal.** A UAE Cabinet meeting statement (S01, 23 April 2026) set the target of moving 50% of federal government sectors, services and operations to agentic AI within two years, and said that ministers and entity heads would be assessed on adoption. Media reports of a later workshop of the Higher Committee for Agentic AI (S06, S07, S09) describe a self assessment classification, a federal platform and a national gateway; these reports are graded as secondary media.
- **Abu Dhabi.** The Abu Dhabi Government Digital Strategy 2025 to 2027 (S02, launched by the Abu Dhabi Media Office) and updates from the Department of Government Enablement (DGE) (S03, S04, S05) describe an AI native government by 2027, a sovereign cloud, digitised processes and a target number of AI solutions. A training programme announced by the Abu Dhabi Media Office (S13) and a cloud agreement involving Microsoft and Core42 (S14) are recorded as context and evidence.
- **National.** The We the UAE 2031 vision (S11) and the UAE National Strategy for Artificial Intelligence 2031 (S12) set the longer horizon.

These targets are tracked because the wording of a public commitment decides whether anyone outside the owning entity can check it. The repository records what each commitment says, what it does not yet say (a number, a unit, a dated deadline, an owner, a way to measure it, defined terms), and what public evidence exists. It does not judge any entity, and "no public evidence" never means "not done".

## Sources

The authoritative list is `data/real/sources.json`. Extraction notes are in `data/real/extracts/` and are protected by a hash.

| Id | Publisher | Kind | Link |
|---|---|---|---|
| S01 | UAE Media Office | official statement | https://mediaoffice.ae/en/news/2026/april/23-04/mohammed-bin-rashid-chairs-uae-cabinet-meeting |
| S02 | Abu Dhabi Media Office | official statement | https://www.mediaoffice.abudhabi/en/government-affairs/abu-dhabi-government-launches-digital-strategy-2025-2027/ |
| S03 | Department of Government Enablement | official self report | https://www.dge.gov.ae/en/news/adg-digital-strategy-update-2025 |
| S04 | Department of Government Enablement | official self report | https://www.dge.gov.ae/en/news/2025-dge-highlights |
| S05 | Department of Government Enablement | official self report | https://www.dge.gov.ae/en/news/2026-adg-microsoft |
| S06 | Gulf News | secondary media | https://gulfnews.com/technology/uae-targets-50-of-government-services-and-operations-to-be-powered-by-agentic-ai-1.500643982 |
| S07 | Artificial Intelligence News | secondary media | https://www.artificialintelligence-news.com/news/agentic-ai-in-government-uae-classification/ |
| S08 | Artificial Intelligence News | secondary media | https://www.artificialintelligence-news.com/news/abu-dhabi-ai-training-government-employees/ |
| S09 | Middle East AI News | secondary media | https://www.middleeastainews.com/p/uae-government-deploys-agentic-ai |
| S10 | UAE Cabinet | official statement | https://uaecabinet.ae/en/news/uae-cabinet-chaired-by-mohammed-bin-rashid-approves-launch-of-first-integrated-regulatory-intelligence-ecosystem-in-uae-government |
| S11 | UAE Government Portal | official statement | https://beta.government.ae/en/about-the-uae/strategies-initiatives-and-awards/strategies-plans-and-visions/innovation-and-future-shaping/we-the-uae-2031-vision |
| S12 | UAE Government (ai.gov.ae) | official statement | https://ai.gov.ae/?p=2362 |
| S13 | Abu Dhabi Media Office | official statement | https://www.mediaoffice.abudhabi/en/government-affairs/department-of-government-enablement-abu-dhabi-launches-ainative-training-programme-in-collaboration-with-openai-microsoft-and-mbzuai/ |
| S14 | Abu Dhabi Media Office | official statement | https://www.mediaoffice.abudhabi/en/technology/abu-dhabi-government-accelerates-digital-strategy-with-landmark-microsoft-g42-partnership/ |

S10, S11 and S12 could not be reached by the automated verifier (two return HTTP 403 and one fails certificate validation). They are reported as unreachable. The verifier does not work around a block and never disables certificate checks.

## Leads not yet in the ledger

Items seen during research that could not be read directly. They are not used in any status.

| Lead | Where it was seen | Why it matters | What is needed |
|---|---|---|---|
| UAE Cabinet meeting statement of 18 May 2026: 80,000 federal employees to be trained as agentic AI experts across 5 occupational categories; a "Phase One" list of services | `mediaoffice.ae/en/news/2026/may/18-05/mohammed-bin-rashid-chairs-uae-cabinet-meeting`, seen during research and reported by media (S07) | Would give C03 an official source, move claim K05 from "not in official statement" to official, and may be the official basis for the "first package of services" in E08 | The page could not be fetched without permission. A person should open it, read it, and add it as a source with an extraction note |
| WAM article pages | `wam.ae/en/article/...` | Official wire copy of several Cabinet statements | Article pages return no body text to the fetch tool; read them in a browser |

## Review lenses

The four review documents in `docs/reviews/` are written from the point of view of kinds of organisation (an executive office, a defence technology group, a research institute, a programme office). They are simulations written by the author from public information. They are not the view of any real organisation and imply no affiliation.

## Reference points

Public commitment trackers informed the neutral default and the written status rules: the Government of Canada Mandate Letter Tracker and the PromiseTracker tool from Code for Africa. They are cited as examples of method only.

## What this document does not say

It does not say whether any target is on track, and it does not rank or rate any entity. Synthetic data in this repository describes no real entity.
