"""Shared button and link styles, including the standalone tool pages."""

CONTROL_STYLES = """
:root{--action:#2457e6;--action-hover:#1844bf;--action-soft:#edf3ff;--action-line:#c7d5f2;}
a:focus-visible,button:focus-visible,summary:focus-visible,select:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #7b9df3;outline-offset:3px;}
:is(.ui-button,.button-link,.portfolio-page .ink-button,.portfolio-page .cover-link,.back-link-button,.hero-link-button,.top-link-button,.lesson-controls a,.writer-page button,.page button,.runtime-overlay button){
  display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;
  padding:10px 20px;border:1px solid transparent;border-radius:10px;background:var(--action);color:#fff;
  font:600 14px/1.5 'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;text-align:center;
  text-decoration:none;cursor:pointer;box-sizing:border-box;
  transition:background-color .15s,border-color .15s,box-shadow .15s;
}
:is(.ui-button,.button-link,.portfolio-page .ink-button,.portfolio-page .cover-link,.back-link-button,.hero-link-button,.top-link-button,.lesson-controls a,.writer-page button,.page button,.runtime-overlay button):hover{
  background:var(--action-hover);border-color:var(--action-hover);color:#fff;text-decoration:none;
}
:is(.ui-button.secondary,.button-link.secondary,.portfolio-page .quiet-link,.back-link-button,.hero-link-button,.top-link-button,.lesson-controls [data-previous],.writer-page button.secondary,.writer-page .runtime-toggle,.writer-page .runtime-close,.page button.secondary,.runtime-overlay button.secondary){
  background:#fff;color:#25416f;border:1px solid var(--action-line);box-shadow:none;
}
:is(.ui-button.secondary,.button-link.secondary,.portfolio-page .quiet-link,.back-link-button,.hero-link-button,.top-link-button,.lesson-controls [data-previous],.writer-page button.secondary,.writer-page .runtime-toggle,.writer-page .runtime-close,.page button.secondary,.runtime-overlay button.secondary):hover{
  background:var(--action-soft);color:var(--action-hover);border-color:#8ca9ed;
}
.portfolio-page .quiet-link{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 15px;border-radius:10px;font-size:13px;font-weight:600;text-align:center;}
:is(.ui-link,.portfolio-page .text-link,.journal-notes .card>a,.post-card .read-more,.lesson-help-link){
  color:var(--action);font-size:14px;font-weight:600;text-decoration:underline;text-decoration-color:#acbfee;
  text-underline-offset:5px;border:0;padding:8px 0;min-height:40px;display:inline-flex;align-items:center;
}
:is(.ui-link,.portfolio-page .text-link,.journal-notes .card>a,.post-card .read-more,.lesson-help-link):hover{color:var(--action-hover);text-decoration:underline;text-decoration-color:currentColor;}
.portfolio-page .quick-index a{border:1px solid var(--action-line);background:#fff;border-radius:8px;padding:8px 14px;min-height:40px;color:#25416f;}
.portfolio-page .quick-index a:hover{background:var(--action-soft);border-color:#8ca9ed;color:var(--action-hover);}
.portfolio-page .project-index a{border-radius:8px;color:#25416f;min-height:44px;}
.portfolio-page .project-index a:hover{background:var(--action-soft);color:var(--action-hover);}
.portfolio-page .other-work>a:hover{background:var(--action-soft);}
.portfolio-page .other-work>a:hover strong{text-decoration:underline;text-underline-offset:5px;}
.lesson-controls a:last-child{background:var(--action);border-radius:10px;}
.lesson-controls a:last-child:hover{background:var(--action-hover);}
.lesson-toolbar button{background:var(--action-soft);color:var(--action);border:1px solid var(--action-line);border-radius:8px;padding:8px 12px;min-height:40px;text-decoration:none;font-weight:600;}
.lesson-toolbar button:hover{background:#dee9ff;border-color:#8ca9ed;}
.lesson-route-choices button{border-radius:12px;background:#fff;border-color:#d0dbea;transition:background-color .15s,border-color .15s;}
.lesson-route-choices button:hover{border-color:#8ca9ed;background:#f6f9ff;}
.lesson-route-choices button[aria-pressed='true']{background:var(--action-soft);border-color:var(--action);}
.lesson-route-choices button[aria-pressed='true']:after{color:var(--action);}
.guide-copy{border-radius:7px;min-height:36px;padding:6px 12px;border-color:#637494;background:#25354f;color:#fff;}
.guide-copy:hover{background:#344a70;}
.guide-code.is-prompt .guide-copy{background:#fff;color:var(--action);border-color:#acbfee;}
.guide-code.is-prompt .guide-copy:hover{background:#e3ecff;}
.lesson-os-options{border-color:var(--action-line);border-radius:10px;background:#f6f9ff;}
.lesson-os-options label{border-radius:7px;}
.lesson-os-options label:has(:checked){background:var(--action);color:#fff;}
.lesson-os-options input{accent-color:#fff;}
.writer-page .runtime-toggle{min-width:0;font-size:14px;line-height:1.5;padding:10px 16px;}
.writer-page .runtime-close{margin:0;min-width:44px;padding:6px 10px;}
.writer-page .runtime-panel{top:54px;z-index:60;}
.page .hero-link-button{margin-left:0;}
.page button:disabled,.writer-page button:disabled,.runtime-overlay button:disabled{background:#e3e9f3;color:#627089;border-color:#d3ddeb;cursor:not-allowed;opacity:1;}
@media(max-width:620px){.portfolio-page .quiet-link{padding:8px 12px;font-size:12px;}.portfolio-page .quick-index a{padding:8px 12px;}.lesson-controls{gap:10px;flex-wrap:wrap;}.lesson-controls a{font-size:12px;padding:9px 12px;}.writer-page .runtime-panel{top:56px;}}
@media(prefers-reduced-motion:reduce){a,button{transition:none!important;}}
"""
