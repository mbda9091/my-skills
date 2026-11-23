# my-skills
记录个人 skill

## PKM 技能

基础流程由 `pkm-operator` 调度 `pkm-capture`、`pkm-triage`、`pkm-distill`、`pkm-link` 和 `pkm-review`。库路径及 QuickAdd 调用方式以各技能的 `SKILL.md` 为准。

## pkm-todo 目标库

`pkm-todo` 通过 `PKM_VALUT_DIR` 选择目标 Obsidian 库。运行前，将此变量设为已存在的绝对目录：

```bash
export PKM_VALUT_DIR="/absolute/path/to/your/vault"
```

变量名沿用 `VALUT` 拼写。变量缺失、为空、使用相对路径或指向无效目录时停止，不回退到当前工作目录或固定路径。

`pkm-todo` 要求显式调用，遵循目标库的 `AGENTS.md`，并使用目标库中 `scripts/pkm_quickadd.py` 的任务接口。

这些环境变量要求仅适用于 `pkm-todo`；其他 PKM 技能按各自说明运行。
