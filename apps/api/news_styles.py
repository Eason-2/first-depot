"""News presentation shared by the home feed and the briefing index."""

NEWS_STYLES = """
.news-room{padding:52px 0 20px;}
.news-masthead{border-top:4px solid #2457e6;border-bottom:1px solid #dce5f2;padding:26px 0 30px;}
.news-edition{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:22px;}
.news-edition strong{font-size:17px;color:#2457e6;}.news-edition>span{font-size:12px;color:#607086;}
.news-masthead h1{font-size:clamp(30px,4.5vw,52px);font-weight:750;letter-spacing:-.04em;line-height:1.3;}
.news-masthead>p{font-size:16px;margin:16px 0 24px;max-width:700px;}
.news-topics{display:flex;flex-wrap:wrap;gap:20px;font-size:12px;color:#465875;}
.news-disclosure{font-size:12px;color:#607086;margin:18px 0 32px;line-height:1.8;}
.news-archive-heading{display:flex;align-items:baseline;justify-content:space-between;gap:16px;border-bottom:1px solid #dce5f2;padding-bottom:14px;}
.news-archive-heading h2{font-size:19px;margin:0;}.news-archive-heading span{font-size:12px;color:#607086;}
.news-archive .news-item{border-bottom:1px solid #dce5f2;padding:26px 0;max-width:960px;}
.news-archive .news-item h2{font-size:23px;line-height:1.55;margin:12px 0;overflow-wrap:anywhere;}
.news-archive .news-item h2 a{color:#17263d;font-weight:650;}.news-archive .news-item h2 a:hover{color:#2457e6;}
.news-archive .news-item:first-of-type{padding:30px;background:#f0f5ff;border:1px solid #dbe7ff;border-radius:12px;margin:24px 0 0;max-width:none;}
.news-archive .news-item:first-of-type h2{font-size:30px;max-width:900px;}
.news-meta{display:flex;align-items:center;flex-wrap:wrap;gap:8px 14px;font-size:11px;color:#607086;line-height:1.65;}
.news-type{display:inline-block;color:#2457e6;background:#e9f0ff;border-radius:4px;padding:3px 7px;font-weight:650;white-space:nowrap;}
.news-meta time{font-variant-numeric:tabular-nums;}
.news-sources{overflow-wrap:anywhere;}
.home-news{min-width:0;}
.home-news .editorial-heading{margin-bottom:14px;}
.home-news .folio-label{color:#2457e6;font-weight:700;}
.home-news .editorial-heading h2{font-size:30px;}
.home-news .dispatch-list{border-top:3px solid #2457e6;}
.home-news .dispatch-row{display:block;position:relative;padding:23px 0;border-top:1px solid #dce5f2;}
.home-news .dispatch-row:first-child{border-top:0;}
.home-news .dispatch-row h3{font-size:19px;line-height:1.65;margin:10px 0 0;}
.home-news .dispatch-row:first-child h3{font-size:25px;line-height:1.5;}
.home-news .dispatch-row h3 a{font-weight:650;}
.home-news .dispatch-row h3 a:hover{text-decoration:underline;text-underline-offset:5px;}
.home-news .dispatch-row h3 a::after{content:'';position:absolute;inset:0;}
.home-news .dispatch-row:has(a:focus-visible){outline:3px solid #7b9df3;outline-offset:5px;}
.home-news .dispatch-row:has(a:focus-visible) a{outline:none;}
.home-news .news-meta time{font-size:11px;color:#607086;}
.home-news .section-caption{font-size:14px;}
@media(max-width:720px){.news-room{padding-top:30px;}.news-edition{align-items:flex-start;flex-direction:column;gap:8px;}.news-masthead{padding-top:20px;}.news-archive .news-item:first-of-type{padding:22px;}.news-archive .news-item:first-of-type h2{font-size:24px;}.news-archive .news-item h2{font-size:20px;}.home-news .editorial-heading{align-items:flex-start;flex-direction:column;gap:14px;}.home-news .editorial-heading h2{font-size:27px;}.home-news .dispatch-row:first-child h3{font-size:22px;}}
"""
