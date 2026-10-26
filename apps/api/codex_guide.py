"""Beginner setup lesson, shared by the live site and static export."""

from __future__ import annotations

from html import escape


def _code(text: str, label: str = "复制到终端，按回车执行") -> str:
    return (
        "<div class='guide-code'><div class='guide-code-heading'>"
        f"<span>{escape(label)}</span><button type='button' class='guide-copy' hidden>复制</button>"
        f"</div><pre tabindex='0'><code>{escape(text.strip())}</code></pre></div>"
    )


def _platforms(windows: str, mac: str) -> str:
    return (
        "<div class='guide-platform' data-guide-os='windows'>"
        "<p class='guide-platform-label'>Windows · PowerShell · <a href='#guide-system'>切换系统 ↑</a></p>" + windows + "</div>"
        "<div class='guide-platform' data-guide-os='mac' hidden>"
        "<p class='guide-platform-label'>macOS · 终端（zsh） · <a href='#guide-system'>切换系统 ↑</a></p>" + mac + "</div>"
    )


def render_codex_guide() -> str:
    return (
        """
<section class='section codex-guide' id='codex-start' aria-labelledby='codex-guide-title'>
  <header class='section-heading' id='start-here'>
    <p class='eyebrow'>零基础第一课 · 安装与配置</p>
    <h2 id='codex-guide-title'>先把 AI 用起来</h2>
    <p>不知道软件怎么装、Key 填在哪里、环境变量是什么？这次从打开命令窗口开始，带你走到收到第一条 AI 回复。先通，再学。</p>
  </header>

  <div class='guide-system' id='guide-system'>
    <fieldset><legend>你准备在哪台电脑上操作？</legend>
      <div class='guide-system-options'>
        <label><input type='radio' name='guide-os' value='windows' checked /><span>Windows <small>默认教程</small></span></label>
        <label><input type='radio' name='guide-os' value='mac' /><span>macOS <small>Mac 教程</small></span></label>
      </div>
    </fieldset>
    <p id='guide-os-status' role='status'>当前显示 Windows 步骤。使用 Mac，请手动切换；下面的命令会一起更换。</p>
  </div>
  <noscript><style>.guide-platform[hidden]{display:block!important}.guide-system fieldset{display:none}</style><p class='guide-check'>浏览器未启用 JavaScript，以下同时展示两套步骤。只跟随标有自己系统的段落操作。</p></noscript>

  <article class='tutorial-block' id='choose-tool'>
    <p class='card-kicker'>这节课用什么</p>
    <h3>从零开始使用 Codex：本篇选用命令行版</h3>
    <p>Codex 是 OpenAI 的 AI 编程助手，可以根据你的描述读写文件。我们先让它回复一句话，确认工具真的可用，再尝试整理一份待办。做网页放在后面的选做练习。</p>
    <p><strong>命令行版（CLI）</strong>就是在一个文字窗口里使用工具。命令都写在下面了，不需要先学编程。桌面应用、编辑器插件的界面不同，请先沿本篇这一条路线操作。</p>
    <div class='guide-facts'>
      <div><h4>要准备</h4><p>一台电脑、可访问所需官方服务的网络，以及有可用权限或额度的账号。手机适合阅读，操作请在电脑上完成。</p></div>
      <div><h4>会安装</h4><p>Node.js 和 Codex CLI。Node.js 是运行所需的基础软件；附带的 npm 帮你安装 Codex。</p></div>
      <div><h4>这次的“部署”</h4><p>把工具安装在自己电脑上。无需先买服务器、域名或显卡；AI 回复仍需连接在线服务。</p></div>
    </div>
    <p class='guide-note'>修订于 2026-10-26。命令选项已对照本机 Codex CLI 0.153.2 的帮助信息；Windows 全新电脑安装、真实新账号注册与付费调用尚未逐项实测。官网当前的系统要求、地区、套餐与额度请先核对，本文不承诺免费可用。</p>
    <p class='guide-note'>官方参考：<a href='https://developers.openai.com/codex/cli' target='_blank' rel='noopener noreferrer'>CLI 安装</a> · <a href='https://developers.openai.com/codex/windows' target='_blank' rel='noopener noreferrer'>Windows 支持</a> · <a href='https://developers.openai.com/codex/auth' target='_blank' rel='noopener noreferrer'>登录与 Key</a> · <a href='https://developers.openai.com/codex/pricing' target='_blank' rel='noopener noreferrer'>费用与额度</a>。本次这些文档的访问未成功，变化较快的信息请以可访问时的官方页面和账号内提示为准。</p>
  </article>

  <nav class='guide-toc' aria-label='安装与配置目录'>
    <p><strong>从你卡住的位置开始</strong></p>
    <ol>
      <li><a href='#codex-account'>先确认账号与使用方式</a></li>
      <li><a href='#setup-terminal'>打开窗口，安装基础软件</a></li>
      <li><a href='#setup-install'>安装 Codex，检查版本</a></li>
      <li><a href='#setup-auth'>登录，或配置 API Key</a></li>
      <li><a href='#codex-folder'>准备一个练习文件夹</a></li>
      <li><a href='#connection-check'>收到第一条 AI 回复</a></li>
    </ol>
    <div class='guide-shortcuts'><a href='#setup-key'>我卡在 Key / 环境变量 →</a><a href='#codex-help'>我遇到了报错 →</a><a href='#first-task'>已经能用，开始做网页 →</a></div>
  </nav>

  <article class='tutorial-block' id='codex-account'>
    <p class='card-kicker'>01 · 先确认自己能用哪种方式</p>
    <h3>账号登录与 API Key，选一条就够了</h3>
    <p>有账号不等于已经有使用权限；有 Key 也不等于有可用额度。先确认下面一条路线可用，再继续安装。</p>
    <div class='grid-2'>
      <div class='guide-route' id='codex-signup'><h4>A · 用 ChatGPT 账号登录</h4><p>还没有账号：打开 <a href='https://chatgpt.com/' target='_blank' rel='noopener noreferrer'>ChatGPT 官网</a>，选择注册（Sign up），按页面提供的方式完成验证；已有账号就登录（Log in）。记住自己选择的登录方式。</p><p>再确认账号当前能否使用 Codex，以及可用额度。<strong>这条路线不需要自己创建 API Key，也不需要设置密钥环境变量。</strong>遇到套餐、组织或地区限制，先按官方提示处理。</p></div>
      <div class='guide-route'><h4>B · 使用自己的 OpenAI API Key</h4><p>适合已经决定使用开发者接口的人。需要自己的 <a href='https://platform.openai.com/' target='_blank' rel='noopener noreferrer'>OpenAI 开发者平台</a>账号、项目、Key 和可用的 API 额度。具体创建过程在 <a href='#setup-key'>第 4 步</a>。</p><p>API 用量计费与 ChatGPT 订阅分开。<strong>先确认价格与账单设置，再决定是否付费。</strong>其他服务商的 Key 不能直接当作本教程的 OpenAI Key 使用。</p></div>
    </div>
    <p class='guide-check'><strong>继续前确认：</strong>你知道要走 A 还是 B，能访问对应官网，并理解可能的费用。两条路线都不可用时，先解决账号或服务可用性；购买一个来路不明的 Key 不能替你完成这些条件。</p>
  </article>

  <article class='tutorial-block' id='setup-terminal'>
    <p class='card-kicker'>02 · 打开输入命令的窗口</p>
    <h3>安装 Node.js，让电脑具备运行条件</h3>
    <p>从 <a href='https://nodejs.org/en/download' target='_blank' rel='noopener noreferrer'>Node.js 官方下载页</a>选择标有 <strong>LTS（长期支持）</strong>、且支持你系统的安装包。这一步安装的是运行环境，还不是 AI 本身。已安装并能通过下面检查的读者可以跳过下载。</p>
"""
        + _platforms(
            "<ol><li>在 Windows 的“设置 → 系统 → 系统信息（关于）”查看系统类型，选择匹配 x64 或 ARM64 的 Windows 安装包（通常为 .msi）。</li>"
            "<li>双击安装包，按安装向导保留默认选项，包括 npm 和添加到 PATH。若出现额外安装编译工具的选项，这一课无需勾选。</li>"
            "<li>安装结束后，关闭已打开的终端窗口。在开始菜单搜索 <strong>PowerShell</strong>，正常打开，不需要选择“以管理员身份运行”。窗口提示一般以 <code>PS</code> 开头。</li>"
            "<li>把下面两行逐行复制进去，每行按一次回车。不要把示例输出或 <code>PS C:…&gt;</code> 这样的提示符一起复制。</li></ol>"
            + _code("node --version\nnpm.cmd --version", "PowerShell · 逐行执行")
            + "<p>本教程在 Windows 使用 <code>npm.cmd</code> 和 <code>codex.cmd</code>，明确调用 Windows 的命令入口，避免把 PowerShell 脚本执行策略问题混进安装步骤。</p>",
            "<ol><li>在“苹果菜单 → 关于本机”查看芯片类型和 macOS 版本，再选择官网支持的 macOS 安装包（.pkg）。</li>"
            "<li>双击 .pkg，按安装器提示完成安装。如果系统版本不受支持，先核对官方系统要求，不要忽略兼容性提示。</li>"
            "<li>按 <strong>Command + 空格</strong>，搜索“终端”或 Terminal，打开。默认使用 zsh；下面的 Mac 命令按 zsh 编写。</li>"
            "<li>如果安装前已经打开终端，先退出终端应用再重新打开。把下面两行逐行输入，每行按一次回车。</li></ol>"
            + _code("node --version\nnpm --version", "Mac 终端 · 逐行执行"),
        )
        + """
    <p class='guide-check'><strong>看到什么才算成功：</strong>两条命令分别显示版本号，例如 Node.js 的输出以 <code>v</code> 开头，npm 显示数字版本。版本号不必与别人的截图相同；出现“找不到命令”时先看 <a href='#help-command'>这条排错</a>。</p>
    <details class='guide-faq'><summary>这里出现的 PATH 和“环境变量”是什么？</summary><p>环境变量是程序读取的一组配置。<code>PATH</code> 告诉电脑去哪些文件夹寻找命令；<code>OPENAI_API_KEY</code> 则是某些工具约定用来读取密钥的变量名。它们用途不同。设置 PATH 时应添加路径，不能把原来的整项覆盖成一个新路径。</p></details>
  </article>

  <article class='tutorial-block' id='setup-install'>
    <p class='card-kicker'>03 · 安装工具</p>
    <h3>安装 Codex，然后检查版本</h3>
    <p>如果电脑已经装过 Codex，先运行下面的版本检查；能显示版本，就不必重复安装。第一次安装时，需要联网下载软件，等命令结束再进行下一步。</p>
"""
        + _platforms(
            _code("npm.cmd install -g @openai/codex", "PowerShell · 安装官方 Codex 包")
            + _code("codex.cmd --version", "PowerShell · 检查是否装好")
            + "<p><code>install</code> 表示安装，<code>-g</code> 表示让当前电脑环境能从不同文件夹调用这个命令。看到 npm 更新提示不等于安装失败，以命令是否报错和版本检查为准。</p>",
            "<p>下面将 Codex 安装到你自己的 <code>.local</code> 目录，不需要用 sudo 安装 npm 包。第一行安装，第二行让当前终端找到它，第三行检查版本。</p>"
            + _code('npm install --global --prefix "$HOME/.local" @openai/codex\nexport PATH="$HOME/.local/bin:$PATH"\ncodex --version', "Mac 终端 · 逐行执行")
            + "<p><code>$HOME</code> 代表当前用户目录，不用替换成姓名。<code>export PATH=…</code> 先只对当前终端生效；要让以后打开的终端也找得到，接着完成下面的小步骤。</p>"
            + "<details class='guide-faq' open><summary>让 Mac 下次打开终端仍然能找到 Codex</summary><p>运行下面的命令，用终端里的文字编辑器打开登录配置文件。文件不存在时会新建；已经有内容时保留原文。</p>"
            + _code('nano "$HOME/.zprofile"', "Mac 终端 · 打开配置文件")
            + "<p>用方向键移动到末尾，在单独一行加入下面这行；如果已有完全相同的一行，就不要重复添加。这行放进编辑器，不是在此时直接执行。</p>"
            + _code('export PATH="$HOME/.local/bin:$PATH"', "粘贴到 .zprofile 的末尾")
            + "<p>按 <strong>Control + O</strong> 保存，按回车确认文件名，再按 <strong>Control + X</strong> 退出。退出并重新打开终端，再运行 <code>codex --version</code>，确认新窗口也能找到命令。这里的 Control 不是 Command。</p></details>",
        )
        + """
    <p class='guide-check'><strong>过关标志：</strong>看到 <code>codex-cli</code> 和版本号。它只代表软件安装成功，还没有验证账号和 AI 服务是否可用。</p>
  </article>

  <article class='tutorial-block' id='setup-auth'>
    <p class='card-kicker'>04 · 连接自己的账号</p>
    <h3>按第 1 步的选择，完成一种认证</h3>
    <p>下面 A、B 二选一。已经用账号登录成功，就可以跳过 B 的 Key 配置。更换认证方式会改变当前 Codex 使用的身份和计费来源。</p>
    <details class='guide-faq' open><summary>A · 使用 ChatGPT 账号登录（不用填 Key）</summary>
      <p>在终端运行登录命令。如果出现登录方式选择，选 <strong>Sign in with ChatGPT</strong>。按提示打开浏览器，使用第 1 步的账号完成登录和授权，再返回终端。只在官方登录页面输入密码、验证码。</p>
"""
        + _platforms(_code("codex.cmd login"), _code("codex login"))
        + """
      <p>成功后按下面的状态检查确认。浏览器没有自动弹出时，可以手动打开终端显示的官方登录链接；不要把整段登录链接、验证码或二维码发给别人。</p>
    </details>

    <details class='guide-faq' id='setup-key'><summary>B · 创建 API Key，并正确设置环境变量</summary>
      <h4>先知道这把“钥匙”属于谁</h4>
      <p>API Key 是让程序调用服务的秘密凭据，不是登录密码，也不是所有 AI 工具通用的激活码。这里配置的是 <strong>OpenAI 官方 API</strong>；其他平台需要按对应客户端说明配置服务地址、模型和认证，不能只换一串 Key。</p>
      <ol>
        <li>打开 <a href='https://platform.openai.com/' target='_blank' rel='noopener noreferrer'>OpenAI 开发者平台</a>并注册或登录。若有组织或项目选择，确认当前是你准备使用和付费的项目。</li>
        <li>在账单（Billing）与用量（Usage）相关页面核对 API 是否可用、价格和付款条件。按平台当前提供的方式设置预算或提醒，并确认它们是否真的会限制扣费；不要把提醒当作必然的硬性限额。</li>
        <li>进入 <a href='https://platform.openai.com/api-keys' target='_blank' rel='noopener noreferrer'>API keys 页面</a>，选择创建新密钥（Create new secret key），取一个便于辨认的名字，例如 <code>codex-practice</code>，按页面设置所属项目与所需权限。</li>
        <li>创建后按页面提示复制密钥，保存在自己的密码管理器中，再按下方步骤使用。如果之后无法查看原值，可以在原平台撤销旧 Key、创建新的，不要在博客或聊天中求别人提供。</li>
      </ol>
      <p><strong>本页没有收集 Key 的输入框。</strong>密钥只填在你自己电脑的配置窗口或隐藏输入提示里。不要截图分享，不要写进网页、公开仓库或练习文件夹。</p>
      <h4>再把 Key 交给本机工具</h4>
"""
        + _platforms(
            "<ol><li>打开开始菜单，搜索 <strong>编辑账户的环境变量</strong>。如果进入“系统属性”，点击“环境变量”，找到上半部分的“用户变量”。</li>"
            "<li>点击“新建”：变量名填写 <code>OPENAI_API_KEY</code>；变量值粘贴刚创建的真实 Key，<strong>不要加引号，也不要把 OPENAI_API_KEY 写进变量值</strong>。如果已有同名项，先确认用途，再编辑该项。</li>"
            "<li>点击确定保存并关闭这些设置窗口。不要改下面的系统变量，也不要把 Key 填进 PATH。</li>"
            "<li><strong>完全退出 PowerShell / Windows Terminal，再从开始菜单打开 PowerShell。</strong>只在旧窗口执行下一步可能读不到新配置；如果在编辑器里使用终端，也需要重新打开编辑器。</li></ol>"
            + _code('if ($env:OPENAI_API_KEY) { "已配置（不显示密钥）" } else { "未读取到，请重新打开终端" }', "PowerShell · 只检查是否存在，不输出 Key")
            + "<p>看到“已配置”后执行下一行。竖线 <code>|</code> 会把 Key 直接传给登录命令，不会把它打印到屏幕。</p>"
            + _code('$env:OPENAI_API_KEY | codex.cmd login --with-api-key', "PowerShell · 用 Key 登录")
            + "<p>用户变量会保留，今后新开的程序可能读取到它。它不是加密的保险箱；不用时可以回到同一窗口删除这一项。删除变量不会自动撤销平台上的 Key，也不会清除 Codex 已保存的登录。</p>",
            "<p>Mac 先使用<strong>当前终端的临时变量</strong>，不用把真实 Key 写进启动配置文件。先单独执行下面这一行，再在出现的提示后粘贴真实 Key，按回车。输入不会显示字符，是正常的。</p>"
            + _code('read -rs "OPENAI_API_KEY?粘贴 API Key 后按回车（输入不显示）: "', "Mac 终端（zsh）· 先执行这一行，再输入 Key")
            + "<p>输入完成后，再逐行执行下面两行。第一行把变量交给子程序读取；第二行只检查是否存在，不显示密钥内容。</p>"
            + _code('export OPENAI_API_KEY\nif [[ -n "$OPENAI_API_KEY" ]]; then printf "已配置（不显示密钥）\\n"; else printf "未读取到，请重新输入\\n"; fi', "Mac 终端 · 检查环境变量")
            + _code('printenv OPENAI_API_KEY | codex login --with-api-key', "Mac 终端 · 将 Key 传给登录命令")
            + "<p>这一行把变量传给 Codex，不要只运行前半段 <code>printenv OPENAI_API_KEY</code>，否则会显示密钥。关闭终端后临时变量消失；Codex 会另外保存登录凭据，下次先检查登录状态，不必反复把 Key 写进配置文件。其他工具若仍需要变量，需要单独设置。</p>",
        )
        + """
      <p>环境变量存在，只能说明“程序有机会读到一段值”，不代表 Key 正确、有余额或有模型权限。真正的调用验证在第 6 步。也不要以为新建一个 <code>.env</code> 文件就会自动生效：只有明确支持读取它的程序才会使用。</p>
    </details>
    <h4>两条路线都要做：检查登录状态</h4>
"""
        + _platforms(_code("codex.cmd login status"), _code("codex login status"))
        + """
    <p class='guide-check'><strong>过关标志：</strong>状态显示已登录，认证方式与你选择的一致。状态文本可能包含账号或密钥片段，请不要直接分享原始输出。登录成功仍不等于一定有调用额度，下一步要实际发送请求。</p>
  </article>

  <article class='tutorial-block' id='codex-folder'>
    <p class='card-kicker'>05 · 准备练习位置</p>
    <h3>只在一个专用文件夹里尝试</h3>
    <p>下面的命令会在“文档”中新建 <code>my-first-codex</code> 文件夹，再进入它。如果同名文件夹已经有重要资料，请先换一个新的练习名称。这里不用 Git，也不需要下载别人的项目。</p>
"""
        + _platforms(
            _code("$practice = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'my-first-codex'\nNew-Item -ItemType Directory -Force -Path $practice | Out-Null\nSet-Location $practice\nGet-Location", "PowerShell · 创建、进入并显示练习路径")
            + "<p>第一行获取你电脑实际的“文档”位置，所以即使文档由 OneDrive 管理，也不用照抄别人的用户名。想查看文件夹，可以在资源管理器中打开“文档”。</p>",
            _code('mkdir -p "$HOME/Documents/my-first-codex"\ncd "$HOME/Documents/my-first-codex"\npwd', "Mac 终端 · 创建、进入并显示练习路径")
            + "<p><code>mkdir</code> 创建文件夹，<code>cd</code> 进入文件夹，<code>pwd</code> 显示当前位置。也可以在访达的“文稿”中找到它。</p>",
        )
        + """
    <p class='guide-check'><strong>过关标志：</strong>最后显示的路径以 <code>my-first-codex</code> 结尾。接下来的命令都在这个窗口里运行；不要选整块磁盘或放有工作资料的文件夹。</p>
  </article>

  <article class='tutorial-block' id='connection-check'>
    <p class='card-kicker'>06 · 真正试一次</p>
    <h3>收到第一条回复，才算配置成功</h3>
    <p>在刚才的文件夹中启动 Codex。这里先使用只读模式，不需要让 AI 修改文件。</p>
"""
        + _platforms(_code("codex.cmd --sandbox read-only"), _code("codex --sandbox read-only"))
        + """
    <p>第一次可能询问是否信任当前目录，确认显示的是自己的练习文件夹再继续。若出现系统环境或沙箱初始化提示，按官方支持步骤完成；安装失败时先去排错，不要使用关闭全部保护的参数。进入 Codex 后，输入位置变成对话框：接下来的中文发给 Codex，<strong>不用再当 PowerShell 或 zsh 命令执行</strong>。</p>
"""
        + _code("请只回复：连接成功，我已经可以开始使用 AI。\n不要读取或修改文件，不要运行命令。", "发到 Codex 对话框 · 验证连接")
        + """
    <p class='guide-check'><strong>第一关完成：</strong>看到 AI 返回的文字，且没有认证、额度或网络错误。只看到输入界面、版本号或“已登录”，都还不算完成这一步。</p>
    <h4>再做一件有用的小事</h4>
"""
        + _code("请把下面的安排整理成待办清单，不要读取文件或执行命令：\n明天上午 10 点开会，周五之前交读书笔记，有空整理书桌。\n保留原文中的相对时间，不要自行推算日期；没有确定时间的标为“待确认”。", "仍然发到 Codex 对话框 · 第一次实际应用")
        + """
    <p>核对三件事：是否保留了三项任务，是否保留了“明天”“周五”的说法，是否给整理书桌标了“待确认”。有遗漏就直接指出，让它修改。你已经可以开始学习提问和检查结果了。</p>
    <details class='guide-faq'><summary>关闭以后，下次怎么再打开？</summary><p>退出 Codex 可以按 Control + C（Windows 是 Ctrl + C），如果提示需要再按一次，就按提示操作。下次打开终端，重新执行第 5 步进入练习文件夹，再运行本步启动命令。先前登录通常会保留；失效时再按第 4 步重新登录，不需要每次重装软件。</p></details>
  </article>

  <section class='tutorial-block' id='codex-help' aria-labelledby='codex-help-title'>
    <p class='card-kicker'>卡住时按现象查</p>
    <h3 id='codex-help-title'>不用先读懂报错，先找到对应的一项</h3>
    <details class='guide-faq' id='help-command'><summary>“找不到命令”“不是内部或外部命令” / command not found</summary><p>先区分是哪条命令：<code>node</code> 或 <code>npm</code> 找不到，回到第 2 步确认 Node.js 安装成功，完全退出并重开终端。只有 Codex 找不到，检查第 3 步安装是否报错，以及 PATH 是否包含安装目录。</p>
"""
        + _platforms(
            _code("npm.cmd config get prefix", "PowerShell · 查看 npm 实际安装目录")
            + "<p>这条命令显示 npm 的安装目录。用资源管理器打开该目录，检查是否有 <code>codex.cmd</code>。有文件却找不到命令时，在“用户变量 → Path → 编辑 → 新建”中添加这一目录，保留原有各项，再完全退出并重新打开终端。没有该文件则先解决安装错误，不要只改 PATH。</p>",
            _code('"$HOME/.local/bin/codex" --version', "Mac 终端 · 用完整路径检查")
            + "<p>完整路径能显示版本，说明只是 PATH 问题，补完第 3 步的 .zprofile 配置；提示文件不存在，则回看安装输出。不要把安装失败和路径设置当成同一种问题。</p>",
        )
        + """
    </details>
    <details class='guide-faq'><summary>Windows 提示“禁止运行脚本” / npm.ps1 无法加载</summary><p>确认按 Windows 教程写的是 <code>npm.cmd</code> 和 <code>codex.cmd</code>，包括后面的 .cmd。它们是 Windows 的命令入口。这篇教程无需修改 PowerShell 的执行策略；公司设备的其他安装限制应由管理员处理。</p></details>
    <details class='guide-faq'><summary>Mac 安装出现 EACCES / permission denied</summary><p>确认使用第 3 步带 <code>--prefix "$HOME/.local"</code> 的安装命令，目标是自己的用户目录。如果此前用其他方式安装过，需要先确认目录归属和已有安装，别直接给整段命令加 sudo。</p></details>
    <details class='guide-faq'><summary>Windows 提示系统不支持，或沙箱初始化失败</summary><p>先记录 Windows 版本、CPU 架构、Codex 版本和完整错误（隐藏私人信息），核对 <a href='https://developers.openai.com/codex/windows' target='_blank' rel='noopener noreferrer'>官方 Windows 支持说明</a>。本文采用原生 PowerShell 路线；如果官方针对你的环境要求 WSL，它就是另一套 Linux 环境，不能直接把本文的 Windows 命令混进去。不要通过关闭沙箱来硬跑。</p></details>
    <details class='guide-faq'><summary>我设置了环境变量，还是说没有 Key</summary><p>Windows 检查是否设置在当前用户下、变量名是否准确，并完全退出再打开终端；Mac 的临时变量必须在同一个终端中使用，而且需要执行 export。先运行第 4 步的“只检查是否存在”命令。不要直接输出真实 Key。变量已存在但登录失败，再检查密钥本身。</p></details>
    <details class='guide-faq'><summary>提示 401 / invalid API key / authentication failed</summary><p>确认走的是 API 路线、Key 来自 OpenAI、没有复制空格或引号、所属项目正确且未被撤销。必要时在原平台撤销旧 Key 并重新创建，再更新变量、重新执行 Key 登录命令；仅修改变量不一定会替换 Codex 保存的登录。账号登录路线则重新完成账号授权。</p></details>
    <details class='guide-faq'><summary>登录成功，但提示无权限、额度不足或 429</summary><p>先看错误正文：账号权限不足、API 余额不足和请求太频繁需要不同处理。账号路线查套餐、组织权限与额度；API 路线查对应项目的账单、用量和模型权限。429 既可能是请求速率限制，也可能是额度问题，不能一律靠充值或重复请求解决。</p></details>
    <details class='guide-faq'><summary>下载失败、一直转圈、超时或 connection refused</summary><p>先判断发生在下载、登录还是发请求：下载阶段检查 Node/npm 的错误和官方下载服务是否可达；登录阶段检查官方登录页面是否能打开；发请求阶段检查网络、服务状态和错误中的地址。若地址指向 127.0.0.1，它是你自己的电脑，可能是之前配置的本地服务没有启动。本教程的官方云服务路线不需要你填写本地服务地址，先核对是否残留了其他配置。</p></details>
    <details class='guide-faq'><summary>终端里出现了 Key，或者我把它发出去了</summary><p>到创建 Key 的平台撤销它，重新创建并更新使用它的工具。删除截图、清空终端或删除环境变量，都不能代替撤销已经泄露的密钥。不要把旧 Key 再贴到求助信息中。</p></details>
    <details class='guide-faq'><summary>我该怎样描述问题，才能得到帮助？</summary><p>写清：Windows 还是 Mac、工具版本、进行到第几步、运行的命令（移除任何密钥）、预期结果、实际错误。截图只保留必要区域，遮住邮箱、Key、验证码和登录链接。反馈前先按上述条目做一次检查。</p></details>
  </section>

  <article class='tutorial-block' id='first-task'>
    <p class='card-kicker'>选做 · 已经收到回复后</p>
    <h3>再用 Codex 做一张学习名片</h3>
    <p>这一步才开始创建文件。在 Codex 中按 Ctrl + C（Mac 也是 Control + C）退出，回到命令提示符，保持当前练习文件夹，再用允许修改当前工作目录的模式启动。权限范围仍只限于这次练习。</p>
"""
        + _platforms(_code("codex.cmd --sandbox workspace-write"), _code("codex --sandbox workspace-write"))
        + _code("我是第一次使用 Codex，没有编程基础。\n请在当前 my-first-codex 文件夹里做一张学习名片。\n先不要修改任何文件，先用三句话说明准备做什么，等我确认。\n\n标题：你好，这是我的第一张 AI 学习名片\n介绍：我正在学习用 AI 把想法变成作品。\n三个兴趣标签：阅读、旅行、AI\n底部文字：今天，我完成了第一次尝试。\n\n只创建一个 index.html 文件，样式也放在这个文件里。\n不要安装依赖或加载网络图片、字体；要能双击文件直接打开。\n不要自动执行删除、上传、发布或修改系统设置的命令。\n完成后告诉我文件保存在哪里。", "发到 Codex 对话框 · 创建前先看计划")
        + """
    <p>确认计划只涉及当前文件夹里的一个网页文件，再回复“可以，按这个计划创建 index.html”。如果请求额外权限，先核对具体内容；不理解的操作先让它解释。</p>
    <h4 id='check-result'>打开成品，自己检查一遍</h4>
    <p>在“文档 / 文稿”的 <code>my-first-codex</code> 文件夹里找到 <code>index.html</code>，右键选择用浏览器打开。核对标题、介绍、三个标签和底部文字，再把窗口缩窄，检查文字是否被截断。若看到一堆代码，检查是否用文本编辑器打开，或文件名误变成 <code>index.html.txt</code>。</p>
    <p>地址以 <code>file://</code> 开头表示打开本机文件；这还不是朋友可以访问的网址。共享文件或发布网站是下一阶段的任务。</p>
    <h4 id='codex-edit'>体验一次修改</h4>
"""
        + _code("把兴趣标签“旅行”改成“摄影”，其他内容保持原样。\n完成后告诉我改了哪个文件，我应该怎样检查。", "发到同一个 Codex 对话框")
        + """
    <p class='guide-check'>刷新浏览器后看到了“摄影”，才算这次修改完成。把练习文件夹复制一份留作备份，再记下自己卡住过的步骤。</p>
  </article>
  <aside class='guide-next'>
    <h3>把第一次配置的经历留下来</h3>
    <p>记下操作系统、使用方式、遇到的错误和解决办法。下次换电脑时，这就是自己的配置清单。</p>
    <p><a href='/about/journal'>看看我的实践与思考 →</a> · <a href='/blog'>去知行简报发现新变化 →</a></p>
    <p class='guide-note'>下方“本地工具箱”是另一个项目的部署说明，先完成上面这一条路线即可。</p>
  </aside>
  <p class='guide-copy-status' role='status' aria-live='polite'></p>
</section>
<script>
(() => {
  const guide = document.getElementById('codex-start');
  const choices = [...guide.querySelectorAll('input[name="guide-os"]')];
  function setPlatform(platform) {
    choices.forEach(input => { input.checked = input.value === platform; });
    guide.querySelectorAll('[data-guide-os]').forEach(part => {
      part.hidden = part.dataset.guideOs !== platform;
    });
    document.getElementById('guide-os-status').textContent = platform === 'mac'
      ? '当前显示 macOS 步骤，所有命令按 Mac 默认的 zsh 终端编写。'
      : '当前显示 Windows 步骤，所有命令在 PowerShell 中执行。';
  }
  choices.forEach(input => input.addEventListener('change', () => setPlatform(input.value)));
  // Every new visit starts with Windows, including on a Mac. Do not infer the OS.
  setPlatform('windows');
  function revealAnchor() {
    const target = document.getElementById(location.hash.slice(1));
    if (!target || !guide.contains(target)) return;
    let node = target;
    let opened = false;
    while (node && node !== guide) {
      if (node.tagName === 'DETAILS' && !node.open) { node.open = true; opened = true; }
      node = node.parentElement;
    }
    if (opened) requestAnimationFrame(() => target.scrollIntoView({block: 'start'}));
  }
  window.addEventListener('hashchange', revealAnchor);
  guide.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash) revealAnchor();
  });
  revealAnchor();
  guide.querySelectorAll('.guide-copy').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const code = button.closest('.guide-code').querySelector('code');
      const status = guide.querySelector('.guide-copy-status');
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.textContent = '已复制';
        status.textContent = '已复制。请按代码框上方标注，粘贴到终端或 Codex 对话框。';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = '请手动复制';
        status.textContent = '浏览器未允许自动复制，已选中文字，请使用系统复制快捷键。';
      }
      setTimeout(() => { button.textContent = '复制'; }, 2500);
    });
  });
})();
</script>
"""
    )
