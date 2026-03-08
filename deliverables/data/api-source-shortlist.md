# Open API Source Shortlist (Phase 0)

## Selection criteria
- Public/open access or low-cost entry.
- Strong AI-news signal and update frequency.
- Stable API docs and legal usage clarity.
- Ability to capture publish timestamp and URL.

## Candidate sources
1. NewsAPI
   - Use: broad tech and AI media aggregation.
   - Data role: headline and article metadata.
   - Integration note: add source-level allowlist to reduce noise.

2. Hacker News API
   - Use: builder-centric trending stories.
   - Data role: engagement proxy via points/comments.
   - Integration note: enrich with linked article domain credibility.

3. arXiv API
   - Use: research and preprint signals.
   - Data role: technical depth and novelty.
   - Integration note: classify topic relevance to practical AI themes.

4. Reddit API (selected subreddits)
   - Use: community attention velocity.
   - Data role: sentiment and discussion intensity.
   - Integration note: strict subreddit allowlist and moderation filters.

5. GitHub Trending (public feed alternatives)
   - Use: open-source project momentum.
   - Data role: ecosystem activity signal.
   - Integration note: map repos to AI categories before scoring.

## Fallback source set
- If one primary source is down, prioritize remaining three with adaptive score normalization.

## Verification checklist before implementation
- Confirm authentication model.
- Confirm rate-limit policy.
- Confirm redistribution rights for snippets.
- Confirm required attribution format.
