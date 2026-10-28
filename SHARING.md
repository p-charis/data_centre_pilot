# Sharing the FORSEE data-centre pilot

## For coauthors who need to read the articles

Share **only** [`forsee_press_explorer.html`](forsee_press_explorer.html) through an access-restricted team channel, such as a Nextcloud share limited to named coauthors. It is a self-contained, offline HTML file (about 14–15 MB). Coauthors can download it and open it in Safari, Chrome or Firefox. Each result is one newspaper article; **Read full article** opens its complete text and highlights the dictionary matches. [`article_index.html`](article_index.html) is a script-free fallback with all 796 full articles in expandable entries. Both files contain press text and should be shared according to your team's corpus rights.

The explorer's **Boolean / advanced** search covers the full text of each screened article. Operators must be uppercase: `AND`, `OR`, `NOT`; parentheses group terms. Multiword terms work as phrases, and quotation marks make phrase boundaries explicit. For example, `data center OR data centre OR centre de données OR centres de données` finds alternative spellings and translations, while `data center AND data centre AND centre de données` requires all three in the same article. To combine concepts, try `(data centre OR centre de données) AND (energy OR énergie OR électricité)`. Search ignores accents and case, but does not stem words or automatically include plurals. Choose **Simple phrase** to search literally for a phrase containing words such as “and.” The two example buttons in the explorer fill in searches you can edit.

## For a public GitHub Pages overview

Use **only the contents of [`pages_site/`](pages_site/)**. Its `index.html` contains 796 article records with dates, outlets, counts and keyword flags, but **no article text, openings or snippets**. It offers the filters and newspaper charts, while the team copy remains separate.
Its Boolean search applies to article metadata only; it cannot search article text.

1. Create a GitHub repository, for example `forsee-data-centres-pilot`.
2. Place `pages_site/index.html` and `pages_site/.nojekyll` at the repository root and commit them. Do not add the raw corpora, local explorer, article index or `dashboard_data.json` to this publishing repository.
3. In the repository, open **Settings → Pages → Build and deployment**. Select **Deploy from a branch**, then `main` and `/(root)`; save.
4. Open the URL GitHub reports in Pages settings, normally `https://USERNAME.github.io/forsee-data-centres-pilot/`, and send it to coauthors together with your restricted Nextcloud link for the full-text team copy.

[GitHub's publishing instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) describe these steps. GitHub says Pages sites are [publicly accessible even when the repository is private](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). A genuinely [private Pages site](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site) requires an eligible GitHub Enterprise Cloud organisation with Pages access control. Repository privacy alone does not restrict the site.

## Reading the terms on the dashboard

“Nearby theme” is a **proximity flag**, not a discourse classification. The script looks for a theme dictionary term within 500 characters of a data-centre term. The dashboard counts each article once per theme; one article can count under ecology, energy and sovereignty simultaneously. “Ecology” includes climate, emissions, water and sustainability terms; “energy” includes electricity and grid terms; “sovereignty” is a narrow dictionary of explicit sovereignty, strategic autonomy and specific dependency expressions. The highlights mark the actual matched words. A term's appearance says nothing by itself about the author's or speaker's position.

The old “passages” were the first four windows around data-centre mentions **from the same article**, so overlapping windows could repeat text. The new reader presents one article once, with its matches in context.

## Actor layer

The team explorer now includes clickable theme dictionaries and an actor network with article evidence. The public Pages copy includes only dictionary actors and metadata; it omits unreviewed NER candidates and article passages. The `actor_analysis` folder is for team use and reproducibility; do not copy it into the public publishing repository. See [actor_analysis/METHOD.md](actor_analysis/METHOD.md) for the model versions, identity decisions and interpretation limits.
