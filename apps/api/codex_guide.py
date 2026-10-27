"""A progressively enhanced beginner lesson for the live and exported site."""

from __future__ import annotations

from html import escape

from apps.api.codex_guide_script import GUIDE_SCRIPT
from apps.api.codex_walkthrough import render_walkthrough


STEPS = (
    ("codex-account", "确认账号", "选一种登录方式", "后面的步骤会跟随你的选择。"),
    ("setup-terminal", "安装 Node.js", "先装 Node.js", "它自带 npm，用来安装下一步的 Codex。"),
    ("setup-install", "安装 Codex", "把 Codex 装好", "接着检查命令能不能运行。"),
    ("setup-auth", "完成登录", "连接你的账号", "在这一节完成登录，再检查状态。"),
    ("codex-folder", "建练习文件夹", "给练习留一个文件夹", "之后生成的文件，都放在这里。"),
    ("connection-check", "发出第一句话", "现在，问它一句话", "这次收到回复，才说明账号和服务都能用。"),
)


def _code(text: str, label: str = "复制到终端，按回车执行", *, prompt: bool = False) -> str:
    kind = " is-prompt" if prompt else ""
    return (
        f"<div class='guide-code{kind}'><div class='guide-code-heading'>"
        f"<span>{escape(label)}</span><button type='button' class='guide-copy' hidden>复制</button>"
        f"</div><pre tabindex='0'><code>{escape(text.strip())}</code></pre></div>"
    )


def _platforms(windows: str, mac: str) -> str:
    return (
        "<div class='guide-platform' data-guide-os='windows'>"
        "<p class='guide-platform-label'>Windows / PowerShell</p>" + windows + "</div>"
        "<div class='guide-platform' data-guide-os='mac' hidden>"
        "<p class='guide-platform-label'>macOS / zsh 终端</p>" + mac + "</div>"
    )


def _result(title: str, text: str) -> str:
    return f"<div class='lesson-result'><p><strong>{escape(title)}</strong>{text}</p></div>"


def _step(index: int, body: str) -> str:
    anchor, short_title, title, description = STEPS[index]
    return (
        f"<article class='lesson-step' id='{anchor}' data-step='{index}' data-short-title='{short_title}' tabindex='-1'>"
        "<header class='lesson-step-header'>"
        f"<span class='lesson-step-number' aria-hidden='true'>{index + 1:02d}</span><div>"
        "<p class='step-settings'><a href='#guide-system'>切换系统 / 跳转章节 ↑</a></p>"
        f"<h2>{title}</h2></div></header>"
        + (_route_choices() if index == 0 else "")
        + render_walkthrough(index, _code)
        + f"<details class='lesson-text'><summary>完整文字步骤与补充说明</summary><div>{body}</div></details></article>"
    )


def _route_choices() -> str:
    return """
<div class='lesson-route-choices' role='group' aria-label='选择登录方式'>
  <button type='button' data-route-choice='account' aria-pressed='true' hidden><small>用已有的产品账号</small><strong>ChatGPT 账号</strong><small>不需要填写 API Key</small></button>
  <button type='button' data-route-choice='api' aria-pressed='false' hidden><small>用开发者接口</small><strong>API Key</strong><small>单独按 API 用量计费</small></button>
</div>
"""


def _account() -> str:
    return """
<div data-auth='account'>
  <ol>
    <li>打开 <a href='https://chatgpt.com/' target='_blank' rel='noopener noreferrer'>ChatGPT 官网</a>。已有账号就点 <strong>Log in（登录）</strong>；没有就点 <strong>Sign up（注册）</strong>，按页面提示完成验证。</li>
    <li>确认自己的账号有 Codex 使用权限和剩余额度。能登录 ChatGPT，不代表一定能使用 Codex。</li>
    <li>记住注册时选择的登录方式，第 4 步还会用到。</li>
  </ol>
  <p class='lesson-margin-note'>如果页面提示升级、组织限制或所在地区不可用，先处理这一项，再继续安装。本文不保证新账号免费可用。</p>
</div>
<div data-auth='api' hidden>
  <p><strong>API Key</strong> 是程序调用服务时使用的凭据。这里采用 OpenAI 官方接口，其他平台的 Key 不能直接照填。</p>
  <ol>
    <li>打开 <a href='https://platform.openai.com/' target='_blank' rel='noopener noreferrer'>OpenAI 开发者平台</a>，注册或登录自己的账号。</li>
    <li>在 <strong>Billing（账单）</strong> 和 <strong>Usage（用量）</strong> 页面确认项目可用、费用和付款条件。</li>
    <li>第 4 步会带你创建 Key，并设置到电脑中。现在先完成安装。</li>
  </ol>
  <p class='lesson-margin-note'>ChatGPT 订阅和 API 费用分开。先看清计费方式，再决定是否付费；预算提醒也不一定是扣费上限。</p>
</div>
<details class='guide-faq'><summary>我还没有账号，也没有 Key</summary><p>先尝试上面的账号注册步骤。只有确认要用 API 接口时，才需要创建 Key。若两条路线的账号或服务都不可用，先解决可用性问题，不要急着买软件或密钥。</p></details>
"""


def _node() -> str:
    return (
        "<p>从 <a href='https://nodejs.org/en/download' target='_blank' rel='noopener noreferrer'>Node.js 官网</a>下载标有 <strong>LTS（长期支持）</strong>、支持你电脑系统的安装包。已经装过的，可以直接检查版本。</p>"
        + _platforms(
            "<ol><li>在“设置 → 系统 → 关于”查看系统类型，下载匹配的 Windows 安装包（通常为 .msi）。</li>"
            "<li>双击安装，保留默认的 npm 和 PATH 选项。额外的编译工具，这一课不用安装。</li>"
            "<li>安装完，关闭原来的终端。在开始菜单搜索 <strong>PowerShell</strong>，正常打开，无需管理员权限。</li></ol>"
            + _code("node --version\nnpm.cmd --version", "在 PowerShell 中逐行执行")
            + "<p>每行按一次回车。只复制框里的命令，不要把窗口原有的 <code>PS C:…&gt;</code> 一起输入。</p>",
            "<ol><li>在“苹果菜单 → 关于本机”查看芯片和系统版本，下载匹配的 macOS 安装包（.pkg）。</li>"
            "<li>打开安装包，按提示完成。系统不支持时，先核对官网下载要求。</li>"
            "<li>按 <strong>Command + 空格</strong>，搜索“终端”并打开。之前开着终端的，退出应用后重新打开。</li></ol>"
            + _code("node --version\nnpm --version", "在 Mac 终端中逐行执行")
            + "<p>每行按一次回车。本教程的 Mac 命令使用默认的 zsh；不需要复制窗口里已有的提示符。</p>",
        )
        + _result("应该看到", "两行版本号：Node.js 通常以 <code>v</code> 开头，npm 是数字。版本不必与别人相同。找不到命令时，查看 <a href='#help-command'>这条排错</a>。")
        + "<details class='guide-faq'><summary>PATH 是什么？为什么 Windows 命令后面有 .cmd？</summary><p>PATH 是电脑寻找命令的位置列表。安装程序会把所需路径加进去；手动修改时不要覆盖原有项。Windows 这里使用 npm.cmd 和 codex.cmd，调用它们的命令入口，避免误用 PowerShell 脚本入口。</p></details>"
    )


def _install() -> str:
    return (
        "<p>在刚才的终端执行安装命令，等它结束。已经安装过 Codex 的，直接运行版本检查即可。</p>"
        + _platforms(
            _code("npm.cmd install -g @openai/codex", "① 安装 Codex")
            + _code("codex.cmd --version", "② 检查版本"),
            "<p>下面安装到你自己的 <code>.local</code> 目录。第一行下载软件，第二行让当前终端找到它，第三行检查版本。</p>"
            + _code('npm install --global --prefix "$HOME/.local" @openai/codex\nexport PATH="$HOME/.local/bin:$PATH"\ncodex --version', "逐行执行，不需要 sudo")
            + "<details class='guide-faq' open><summary>再保存一次 PATH，下次打开终端也能用</summary><p>运行下面的命令，打开配置文件。不存在时会新建，已有文字请保留。</p>"
            + _code('nano "$HOME/.zprofile"', "打开文字编辑器")
            + "<p>在文件末尾单独加一行；已经有相同内容就不用重复添加：</p>"
            + _code('export PATH="$HOME/.local/bin:$PATH"', "这行放进编辑器里的文件")
            + "<p>按 <strong>Control + O</strong>、回车保存，再按 <strong>Control + X</strong> 退出。重新打开终端，运行 <code>codex --version</code>。这里用的是 Control，不是 Command。</p><p><code>$HOME</code> 代表你的用户目录，照抄即可。</p></details>",
        )
        + _result("安装完成的标志", "终端显示 <code>codex-cli</code> 和版本号。若只有 npm 更新提示，继续做版本检查；如果报错，先处理错误。")
    )


def _auth() -> str:
    return (
        "<div data-auth='account'><p>执行下面的命令。出现选择时，选 <strong>Sign in with ChatGPT</strong>。</p>"
        + _platforms(_code("codex.cmd login", "PowerShell · 账号登录"), _code("codex login", "Mac 终端 · 账号登录"))
        + "<ol><li>在打开的官方网页中，用第 1 步的账号登录并授权。</li><li>完成后返回终端。浏览器没自动打开时，手动打开终端给出的官方登录链接。</li></ol>"
        + "<p>这条路线不用设置 API Key。登录链接和验证码不要分享给别人。</p></div>"
        + """
<section data-auth='api' id='setup-key-reference' hidden>
  <h3>1. 创建自己的 Key</h3>
  <ol>
    <li>登录 <a href='https://platform.openai.com/' target='_blank' rel='noopener noreferrer'>开发者平台</a>，确认当前项目和账单设置。</li>
    <li>进入 <a href='https://platform.openai.com/api-keys' target='_blank' rel='noopener noreferrer'>API keys 页面</a>，点 <strong>Create new secret key</strong>，按页面设置项目与所需权限。名称可用 <code>codex-practice</code>。</li>
    <li>按提示复制密钥，保存在自己的密码管理器里。下面会把它交给你电脑上的 Codex。</li>
  </ol>
  <p class='lesson-margin-note'>Key 只填在自己的电脑里。不要贴到本博客、聊天截图或公开仓库。</p>
  <h3>2. 配置环境变量</h3>
  <p>环境变量是一项给程序读取的设置：<code>OPENAI_API_KEY</code> 是名称，你的 Key 是它的值。</p>
"""
        + _platforms(
            "<ol><li>在开始菜单搜索 <strong>编辑账户的环境变量</strong>。如果打开的是“系统属性”，再点“环境变量”。</li>"
            "<li>在上半部分的<strong>用户变量</strong>中点“新建”，按下面的示意填写。有同名项时，先确认原有用途，再编辑。</li></ol>"
            + "<figure class='lesson-config-example'><figcaption>填写示意 · 在 Windows 设置窗口中操作</figcaption><dl><dt>变量名</dt><dd><code>OPENAI_API_KEY</code></dd><dt>变量值</dt><dd>粘贴你刚创建的 Key，不加引号</dd></dl></figure>"
            + "<p>点“确定”保存。<strong>完全退出 PowerShell / Windows Terminal，再从开始菜单打开。</strong>如果用的是编辑器里的终端，也重新打开编辑器。</p>"
            + _code('if ($env:OPENAI_API_KEY) { "已配置（不显示密钥）" } else { "未读取到，请重新打开终端" }', "③ 检查是否读到了设置")
            + "<p>看到“已配置”后，执行下面这一整行：</p>"
            + _code('$env:OPENAI_API_KEY | codex.cmd login --with-api-key', "④ 将 Key 传给 Codex")
            + "<details class='guide-faq'><summary>关掉窗口以后，这个设置还在吗？</summary><p>Windows 用户变量会保留，之后新开的程序也可能读取它。它不是加密的保险箱。不再需要时可在同一设置窗口删除这一项；删除变量不会撤销平台上的 Key，也不会清除 Codex 保存的登录。不要把 Key 填进 PATH 或系统变量。</p></details>",
            "<p>Mac 先用当前终端的临时变量。<strong>先单独执行这一行</strong>，再在提示后粘贴 Key，按回车。输入不会显示字符。</p>"
            + _code('read -rs "OPENAI_API_KEY?粘贴 API Key 后按回车（输入不显示）: "', "① 执行后，再输入你的 Key")
            + "<p>输入完成后，逐行执行：</p>"
            + _code('export OPENAI_API_KEY\nif [[ -n "$OPENAI_API_KEY" ]]; then printf "已配置（不显示密钥）\\n"; else printf "未读取到，请重新输入\\n"; fi', "② 让程序读取变量，并检查是否存在")
            + _code('printenv OPENAI_API_KEY | codex login --with-api-key', "③ 将 Key 传给 Codex · 执行整行")
            + "<details class='guide-faq'><summary>关掉终端以后，下次还需要输入吗？</summary><p>临时变量会消失，但 Codex 会另外保存登录凭据。下次先检查登录状态，失效时再登录；其他工具需要变量时要另行设置。不要只执行上面命令的前半段 printenv OPENAI_API_KEY，否则会显示真实密钥。</p></details>",
        )
        + "<p>这里只检查设置是否存在。Key 是否正确、额度是否可用，要等第 6 步实际请求才能确认。</p></section>"
        + "<h3>最后，检查登录状态</h3>"
        + _platforms(_code("codex.cmd login status"), _code("codex login status"))
        + _result("应该看到", "已登录的状态，且登录方式与你的选择一致。状态可能带账号或密钥片段，请勿直接分享原始输出。")
    )


def _folder() -> str:
    return (
        "<p>在“文档”里新建 <code>my-first-codex</code>。如果已有同名文件夹且存了重要资料，请换一个练习名称。</p>"
        "<div class='lesson-folder'><svg width='38' height='32' viewBox='0 0 38 32' fill='none' aria-hidden='true'><path d='M2 7V3h13l4 4h17v22H2V7Z' fill='currentColor' opacity='.2'/><path d='M2 10V3h13l4 4h17v22H2V10Zm0 0h34' stroke='currentColor' stroke-width='1.5'/></svg><p><small>文档 / 文稿</small><code>my-first-codex/</code></p></div>"
        + _platforms(
            _code("$practice = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'my-first-codex'\nNew-Item -ItemType Directory -Force -Path $practice | Out-Null\nSet-Location $practice\nGet-Location", "创建文件夹 → 进入 → 显示位置")
            + "<p>第一行会找到你电脑实际的“文档”目录，包括由 OneDrive 管理的情况。不用替换成别人的用户名。</p>",
            _code('mkdir -p "$HOME/Documents/my-first-codex"\ncd "$HOME/Documents/my-first-codex"\npwd', "创建文件夹 → 进入 → 显示位置")
            + "<p><code>mkdir</code> 创建文件夹，<code>cd</code> 进入，<code>pwd</code> 显示位置。在访达的“文稿”里也能找到它。</p>",
        )
        + _result("看最后一行", "路径以 <code>my-first-codex</code> 结尾。接下来继续在这个窗口操作，不要选整块磁盘或放着工作资料的目录。")
    )


def _first_reply() -> str:
    return (
        "<p>在刚才的练习文件夹中启动 Codex。这次只需要回复文字，先用只读模式。</p>"
        + _platforms(_code("codex.cmd --sandbox read-only"), _code("codex --sandbox read-only"))
        + "<p>如果询问是否信任目录，确认是自己的练习文件夹再继续。进入对话界面后，把下面这段话发给 Codex：</p>"
        + _code("请只回复：连接成功。\n不要读取或修改文件，不要运行命令。", "发到 Codex 对话框，不是终端命令", prompt=True)
        + _result("等它回复", "收到“连接成功”或意思相同的回答，且没有认证、额度或网络错误，配置就完成了。")
        + "<details class='guide-faq'><summary>想再试一个日常任务</summary>"
        + _code("请整理成待办清单，不要读取文件或执行命令：\n明天上午 10 点开会，周五之前交读书笔记，有空整理书桌。\n保留原文中的相对时间；没有确定时间的标为“待确认”。", "继续发到 Codex 对话框", prompt=True)
        + "<p>核对是否保留了三项任务，有没有自行编造日期。漏了或理解错了，直接指出，让它改。</p></details>"
        + "<details class='guide-faq'><summary>下次怎么再打开？</summary><p>按 Ctrl + C（Mac 用 Control + C）退出；如果提示需要再按一次，按提示操作。下次打开终端，重复第 5 步进入文件夹，再运行本步的启动命令。不必每次重新安装；登录失效时再完成第 4 步。</p></details>"
        + "<p class='lesson-margin-note'>沙箱或系统初始化失败时，先看 <a href='#help-windows'>对应排错</a>。不要用关闭全部保护的参数跳过错误。</p>"
    )


def _help() -> str:
    return (
        "<section class='lesson-support' id='codex-help' aria-labelledby='codex-help-title'><header><h2 id='codex-help-title'>卡在这里？</h2><p>按屏幕上的报错找。</p></header><div>"
        "<details class='guide-faq' id='help-command'><summary>找不到命令 / command not found</summary><p>找不到 node 或 npm：确认 Node.js 安装成功，完全退出再打开终端。只有 Codex 找不到：先检查安装有没有报错，再检查 PATH。</p>"
        + _platforms(
            _code("npm.cmd config get prefix", "查看 npm 安装目录")
            + "<p>用资源管理器打开显示的目录，检查有无 codex.cmd。有文件时，在“用户变量 → Path → 编辑 → 新建”中添加这一目录，保留原有项，再重开终端。没有文件则回到 <a href='#setup-install'>安装步骤</a>处理报错。</p>",
            _code('"$HOME/.local/bin/codex" --version', "用完整路径检查")
            + "<p>能显示版本，说明是 PATH 问题，补完 <a href='#setup-install'>第 3 步</a>的 .zprofile 配置；文件不存在则先处理安装错误。</p>",
        )
        + """
</details>
<details class='guide-faq'><summary>禁止运行脚本 / npm.ps1 无法加载</summary><p>Windows 按本文使用 <code>npm.cmd</code> 和 <code>codex.cmd</code>，包括 .cmd 后缀。无需修改 PowerShell 执行策略；公司设备的其他安装限制应由管理员处理。</p></details>
<details class='guide-faq'><summary>Mac 提示 EACCES / permission denied</summary><p>使用 <a href='#setup-install'>第 3 步</a>带 <code>--prefix "$HOME/.local"</code> 的命令，安装到自己的目录。若之前用过其他安装方式，先核对目录归属，不要直接给命令加 sudo。</p></details>
<details class='guide-faq' id='help-windows'><summary>Windows 不支持 / 沙箱初始化失败</summary><p>核对系统版本、CPU 架构、Codex 版本与 <a href='https://developers.openai.com/codex/windows' target='_blank' rel='noopener noreferrer'>官方 Windows 支持说明</a>。本文是原生 PowerShell 路线；若你的环境需要 WSL，应按对应的 Linux 环境说明操作，不要混用命令或关闭沙箱来硬跑。</p></details>
<details class='guide-faq' id='help-key'><summary>环境变量设了，仍然读不到 Key</summary><p>Windows 检查名称是否为 OPENAI_API_KEY、是否属于当前用户，再完全退出并重开终端。Mac 的临时变量要在同一个窗口使用，并执行 export。回到 <a href='#setup-key'>Key 配置</a>做存在性检查，不要输出密钥。</p><p>新建 .env 文件不会让所有程序自动读取它，只有明确支持的程序才会使用。</p></details>
<details class='guide-faq'><summary>401 / invalid API key / 认证失败</summary><p>确认 Key 来自 OpenAI、项目正确、未被撤销，复制时没有空格或引号。更换 Key 后，更新变量并重新执行 Key 登录；仅修改变量不一定会替换 Codex 保存的登录。账号路线则重新完成授权。</p></details>
<details class='guide-faq'><summary>无权限 / 额度不足 / 429</summary><p>账号路线查套餐、组织权限和额度；API 路线查项目账单、用量和模型权限。429 可能是频率限制，也可能是额度问题，要看错误正文，不能一律靠充值或反复重试解决。</p></details>
<details class='guide-faq'><summary>下载失败 / 超时 / connection refused</summary><p>先分清发生在哪一步：下载失败查官方软件下载和 npm 错误；登录失败查官网是否能打开；发请求失败查网络、服务状态和报错中的地址。</p><p>127.0.0.1 代表你自己的电脑。若错误指向它，可能是原先配置的本地服务没启动。本文的官方云服务路线不需要填本地地址，先核对是否残留其他配置。</p></details>
<details class='guide-faq'><summary>Key 不小心发出去了</summary><p>到创建它的平台撤销旧 Key，再创建新的并更新工具。删除截图、清空终端或删掉环境变量，不能代替撤销密钥。</p></details>
<details class='guide-faq'><summary>还有问题，怎样描述才清楚？</summary><p>写明操作系统、工具版本、进行到第几步、运行的命令和实际错误。移除密钥、邮箱、验证码、登录链接，再提供必要的文字或截图。</p></details>
</div></section>
"""
    )


def _exercise() -> str:
    return (
        "<details class='lesson-exercise' id='first-task'><summary><span><small>配置完成后 · 选做</small><strong>做一张能打开的学习名片</strong></span></summary><div class='lesson-exercise-content'>"
        "<p>先用 Ctrl + C（Mac 也是 Control + C）退出 Codex，留在练习文件夹中，再启动允许修改当前工作目录的模式：</p>"
        + _platforms(_code("codex.cmd --sandbox workspace-write"), _code("codex --sandbox workspace-write"))
        + _code("请在当前 my-first-codex 文件夹里做一张学习名片。\n先不要修改任何文件，先说明计划，等我确认。\n\n标题：我的第一张 AI 学习名片\n介绍：我正在尝试用 AI 做一个网页。\n三个兴趣标签：阅读、旅行、AI\n\n只创建一个 index.html 文件，样式也放在里面。\n不安装依赖，不加载网络图片或字体，能双击直接打开。\n不要自动执行删除、上传、发布或修改系统设置的命令。\n完成后告诉我文件保存在哪里。", "发给 Codex · 先看计划，再确认创建", prompt=True)
        + "<p>核对计划只涉及当前文件夹中的网页，再回复“可以，按这个计划创建 index.html”。不理解的权限请求先让它解释。</p>"
        + "<h3 id='check-result'>打开看看</h3><p>在“文档 / 文稿”的练习文件夹中找到 <code>index.html</code>，右键选择浏览器打开。核对文字和标签，再把窗口缩窄，看看有没有内容被截断。</p>"
        + "<p>如果显示一堆代码，检查是否用文本编辑器打开，或文件名变成了 <code>index.html.txt</code>。地址以 <code>file://</code> 开头说明它还在本机，不能把这个路径当作网站链接发给朋友。</p>"
        + "<h3 id='codex-edit'>试着改一个地方</h3>"
        + _code("把“旅行”改成“摄影”，其他内容保持原样。\n告诉我改了哪个文件，怎样检查。", "发到同一个 Codex 对话框", prompt=True)
        + "<p>刷新浏览器，看到“摄影”后，把文件夹复制一份留作备份。</p></div></details>"
    )


def render_codex_guide() -> str:
    links = "".join(
        f"<li><a href='#{anchor}' data-step-link><span>{i + 1:02d}</span>{short}</a></li>"
        for i, (anchor, short, _, _) in enumerate(STEPS)
    )
    options = "".join(
        f"<option value='{anchor}'>{i + 1:02d} · {short}</option>"
        for i, (anchor, short, _, _) in enumerate(STEPS)
    )
    lessons = "".join(_step(i, render()) for i, render in enumerate((_account, _node, _install, _auth, _folder, _first_reply)))
    return (
        """
<section class='codex-guide' id='codex-start' aria-labelledby='codex-guide-title'>
  <header class='lesson-cover' id='start-here'>
    <div><p class='eyebrow'>实战教程 / 01 · 看图跟练</p><h1 id='codex-guide-title'>第一次用 Codex，<br />我们从打开窗口开始。</h1>
      <p class='cover-description' id='choose-tool'>不知道 Key 是什么，也没用过终端？把教程放在旁边，一屏做一件事。先装好，再收到第一条回复。</p>
      <div class='hero-actions'><a class='button-link' href='#codex-account'>开始跟练</a><a href='#codex-help'>我卡在某一步</a></div>
      <p class='cover-meta'>从零开始使用 Codex · Windows / macOS<br />无需编程基础 · 需要可用账号与网络</p>
    </div>
    <aside class='lesson-demo' aria-label='本课目标示意'>
      <div class='lesson-demo-bar'><i></i><i></i><i></i><span>练习目标</span></div>
      <p class='demo-command'>&gt; Codex 已打开</p>
      <p class='demo-message'>请只回复：连接成功。</p>
      <p class='demo-reply'>↳ 连接成功。</p>
      <small>这一课的终点：在你自己的电脑上收到回复。<br />此处为对话示意。</small>
    </aside>
  </header>
  <div class='lesson-intro-line'><p>只在自己的电脑上安装工具，这一课不用购买服务器。</p><a href='#setup-key'>已经卡在 Key 配置？直接看这里</a></div>
  <noscript><style>.codex-guide [data-guide-os][hidden],.codex-guide [data-auth][hidden]{display:block!important}.lesson-os-settings{display:none}</style><p>当前浏览器未启用 JavaScript，下面显示完整教程及两套系统步骤，请选择与你的电脑对应的部分。</p></noscript>
  <div class='lesson-frame'>
    <aside class='lesson-sidebar' id='guide-system' aria-label='教程设置与目录'>
      <fieldset class='lesson-os-settings'><legend>操作系统</legend><div class='lesson-os-options'>
        <label><input type='radio' name='guide-os' value='windows' checked /><span>Windows</span></label>
        <label><input type='radio' name='guide-os' value='mac' /><span>macOS</span></label>
      </div></fieldset>
      <div data-enhance hidden><label class='lesson-select-label' for='guide-auth'>登录方式</label><select id='guide-auth'><option value='account'>ChatGPT 账号</option><option value='api'>API Key</option></select></div>
"""
        + f"<nav aria-label='教程章节'><ol>{links}</ol></nav>"
        + f"<div class='lesson-mobile-navigation' data-enhance hidden><label class='lesson-select-label' for='guide-step-select'>跳到某一步</label><select id='guide-step-select'>{options}</select></div>"
        + """
      <a class='lesson-help-link' href='#codex-help'>遇到问题？查看排错</a>
      <span id='guide-os-status' class='lesson-sr-only' role='status'></span>
    </aside>
    <div class='lesson-paper'>
      <div class='lesson-toolbar' data-enhance hidden><span id='guide-reading-status' aria-live='polite'>第 1 章 / 共 6 章</span><button type='button' id='guide-read-all' aria-pressed='false'>展开全部操作</button></div>
"""
        + lessons
        + """
      <nav class='lesson-controls' aria-label='翻到上一或下一步' data-enhance hidden><a href='#codex-account' data-previous>上一步</a><a href='#setup-terminal' data-next>下一步：安装 Node.js</a></nav>
    </div>
  </div>
  <div class='lesson-afterword'><p>不需要一次记住所有命令。哪一步出错，就记下那一步和解决方法，下次换电脑时还能用。</p><a href='/about/journal'>我的实践记录</a></div>
"""
        + _help()
        + _exercise()
        + """
  <details class='lesson-references'><summary>图片来源、适用范围与参考 · 修订于 2026-10-27</summary>
    <p>Node.js 下载区是 2026-10-27 的官网截图，点击可放大。其余操作画面为本站绘制的示意，不冒充实机截图；网页里的练习不会安装软件或设置环境变量。</p>
    <p>结构参考：<a href='https://www.bilibili.com/video/BV1SjGi6nEZ6/' target='_blank' rel='noopener noreferrer'>枫枫知道 · Codex 新手教程</a>及其公开安装图文。只参考可公开访问的内容，未转载课程视频。具体命令以本课说明及官方资料为准。</p>
    <p>命令选项曾对照本机 Codex CLI 0.153.2 帮助信息核对。Windows 全新安装、真实新账号注册和付费调用尚未逐项实测；这篇教程不保证所有新账号免费可用。</p>
    <p>官方资料：<a href='https://developers.openai.com/codex/cli' target='_blank' rel='noopener noreferrer'>CLI 安装</a> · <a href='https://developers.openai.com/codex/windows' target='_blank' rel='noopener noreferrer'>Windows 支持</a> · <a href='https://developers.openai.com/codex/auth' target='_blank' rel='noopener noreferrer'>认证方式</a> · <a href='https://developers.openai.com/codex/pricing' target='_blank' rel='noopener noreferrer'>费用与额度</a>。</p>
    <p>上一轮核验时文档访问返回 403，当前系统要求、地区、套餐及额度未复核。以官方页面和账号内提示为准。</p>
  </details>
  <p class='guide-copy-status lesson-sr-only' role='status' aria-live='polite'></p>
</section>
"""
        + GUIDE_SCRIPT
    )
