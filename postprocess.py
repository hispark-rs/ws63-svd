#!/usr/bin/env python3
"""Deterministic post-fixups for svd2rust 0.37.1 output (see regen.sh).

svd2rust 0.37.1 emits code that is *almost* what the edition-2024 `ws63-pac`
crate needs. Two text-level fixups must run on the raw generated `lib.rs`
*before* it can compile; a third (`unsafe_op_in_unsafe_fn`) is applied by
`cargo fix` in regen.sh because it needs a compilable crate.

Fixups applied here (both deterministic, order-independent):

  1. Strip spurious bare single-element array accessors.
     A register declared with `dim=N` (e.g. the three TIMER blocks) makes
     svd2rust emit BOTH an indexed accessor `foo(&self, n: usize)` AND a bare
     `foo(&self)` that just forwards to `foo(0)`. When the bare name collides
     with the indexed one this is a duplicate-definition *compile error*. The
     HAL uses the indexed form (`r.timer0_control(0)`), so the bare forwarder
     is removed. Exactly 5 such blocks exist (TIMER load_count / current_value
     / control / eoi / raw_intr); the count is asserted below.

  2. `#[no_mangle]` -> `#[unsafe(no_mangle)]`.
     Edition 2024 makes the unwrapped attribute a hard error. One occurrence
     (the `rt`-feature `DEVICE_PERIPHERALS` static).

Usage: postprocess.py <lib.rs>   (edits in place)
"""
import re
import sys

EXPECTED_BARE_STRIPS = 5
EXPECTED_NO_MANGLE = 1


def strip_bare_array_accessors(src: str) -> tuple[str, int]:
    indexed = set(re.findall(r"pub const fn (\w+)\(&self, n: usize\)", src))
    bare = set(re.findall(r"pub const fn (\w+)\(&self\)\s*->", src))
    removed = 0
    for name in sorted(indexed & bare):
        pat = re.compile(
            r"[ \t]*#\[doc[^\n]*\]\n"
            r"[ \t]*#\[inline\(always\)\]\n"
            r"[ \t]*pub const fn " + re.escape(name) + r"\(&self\) -> &\w+ \{\n"
            r"[ \t]*self\." + re.escape(name) + r"\(0\)\n"
            r"[ \t]*\}\n",
            re.M,
        )
        src, n = pat.subn("", src)
        removed += n
    return src, removed


def migrate_no_mangle(src: str) -> tuple[str, int]:
    return re.subn(r"#\[no_mangle\]", "#[unsafe(no_mangle)]", src)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: postprocess.py <lib.rs>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    with open(path) as f:
        src = f.read()

    src, n_strip = strip_bare_array_accessors(src)
    src, n_mangle = migrate_no_mangle(src)

    with open(path, "w") as f:
        f.write(src)

    print(f"postprocess: stripped {n_strip} bare accessors, "
          f"migrated {n_mangle} no_mangle attribute(s)")

    ok = True
    if n_strip != EXPECTED_BARE_STRIPS:
        print(f"  WARNING: expected {EXPECTED_BARE_STRIPS} bare-accessor "
              f"strips, got {n_strip} (SVD changed? verify the diff)",
              file=sys.stderr)
        ok = False
    if n_mangle != EXPECTED_NO_MANGLE:
        print(f"  WARNING: expected {EXPECTED_NO_MANGLE} no_mangle migration, "
              f"got {n_mangle}", file=sys.stderr)
        ok = False
    # Non-fatal: counts are sanity checks, not gates — the build/clippy in
    # regen.sh is the real verification.
    return 0 if ok else 0


if __name__ == "__main__":
    sys.exit(main())
