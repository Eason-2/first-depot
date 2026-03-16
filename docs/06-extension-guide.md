# 新增内容操作说明

这份文档用于说明：如果后续要给项目“加东西”，应该改哪里、按什么顺序改、改完怎么验证。

## 先判断你要加的是哪一类
- 新增数据源：例如再接一个新闻 API、论坛、论文站点。
- 新增排序规则：例如修改热点分数、聚类逻辑、筛选条件。
- 新增生成规则：例如调整文章结构、标题风格、引用方式。
- 新增 QA 规则：例如多一条安全检查、格式检查、引用检查。
- 新增发布方式：例如发到别的 CMS，而不是本地 Markdown。
- 新增接口或页面：例如多一个 API 路由或博客页面能力。
- 新增配置项：例如新的环境变量、开关、路径。

## 不建议直接改的目录
- `runtime/`：这里是运行时数据，通常不作为源码修改入口。
- `deliverables/published/`：这里是产出的文章内容，不是主逻辑代码。
- `site/`：这里是导出的静态站点结果，通常应由脚本重新生成。

## 通用操作顺序
1. 先确定改动落在哪个模块。
2. 如果涉及新字段，先看 `core/models.py` 和 `core/storage.py`。
3. 如果涉及新配置，先加到 `core/config.py`，再补 README。
4. 代码改完后补测试。
5. 最后运行一次主流程确认没有把已有链路改坏。

## 常见新增方式

### 1. 新增数据源
适用目录：
- `workers/ingestion/connectors/`
- `workers/ingestion/pipeline.py`
- `workers/ingestion/normalize.py`

操作步骤：
1. 在 `workers/ingestion/connectors/` 下新建一个 connector 文件。
2. 参考 `workers/ingestion/base.py` 中的 `BaseConnector`，实现 `fetch_items()`。
3. 在 `workers/ingestion/pipeline.py` 的 `_default_connectors()` 里注册新 connector。
4. 如果返回字段和现有来源不同，在 `workers/ingestion/normalize.py` 里补充标准化逻辑。
5. 如果这个来源需要密钥或开关，在 `core/config.py` 里增加配置读取。

改完至少验证：
- `python -m unittest discover -s tests -p "test_*.py"`
- `python -m scripts.run_once`

### 2. 新增或修改排序逻辑
适用目录：
- `workers/ranking/scoring.py`
- `workers/ranking/clustering.py`
- `workers/ranking/pipeline.py`

操作建议：
- 改“分数”优先看 `scoring.py`。
- 改“事件如何合并成主题”优先看 `clustering.py`。
- 改“整体排序入口”看 `pipeline.py`。

改完最好同步更新：
- `tests/test_ranking.py`
- 如果会影响最终文章结果，也要看 `tests/test_e2e_pipeline.py`

### 3. 新增或修改文章生成规则
适用目录：
- `workers/generation/draft_builder.py`

这里控制的内容包括：
- 标题生成
- 正文结构
- 引用列表
- 输出长度
- 标签

注意：
- 生成结构改动后，很容易连带影响 QA。
- 改完要一起检查 `workers/qa/checks/` 下的规则是否还适配。

建议验证：
- `tests/test_generation_qa.py`
- `python -m scripts.run_once`

### 4. 新增 QA 检查
适用目录：
- `workers/qa/checks/`
- `workers/qa/pipeline.py`

操作步骤：
1. 在 `workers/qa/checks/` 下新增检查函数。
2. 在 `workers/qa/pipeline.py` 里接入执行顺序。
3. 给失败场景定义清晰的 `reason_code`。

建议：
- 新规则尽量返回“是否通过 + 详细原因”，方便排查。
- 不要只返回布尔值，否则后续不好定位问题。

### 5. 新增发布目标
适用目录：
- `workers/publishing/cms_adapter/`
- `workers/publishing/scheduler.py`
- `core/config.py`

操作步骤：
1. 在 `workers/publishing/cms_adapter/` 下新增适配器。
2. 按 `TARGET_CMS` 或其他配置决定使用哪个 adapter。
3. 在 `workers/publishing/scheduler.py` 中接入。
4. 如果新增环境变量，也要更新 `README.md`。

注意：
- 当前默认发布器是本地 Markdown。
- 如果接第三方平台，记得把失败信息写清楚，避免发布失败时只看到空结果。

### 6. 新增 API 或页面
适用目录：
- `apps/api/server.py`
- `apps/api/blog_view.py`
- `apps/api/contracts/event-schema.json`

操作步骤：
1. 在 `apps/api/server.py` 中新增路由。
2. 如果是博客页面渲染，改 `apps/api/blog_view.py`。
3. 如果返回结构属于对外接口，记得同步更新 contract 或文档。

建议验证：
- `tests/test_server_auth.py`
- `python -m scripts.start_api`

### 7. 新增配置项或环境变量
适用目录：
- `core/config.py`
- `README.md`

操作步骤：
1. 在 `Settings` 中加字段。
2. 在 `Settings.from_env()` 中读取并处理默认值。
3. 如果配置会影响目录、端口、定时等行为，顺手补一条测试或启动验证。
4. 在 `README.md` 的环境变量部分补说明。

## 如果新增字段或数据结构
优先检查这几个地方：
- `core/models.py`
- `core/storage.py`
- `apps/api/server.py`
- 对应测试文件

说明：
- 如果只是往 `payload_json` 里多存一点内容，通常改动较小。
- 如果新增了需要单独查询的字段，往往还要改 SQLite 表结构。
- 改了 SQLite 表结构后，旧的 `runtime/autopublisher.db` 可能不兼容；本地验证时要注意这一点。

## 建议的最小验证流程
每次新增功能后，至少跑这三步：

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m scripts.run_once
python -m scripts.start_api
```

说明：
- 第 1 步看单元测试和基础回归。
- 第 2 步看主流程能不能从抓取走到生成/发布。
- 第 3 步只要接口或页面相关改动，就应该实际启动检查。

## 提交前检查清单
- 代码是否放在正确模块，而不是直接堆到脚本里。
- 新增配置是否同步写进 `README.md`。
- 新增能力是否补了至少一个测试。
- 是否会影响已有脚本：`scripts/run_once.py`、`scripts/run_scheduler.py`、`scripts/start_api.py`。
- 是否误改了 `runtime/`、`site/`、`deliverables/published/` 这类结果目录。

## 一句话原则
新增功能时，优先沿着“connector -> pipeline -> qa -> publish -> api -> docs/tests”这条线扩展，不要把逻辑直接散落到多个脚本里。
