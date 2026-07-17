# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Model the WS63 RISC-V mask-ROM instruction patch controller at
  `0xE000_0000`, including its 192 instruction comparison registers.

### Added
- SPACC symmetric channel 1/2 input/output descriptor rings, completion/error
  status, and the KM/KLAD clear-key and MCipher keyslot registers used by AES.
- Shared-RAM ownership fields for `CFG_RAM_CKEN` / `CFG_RAM_SEL` and the missing
  `BT_EM_CTL.EM_GT_MODE` register used by the official `dyn_mem_cfg` sequence.
- cfg-gating of interrupt module's RISC-V coupling for host builds (allows ws63-pac and ws63-hal to compile for x86 targets in test scenarios)
- ARCHITECTURE.md documenting the SVD source and reproducible PAC generation pipeline

### Changed
- Move the Edition 2024 `Peripherals::steal` unsafe-body fix into deterministic
  postprocessing instead of relying on `cargo fix` during regeneration.
- Reproducible svd2rust 0.37.1 PAC generation pipeline (regen.sh + postprocess.py deterministic transforms)
- Fixed eFuse register map to match WS63 C SDK (control block at base+0x30, 16-bit mode-select magic field, 0x800 data window)
- Fixed LSADC register map to contiguous layout (CTRL_0/1/8/9/11, CFG_* registers)

### Fixed
- Correct UART0/1/2 register slots to 32-bit APB accesses and mark UART, GPIO,
  I2C, PWM, DMA, SFC, and TSENSOR command/status registers with explicit access
  directions instead of inheriting the device-wide read-write default.
- Rebuild the SSI v151 SPI0/SPI1 register window from the vendor register
  structure: the 36 data registers start at `0x2C`, and the previously omitted
  Microwire, sample-delay, drive-edge, FIFO-level, interrupt-clear, version, and
  extension registers are now modeled through `0xF8`.
- Add IRQ 67 (`GLP_UART_RX_WAKE_INT`) and IRQ 68 (`TIMING_GEN_INT`), and remove
  the duplicate PKE interrupt association from the SPACC peripheral.
- Correct AES key-length encoding to `1/2/3` for 128/192/256 bits and model
  symmetric/KLAD completion registers as write-one-to-clear.
- **SPI_WSR bit layout** corrected to the HiSilicon SSI v151 silicon (vendor
  `hal_spi_v151_regs_def.h` `spi_wsr_data`), which is NOT the textbook DesignWare
  SR: `rxfne`=bit4, `rxff`=bit5, `txfnf`=bit11, `txfe`=bit12, `busy`=bit15,
  `dcol`=bit0 (was the wrong packed `busy`=0/`txfnf`=1/`txfe`=2/`rxfne`=3). The old
  layout made `txfnf` poll a reserved bit that is always 0, so every SPI transfer
  timed out. Reset value 0x1800 (TXFNF|TXFE idle). Verified on WS63 silicon
  2026-06-14: SPI0 MOSI→MISO loopback now round-trips (was `Err(Timeout)`).
- Added missing KM keyslot registers (KC_REE, PCPU, AIDSP_LOCK_CMD, KC_RD_SLOT_NUM)
- PWM channels 2–7 now have proper enumeratedValues and field definitions (copy from ch0)
- CMSIS-SVD schema compliance (CPU name 'custom_riscv' → 'other', license text placement, element ordering)
- Removed non-standard deviceNumInterrupts and sauNumRegions from CPU element

## [2026-05-28] — Initial SVD and Tooling

### Added
- WS63 RISC-SVD file (WS63.svd) with complete SoC peripheral register definitions
- Security subsystem and SYS_CTL0 peripherals
- TCXO and CLDO_CRG peripherals
- SDMA and ULP_GPIO peripherals
- SYS_CTL2 sub-blocks (RF_WB_CTL, SHARE_MEM_CTL, FAMA_REMAP)
- CPU section with RV32IMFC_Zicsr ISA description and fpuPresent=true
- addressBlock annotations for all 35 peripherals
- dimElementGroup and writeConstraint annotations
- 46 enumeratedValues blocks across UART, SPI, GPIO, I2C, DMA, SPACC, PKE, PWM, Timer, WDT, SFC_CFG peripherals
- 21 interrupt connections (COEX_WL/BT/WIFI_RESUME, WLPHY, WLMAC, BLE, SLE, TIMER_INT0/1/2, TIMER_ABNOR, PWM_CFG, I2S_TX/RX, PMU_CMU_ERR, DIAG, MAC/MEM/TCM_MONITOR, RKP_REE)
- SVD validation tooling (validate.py) against official ARM CMSIS-SVD XSD
- svd2rust settings file (ws63-settings.yaml) for RISC-V PAC generation
- Python uv project setup with xmlschema dependency
