"""Editorial presentation for the home and project pages only."""

PORTFOLIO_STYLES = """
.portfolio-shell {
  --ink:#17263d; --muted:#607086; --teal:#2457e6; --orange:#2457e6;
  --line:#dce5f2; --paper:#fff; --canvas:#fff;
  --display:'Inter','Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;
  background:var(--canvas); color:var(--ink);
}
.portfolio-shell .site-shell {padding:0 36px 36px;}
.portfolio-shell main,.portfolio-shell .site-header,.portfolio-shell .site-footer {max-width:1180px;}
.portfolio-shell .site-header {background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);min-height:96px;}
.portfolio-shell .site-brand {color:var(--ink);}
.portfolio-shell .site-brand-mark {background:var(--ink);}
.portfolio-shell .site-brand small {color:var(--muted);font-weight:400;}
.portfolio-shell .site-nav {background:transparent;box-shadow:none;border:0;padding:0;gap:6px;}
.portfolio-shell .site-nav-link {color:var(--ink);font-size:14px;padding:8px 12px;}
.portfolio-shell .site-nav-link:hover {background:#f0f5ff;color:var(--teal);}
.portfolio-shell .site-nav-link.is-active {background:#edf3ff;color:var(--teal);border-color:#c7d5f2;}
.portfolio-page {overflow-wrap:anywhere;}
.portfolio-page a {color:inherit;}
.portfolio-page a:hover {text-decoration:none;color:var(--teal);}
.portfolio-page a:focus-visible {outline:2px solid var(--teal);outline-offset:5px;}
.portfolio-page h1,.portfolio-page h2,.portfolio-page h3 {font-weight:650;}
.portfolio-page p {line-height:1.85;}
.portfolio-page .folio-label {font-size:11px;font-weight:500;letter-spacing:.12em;color:var(--muted);margin:0 0 20px;}
.folio-label span {padding:0 12px;color:#8393aa;}
.notebook-opening {display:grid;grid-template-columns:1.2fr 1fr;gap:100px;padding:72px 0 64px;align-items:center;}
.opening-copy h1 {font-family:var(--display);font-weight:750;font-size:clamp(76px,8vw,108px);line-height:1.15;letter-spacing:-.065em;margin:0 0 26px;}
.portfolio-page em {font-style:normal;color:var(--teal);}
.opening-intro {font-size:17px;margin-bottom:26px;}

.opening-actions {display:flex;align-items:center;flex-wrap:wrap;gap:12px;}

.starter-cover {position:relative;background:#eef4ff;border:1px solid #d6e3ff;padding:28px 34px 20px;border-radius:18px;}
.cover-top,.cover-bottom {display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:11px;letter-spacing:.1em;}
.cover-top {border-bottom:1px solid #c9d9f6;padding-bottom:18px;}
.cover-top span:last-child {font-family:var(--display);font-size:26px;line-height:1;}
.portfolio-page .cover-margin {font-size:12px;margin:28px 0 12px;color:#526888;}
.starter-cover h2 {font-family:var(--display);font-size:clamp(29px,3vw,40px);line-height:1.6;letter-spacing:-.03em;margin:0 0 18px;}
.starter-cover h2 span {color:var(--teal);}
.portfolio-page .cover-caption {font-size:13px;color:#526888;margin-bottom:20px;}
.cover-link {width:100%;margin:6px 0 14px;}
.cover-bottom {color:#526888;font-size:10px;margin-top:10px;letter-spacing:.03em;}
.quick-index {display:flex;align-items:center;gap:32px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:17px 0;font-size:13px;}
.quick-index>span {color:var(--muted);margin-right:auto;font-size:12px;}
.quick-index a {display:flex;align-items:center;gap:24px;font-weight:500;padding:5px 0;}
.notebook-section {padding:80px 0 0;}
.editorial-heading {display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:30px;}
.editorial-heading .folio-label {margin-bottom:12px;}
.editorial-heading h2 {font-family:var(--display);font-size:34px;margin:0;}
.home-feature {display:grid;grid-template-columns:1.15fr 1fr;align-items:center;gap:64px;}
.publishing-sheet {margin:0;background:#132c56;color:#fff;padding:26px 32px;min-width:0;}
.publishing-sheet figcaption {display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:1px solid #3f5b83;padding-bottom:18px;font-size:14px;}
.publishing-sheet figcaption span:last-child {font-size:10px;color:#b9cce8;letter-spacing:.06em;}
.source-line {display:flex;flex-wrap:wrap;gap:8px;margin:22px 0;font-size:10px;font-family:monospace;color:#dce8fb;}
.source-line span {border:1px solid #4e6a90;padding:4px 9px;}
.publishing-flow {list-style:none;margin:0;padding:0;}
.publishing-flow li {display:flex;gap:20px;align-items:center;margin:0;padding:16px 0;border-top:1px solid #354f77;}
.publishing-flow li>span {font-family:var(--display);font-size:28px;color:#a5c8ff;}
.publishing-flow strong {font-size:17px;font-weight:500;display:block;}
.publishing-flow small {display:block;font-size:11px;color:#b9cce8;margin-top:5px;}
.portfolio-page .sheet-footnote {font-size:11px;margin:18px 0 0;color:#b9cce8;}
.sheet-footnote span {margin-right:8px;}
.feature-copy h3 {font-family:var(--display);font-size:34px;line-height:1.5;margin-bottom:22px;}
.feature-copy h3 a {font-weight:500;}
.feature-copy>p:not(.folio-label) {font-size:15px;max-width:390px;}
.feature-copy .text-link {margin-top:6px;}
.other-work {display:grid;grid-template-columns:1fr 1fr;margin-top:28px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);}
.other-work>a {display:grid;grid-template-columns:26px 1fr;gap:18px;align-items:center;padding:26px 26px 26px 0;}
.other-work>a+ a {border-left:1px solid var(--line);padding-left:26px;padding-right:0;}
.work-index {font-family:var(--display);font-size:18px;color:var(--teal);}
.other-work strong {font-size:16px;font-weight:500;display:block;}
.other-work small {font-size:12px;color:var(--muted);font-weight:400;display:block;margin-top:5px;}
.reading-desk {display:grid;grid-template-columns:1.65fr 1fr;gap:56px;padding:56px 0 64px;border-bottom:1px solid var(--line);}
.reading-desk .editorial-heading {margin-bottom:20px;}
.portfolio-page .section-caption {font-size:13px;margin-bottom:24px;}






.journal-column {border-left:1px solid var(--line);padding-left:36px;}
.journal-notes .card {border:0;border-top:1px solid var(--line);border-radius:0;background:none;padding:24px 0;}
.journal-notes .card-kicker {font-size:11px;color:var(--muted);font-weight:400;}
.journal-notes h3 {font-family:var(--display);font-size:21px;line-height:1.65;margin:12px 0;}
.journal-notes h3 a {font-weight:500;}
.journal-notes .card>p:not(.card-kicker) {font-size:13px;}
.journal-notes .card>a {font-size:12px;}
.closing-note {margin-top:64px;border-top:1px solid var(--line);padding:32px 0 0;display:flex;justify-content:space-between;gap:20px;align-items:center;}
.portfolio-page .closing-note p {font-family:var(--display);font-size:18px;margin:0;color:var(--ink);}
.portfolio-shell .site-footer {margin-top:64px;border-color:var(--line);font-size:12px;color:var(--muted);}
.portfolio-shell .site-footer a {color:var(--ink);}
.projects-opening {padding:60px 0 48px;}
.projects-opening>div {display:grid;grid-template-columns:1.3fr 1fr;gap:60px;align-items:end;}
.projects-opening h1 {font-family:var(--display);font-size:clamp(52px,6vw,76px);line-height:1.3;letter-spacing:-.05em;}
.projects-opening>div>p {font-size:15px;margin:0 0 8px;}
.project-index {display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--ink);border-bottom:1px solid var(--line);}
.project-index a {display:flex;align-items:center;gap:16px;padding:21px 22px;font-size:14px;font-weight:500;}
.project-index a:first-child {padding-left:0;}
.project-index a+a {border-left:1px solid var(--line);}
.project-index a>span:first-child {font-family:var(--display);color:var(--teal);}

.project-story {padding:64px 0;border-bottom:1px solid var(--line);scroll-margin-top:116px;}
.story-heading {display:flex;align-items:flex-start;gap:32px;margin-bottom:40px;}
.story-number {font-size:52px;line-height:1;font-family:var(--display);color:var(--teal);flex:0 0 62px;white-space:nowrap;}
.story-heading .folio-label {margin-bottom:12px;}
.story-heading h2 {font-family:var(--display);font-size:34px;margin:0 0 10px;}
.story-heading>div>p:last-child {font-size:12px;margin:0;}
.publisher-layout {display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start;}
.story-prose {min-width:0;max-width:540px;}
.portfolio-page .story-lead {font-size:24px;font-family:var(--display);line-height:1.65;color:var(--ink);margin-bottom:22px;}
.story-prose>p {font-size:15px;margin-bottom:18px;}
.story-prose h3 {font-size:21px;font-family:var(--display);margin:28px 0 14px;}
.story-prose h3:first-child {margin-top:0;}
.project-actions {display:flex;align-items:center;flex-wrap:wrap;gap:26px;margin:24px 0;}
.portfolio-page .tag-row {gap:6px 18px;margin-top:24px;}
.portfolio-page .tag {background:none;color:var(--muted);border-radius:0;padding:0;font-size:11px;font-weight:400;font-family:'SFMono-Regular',Consolas,monospace;}
.project-afterword {display:grid;grid-template-columns:140px 1fr;gap:32px;background:#f0f5ff;padding:24px 28px;margin-top:36px;}
.project-afterword>span {color:var(--teal);font-size:12px;}
.portfolio-page .project-afterword p {font-size:13px;margin:0;}
.listing-layout {display:grid;grid-template-columns:1fr 1.05fr;gap:64px;align-items:center;}
.listing-sheet {border:1px solid #cfdaed;padding:30px;background:#f2f6fc;}
.listing-input,.listing-output {display:flex;flex-direction:column;gap:8px;padding:14px 0;}
.listing-input>span,.listing-output>span {font-size:11px;color:var(--muted);}
.listing-input strong,.listing-output strong {font-size:17px;font-weight:500;}
.listing-fields {display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#d5e0f2;border:1px solid #d5e0f2;margin:14px 0;}
.listing-fields span {background:#fff;padding:15px;font-size:13px;}
.listing-check {display:flex;gap:12px;align-items:start;padding:12px 0;}
.listing-check>span {color:var(--teal);font-size:26px;}
.portfolio-page .listing-check p {font-size:12px;margin:0;}
.listing-check strong {font-weight:500;color:var(--teal);}
.listing-output {border-top:1px solid #d5e0f2;margin-top:16px;}
.support-layout {display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start;}
.answer-sheet {background:#edf4ff;padding:32px;}
.answer-sheet h3 {font-family:var(--display);font-size:34px;line-height:1.55;margin:0 0 28px;}
.answer-route {display:grid;grid-template-columns:58px 1fr;gap:14px;border-top:1px solid #c7d8f0;padding:18px 0;align-items:baseline;font-size:12px;}
.portfolio-page .answer-route p {font-size:13px;color:#405779;margin:0;}
.portfolio-page .answer-note {font-size:10px;margin:12px 0 0;color:#586f90;}
@media(min-width:821px) and (max-width:1060px) {
  .portfolio-shell .site-header {gap:16px;}
  .portfolio-shell .site-nav {gap:0;}
  .portfolio-shell .site-nav-link {font-size:13px;padding:8px;}
}
@media(max-width:980px) {
  .notebook-opening {gap:48px;}
  .home-feature,.publisher-layout,.listing-layout,.support-layout {gap:32px;}
  .reading-desk {gap:32px;grid-template-columns:1.3fr 1fr;}
  .journal-column {padding-left:24px;}
  .projects-opening>div {gap:32px;}
}
@media(max-width:720px) {
  .portfolio-shell .site-shell {padding:0 22px 28px;}
  .notebook-opening {grid-template-columns:1fr;gap:36px;padding:40px 0;}
  .opening-copy h1 {font-size:82px;}
  .opening-intro {font-size:15px;}
  .starter-cover {padding:24px;}
  .starter-cover h2 {font-size:34px;line-height:1.45;}
  .quick-index {flex-wrap:wrap;gap:8px 24px;padding:16px 0;}
  .quick-index>span {width:100%;}
  .quick-index a {gap:12px;font-size:12px;}
  .notebook-section {padding-top:48px;}
  .editorial-heading h2 {font-size:29px;}
  .editorial-heading {gap:12px;margin-bottom:24px;}
  .home-feature,.publisher-layout,.listing-layout,.support-layout,.reading-desk {grid-template-columns:1fr;gap:28px;}
  .feature-copy h3 {font-size:29px;}
  .feature-copy>p:not(.folio-label) {max-width:none;}
  .publishing-sheet {padding:24px;}
  .other-work {grid-template-columns:1fr;}
  .other-work>a {padding:22px 0;gap:12px;}
  .other-work>a+a {padding:22px 0;border-left:0;border-top:1px solid var(--line);}
  .other-work strong {font-size:15px;}
  .reading-desk {padding-top:48px;gap:40px;}
  .journal-column {border-left:0;padding:28px 24px 20px;background:#f0f5ff;}
  .closing-note {flex-direction:column;align-items:flex-start;margin-top:40px;padding-top:28px;gap:12px;}
  .portfolio-page .closing-note p {font-size:17px;}
  .projects-opening {padding:38px 0 30px;}
  .projects-opening>div {grid-template-columns:1fr;gap:24px;}
  .projects-opening h1 {font-size:54px;}
  .projects-opening>div>p {font-size:14px;}
  .project-index a {padding:16px 10px;gap:7px;font-size:12px;}
  .story-heading {gap:18px;margin-bottom:28px;}
  .story-number {font-size:36px;flex-basis:44px;}
  .story-heading h2 {font-size:27px;line-height:1.5;}
  .story-heading .folio-label {font-size:10px;}
  .project-story {padding:40px 0;scroll-margin-top:20px;}
  .project-afterword {grid-template-columns:1fr;gap:12px;padding:22px;}
  .listing-sheet,.answer-sheet {padding:24px;}
  .answer-sheet h3 {font-size:30px;}
  .answer-route {grid-template-columns:48px 1fr;gap:8px;}
}
@media(max-width:380px) {
  .portfolio-shell .site-shell {padding-left:16px;padding-right:16px;}
  .portfolio-shell .site-nav-link {padding:7px 3px;font-size:12px;}
  .opening-copy h1 {font-size:72px;}
  .quick-index {column-gap:16px;}
  .publishing-sheet,.starter-cover,.listing-sheet,.answer-sheet {padding:20px;}
  .source-line {gap:6px;}
  .source-line span {padding:3px 6px;}
  .project-index a {font-size:11px;}
}
"""
