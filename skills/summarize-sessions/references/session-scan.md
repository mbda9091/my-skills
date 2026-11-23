# session-scan 接入

先检查 `command -v session-scan` 和 `session-scan --help`，以当前安装版本为准。不要假设存在 `read`、`export`、`--session-id` 等接口。

## 定位文件

以下日期和目录是示例，调用时换成用户要求的范围：

```bash
session-scan --source all \
  --directory /path/to/project \
  --since '2026-11-23T00:00:00+08:00' \
  --until '2026-11-24T00:00:00+08:00'
```

- `--source`：`all`、`codex` 或 `dsh`，默认 `all`。
- `--directory` 可重复，默认包含子目录；添加 `--exact-directory` 才只匹配指定目录。
- `--codex-home` 和 `--dsh-root` 可指定日志根目录；默认使用 `$CODEX_HOME` 或 `~/.codex`，以及 `~/.dsh/sessions`。
- 日期 `YYYY-MM-DD` 按运行环境本地时区解释，`--since` 包含当天起点，`--until` 包含当天全天。带时区的 ISO 时间则采用左闭右开区间；优先使用明确时区以避免环境差异。
- 按消息发生时间选择文件，不是按文件修改时间。没有时间筛选时，返回结果可能只检查过文件头。

## 解释返回结果

JSON 顶层包含 `schema_version`、`status`、`filters`、`results`、`summary`、`warnings`、`errors`。

- `results[]` 提供 `source`、`session_id`、`path`、`cwd`、`title`、`updated_at` 及其来源。不要依赖标题非空或仅用排序确认目标会话。
- 时间筛选的 `match` 提供首条命中的 `timestamp`、`line_number`，可能有 Codex `ordinal` 或 DSH `seq`。`line_number` 是解压后的 JSONL 行号。
- `match.scan_state=first_match` 只代表扫描到首条匹配即停止，后续文件内容仍可能有错误；不是全量验证。
- 退出码 `0` 对应 `completed`；`1` 可返回 `partial_failure` 和部分结果；`2` 可返回 `invalid_source`，参数错误也可能以 `2` 退出且没有 JSON。先确认是否有可解析 JSON，不因非零退出码丢弃已有结果。
- `ambiguous_message_origin` 表示扫描器无法确认某条消息的来源，可能导致筛选遗漏；说明此限制，不把它描述为确定的文件损坏。检查错误是否涉及目标文件。

## 读取正文

仅打开 `results[].path` 中选定的文件，不自行遍历其他会话目录。普通 JSONL 逐行解析；`.jsonl.zstd` 使用已安装的 `zstd -dc` 或可用的 Zstandard 库流式解压。传参时将路径作为独立参数或正确引用，不把日志内容作为 shell 代码。

保留实际来源、会话标识、解压后的行号和可用的消息时间、序号。按需读取关键工具结果，避免把整份原始记录一次性灌入上下文。

- Codex：按实际 `type` 和 `payload` 解析消息及工具事件；留意 `event_msg` 与 `response_item` 的镜像，分页历史及 `replayed` / `retained_source` 等重放标记，不把上下文注入当成用户新要求。
- DSH：按实际 `type`、`data`、`surfaceOp` 和消息来源解析。保留用户与模型的真实消息，区分追加和替换，结合 `seedLength` 或 `session/end-seed` 识别继承历史，避免把同一内容重复统计为新进展。
- 不能只按 `role` 抽文本：工具结果可能承载执行证据，注入内容也可能带有用户角色。结构不明确时先查看少量记录确认，再分段读取；无法确认的范围明确标注。

选中文件后仍需按正文时间过滤。范围外的历史只补充必要背景；某个工具结果缺少时间时，结合关联调用及相邻事件判断，不自行编造时间。
