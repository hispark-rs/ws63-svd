# WS63 TCXO data-register profile

The WS63 SDK checkout at `731bc668865fd8dc89bc40da0583b4e4023095a0`
defines `CONFIG_TCXO_WITH_TWO_DATA_REGS` for WS63 targets in
`src/build/config/target_config/ws63/target_config.py` (SHA-256
`f3c36ba7c949a3a0e3536d53a8c1c03f0a5ce8e04dd2742186425dc908742428`).
Under that configuration `src/drivers/drivers/hal/tcxo/hal_tcxo_v150_regs_op.c`
(SHA-256 `2552bc908c72022ae240f03c58fe61f618fdb873359a1b469cb4de52fc120964`)
reads count1 as the high 32 bits and count0 as the low 32 bits.

The old 16-bit field accessors and extra register names remain for API
compatibility. Their previous descriptions are not evidence that WS63 uses a
four-register counter, and count2/count3 semantics in this profile remain
unverified. This is an SDK/source correction, not a new physical-board result.
