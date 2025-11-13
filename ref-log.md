# Reflection – Multi-Agent Travel Planner (~300 words)

**What I learned:**  
Implementing a Planner→Reviewer loop clarified how distinct, well-scoped system prompts reduce role bleed. The Planner produced structured, assumption-driven itineraries without tools, while the Reviewer acted as a fact-checker grounded in sources. This separation made outputs more reliable and explainable, especially once I enforced a fixed markdown schema and a surgical “Delta List.”

**Challenges & fixes:**  
1) **Overpacking days:** Early plans exceeded 12 active hours. I added pacing rules and buffers in the Planner prompt, plus a Reviewer check that flags >90 minutes of unaccounted transit.  
2) **Fragile fact-checking:** Reviewer searches were too broad at first. I constrained queries to “official site + venue + hours/price” and required citing titles/URLs under “Validation Findings.”  
3) **Change propagation:** After one fix (e.g., a closed museum), budgets/times drifted. I added a “Budget & Timing Adjustments” section and required the Reviewer to propagate net changes.  
4) **Hallucinated prices:** Marked all costs “approx.” in Planner; Reviewer replaces with sourced values when available and tags ambiguity as “seasonal/dynamic.”

**Design choices / prompt ideas:**  
- **Planner persona:** “Decisive trip architect” with clustering and budget split (lodging/food/transport/activities).  
- **Reviewer persona:** “Strict fact-checker” prioritizing official sources, using compact ✅/⚠️ findings and numbered deltas.  
- **Format contract:** Stable markdown sections enable UI rendering and partial reprint of only changed lines.

**External tools or GenAI assistance (does not count toward 300 words):**  
- Used the provided `internet_search` tool for fact-checking opening hours, ticket prices, and long transfers.  
- LLM assistance helped refine the two system prompts and the Reviewer’s output schema. No keys were exposed.

