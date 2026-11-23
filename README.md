# my-skills
记录个人 skill

## PKM 技能

基础流程由 `pkm-operator` 调度 `pkm-capture`、`pkm-triage`、`pkm-distill`、`pkm-link` 和 `pkm-review`，使用现有 QuickAdd 工作流。

## PKM 目标库

所有 `pkm-*` 技能通过 `PKM_VALUT_DIR` 选择目标 Obsidian 库。运行前，将此变量设为已存在的绝对目录：

```bash
export PKM_VALUT_DIR="/absolute/path/to/your/vault"
```

变量名沿用 `VALUT` 拼写。变量缺失、为空、使用相对路径或指向无效目录时停止，不回退到当前工作目录或固定路径。

笔记、模板和 `AGENTS.md` 从目标库解析；技能附带的参考文件和辅助脚本从技能自身目录解析。库内 `scripts/pkm_quickadd.py` 显式接收 `--vault-root "$PKM_VALUT_DIR"`；Obsidian 的库标识也必须对应同一目标库。原有 QuickAdd choice 和检查顺序保持不变。

附带的 capture、link、review 脚本也要求该变量；`--vault` 只用于确认相同地址，不能覆盖环境变量。`pkm-todo` 继续要求显式调用，任务操作使用目标库中 `pkm_quickadd.py` 的既有接口。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
