# my-skills
记录个人 skill

## PKM 目标库

所有 `pkm-*` 技能通过 `PKM_VALUT_DIR` 选择目标 Obsidian 库。运行技能前，将此变量设为已存在的绝对目录：

```bash
export PKM_VALUT_DIR="/absolute/path/to/your/vault"
```

变量名沿用 `VALUT` 拼写。变量缺失、为空、使用相对路径或指向无效目录时停止，不回退到当前工作目录或固定路径。相对笔记路径、库内规则、模板和库内脚本都从目标库解析；技能自身的参考文件和附带脚本仍从技能目录解析。

内部操作遵循目标库的 `AGENTS.md`；`pkm-ingress` 仅接收外部投递，不读取该规则文件。`pkm-todo` 继续要求显式调用。

目标库需提供相应的 `scripts/pkm_ops.py`；`pkm-todo` 使用目标库的 `scripts/pkm_quickadd.py` 任务接口。调用库内脚本时在目标库目录运行；脚本支持 `--vault-root` 时传入同一目标地址。若库内脚本写死了其他库地址，先修正该脚本，避免操作错误的库。

附带的 capture、link、review 脚本也要求 `PKM_VALUT_DIR`；原有 `--vault` 参数仅能确认同一地址，不能覆盖环境变量。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
