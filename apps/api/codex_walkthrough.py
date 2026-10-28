"""Small, illustrated actions. Illustrations never claim to be live system UI."""

from html import escape


def _window(title: str, body: str, *, kind: str = "desktop") -> str:
    return f"<div class='walk-window is-{kind}'><div class='walk-titlebar'><span>{title}</span><span aria-hidden='true'>− &nbsp; □ &nbsp; ×</span></div><div class='walk-window-body'>{body}</div></div>"


def _path(*parts: str) -> str:
    return "<div class='walk-path'>" + "<span aria-hidden='true'>/</span>".join(f"<b>{p}</b>" for p in parts) + "</div>"


def _mark(number: int, text: str) -> str:
    return f"<div class='walk-mark'><b>{number}</b><span>{text}</span></div>"


def _terminal(code, command: str, output: str = "", *, label: str = "复制到自己电脑的终端，按回车", mac: bool = False) -> str:
    body = code(command, label)
    if output:
        body += f"<div class='walk-output'><small>结果示例 · 不是你电脑的检测结果</small><pre>{escape(output)}</pre></div>"
    return _window("终端 / zsh" if mac else "Windows PowerShell", body, kind="terminal")


def _scene(key: str, title: str, instruction: str, display: str, result: str,
           *, os: str = "", auth: str = "", real: bool = False, help: str = "", anchor: str = "") -> str:
    attrs = f" data-scene-os='{os}' data-scene-auth='{auth}'"
    labels = " · ".join(x for x in (("macOS" if os == "mac" else "Windows") if os else "", "账号登录" if auth == "account" else "API Key" if auth else "") if x)
    return (
        f"<section class='walk-scene' id='{anchor or 'walk-' + key}' data-scene='{key}'{attrs} aria-label='{escape(title)}'>"
        f"<header class='walk-scene-heading'><span>{labels or '两种系统通用'}</span><h3>{title}</h3></header>"
        "<div class='walk-layout'><figure class='walk-display'>"
        f"<figcaption>{'官网实拍 · 2026-10-27' if real else '操作示意 · 按钮位置随版本可能不同'}</figcaption>{display}</figure>"
        f"<aside class='walk-instruction'><p class='walk-do-label'>在你的电脑上</p><p>{instruction}</p>"
        f"<div class='walk-check'><span>做到这里</span><p>{result}</p></div>"
        + (f"<a class='walk-help' href='{help}'>对不上？看排错</a>" if help else "")
        + "</aside></div></section>"
    )


def _account(code) -> str:
    return (
        _scene("account-open", "先登录自己的 ChatGPT 账号", "打开官网。没有账号，选注册；已有账号，选登录。验证只在官网完成。",
               _window("浏览器 · chatgpt.com", "<div class='walk-browser-start'><strong>ChatGPT</strong><p>你现在属于哪一种？</p><div class='walk-account-paths'><div><span>还没有账号</span><b>Sign up / 注册</b><small>邮箱或可用的第三方账号<br>按官网提示验证</small></div><div><span>已经有账号</span><b>Log in / 登录</b><small>选原来的登录方式<br>不要重复注册</small></div></div><a class='ui-button' href='https://chatgpt.com/' target='_blank' rel='noopener noreferrer'>打开 ChatGPT 官网</a></div>", kind="browser"),
               "能够进入自己的账号。还打不开官网，就先停在这一步。", auth="account", anchor="codex-signup")
        + _scene("account-access", "再确认这个账号能用 Codex", "在官方 Codex 页面查看账号提示。若要求升级或显示不可用，先看清条件再决定。",
                 _window("浏览器 · chatgpt.com/codex", "<div class='walk-decision'><a href='https://chatgpt.com/codex' target='_blank' rel='noopener noreferrer'>打开官方 Codex 页面</a>" + _mark(1, "登录刚才的账号") + _mark(2, "查看 Codex 的使用权限、额度或升级提示") + "<div class='walk-branch'><div><b>可以使用</b><span>记住登录方式，继续安装</span></div><div><b>要求升级 / 不可用</b><span>先处理账号条件，不要继续盲装</span></div></div></div>", kind="browser"),
                 "确认账号有 Codex 使用权限。这条路线不需要买 Key。", auth="account")
        + _scene("api-account", "API 路线：先看项目与账单", "登录 OpenAI 开发者平台，检查项目、Billing 和 Usage。API 与 ChatGPT 订阅分开计费。",
                 _window("浏览器 · platform.openai.com", "<div class='walk-decision'><a href='https://platform.openai.com/' target='_blank' rel='noopener noreferrer'>打开 OpenAI 开发者平台</a>" + _path("当前项目", "Settings / 设置") + "<div class='walk-settings-row'><b>Billing / 账单</b><span>付款条件、余额与费用</span></div><div class='walk-settings-row'><b>Usage / 用量</b><span>项目用量与限制</span></div><div class='walk-callout'>第 4 章再创建 Key。<br>现在不用复制任何密钥。</div></div>", kind="browser"),
                 "确认自己的项目可以调用 API，并了解费用。预算提醒不一定是扣费上限。", auth="api")
    )


def _node(code) -> str:
    scenes = []
    for os in ("windows", "mac"):
        mac = os == "mac"
        about = ("苹果菜单", "关于本机") if mac else ("设置", "系统", "关于")
        specs = "<b>芯片：Apple M…</b><span>下载选 ARM64</span><b>处理器：Intel…</b><span>下载选 x64</span>" if mac else "<b>基于 x64 的处理器</b><span>下载选 x64</span><b>基于 ARM 的处理器</b><span>下载选 ARM64</span>"
        scenes.append(_scene(f"{os}-system", "看一眼自己的系统类型", "在电脑里打开图中位置，记下芯片 / 系统类型。安装包要与它一致。",
                             _window("关于本机" if mac else "设置 · 系统 · 关于", _path(*about) + "<div class='walk-specs'>" + specs + "</div><p class='walk-callout'>如果系统太旧，先核对 Node.js 的支持要求。</p>"), "知道下一步该选 x64 还是 ARM64。", os=os))
        download = "macos" if mac else "windows"
        scenes.append(_scene(f"{os}-download", "下载这个安装包", "打开下载页，选 LTS。往下找到图中这块，核对系统和芯片，再点安装包。上面的脚本先不用。",
                             f"<div class='walk-photo'><a href='/tutorials/assets/node-{download}-download.webp' target='_blank' rel='noopener'><picture><source media='(max-width:620px)' srcset='/tutorials/assets/node-{download}-mobile.webp' /><img src='/tutorials/assets/node-{download}-download.webp' alt='Node.js 官网下载区：{'macOS，ARM64，macOS Installer (.pkg)' if mac else 'Windows，x64，Windows Installer (.msi)'}；按自己电脑更改架构' width='735' height='122' loading='lazy' /></picture></a><div class='walk-photo-notes'>" + _mark(1, "核对系统和架构") + _mark(2, "点 Installer 安装包") + "</div><a class='walk-external' href='https://nodejs.org/en/download' target='_blank' rel='noopener noreferrer'>去 Node.js 官网下载</a><small>截图中的架构仅为示例，点图片可放大。</small></div>",
                             "下载文件以 .pkg 结尾。" if mac else "下载文件以 .msi 结尾。不要选 Standalone Binary 压缩包。", os=os, real=True))
        installer = (_mark(1, "在“下载”里双击 .pkg 文件") + _mark(2, "按“继续”，阅读许可并同意后安装") + _mark(3, "如系统要求，输入这台 Mac 的登录密码") + "<div class='walk-installer-end'><b>安装完成</b><span>关闭安装器，再开一个新的终端</span></div>" if mac else
                     _mark(1, "在“下载”里双击 .msi 文件") + _mark(2, "Next → 阅读许可并同意 → Next") + "<div class='walk-feature-list'><span>保留默认组件</span><b>✓ Node.js runtime</b><b>✓ npm package manager</b><b>✓ Add to PATH</b></div>" + _mark(3, "额外编译工具不用勾选；Install → Finish"))
        scenes.append(_scene(f"{os}-installer", "把安装向导走完", "按图中顺序完成安装。看到系统权限确认时，核对是刚下载的 Node.js 安装程序。", _window("Node.js Installer" if mac else "Node.js Setup", installer), "看到安装完成。下载完文件本身不代表已安装。", os=os))
        search = "终端" if mac else "PowerShell"
        scenes.append(_scene(f"{os}-terminal", "打开输入命令的窗口", "按 Command + 空格，搜索“终端”，按回车。粘贴命令用 Command + V，执行用回车。" if mac else "按 Windows 键搜索 PowerShell，点普通的“打开”，无需管理员权限。粘贴用 Ctrl + V，执行用回车。",
                             _window("Spotlight 搜索" if mac else "开始菜单 · 搜索", f"<div class='walk-search'><span>搜索</span><b>{search}</b></div><div class='walk-app-result'><span class='walk-app-icon' aria-hidden='true'>&gt;_</span><div><b>{'终端' if mac else 'Windows PowerShell'}</b><span>应用</span></div><em>打开</em></div><div class='walk-terminal-hint'><code>{'~ %' if mac else 'PS C:\\Users\\你的用户名&gt;'}</code><span>打开后，会有一行这样的提示符。<br>从光标处输入，不用抄提示符。</span></div>"),
                             "有一个可以输入文字的终端窗口。旧窗口要完全退出后重新打开。", os=os))
        scenes.append(_scene(f"{os}-node-check", "先试一行，再试下一行", "复制第一行，粘贴到刚才的窗口，按回车；出结果后再做第二行。",
                             _terminal(code, "node --version", "v24.x.x", mac=mac) + _terminal(code, "npm --version" if mac else "npm.cmd --version", "11.x.x", mac=mac),
                             "两条命令都返回版本号。数字可以不同；报错先别往下走。", os=os, help="#help-command"))
    return "".join(scenes)


def _install(code) -> str:
    scenes = []
    for os in ("windows", "mac"):
        mac = os == "mac"
        cmd = 'npm install --global --prefix "$HOME/.local" @openai/codex' if mac else "npm.cmd install -g @openai/codex"
        scenes.append(_scene(f"{os}-install", "安装 Codex，等命令结束", "复制这一行到刚才的终端，按回车。下载时先等；重新出现提示符后再继续。",
                             _terminal(code, cmd, "added … packages in …s\n… %" if mac else "added … packages in …s\nPS C:\\Users\\…>", mac=mac),
                             "安装过程没有 error。npm 的更新通知不是 Codex 安装失败。", os=os, help="#help-command"))
        if mac:
            scenes.append(_scene("mac-path-now", "让这个窗口找到 Codex", "整行复制执行。$HOME 代表你的用户目录，直接照抄。",
                                 _terminal(code, 'export PATH="$HOME/.local/bin:$PATH"', mac=True) + "<div class='walk-path-diagram'><b>$HOME/.local/bin</b><span>加入 PATH 后</span><b>终端能找到 codex</b></div>", "这行通常没有输出，也不是报错。下一步保存它。", os=os))
            scenes.append(_scene("mac-path-editor", "把这个设置留到下次", "先执行 nano 命令。在打开的编辑器末尾加上图中这一行；已有内容请保留。",
                                 _terminal(code, 'nano "$HOME/.zprofile"', mac=True) + _window("nano · ~/.zprofile", "<p class='walk-editor-note'>原有文字保留。在末尾另起一行：</p>" + code('export PATH="$HOME/.local/bin:$PATH"', "复制到 nano 编辑器里，不是终端提示符后") + "<div class='walk-editor-keys'><b>Control + O</b><span>保存</span><b>Enter</b><span>确认文件名</span><b>Control + X</b><span>退出</span></div>", kind="editor"),
                                 "保存、退出，完全关闭再重新打开终端。已有同一行不用再加。", os=os))
        scenes.append(_scene(f"{os}-codex-version", "检查 Codex 能不能打开", "在终端执行版本检查。Mac 请在刚重新打开的窗口做这一步。" if mac else "在终端执行版本检查。记得保留 .cmd 后缀。",
                             _terminal(code, "codex --version" if mac else "codex.cmd --version", "codex-cli 0.xxx.x", mac=mac), "看到 codex-cli 和版本号。版本不要求与图中一致。", os=os, help="#help-command"))
    return "".join(scenes)


def _key_creation() -> str:
    return _scene("create-key", "在官网创建一个 Key", "进入 API keys，点 Create new secret key。确认项目与权限后创建，复制并存到自己的密码管理器。",
                  _window("浏览器 · platform.openai.com/api-keys", _path("当前项目", "API keys") + "<a class='walk-external' href='https://platform.openai.com/api-keys' target='_blank' rel='noopener noreferrer'>打开官网的 API keys 页面</a><div class='walk-key-dialog'><b>Create new secret key</b><span>Name / 名称</span><div>codex-practice</div><span>Project / 项目</span><div>你刚确认账单的项目</div><span>Permissions / 权限</span><p>按需要授权；权限不足时核对 API 报错。</p><span class='walk-fake-button'>Create secret key</span></div><div class='walk-callout'>创建后按平台提示保存。<br>真实 Key 不要粘贴到本博客。</div>", kind="browser"),
                  "手里有一个自己项目的官方 Key。它相当于调用凭据，需要保密。", auth="api", anchor="setup-key")


def _auth(code) -> str:
    scenes = [_key_creation()]
    for os in ("windows", "mac"):
        mac = os == "mac"
        cmd = "codex" if mac else "codex.cmd"
        scenes.append(_scene(f"{os}-login", "让 Codex 打开登录页面", "执行下面这一行。如果出现登录方式选项，选 Sign in with ChatGPT。",
                             _terminal(code, cmd + " login", "浏览器会打开官方授权页；\n没打开时，终端会给出登录链接。", mac=mac), "浏览器打开了官方登录 / 授权页。", os=os, auth="account"))
        scenes.append(_scene(f"{os}-authorize", "网页登录完，记得回终端", "用第 1 章的账号登录，按官方页面完成授权。不要把登录链接或验证码发给别人。",
                             "<div class='walk-handoff'>" + _window("浏览器 · 官方登录 / 授权页", _mark(1, "选原来的登录方式") + _mark(2, "按页面提示验证、授权") + "<b class='walk-state'>页面提示完成后</b>", kind="browser") + "<span class='walk-handoff-label'>切回刚才的窗口</span>" + _window("终端", "<p>等待登录命令结束</p><b>下一步检查登录状态</b>", kind="terminal") + "</div>",
                             "回到终端。浏览器没有自动打开，就用终端给出的官方链接。", os=os, auth="account"))
        if not mac:
            scenes.append(_scene("windows-env-open", "找到“用户变量”", "按 Windows 键搜索“编辑账户的环境变量”。如果先打开系统属性，再点“环境变量”。",
                                 _window("环境变量", "<div class='walk-search'><span>开始菜单搜索</span><b>编辑账户的环境变量</b></div><div class='walk-env-table'><b>上半部分：用户变量</b><div><span>变量</span><span>值</span></div><div><span>Path</span><span>原有项保持不动</span></div><span class='walk-fake-button'>新建…</span></div><div class='walk-env-table is-muted'><b>下半部分：系统变量</b><p>这一课不改这里</p></div>"),
                                 "在上半部分点“新建”。有 OPENAI_API_KEY 同名项时先确认用途，再编辑。", os=os, auth="api"))
            scenes.append(_scene("windows-env-fill", "名字和值，分别填进这两格", "在自己的设置窗口，变量名填 OPENAI_API_KEY；变量值填真实 Key，不加引号。然后逐层点“确定”。",
                                 _window("新建用户变量 · 下方仅是网页练习", "<div class='walk-env-demo' data-env-demo><div><span>变量名</span><code>OPENAI_API_KEY</code></div><div><span>变量值</span><code data-demo-value>（这里不接收真实 Key）</code></div><p>想先看一遍填写效果，可以点下面的按钮。</p><div class='walk-demo-actions' hidden><button type='button' class='walk-button' data-demo-fill>填入演示值</button><button type='button' class='walk-button secondary' data-demo-save disabled>练习点“确定”</button></div><p class='walk-demo-feedback' role='status'>演示值固定为 DEMO-KEY-NOT-VALID，没有调用能力。</p></div>"),
                                 "电脑里的变量已保存。网页练习不会修改你的电脑。", os=os, auth="api"))
            scenes.append(_scene("windows-env-check", "关掉旧窗口，再检查一次", "完全退出 PowerShell / Windows Terminal，再从开始菜单打开。复制整行检查命令。",
                                 _terminal(code, 'if ($env:OPENAI_API_KEY) { "已配置（不显示密钥）" } else { "未读取到，请重新打开终端" }', "已配置（不显示密钥）"),
                                 "看到“已配置”。若读不到，检查拼写和是否重新打开终端。", os=os, auth="api", help="#help-key"))
        else:
            scenes.append(_scene("mac-key-input", "粘贴 Key 时，屏幕不会显示字符", "先只执行下面这一行，再在提示后粘贴自己的 Key，按回车。没有星号、没有文字都是正常的。",
                                 _terminal(code, 'read -rs "OPENAI_API_KEY?粘贴 API Key 后按回车（输入不显示）: "', "粘贴 API Key 后按回车（输入不显示）: ▋", mac=True) + "<div class='walk-callout'>先执行命令，再输入 Key。<br>不要把 Key 放进命令文本或贴在网页上。</div>",
                                 "按回车回到提示符。继续用同一个终端窗口。", os=os, auth="api"))
            scenes.append(_scene("mac-key-export", "让 Codex 能读到这个设置", "在同一个窗口逐行执行。export 让程序读取变量，下一行只检查有没有值。",
                                 _terminal(code, 'export OPENAI_API_KEY\nif [[ -n "$OPENAI_API_KEY" ]]; then printf "已配置（不显示密钥）\\n"; else printf "未读取到，请重新输入\\n"; fi', "已配置（不显示密钥）", mac=True),
                                 "看到“已配置”。此时不要关窗口，临时变量还要用于下一步登录。", os=os, auth="api", help="#help-key"))
        scenes.append(_scene(f"{os}-key-login", "把 Key 交给本机的 Codex", "整行复制执行。不要只运行竖线前面的部分，那样会把 Key 显示出来。",
                             _terminal(code, 'printenv OPENAI_API_KEY | codex login --with-api-key' if mac else '$env:OPENAI_API_KEY | codex.cmd login --with-api-key', mac=mac)
                             + "<div class='walk-path-diagram'><b>环境变量里的 Key</b><span>通过 | 交给</span><b>Codex 登录命令</b></div>",
                             "命令结束后，下一步查登录状态。这里只连接官方 OpenAI Key。", os=os, auth="api"))
        scenes.append(_scene(f"{os}-login-status", "看一眼登录方式是否正确", "复制检查命令。输出可能含账号或密钥片段，不要直接发截图。",
                             _terminal(code, cmd + " login status", mac=mac) + "<div class='walk-status-examples'><div><b>账号路线</b><code>Logged in using ChatGPT</code></div><div><b>Key 路线</b><code>Logged in using an API key</code><small>密钥片段不在这里展示</small></div></div>",
                             "显示已登录，且方式与你选的一致。能否实际调用，最后一章再确认。", os=os))
    return "".join(scenes)


def _folder(code) -> str:
    scenes = []
    for os in ("windows", "mac"):
        mac = os == "mac"
        command = ('mkdir -p "$HOME/Documents/my-first-codex"\ncd "$HOME/Documents/my-first-codex"\npwd' if mac else
                   "$practice = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'my-first-codex'\nNew-Item -ItemType Directory -Force -Path $practice | Out-Null\nSet-Location $practice\nGet-Location")
        scenes.append(_scene(f"{os}-folder-create", "给练习单独建个文件夹", "逐行执行。命令会创建并进入练习目录；如果同名文件夹里有重要资料，先换一个练习名称。",
                             _terminal(code, command, "/Users/你的用户名/Documents/my-first-codex" if mac else "Path\n----\nC:\\Users\\你的用户名\\Documents\\my-first-codex", mac=mac),
                             "最后的路径以 my-first-codex 结尾。Windows 的文档路径可能带 OneDrive，这也正常。", os=os))
        scenes.append(_scene(f"{os}-folder-view", "在文件管理器里也能找到它", "打开访达，在“文稿”里找 my-first-codex。" if mac else "按 Windows + E 打开资源管理器，进“文档”，找到 my-first-codex。",
                             _window("访达" if mac else "文件资源管理器", _path("文稿" if mac else "文档", "my-first-codex") + "<div class='walk-file-view'><aside>" + ("个人收藏<br>下载<br><b>文稿</b>" if mac else "快速访问<br>下载<br><b>文档</b>") + "</aside><div><span class='walk-folder-icon' aria-hidden='true'></span><b>my-first-codex</b><small>新建时应是空文件夹</small></div></div>"),
                             "能找到这个文件夹。下一章回到刚才的终端，继续在这个目录操作。", os=os))
    return "".join(scenes)


def _reply(code) -> str:
    scenes = []
    for os in ("windows", "mac"):
        mac = os == "mac"
        scenes.append(_scene(f"{os}-start", "打开 Codex 的对话界面", "在第 5 章的终端里执行。若询问信任目录，确认是自己的练习文件夹再继续。",
                             _terminal(code, "codex --sandbox read-only" if mac else "codex.cmd --sandbox read-only", mac=mac) + "<div class='walk-codex-pane'><b>Codex</b><span>directory: …/my-first-codex</span><div>&gt; <span>从这里开始输入你的问题</span><i aria-hidden='true'></i></div></div>",
                             "看到 Codex 对话输入位置。沙箱初始化报错时先排查，别关闭保护硬跑。", os=os, help="#help-windows"))
    scenes.append(_scene("first-message", "把这句话发给 Codex", "复制下面这段，粘贴到 Codex 的输入位置，再按回车。不要粘到还没打开 Codex 的终端提示符后。",
                         _window("Codex · 对话练习示意", code("请只回复：连接成功。\n不要读取或修改文件，不要运行命令。", "发给 Codex，不是终端命令", prompt=True) + "<div class='walk-reply-example'><span>等待它的回答</span><b>连接成功。</b><small>这是目标示例。要以你电脑实际收到的回复为准。</small></div>", kind="terminal"),
                         "自己的电脑收到回复，且没有认证、网络或额度错误，才算真正用上了。", help="#codex-help"))
    scenes.append(_scene("again", "关掉以后，下次这样打开", "本次完成后可按 Ctrl + C 退出（Mac 用 Control）。下次按图中三步打开，无需重新安装。",
                         "<div class='walk-return'>" + _mark(1, "打开 PowerShell / Mac 终端") + _mark(2, "重复第 5 章命令，进入练习文件夹") + _mark(3, "运行本章启动命令，再输入你的问题") + "<div class='walk-callout'>登录失效才回第 4 章。<br>接下来可以展开“做一张学习名片”，试着生成文件。</div></div>",
                         "能独立再打开一次，并发出第二条消息。"))
    return "".join(scenes)


def render_walkthrough(index: int, code) -> str:
    scenes = (_account, _node, _install, _auth, _folder, _reply)[index](code)
    proofs = (
        "我确认自己的账号 / API 项目可用，并看过费用条件",
        "我在自己电脑上运行了两条命令，都看到版本号",
        "我在自己电脑上看到了 codex-cli 版本号",
        "我在自己电脑上检查了登录状态，方式与选择一致",
        "我确认终端当前路径以 my-first-codex 结尾",
        "我在自己的 Codex 里收到了实际回复",
    )
    return (
        f"<div class='walkthrough' data-walkthrough='{index}'>"
        "<div class='walk-reading' hidden><span data-scene-count role='status'></span><span>看图，在自己的电脑上做</span></div>"
        + scenes
        + "<nav class='walk-controls' aria-label='本章操作步骤' hidden><button type='button' class='walk-button secondary' data-scene-prev>上一步</button>"
        "<button type='button' class='walk-button' data-scene-next>下一步</button><button type='button' class='walk-button secondary' data-scene-replay hidden>从本章第一步重看</button></nav>"
        f"<div class='walk-proof'><label><input type='checkbox' data-proof disabled />{proofs[index]}</label>"
        "<small>自己核对后勾选；本网页无法检测你的电脑。</small></div></div>"
    )
