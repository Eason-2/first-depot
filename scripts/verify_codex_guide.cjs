// Run against a static export or the live site. Does not log in or call an AI API.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {spawnSync} = require('node:child_process');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = (process.env.GUIDE_BASE || 'http://127.0.0.1:8780/first-depot').replace(/\/$/, '');
const widths = (process.env.GUIDE_WIDTHS || '1440,1228,1024,900,820,768,620,390,320').split(',').map(Number);
const chapters = ['codex-account', 'setup-terminal', 'setup-install', 'setup-auth', 'codex-folder', 'connection-check'];

(async () => {
  const browser = await chromium.launch({channel:'chrome', headless:true});
  const context = await browser.newContext({viewport:{width:1280,height:950}, permissions:['clipboard-read','clipboard-write']});
  const page = await context.newPage();
  page.setDefaultTimeout(7000);
  const errors = [], metrics = [];
  page.on('pageerror', e => errors.push(e.message));
  const start = async hash => {
    await page.goto(base + '/tutorials/' + (hash || ''));
    await page.reload();
    await page.locator('#guide-read-all').waitFor();
  };
  const assertStep = async id => {
    await page.locator('#' + id).waitFor({state:'visible'});
    assert.equal(await page.locator('[data-step]:visible').count(),1);
    assert.equal(await page.locator('[aria-current="step"]').getAttribute('href'),'#'+id);
  };
  try {
    await start('');
    assert(await page.locator('[name="guide-os"][value="windows"]').isChecked());
    assert.equal(await page.locator('#guide-auth').inputValue(),'account');
    assert.equal(await page.locator('[data-scene]:visible').count(),1);
    assert.equal(await page.locator('.lesson-controls').isVisible(),false);
    await page.locator('[data-scene-next]:visible').focus();
    await page.keyboard.press('Space');
    await page.waitForFunction(()=>document.activeElement.tagName === 'H3');
    assert(await page.locator('.lesson-controls').isVisible());
    await page.locator('[data-proof]:visible').check();
    await page.locator('[data-next]').click();
    await assertStep('setup-terminal');
    await page.goBack();
    await assertStep('codex-account');
    await page.goForward();
    await assertStep('setup-terminal');
    console.log('PASS defaults, keyboard scene navigation, chapter navigation and browser history');

    await start('#setup-key');
    await assertStep('setup-auth');
    assert.equal(await page.locator('#guide-auth').inputValue(),'api');
    assert(await page.locator('#setup-key').isVisible());
    await page.locator('[data-scene-next]:visible').click();
    await page.locator('[data-scene-next]:visible').click();
    assert(await page.locator('[data-env-demo]').isVisible());
    assert.equal(await page.locator('[data-demo-save]').isDisabled(),true);
    const demoRequests=[];
    const onRequest=request=>demoRequests.push(request.url());
    page.on('request',onRequest);
    await page.locator('[data-demo-fill]').click();
    assert.equal(await page.locator('[data-demo-value]').textContent(),'DEMO-KEY-NOT-VALID');
    await page.locator('[data-demo-save]').click();
    assert.match(await page.locator('.walk-demo-feedback').textContent(),/网页练习完成/);
    page.off('request',onRequest);
    assert.deepEqual(demoRequests,[]);
    assert.equal(await page.locator('#codex-start input:not([type="radio"]):not([type="checkbox"]), #codex-start textarea').count(),0);
    await page.locator('[name="guide-os"][value="mac"]').check();
    assert.equal(new URL(page.url()).hash,'#setup-auth');
    assert.equal(await page.locator('[data-scene-os="windows"]:visible').count(),0);
    await page.locator('#guide-auth').selectOption('account');
    assert.equal(await page.locator('[data-scene-auth="api"]:visible').count(),0);
    console.log('PASS direct Key link, safe demo with no input or network requests, route and OS changes');

    await start('#walk-windows-codex-version');
    const block=page.locator('[data-scene]:visible .guide-code').first();
    await block.locator('.guide-copy').click();
    assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),'codex.cmd --version');
    await page.evaluate(()=>{navigator.clipboard.writeText=async()=>{throw new Error('denied');};});
    await block.locator('.guide-copy').click();
    assert.equal(await page.evaluate(()=>getSelection().toString()),'codex.cmd --version');
    await page.locator('#guide-read-all').click();
    assert.equal(await page.locator('[data-step]:visible').count(),6);
    assert.equal(await page.locator('[data-scene-os="mac"]:visible').count(),0);
    await page.locator('#guide-read-all').click();
    await assertStep('setup-install');
    for(const id of ['check-result','help-command','help-key','local-toolbox']) {
      await page.goto(base+'/tutorials/#'+id);
      await page.locator('#'+id).waitFor({state:'visible'});
      assert(await page.locator('#'+id).evaluate(el=>{
        let node=el;while(node){if(node.tagName==='DETAILS'&&!node.open)return false;node=node.parentElement;}return true;
      }));
    }
    console.log('PASS clipboard including denied permission, expand all, legacy and troubleshooting anchors');

    for(const width of widths) {
      await page.setViewportSize({width,height:950});
      await start('');
      for(const os of ['windows','mac']) for(const auth of ['account','api']) {
        await page.locator(`[name="guide-os"][value="${os}"]`).check();
        await page.locator('#guide-auth').selectOption(auth);
        let visualArea=0, bodyArea=0, scenes=0;
        for(const id of chapters) {
          if(width<=900) await page.locator('#guide-step-select').selectOption(id);
          else await page.locator(`[data-step-link][href="#${id}"]`).click();
          await assertStep(id);
          while(true) {
            const scene=page.locator('[data-scene]:visible');
            assert.equal(await scene.count(),1);
            const attrs=await scene.evaluate(el=>({os:el.dataset.sceneOs,auth:el.dataset.sceneAuth,id:el.id}));
            assert(!attrs.os || attrs.os===os);
            assert(!attrs.auth || attrs.auth===auth);
            for(const img of await scene.locator('img').all()) {
              await img.scrollIntoViewIfNeeded();
              await img.evaluate(el=>el.decode());
              assert(await img.evaluate(el=>el.naturalWidth>0));
              assert((await img.getAttribute('src')).startsWith(new URL(base).pathname.replace(/\/$/,'')+'/tutorials/assets/'));
              assert((await img.evaluate(el=>el.currentSrc)).includes(width<=620?'-mobile.webp':'-download.webp'));
            }
            const dimensions=await scene.evaluate(el=>{
              const s=el.querySelector('.walk-display').getBoundingClientRect();
              const row=el.querySelector('.walk-layout').getBoundingClientRect();
              const overflow=[...document.querySelectorAll('main, main *, .site-header *')].filter(e=>{
                const r=e.getBoundingClientRect();return e.checkVisibility() && r.width && (r.right>innerWidth+1||r.left< -1);
              }).map(e=>e.className||e.tagName);
              return {visual:s.width*s.height,total:row.width*row.height,overflow};
            });
            assert.deepEqual(dimensions.overflow,[],`${width} ${os} ${auth} ${attrs.id}`);
            visualArea+=dimensions.visual;bodyArea+=dimensions.total;scenes++;
            const next=page.locator('[data-scene-next]:visible');
            if(!await next.count()) break;
            await next.click();
          }
          assert(await page.locator('.walk-proof:visible').isVisible());
          assert(await page.locator('.lesson-controls').isVisible());
        }
        const ratio=visualArea/bodyArea;
        assert(ratio>=0.7,`${width} ${os} ${auth}: visual share ${ratio}`);
        metrics.push({width,os,auth,scenes,visualShare:Number(ratio.toFixed(4))});
      }
      console.log(`PASS ${width}px: every screen in Windows/Mac × account/API, images, no overflow, visual share >=70%`);
    }
    await start('');
    if(process.platform==='darwin') {
      const snippets=await page.locator('[data-guide-os="mac"] .guide-code:not(.is-prompt) code').allTextContents();
      for(const snippet of snippets) {
        const r=spawnSync('/bin/zsh',['-n'],{input:snippet,encoding:'utf8'});
        assert.equal(r.status,0,r.stderr);
      }
      console.log('PASS Mac command syntax (not executed)');
    }
    const noJS=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
    const fallback=await noJS.newPage();
    await fallback.goto(base+'/tutorials/');
    assert.equal(await fallback.locator('[data-step]:visible').count(),6);
    assert(await fallback.locator('#setup-key').isVisible());
    assert(await fallback.locator('[data-scene-os="mac"]').first().isVisible());
    assert(await fallback.locator('[data-scene-os="windows"]').first().isVisible());
    assert.equal(await fallback.locator('.walk-controls:visible,.walk-demo-actions:visible').count(),0);
    await noJS.close();
    assert.deepEqual(errors,[]);
    if(process.env.GUIDE_REPORT) fs.writeFileSync(process.env.GUIDE_REPORT,JSON.stringify(metrics,null,2));
    console.log(`PASS no-JavaScript reading and no JavaScript errors; ${metrics.length} route/viewport checks`);
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1);});
