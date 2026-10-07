"""Reader-facing Codex lesson shared by the live site and static export."""

from __future__ import annotations


def render_codex_guide() -> str:
    return """
<section class='section codex-guide' id='codex-start' aria-labelledby='codex-guide-title'>
  <header class='section-heading' id='start-here'>
    <p class='eyebrow'>第一课 · 从没有账号开始</p>
    <h2 id='codex-guide-title'>从零开始使用 Codex</h2>
    <p>还不知道 Codex 是什么，也没有所谓的 Key？先看下面三个问题。准备好之后，我们用中文告诉它需求，做出一个能在自己电脑上打开的小网页。</p>
  </header>

  <div class='guide-facts' aria-label='开始前最常见的三个问题'>
    <div><h3>Codex 是什么？</h3><p>OpenAI 提供的 AI 编程助手。你说“帮我做一个介绍自己的网页”，它可以在你选定的文件夹里创建网页文件，也能根据你的意见修改。</p></div>
    <div><h3>没有 Key 能用吗？</h3><p><strong>可以走 ChatGPT 账号登录这条路，不需要自己创建或填写 API Key。</strong>前提是你的账号具备 Codex 使用权限，而且还有可用额度。</p></div>
    <div><h3>需要先买东西吗？</h3><p><strong>先确认账号能否使用，再决定是否付费。</strong>能登录不等于所有功能都免费；套餐、试用和额度可能变化，不要为了跟教程先买一个 Key。</p></div>
  </div>

  <article class='tutorial-block' id='codex-account'>
    <p class='card-kicker'>先读懂这三个词</p>
    <h3>账号、订阅、Key，各管什么？</h3>
    <dl class='guide-glossary'>
      <dt>ChatGPT 账号</dt><dd>用来登录 OpenAI 产品的身份。已经在 ChatGPT 聊过天，就先尝试使用同一个账号；你的 GitHub、豆包或其他 AI 平台账号不能直接当作它的登录凭据。</dd>
      <dt>订阅与额度</dt><dd>订阅是购买某个产品套餐；额度是账号目前能使用多少服务。是否包含 Codex、还有多少可用量，要看你登录后的账号提示，不能只凭“我有账号”来判断。</dd>
      <dt>API Key（密钥）</dt><dd>一串让软件调用某个平台服务的秘密凭据，可以把它理解成“给程序用的钥匙”。它不是 ChatGPT 登录密码，也不是买了就能解锁所有 AI 工具的通用激活码。OpenAI API 的费用与 ChatGPT 订阅分开，其他平台的 Key 通常不能直接填到 OpenAI 的登录入口。</dd>
    </dl>
    <p class='guide-check'>这篇只教一条路线：电脑桌面应用 + ChatGPT 账号登录。暂时用不到 API Key、GitHub、终端（输入命令的窗口）和本地模型。</p>
    <p class='guide-note'>修订于 2026-10-07 · 操作路线参考 <a href='https://developers.openai.com/codex/quickstart' target='_blank' rel='noopener noreferrer'>官方入门页</a>。当前套餐价格、免费额度及支持地区未在本文确认，请先核对 <a href='https://developers.openai.com/codex/pricing' target='_blank' rel='noopener noreferrer'>官方费用说明</a>及账号内提示；登录方式参见 <a href='https://developers.openai.com/codex/auth' target='_blank' rel='noopener noreferrer'>官方账号登录与 API Key 说明</a>。</p>
  </article>

  <nav class='guide-toc' aria-label='Codex 第一课目录'>
    <p><strong>跟着这个顺序走</strong> · 已有账号可以从第 2 步开始</p>
    <ol>
      <li><a href='#codex-signup'>注册或登录账号</a></li>
      <li><a href='#choose-tool'>下载应用，用账号登录</a></li>
      <li><a href='#codex-folder'>建一个专用练习文件夹</a></li>
      <li><a href='#first-task'>发送第一条中文需求</a></li>
      <li><a href='#check-result'>打开网页，亲眼检查</a></li>
      <li><a href='#codex-edit'>改一处内容，保存成果</a></li>
    </ol>
    <a href='#codex-help'>遇到账号、Key 或打开失败的问题 →</a>
  </nav>

  <article class='tutorial-block' id='codex-signup'>
    <p class='card-kicker'>第 1 步 · 先准备账号</p>
    <h3>从 ChatGPT 官网开始</h3>
    <ol>
      <li>在浏览器打开 <a href='https://chatgpt.com/' target='_blank' rel='noopener noreferrer'>ChatGPT 官网：chatgpt.com</a>。这是外部网站，本博客没有提供账号，也不会要求你在这里填写密码。</li>
      <li>没有账号就选择注册（Sign up），按照页面实际提供的邮箱或第三方登录方式完成验证；已有账号就选择登录（Log in）。记住你用的是哪种登录方式，稍后在应用中仍用同一种。</li>
      <li>登录后先确认能进入自己的账号页面。遇到不支持所在地区、注册验证失败或组织账号限制时，先按官方提示处理，这一步没有完成就先停在这里。</li>
    </ol>
    <p class='guide-check'><strong>过关标志：</strong>你能进入自己的 ChatGPT 账号，知道下次怎么登录。注册成功只代表有账号，还要在下一步确认 Codex 是否可用。</p>
    <p>官网打不开时，买 Key 并不能解决网页访问问题；账号尚不可用时，可以先读下文了解流程，不需要急着付款。</p>
  </article>

  <article class='tutorial-block' id='choose-tool'>
    <p class='card-kicker'>第 2 步 · 下载并登录</p>
    <h3>在电脑上打开 Codex</h3>
    <p>这篇练习要直接在电脑里生成文件，所以跟着桌面端走。网页版、编辑器插件和命令行是其他入口，操作路径不同，先不用一起学。手机可以阅读教程，下面的操作请在电脑上完成。</p>
    <ol>
      <li>打开 <a href='https://developers.openai.com/codex/quickstart' target='_blank' rel='noopener noreferrer'>官方 Codex 入门页</a>，找到桌面应用的下载入口。也可以从 <a href='https://chatgpt.com/download' target='_blank' rel='noopener noreferrer'>ChatGPT 官方下载页</a>查看适合自己系统的安装包；以官网当前提供的 Codex 入口和系统要求为准。</li>
      <li><strong>Windows：</strong>按官网提供的安装器或商店页面安装。<strong>Mac：</strong>打开下载的安装包，按提示安装；如果出现拖入 Applications 的窗口，就把应用拖进“应用程序”。系统提示版本不兼容时，先核对官网要求。</li>
      <li>打开安装好的应用，使用第 1 步的 ChatGPT 账号登录。若看到账号登录和 API Key 两种选择，选择“使用 ChatGPT 登录”（Sign in with ChatGPT），不要选填写 Key 的方式。</li>
      <li>浏览器可能会打开登录页面；完成后按提示返回应用。如果当前显示 ChatGPT，点击 ChatGPT 名称旁的下拉选择，切换到 Codex；如果已经进入 Codex 界面，就继续下一步。</li>
      <li>查看有没有“升级”“达到使用上限”或“联系管理员”等提示。若有，先处理对应的权限或额度问题；不确定是否付费时，先查看金额、续费规则和包含的使用量。</li>
    </ol>
    <p class='guide-check'><strong>过关标志：</strong>应用显示已登录，能进入 Codex 并找到开始任务的输入区域，当前没有阻止使用的提示。实际能否运行任务，在第 4 步发出请求时再确认。</p>
    <p>应用名称、按钮位置可能随版本变化。这些步骤描述的是操作目标，不是逐像素的界面截图。如果找不到 Codex，或界面只有 Key 输入框，先看 <a href='#codex-help'>下面的排错说明</a>，不要随便购买密钥。</p>
  </article>

  <article class='tutorial-block' id='codex-folder'>
    <p class='card-kicker'>第 3 步 · 给作品找个位置</p>
    <h3>“项目”先理解成一个装作品的文件夹</h3>
    <p>不用先学 Git，也不用下载别人写好的代码。我们新建一个空文件夹，只放本次练习的文件。</p>
    <ol>
      <li>Windows 打开“文件资源管理器”，Mac 打开“访达”，进入“文档”目录。</li>
      <li>新建一个文件夹，命名为 <code>my-first-codex</code>。里面暂时没有任何文件，这是正常的。</li>
      <li>回到应用，使用新建项目或打开文件夹的入口，选中这个文件夹。进入该项目并新建一个任务；有本地与云端选项时，选择本地，也就是在这台电脑上工作。</li>
    </ol>
    <p class='guide-check'><strong>过关标志：</strong>当前项目指向 <code>my-first-codex</code>。如果显示的是另一个项目，先重新选择，不要在错误位置开始。</p>
    <p>允许访问这个练习文件夹就够了。不要选择整块磁盘，也不要把真实联系方式、密码或工作资料放进去。稍后生成的文件保存在这里，但 AI 服务处理任务可能涉及网络传输，“本地项目”不等于完全离线。</p>
  </article>

  <article class='tutorial-block' id='first-task'>
    <p class='card-kicker'>第 4 步 · 用中文说需求</p>
    <h3>让 Codex 做一张“我的学习名片”</h3>
    <p>下面这段话叫提示词，就是你发给 AI 的任务说明。选中框内全部文字复制，在 Codex 的任务输入框粘贴，然后点击发送。</p>
    <pre class='prompt-example'><code>我是第一次使用 Codex，没有编程基础。
请在当前 my-first-codex 文件夹里帮我做一张“我的学习名片”网页。
先不要修改任何文件，先用三句话说明准备做什么，等我确认。

页面内容：
标题：你好，这是我的第一张 AI 学习名片
介绍：我正在学习用 AI 把想法变成作品。
三个兴趣标签：阅读、旅行、AI
底部文字：今天，我完成了第一次尝试。

只创建一个 index.html 文件，样式也放在这个文件里。
不要安装软件或依赖，不要联网加载图片和字体。
网页要能通过双击文件直接在浏览器打开，手机大小的窗口也能看清楚。
不要上传或发布。完成后告诉我文件保存在哪里。</code></pre>
    <p><code>index.html</code> 是我们约定的网页文件名；HTML 是浏览器能够读懂的网页格式。你暂时不用会写它。</p>
    <p>读计划时只核对三件事：它是否准备在刚才的文件夹里创建一个文件、是否包含四项页面内容、是否需要额外安装东西。范围对了，再发送：</p>
    <pre class='prompt-example'><code>可以，按这个计划创建 index.html。完成后请检查文件是否已保存，说明检查结果和我该怎么打开它。</code></pre>
    <p class='guide-check'><strong>过关标志：</strong>Codex 报告已创建文件，而且你能在练习文件夹里找到 <code>index.html</code>。若它只在对话里贴了一段代码，回复：“请把这段代码保存为当前项目里的 index.html 文件。”</p>
    <p>如果弹出允许修改文件的请求，先看目标是否为这个练习文件夹。如果它突然要求安装一堆软件、运行你看不懂的命令或扩大访问范围，可以先取消并回复：“请按刚才的要求，只生成能直接打开的单个网页文件。”</p>
  </article>

  <article class='tutorial-block' id='check-result'>
    <p class='card-kicker'>第 5 步 · 亲眼看到成品</p>
    <h3>双击文件，在浏览器里检查</h3>
    <ol>
      <li>回到“文档”中的 <code>my-first-codex</code> 文件夹，找到 <code>index.html</code>。Windows 若隐藏了扩展名，它可能只显示为 <code>index</code>，类型显示为 HTML 文档。</li>
      <li>双击文件。若打开的是文本编辑器，就右键文件，选择“打开方式”，再选 Edge、Chrome 或 Safari 等浏览器。</li>
      <li>应该看到标题、自我介绍、三个标签和底部文字。浏览器地址以 <code>file://</code> 开头是正常的，表示正在打开电脑里的文件；这还不是别人可以访问的网站。</li>
      <li>把浏览器窗口缩窄，观察有没有文字被截掉、内容挤在一起或必须横向滚动才能看完。</li>
    </ol>
    <figure class='guide-preview'>
      <figcaption>内容参考 · 排版可以不同，不是 Codex 界面截图</figcaption>
      <div><h4>你好，这是我的第一张 AI 学习名片</h4><p>我正在学习用 AI 把想法变成作品。</p><p class='tag-row'><span class='tag'>阅读</span><span class='tag'>旅行</span><span class='tag'>AI</span></p><p>今天，我完成了第一次尝试。</p></div>
    </figure>
    <p class='guide-check'><strong>过关标志：</strong>网页真的打开了，四项内容齐全，缩窄窗口后仍能读。Codex 说“检查通过”和你自己看到正常，是两件都要做的事。</p>
    <p>看到空白或错误时，不必先学会报错里的术语。把具体看到的现象发回同一个任务，例如：</p>
    <pre class='prompt-example'><code>我双击了 my-first-codex 里的 index.html，浏览器打开后是一片空白。
请先检查原因，只修复这个文件，并告诉我修改后应该看到什么。
不要自动执行删除、上传、发布或修改系统设置的命令。</code></pre>
  </article>

  <article class='tutorial-block' id='codex-edit'>
    <p class='card-kicker'>第 6 步 · 体验一次修改</p>
    <h3>把“旅行”换成你的另一个兴趣</h3>
    <p>回到同一个 Codex 任务，发送一句具体的修改意见：</p>
    <pre class='prompt-example'><code>请把兴趣标签“旅行”改成“摄影”，其他文字和样式保持原样。
修改完成后告诉我改了哪个文件，以及修改前后有什么区别。</code></pre>
    <p>回到浏览器刷新页面，看到“摄影”就说明修改生效了。如果没变化，确认当前打开的是否是这个文件夹里的文件，再刷新一次。</p>
    <p>Codex 的“修改”或“差异”（diff）区域是新旧文件的对照；通常红色表示移除、绿色表示新增。这次应该只涉及“旅行”到“摄影”的替换。如果看不懂，先让它解释这一处变化，不需要一下子读懂整份代码。</p>
    <p class='guide-check'><strong>这节课完成了：</strong>你用自己的账号登录，创建了网页文件，在浏览器看到了它，还通过一句中文完成了修改。</p>
    <p>把 <code>my-first-codex</code> 文件夹复制一份作为备份，接着尝试改颜色或字号。<strong>关闭应用不会自动删除已经保存的文件。</strong>分享这个网页前要另外学习发布；只把自己电脑上的文件路径发给朋友，对方打不开。</p>
  </article>

  <section class='tutorial-block' id='codex-help' aria-labelledby='codex-help-title'>
    <h3 id='codex-help-title'>卡住时，先对照这里</h3>
    <details class='guide-faq'><summary>我连账号都没有，能直接跟做吗？</summary><p>先完成第 1 步注册与登录。没有可用的账号，或账号没有 Codex 权限，就还不能按本文完成操作。你可以阅读后续流程，但这篇教程不会提供账号或代替你购买服务。</p></details>
    <details class='guide-faq'><summary>只有一个填写 Key 的框，没有账号登录按钮</summary><p>先确认你使用的是从官方入门页下载的应用，而不是其他平台的客户端；也检查是否误选了 API Key 登录。若可以返回登录选择页，就选 ChatGPT 账号登录。找不到该选项时，记录应用名称、版本和提示，按官方入门页核对。不要把别人的 Key 直接填进去。</p></details>
    <details class='guide-faq'><summary>我有 ChatGPT 账号，却提示升级或达到上限</summary><p>这说明“登录成功”和“目前可用”不是同一件事。查看当前账号的套餐与额度提示：额度用完可按页面说明等待恢复；若需升级，先看清费用与续费条件；组织账号可能需要管理员开放权限。本文不承诺所有新账号都能免费使用。</p></details>
    <details class='guide-faq'><summary>我已经有 Key，或者想走 API 方式呢？</summary><p>先确认 Key 来自哪个服务商。OpenAI API Key 属于开发者平台的调用凭据，通常走 API 用量计费；它与 ChatGPT 的订阅和额度不是一回事。确实要采用这条路线时，从 <a href='https://platform.openai.com/' target='_blank' rel='noopener noreferrer'>OpenAI 开发者平台</a>核对自己的项目、账单与密钥管理，再按 <a href='https://developers.openai.com/codex/auth' target='_blank' rel='noopener noreferrer'>官方认证说明</a>操作。本文后续练习不要求你改用这条路线；不要在博客评论、聊天截图或网页源代码里公开 Key。</p></details>
    <details class='guide-faq'><summary>它要求连接 GitHub，或者我找不到本地文件夹</summary><p>先核对是否进入了网页或云端任务流程。GitHub 是在线保存和协作管理代码的平台；它不是本课本地文件夹练习的前提。回到桌面应用，选本地项目；如果你的版本没有这个入口，先根据官网核对版本支持，不要把网页端步骤和本教程混着做。</p></details>
    <details class='guide-faq'><summary>网页打开后是一堆代码，或者修改后没变化</summary><p>一堆代码通常说明你用文本编辑器打开了文件，改用浏览器打开。若浏览器本身也显示代码，检查文件是否变成了 index.html.txt；可以让 Codex 核对文件名和内容。修改后没变化，先刷新，并核对打开的文件路径；不要连续新建多个同名文件。</p></details>
    <details class='guide-faq'><summary>页面、登录或请求失败，该把什么发给 Codex？</summary><p>说明你做到第几步、点了什么、预期看到什么、实际看到什么，再附上不含敏感信息的错误文字或局部截图。先遮住邮箱、密钥、验证码和其他私密内容。登录都没完成时，先按官方帮助处理，不要继续照抄后面的任务。</p></details>
  </section>

  <aside class='guide-next'>
    <h3>接下来，记录一次自己的尝试</h3>
    <p>写三句话就够了：我想做什么、哪一步卡住了、最后怎么解决。下一次可以让 Codex 把这段记录加入网页，再检查结果。</p>
    <p><a href='/about/journal'>看看我的实践与思考 →</a> · <a href='/blog'>去知行简报发现新变化 →</a></p>
    <p class='guide-note'>下方的本地工具箱是另一篇需要编程环境的教程，不是完成这节课的必做步骤。</p>
  </aside>
</section>
"""
