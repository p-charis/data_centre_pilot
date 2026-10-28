# Data centres in the FORSEE France and Ireland press corpus: pilot

**Status:** exploratory screening, 4 October 2026. This is a reproducible feasibility check, not an IRaMuTeQ classification or a finished content analysis.

For a closer, paper-oriented reading of the articles and candidate patterns, start with [READING_DOSSIER.md](READING_DOSSIER.md).

For coauthor access and GitHub Pages, see [SHARING.md](SHARING.md).

For the named-actor layer, start with [actor_analysis/ACTOR_FINDINGS.md](actor_analysis/ACTOR_FINDINGS.md) and its [method](actor_analysis/METHOD.md). Click a nearby-theme label in the explorer to inspect its French/English vocabulary. The actor network uses the same article filters; click nodes or connections for article evidence and selected-name highlights.

## Scope and conference fit

The relevant methodological precedent is [FORSEE D4.2, *Media Discourse Analysis*](https://zenodo.org/records/18503359), which examines newspaper coverage of AI. [D4.1](https://zenodo.org/records/18503032) examines social media and is useful mainly for the shared conceptual background. Here the material is the two raw IRaMuTeQ press files in `../Presse_LL_été_2025/France/france/FR_pol.txt` and `../Presse_LL_été_2025/Irlande/irish/IR_pol.txt`.

The [*Terminal* call, “Écologie et souveraineté dans le domaine numérique, entre conflictualité et alignement”](https://journals.openedition.org/terminal/12395), explicitly mentions the water, energy and land demands of sovereignty projects and asks how infrastructure policy may align or conflict with ecological aims. It requests a **two-page extended abstract by 30 October 2026**; a full article is due 15 February 2027. The [DIGISOV 2027 call](https://digisov2027.sciencesconf.org/) explicitly mentions AI-driven data-centre construction and welcomes comparative work on infrastructure dependency and contestation (axis 2). It requests an **abstract of at most 800 words, including references, by 30 October 2026**. The same empirical study could speak to both calls, with different emphasis: ecology–sovereignty articulation for *Terminal*, competing claims to infrastructure control and dependency for DIGISOV.

The [Commission's April 2025 AI Continent Action Plan](https://commission.europa.eu/topics/competitiveness/ai-continent_en) already proposed expanding EU data-centre capacity while prioritising sustainability, so part of the policy context overlaps the corpus. The [June 2026 Cloud and AI Development Act proposal](https://digital-strategy.ec.europa.eu/en/library/proposal-cloud-and-ai-development-act-cada) explicitly combines capacity, sustainability and autonomy, but **postdates the corpus**. It should be used as a present-day motivation, not as an explanation of 2022–June 2025 press discourse.

## What the files can support

| Measure | France | Ireland |
|---|---:|---:|
| Raw articles | 11,197 | 3,319 |
| Articles after removal of probable near duplicates | 11,193 | 3,316 |
| Articles mentioning a data centre | 642 (5.7%) | 154 (4.6%) |
| Articles with at least two mentions | 271 | 86 |
| AI term anywhere in the data-centre article | 638 (99.4%) | 150 (97.4%) |
| Ecology term near a data-centre mention | 210 (32.7%) | 82 (53.2%) |
| Energy/grid term near a data-centre mention | 296 (46.1%) | 93 (60.4%) |
| Explicit sovereignty term near a data-centre mention | 43 (6.7%) | 0 |
| Both ecology and sovereignty terms nearby | 20 (3.1%) | 0 |

“Near” means within 500 characters of a data-centre mention. The dictionaries are in `analyse.py`. The sovereignty dictionary is deliberately narrow: it captures explicit sovereignty, strategic autonomy, specific technological dependency and data-control expressions. It does **not** treat every mention of national policy, planning, security or investment as sovereignty. The energy dictionary includes demand, electricity and grid terms that are not automatically environmental criticism. Therefore these percentages are screening indicators, not proportions of frames or argumentative positions.

The 2025 coverage stops in **June 2025** (the last data-centre article is 30 June in France and 21 June in Ireland). The data-centre share of each yearly corpus rises from about 2–3% in 2022–23 to 6% in 2024 and 9–11% in the partial 2025 sample. This is a change *within this AI-focused corpus*, not a demonstrated increase in all newspaper coverage.

The two country files differ in size and publication mix. Among data-centre articles, *Les Échos* contributes 294/642 in France and *The Irish Times* 88/154 in Ireland. Articles may report on foreign data centres. Neither country file is a representative sample of national public opinion, and article language cannot by itself establish who supports or contests a project.

## Preliminary reading

There is ample material for a comparison and a narrower qualitative sample. The Irish subset contains recurring debate about grid connection, electricity demand, climate commitments, investment and the prospect of losing technology projects. The French subset contains debate about AI infrastructure growth and sovereignty, but also substantial discussion of electricity, carbon, land and local impacts. In the more sustained subset (at least two data-centre mentions), ecology terms occur nearby in **134/271** French and **58/86** Irish articles; explicit sovereignty terms occur nearby in **29/271** French and **0/86** Irish articles. **19** sustained French articles place both term families near data-centre mentions. These findings support a comparison of *how* the two concerns are brought together or kept apart. They do **not** support the strong version of the starting assumption that French coverage is predominantly sovereignty-oriented while Irish coverage is predominantly ecological.

Useful French leads include `FR-06161` (*Le Monde*, 15 June 2024, on the spread of data centres), `FR-07904` (*La Croix*, 15 October 2024, on Marseille), `FR-10896` (*Libération*, 19 June 2025, on Marseille), and `FR-10994` (*Le Monde*, 2 June 2025, on gigantism and energy-transition risk). Irish leads include `IE-02304` (*The Irish Times*, 2 January 2025, on the incoming government's treatment of data centres), `IE-02571` (*Irish Independent*, 18 February 2025, on fossil-fuel risk), `IE-02827` (*Irish Independent*, 29 May 2025, on capacity choices), and `IE-03024` (*The Irish Times*, 10 December 2024, on climate targets). IDs map to original article order and can be found in the dashboard.

## Proposed question and next analytical step

**Question:** How did French and Irish newspapers make AI-related data-centre expansion intelligible between 2022 and June 2025, and when did they cast electricity, land and climate constraints as limits to, costs of, or conditions for digital autonomy and economic development?

1. Code article relevance and location manually: domestic project/policy, foreign comparison, or passing mention. Use a purposive sample of the 271 French and 86 Irish articles with at least two mentions, then check a random sample of single-mention articles to estimate what that threshold misses. Check the seven probable near duplicates excluded by the script.
2. Develop equivalent, language-specific frame codes for resource constraint, ecological harm, green justification, grid and energy security, industrial competitiveness, control/dependency, local opposition and pro-development claims. Record **speaker and stance**, so actor claims are not flattened into article-level keywords. Treat “sovereignty” as an empirical vocabulary as well as an analytic concept.
3. Run separate IRaMuTeQ classifications on the focused French and Irish subsets, inspect characteristic segments and classes, and then compare the *interpretations* of classes across languages. The original AI-wide classes are not a substitute for this focused run. Use the manual coding to test whether the classes reflect the hypothesised frames and identify counterexamples.
4. Analyse 2024–June 2025 separately or include year as a supplementary variable, because AI infrastructure coverage becomes much more common then. Situate the press period against policies available at the time; mark post-June 2025 EU policy explicitly as subsequent context.

## Reproduce and explore

Run `python3 analyse.py` and then `python3 build_dashboard.py` in this folder. Open `forsee_press_explorer.html` directly in a browser; it works offline and has country, year, newspaper, nearby-theme and full-article Boolean search. Use uppercase `AND`, `OR`, `NOT` and parentheses; `OR` combines translations or spellings, while `AND` requires every phrase in one article. Search ignores accents and case but does not stem or expand plurals. See [SHARING.md](SHARING.md) for examples. One card represents one article; its reader opens the full article and highlights dictionary matches. `article_index.html` is a complete, script-free full-text index. **Both local HTML files contain complete press articles.** The separate `pages_site/index.html` is a metadata-only publishing copy; its search covers metadata only. `newspaper_distribution.csv` reports counts and outlet-specific rates; `screened_articles.csv` holds article-level flags, and `summary.json` holds totals. The explorer is a navigation aid, not an IRaMuTeQ replacement.
