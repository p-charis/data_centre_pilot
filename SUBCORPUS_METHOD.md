# Subcorpus selection and reproduction

Verified against the scripts and exported files on 5 October 2026.

The input files are `../Presse_LL_été_2025/France/france/FR_pol.txt` and `../Presse_LL_été_2025/Irlande/irish/IR_pol.txt`. Each block beginning with `****` is treated as one article. Selection searches the article body, excluding its starred metadata header.

An article is included when its original body contains at least one case-insensitive match to the following Python regular expression, before lemmatisation:

France:
```regex
\b(?:centres? de donn[ée]es|data[ -]?cent(?:er|re)s?|centres? informatiques?)\b
```

Ireland:
```regex
\b(?:data[ -]?cent(?:er|re)s?|server farms?)\b
```

The alternatives are combined with OR. The English data-centre variants cover singular/plural, center/centre, and a single space, ASCII hyphen or no separator. French also includes centre(s) de données/donnees and centre(s) informatique(s). Irish also includes server farm(s). There is no requirement for AI, ecology, energy or sovereignty vocabulary. No two-mention threshold, geographical relevance judgement or additional date filter was applied.

These are the exact historical screening patterns. They do not match `centre des données`, underscore-separated compounds or phrases broken by a newline. They are not identical to the dashboard's later accent/punctuation-normalised Boolean search. `centre informatique` can also retrieve uses needing manual relevance checking. The two language dictionaries are not a claim of perfect conceptual equivalence.

## Duplicate handling

Before selection, a probable duplicate is excluded when a previously retained article has the same date, source and first 100 characters after whitespace collapse; body lengths differ by less than 10% of the longer body; and Python SequenceMatcher similarity of their first 1,500 original body characters exceeds 0.98. Comparisons are case-sensitive. Four French and three Irish articles were excluded overall. Only one excluded article matched the data-centre dictionary: original Irish article 1,143 (`IE-01143`). Thus the raw phrase search gives 642 French and 155 Irish articles; removing that probable duplicate gives 642 and 154.

## Export and IRaMuTeQ comparison

`prepare_iramuteq.py` uses the selected IDs in `dashboard_data.json` to copy complete original articles in original order. It retains the original starred metadata and appends a tracing variable such as `*dcid_FR00001`. It trims outer whitespace around the header/body and writes UTF-8. It does not lemmatise, translate, replace phrases, retain only matched segments, or alter internal article wording.

For an independent IRaMuTeQ selection, reproduce the OR vocabulary above and retain the complete texts containing the phrases. A selection using isolated words such as `data`, `centre` or `données`, or exporting only matching segments, will differ. Check whether your version searches surface forms, lemmas or recognised expressions: the original selection searches raw phrases. Deduplicate the Irish result as above. Compare the selected original article IDs, not only total counts. `screened_articles.csv` contains the expected IDs; the exported files contain their corresponding `*dcid_...` tags. Exact GUI operations depend on the IRaMuTeQ version and phrase-search facilities; Python regex syntax should not be assumed to work in its search field.

The existing exports have been checked: `FR_data_centres_all.txt` has 642 texts, and `IE_data_centres_all.txt` has 154, with IDs/order identical to the screening table. The separate 271/86 figures in the dossier describe articles with two or more mentions; those are not the current exported subcorpora. The 500-character proximity rule only supplies theme flags, and does not select or truncate these exports.

To reproduce the current exports from the original files, run in this directory:
```sh
python3 analyse.py
python3 prepare_iramuteq.py
```

## Reusing the explorer

`explorer.template` is the presentation/search layer. Language is an explicit article field, `language`, populated from `LANGUAGES` in `analyse.py` for these source corpora (French and English). It is source-corpus metadata, not automatic language detection. The language selector derives its options from the records and combines with the other filters. Missing language values appear as Unspecified. Mixed-language corpora should supply language per article.

The import/screening and build scripts still contain FORSEE-specific paths, data-centre/theme dictionaries, dates and labels. Adding an unrelated IRaMuTeQ corpus will require adapting those inputs and labels; the template does not yet directly import arbitrary IRaMuTeQ files. Both local and public explorers have the language filter; the public copy retains metadata only. The dashboard continues to search the 796 selected articles, not all articles in the original AI corpora.
