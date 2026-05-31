# ws63-svd

HiSilicon **WS63**（RISC-V RV32IMFC_Zicsr，Wi-Fi 6 + BLE + SLE/星闪）的手写 CMSIS-SVD 描述，
是 [`ws63-pac`](https://github.com/sanchuanhehe/ws63-pac)（经 svd2rust 生成）的上游真值。

## 内容

- `WS63.svd` — CMSIS-SVD 源（含 `enumeratedValues`、`derivedFrom`、`writeConstraint`、`addressBlock`）。
- `validate.py` — 对照官方 ARM CMSIS-SVD XSD 校验。
- `ws63-settings.yaml` — svd2rust 目标设置。
- `regen.sh` — **可复现**的 SVD→PAC 生成流水线（见下）。
- `postprocess.py` — `regen.sh` 调用的确定性文本修补（svd2rust 0.37.1 → edition 2024）。

## 从 SVD 生成 PAC

`ws63-pac/src/lib.rs` 现在由 `regen.sh` **可复现地**生成——不要再手补 lib.rs
（主仓有 PreToolUse hook 拦截手改）。改寄存器：编辑 `WS63.svd` 后重跑：

```bash
bash regen.sh        # 默认写入 ../ws63-pac/src/lib.rs，并 build+clippy 校验
git -C ../ws63-pac diff src/lib.rs   # 审查 diff 后再提交
```

流水线（已固定工具版本 `cargo install svd2rust@0.37.1 form@0.13.0`）：

1. `svd2rust -i WS63.svd --target riscv --settings ws63-settings.yaml`
2. `rustfmt`（svd2rust 原始输出未格式化）
3. `postprocess.py` —— 两处确定性修补：
   - 删除 5 个由 `dim` 重复生成的 TIMER 裸访问器（否则重复定义编译错误）；
   - `#[no_mangle]` → `#[unsafe(no_mangle)]`（edition 2024 硬错误）。
4. `cargo fix` —— 自动套用 `unsafe_op_in_unsafe_fn`（`rt`+`critical-section` 特性下的 `steal()`）。
5. `cargo fmt`，随后 build + clippy 作为门禁。

> 该流水线幂等：同一 SVD 重跑产出字节一致的 lib.rs。

## 校验

```bash
uv run validate.py        # 对照 CMSIS-SVD XSD
```

## 架构与评审

见主仓库 <https://github.com/sanchuanhehe/ws63-rs/blob/main/docs/architecture/ws63-svd.md>。
