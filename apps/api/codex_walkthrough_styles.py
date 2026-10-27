"""Visual walkthrough styles; each illustration has its own useful layout."""

WALKTHROUGH_STYLES = """
.tutorials-page .lesson-frame{grid-template-columns:184px minmax(0,1fr);gap:26px;}
.tutorials-page .lesson-sidebar{padding-right:14px;}
.tutorials-page .lesson-paper{background:transparent;border:0;box-shadow:none;}
.tutorials-page .lesson-step{padding:24px 0 0;}
.tutorials-page .lesson-toolbar{padding:12px 0;}
.tutorials-page .lesson-step-header{margin-bottom:20px;gap:14px;}
.tutorials-page .lesson-step-number{font:500 28px/1.4 'Segoe UI',sans-serif;color:#8fa8cd;}
.tutorials-page .lesson-step h2{font-size:26px;}
.tutorials-page .lesson-controls{margin:0;padding:18px 0;}
.tutorials-page .lesson-route-choices{max-width:540px;margin:0 0 20px;gap:10px;}
.tutorials-page .lesson-route-choices button{min-height:90px;padding:15px;}
.tutorials-page .lesson-route-choices strong{font-size:16px;}
.tutorials-page .lesson-route-choices button[aria-pressed='true']{padding:14px;}
.lesson-text{margin:20px 0;border-top:1px solid #dce5f2;}
.lesson-text>summary{font-size:13px;color:#526888;padding:16px 0;cursor:pointer;}
.lesson-text>div{padding:8px 18px 20px;background:#fff;border:1px solid #dce5f2;border-radius:8px;}
.walkthrough{scroll-margin-top:112px;min-width:0;}
.walk-reading{display:flex;justify-content:space-between;gap:12px;color:#607086;font-size:12px;margin-bottom:14px;}
.walk-reading>[data-scene-count]{color:#2457e6;font-weight:650;}
.walk-scene{scroll-margin-top:110px;min-width:0;}
.walk-scene-heading{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:14px;}
.walk-scene-heading>span{font-size:11px;color:#607086;border:1px solid #dce5f2;padding:4px 7px;border-radius:4px;}
.lesson-step .walk-scene-heading h3{font-size:19px;font-weight:650;margin:0;line-height:1.5;}
.walk-layout{display:grid;grid-template-columns:minmax(0,3.8fr) minmax(0,1fr);gap:18px;align-items:start;}
.walk-display{margin:0;min-width:0;border:1px solid #d4deec;border-radius:10px;overflow:hidden;background:#edf2f8;box-shadow:0 8px 24px #17263d08;}
.walk-display>figcaption{padding:10px 16px;font-size:10px;color:#53667f;background:#f6f8fc;border-bottom:1px solid #dce5f2;}
.walk-instruction{padding:0 0 0 2px;min-width:0;}
.lesson-step .walk-instruction p{font-size:13px;line-height:1.8;margin:6px 0;color:#334155;}
.lesson-step .walk-instruction .walk-do-label{font-size:10px;color:#2457e6;letter-spacing:.08em;margin:3px 0 9px;font-weight:700;}
.walk-check{border-top:2px solid #b4c8ee;padding-top:12px;margin-top:24px;}
.walk-check>span{font-size:11px;font-weight:700;color:#2457e6;}
.walk-help{display:inline-block;font-size:11px;margin-top:16px;text-decoration:underline;text-underline-offset:4px;}
.walk-window{background:#fff;margin:16px;border:1px solid #bac9dd;border-radius:7px;overflow:hidden;}
.walk-titlebar{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 14px;background:#f0f3f8;border-bottom:1px solid #d4deec;font:11px/1.4 'Segoe UI',sans-serif;color:#435676;}
.walk-titlebar>span:first-child{overflow-wrap:anywhere;}
.walk-titlebar>span:last-child{white-space:nowrap;color:#7a8da7;}
.walk-window-body{padding:22px;min-width:0;}
.walk-window.is-terminal{background:#142338;border-color:#243b5a;color:#e7effa;}
.is-terminal .walk-titlebar{background:#233851;border-color:#324b6b;color:#d5e4f8;}
.is-terminal .walk-window-body{padding:16px;}
.is-terminal .walk-window-body>p{color:#c1d4ee;}
.walk-display .guide-code{margin:0;border-radius:4px;}
.walk-display .guide-code-heading{padding:8px 10px;font-size:10px;line-height:1.5;}
.walk-display .guide-code pre{padding:16px 12px;font-size:12px;line-height:1.9;}
.walk-output{border-top:1px solid #364a65;margin-top:20px;padding:16px 0 4px;}
.walk-output>small{display:block;font-size:10px;color:#9eb5d4;}
.walk-output pre{padding:10px 0 0;margin:0;background:transparent;color:#9eddcb;white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.9 Consolas,monospace;}
.walk-path{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px;background:#f5f7fa;border:1px solid #dce5f2;font-size:12px;}
.walk-path>span{color:#93a3b8;}
.walk-specs{display:grid;grid-template-columns:1fr 1fr;gap:22px 14px;align-items:center;padding:26px 0;font-size:13px;}
.walk-specs>span{padding:10px;color:#2457e6;border-left:2px solid #2457e6;background:#f3f6fd;}
.lesson-step .walk-callout{font-size:12px;line-height:1.8;margin:20px 0 0;padding:14px;border-left:2px solid #6392e7;background:#f3f7ff;color:#476080;}
.walk-display>.walk-callout{margin:16px;}
.walk-mark{display:flex;align-items:flex-start;gap:12px;padding:14px 0;font-size:13px;line-height:1.8;}
.walk-mark>b{display:inline-grid;place-items:center;width:24px;height:24px;flex:0 0 24px;border-radius:50%;background:#2457e6;color:#fff;font-size:12px;}
.walk-photo{background:#fff;}
.walk-photo>a:first-child{display:block;padding:18px 10px 0;background:#fff;}
.walk-photo img{display:block;width:100%;height:auto;}
.walk-photo-notes{display:flex;gap:20px;padding:0 18px;border-bottom:1px solid #e1e8f2;flex-wrap:wrap;}
.walk-photo-notes .walk-mark{font-size:12px;gap:8px;}
.walk-photo>small{display:block;color:#6b7c94;font-size:11px;padding:0 18px 18px;}
.walk-external{display:inline-flex;padding:16px 18px;font-size:13px;text-decoration:underline;text-underline-offset:4px;}
.walk-feature-list{display:grid;gap:8px;padding:18px;background:#f2f7ff;border:1px solid #baccdf;font:12px/1.7 Consolas,monospace;}
.walk-feature-list>span{font:11px/1.6 'Segoe UI',sans-serif;color:#607086;}
.walk-installer-end{display:flex;flex-direction:column;gap:10px;padding:20px;background:#ecf8f3;border-left:3px solid #358769;}
.walk-installer-end>b{font-size:16px;}.walk-installer-end>span{font-size:12px;}
.walk-search{display:flex;align-items:center;gap:14px;border:1px solid #9eb6d8;border-bottom:2px solid #3977cf;border-radius:6px;padding:14px 12px;background:#fff;}
.walk-search>span{font-size:11px;color:#73849a;}.walk-search>b{font-size:14px;}
.walk-app-result{display:flex;align-items:center;gap:12px;margin:24px 0;background:#eef4fd;padding:16px;border:1px solid #cad8ed;}
.walk-app-icon{background:#254b7d;color:white;border-radius:4px;font:20px/36px Consolas,monospace;width:40px;text-align:center;flex-shrink:0;}
.walk-app-result>div{display:flex;flex-direction:column;gap:6px;font-size:13px;}
.walk-app-result>div>span{font-size:11px;color:#667991;}.walk-app-result>em{font-style:normal;color:#2457e6;margin-left:auto;font-size:12px;}
.walk-terminal-hint{background:#15293f;padding:20px;color:#def0ff;display:flex;flex-direction:column;gap:20px;}
.walk-terminal-hint>code{font-size:12px;overflow-wrap:anywhere;}.walk-terminal-hint>span{font-size:12px;line-height:1.8;color:#b2c9e5;}
.walk-path-diagram{display:flex;flex-direction:column;gap:12px;text-align:center;padding:24px 20px;font-size:13px;}
.walk-path-diagram>b{border:1px solid #c3d3ea;background:#fff;padding:16px;overflow-wrap:anywhere;}.walk-path-diagram>span{font-size:11px;color:#617b9b;}
.walk-editor-note{margin:0 0 14px!important;font-size:12px!important;}
.walk-editor-keys{display:grid;grid-template-columns:auto 1fr;align-items:center;gap:10px 14px;padding-top:22px;font-size:12px;}
.walk-editor-keys>b{background:#15293f;color:white;padding:7px 10px;font:12px/1.5 Consolas,monospace;}
.walk-browser-start{text-align:center;}
.walk-browser-start>strong{font-size:30px;color:#17263d;}
.walk-browser-start>p{font-size:13px!important;}
.walk-account-paths{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:24px 0;}
.walk-account-paths>div{display:flex;flex-direction:column;gap:16px;align-items:center;padding:22px 10px;background:#f5f7fb;}
.walk-account-paths span{font-size:11px;color:#637991;}.walk-account-paths b{background:#1c293c;border-radius:24px;padding:10px 16px;color:white;font-size:12px;}
.walk-account-paths small{font-size:11px;line-height:1.9;color:#637991;}
.walk-decision>a{display:inline-flex;font-size:13px;margin-bottom:14px;text-decoration:underline;text-underline-offset:4px;}
.walk-branch{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px;}
.walk-branch>div{display:flex;flex-direction:column;gap:10px;padding:18px 12px;background:#f0f6ff;border-top:2px solid #477fe1;}
.walk-branch>div:last-child{background:#f8f6f0;border-color:#c5a867;}
.walk-branch b{font-size:13px;}.walk-branch span{font-size:11px;line-height:1.8;color:#526888;}
.walk-settings-row{display:flex;flex-direction:column;gap:10px;padding:20px;border-bottom:1px solid #dce5f2;font-size:13px;}.walk-settings-row>span{font-size:12px;color:#607086;}
.walk-key-dialog{display:grid;gap:10px;margin-top:20px;padding:22px;border:1px solid #ced9e9;border-radius:8px;}
.walk-key-dialog>b{font-size:17px;margin-bottom:8px;}.walk-key-dialog>span:not(.walk-fake-button){font-size:11px;color:#607086;}.walk-key-dialog>div{padding:10px;border:1px solid #bac9dd;background:#f8faff;font-size:12px;}
.walk-key-dialog>p{font-size:12px!important;margin:0;}
.walk-fake-button{display:inline-block;background:#eaf1fc;color:#285ca7;border:1px solid #a7bde0;padding:8px 14px;font-size:12px;text-align:center;border-radius:4px;}
.walk-key-dialog>.walk-fake-button{justify-self:end;margin-top:10px;}
.walk-handoff .walk-window{margin-bottom:0;}
.walk-handoff-label{display:block;font-size:11px;color:#59749b;text-align:center;padding:14px;}
.walk-handoff .walk-window:last-child{margin-top:0;margin-bottom:16px;}
.walk-state{display:block;text-align:center;background:#edf6f2;color:#34745d;padding:14px;font-size:13px;margin-top:16px;}
.walk-env-table{margin-top:22px;padding:16px;border:2px solid #5a86d9;border-radius:5px;}
.walk-env-table>b{display:block;font-size:13px;margin-bottom:12px;}.walk-env-table>div{display:grid;grid-template-columns:1fr 2fr;gap:12px;padding:8px;border:1px solid #e0e6ee;font-size:11px;}
.walk-env-table>.walk-fake-button{margin-top:14px;}.walk-env-table.is-muted{border:1px solid #d7e0eb;color:#8a98ad;}.walk-env-table.is-muted p{font-size:12px;margin:0;}
.walk-env-demo>div:not(.walk-demo-actions){display:grid;gap:10px;margin-bottom:24px;font-size:12px;}
.walk-env-demo code{display:block;padding:12px;background:#f8faff;border:1px solid #9fb5d6;overflow-wrap:anywhere;}
.walk-env-demo>p{font-size:12px!important;}
.walk-demo-actions{display:flex;gap:10px;flex-wrap:wrap;}
.walk-env-demo .walk-demo-feedback{margin-top:24px;background:#f1f6ff;padding:12px;color:#3a5b8d;}
.walk-status-examples{display:grid;gap:16px;padding:6px 16px 20px;}
.walk-status-examples>div{display:flex;flex-direction:column;gap:10px;background:#fff;padding:18px;border-left:3px solid #9bb6e7;}
.walk-status-examples b{font-size:12px;}.walk-status-examples code{font-size:12px;overflow-wrap:anywhere;}.walk-status-examples small{font-size:10px;color:#607086;}
.walk-file-view{display:grid;grid-template-columns:100px 1fr;min-height:230px;padding-top:22px;}
.walk-file-view>aside{font-size:12px;line-height:2.6;color:#7789a2;border-right:1px solid #dce5f2;}
.walk-file-view>div{display:flex;flex-direction:column;gap:16px;align-items:center;justify-content:center;text-align:center;font-size:12px;min-width:0;}
.walk-file-view b{overflow-wrap:anywhere;max-width:100%;}.walk-file-view small{font-size:11px;color:#7588a3;}
.walk-folder-icon{display:block;position:relative;width:60px;height:42px;border-radius:4px;background:#e6b84e;box-shadow:0 3px 0 #d7a744;}
.walk-folder-icon:before{content:'';position:absolute;top:-7px;left:0;width:26px;height:10px;background:#d7a744;border-radius:4px 4px 0 0;}
.walk-codex-pane{background:#15293f;color:#e5efff;margin:16px;padding:22px;display:flex;flex-direction:column;gap:16px;font:13px/1.8 Consolas,monospace;}
.walk-codex-pane>span{font-size:11px;color:#a5bbd6;overflow-wrap:anywhere;}.walk-codex-pane>div{margin-top:12px;padding:14px 0;border-top:1px solid #526783;}
.walk-codex-pane>div>span{color:#9bb2d2;font-size:12px;}
.walk-reply-example{margin:28px 0 6px;display:flex;flex-direction:column;gap:20px;}
.walk-reply-example>span{font-size:11px;color:#a5bbd6;}.walk-reply-example>b{color:#9eddcb;font-size:20px;font-weight:500;}.walk-reply-example>small{font-size:10px;color:#a5bbd6;line-height:1.8;}
.walk-return{padding:24px;}.walk-return>.walk-mark{padding:22px 0;}
.walk-controls{display:flex;justify-content:space-between;gap:12px;padding:18px 0 0;}
.codex-guide .walk-button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;max-width:100%;padding:9px 16px;border:1px solid #2457e6;background:#2457e6;border-radius:8px;font:600 12px/1.6 'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;cursor:pointer;}
.codex-guide .walk-button.secondary{background:#fff;color:#375b91;border-color:#c5d5ed;}
.codex-guide .walk-button:hover{background:#1844bf;border-color:#1844bf;color:#fff;}
.codex-guide .walk-button:disabled{background:#f2f5f9;color:#8796ac;border-color:#dbe3ee;cursor:default;}
.walk-proof{margin:22px 0 0;padding:16px;background:#edf4ff;border-left:2px solid #7199e6;}
.walk-proof label{display:flex;gap:10px;align-items:flex-start;font-size:13px;line-height:1.8;color:#345780;cursor:pointer;}.walk-proof input{width:17px;height:17px;margin-top:3px;accent-color:#2457e6;flex-shrink:0;}
.walk-proof>small{display:block;font-size:10px;color:#667c9b;margin:8px 0 0 27px;}
.walk-scene:not([hidden])~.walk-scene:not([hidden]){margin-top:36px;}
@media(max-width:1060px){.walk-layout{grid-template-columns:minmax(0,3.5fr) minmax(0,1fr);gap:12px;}.walk-window-body{padding:16px;}.walk-window{margin:10px;}.walk-instruction p{font-size:12px;}.walk-account-paths{gap:10px;}}
@media(max-width:900px){.tutorials-page .lesson-frame{grid-template-columns:1fr;gap:18px;}.tutorials-page .lesson-sidebar{padding:16px;}.walk-layout{grid-template-columns:minmax(0,3.8fr) minmax(0,1fr);}}
@media(max-width:620px){.tutorials-page .lesson-cover h1{font-size:34px;}.tutorials-page .lesson-step h2{font-size:23px;}.walk-layout{grid-template-columns:1fr;gap:14px;}.walk-display{border-radius:7px;}.walk-instruction{padding:0;display:grid;grid-template-columns:1fr 1fr;gap:0 16px;}.walk-instruction .walk-do-label{grid-column:1;}.lesson-step .walk-instruction p{font-size:12px;line-height:1.75;margin:0;}.walk-instruction>p:nth-child(2){grid-column:1;grid-row:2;}.walk-check{grid-column:2;grid-row:1/3;margin:0;padding:0 0 0 12px;border-top:0;border-left:2px solid #b4c8ee;}.walk-check>span{display:block;margin-bottom:6px;font-size:10px;}.walk-help{grid-column:1/-1;margin-top:10px;}.walk-window{margin:10px;}.walk-window-body{padding:18px 14px;}.walk-titlebar{font-size:10px;padding:9px 11px;}.walk-account-paths{gap:8px;}.walk-account-paths>div{padding:18px 7px;gap:12px;}.walk-account-paths b{font-size:11px;padding:9px 11px;}.walk-reading{font-size:10px;}.walk-scene-heading{gap:8px;}.lesson-step .walk-scene-heading h3{font-size:17px;}.walk-photo>a:first-child{padding:10px 0 0;}.walk-photo-notes{gap:0;padding:0 12px;}.walk-photo-notes .walk-mark{width:100%;padding:10px 0;}.walk-photo img{min-height:0;}.walk-controls{gap:10px;}.codex-guide .walk-button{padding:9px 13px;font-size:12px;}.walk-display .guide-code-heading{flex-wrap:wrap;gap:8px;}.walk-display .guide-code pre{font-size:12px;padding:12px;}.walk-specs{gap:18px 10px;font-size:12px;}.walk-branch{gap:8px;}.walk-branch>div{padding:16px 10px;}.walk-branch b{font-size:12px;}.walk-file-view{grid-template-columns:70px 1fr;}.walk-env-table>div{grid-template-columns:1fr 1.5fr;}.walk-app-result{padding:12px;gap:10px;}.walk-app-result>div{font-size:12px;}.walk-titlebar>span:last-child{display:none;}.walk-proof{padding:12px;}.walk-proof label{font-size:12px;}.walk-mark{font-size:12px;}.walk-key-dialog{padding:14px;}.walk-display>figcaption{font-size:10px;padding:9px 12px;}.walk-through{scroll-margin-top:20px;}}
@media print{.walk-scene[hidden]{display:block!important;}.walk-controls,.walk-reading,.walk-demo-actions,.walk-proof input{display:none!important;}.walk-layout{display:block;}.walk-display{break-inside:avoid;}.lesson-text{display:block;}}
"""
