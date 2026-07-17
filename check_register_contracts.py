"""Check audited WS63 register contracts that the XML schema cannot express."""

from pathlib import Path
import xml.etree.ElementTree as ET


SVD = Path(__file__).with_name("WS63.svd")


def main() -> None:
    root = ET.parse(SVD).getroot()
    peripherals = {p.findtext("name"): p for p in root.findall("./peripherals/peripheral")}

    def peripheral(name: str) -> ET.Element:
        assert name in peripherals, f"missing peripheral {name}"
        return peripherals[name]

    def registers(name: str) -> dict[str, ET.Element]:
        return {
            r.findtext("name"): r
            for r in peripheral(name).findall("./registers/register")
        }

    def require_access(peripheral_name: str, names: list[str], access: str) -> None:
        regs = registers(peripheral_name)
        for name in names:
            assert name in regs, f"missing {peripheral_name}.{name}"
            actual = regs[name].findtext("access")
            assert actual == access, (
                f"{peripheral_name}.{name}: expected {access}, got {actual}"
            )

    uart = registers("UART0")
    assert len(uart) == 24
    assert all(r.findtext("size") == "32" for r in uart.values())
    assert peripheral("UART1").get("derivedFrom") == "UART0"
    assert peripheral("UART2").get("derivedFrom") == "UART0"
    require_access(
        "UART0",
        [
            "INTR_ID",
            "INTR_STATUS",
            "MODEM_STATUS",
            "LINE_STATUS",
            "TX_FIFO_READ",
            "FIFO_STATUS",
            "TX_FIFO_CNT",
            "RX_FIFO_CNT",
            "UART_PARAMETER",
        ],
        "read-only",
    )
    require_access("UART0", ["FIFO_CTL"], "write-only")

    spi = registers("SPI0")
    data = spi["SPI_DRNM%s"]
    assert data.findtext("addressOffset") == "0x2C"
    assert data.findtext("dim") == "36"
    assert data.findtext("dimIncrement") == "0x4"
    assert data.findtext("dimIndex") == "0-35"
    required_spi_offsets = {
        "SPI_RSDR": "0x24",
        "SPI_TDER": "0x28",
        "SPI_RAINSR": "0xBC",
        "SPI_WSR": "0xE4",
        "SPI_ID": "0xEC",
        "SPI_ICR": "0xF8",
    }
    for name, offset in required_spi_offsets.items():
        assert spi[name].findtext("addressOffset") == offset
    assert peripheral("SPI1").get("derivedFrom") == "SPI0"

    require_access("GPIO0", ["GPIO_INT_RAW", "GPIO_INTR"], "read-only")
    require_access(
        "GPIO0", ["GPIO_INT_EOI", "GPIO_DATA_SET", "GPIO_DATA_CLR"], "write-only"
    )
    require_access("I2C0", ["I2C_SR", "I2C_RXR", "I2C_FIFOSTATUS"], "read-only")
    require_access("DMA", ["DMAC_INT_ST", "DMAC_ORI_INT_ST", "DMAC_EN_CHNS"], "read-only")
    require_access("SFC_CFG", ["INT_RAW_STATUS", "INT_STATUS", "LEA_DFX_INFO"], "read-only")
    require_access("SFC_CFG", ["INT_CLEAR"], "write-only")
    require_access("TSENSOR", ["TSENSOR_CTL_ID", "TSENSOR_TEMP_INT_STS"], "read-only")
    require_access("TSENSOR", ["TSENSOR_START", "TSENSOR_TEMP_INT_CLR"], "write-only")
    require_access(
        "PWM",
        [
            *[f"PWM_PERIODLOAD_FLAG{i}" for i in range(8)],
            *[f"PWM_PERIODCNT{i}" for i in range(8)],
            "PWM_ABNOR_STATE0",
            "PWM_ABNOR_STATE1",
        ],
        "read-only",
    )
    require_access(
        "PWM",
        [
            *[f"PWM_START{i}" for i in range(4)],
            "PWM_ABNOR_STATE_CLR0",
            "PWM_ABNOR_STATE_CLR1",
            "PWM_CFG_INT_CLR0",
        ],
        "write-only",
    )

    interrupts: list[tuple[str, str, str]] = []
    for peripheral_name, p in peripherals.items():
        for interrupt in p.findall("interrupt"):
            interrupts.append(
                (peripheral_name, interrupt.findtext("name"), interrupt.findtext("value"))
            )
    assert ("SYS_CTL1", "GLP_UART_RX_WAKE_INT", "67") in interrupts
    assert ("SYS_CTL1", "TIMING_GEN_INT", "68") in interrupts
    assert [(p, n) for p, n, value in interrupts if value == "63"] == [
        ("PKE", "PKE_REE_INT")
    ]

    print("PASS: audited WS63 register contracts are intact.")


if __name__ == "__main__":
    main()
