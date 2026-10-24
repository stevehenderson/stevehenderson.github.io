#!/usr/bin/env python3
"""Estimate one year of storage for a mid-size AI-for-cyber project.

Every input lives in ASSUMPTIONS below. An input whose status reads
"ASSUMPTION - Steve to confirm" is a placeholder to replace with real
numbers. Inputs taken from a published source carry that source's URL
in `basis`.

Usage:
    python3 scripts/storage_estimate.py             # plain-text tables
    python3 scripts/storage_estimate.py --markdown  # GFM tables for the blog post

Units are decimal, as drives are sold: 1 TB = 1,000 GB = 10**12 bytes.
Costs cover raw media (drives) only, before servers, networking, power,
and support.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

CONFIRM = "ASSUMPTION - Steve to confirm"
SOURCED = "Sourced"

M_26_14 = (
    "https://www.whitehouse.gov/wp-content/uploads/2026/05/"
    "M-26-14-Ensuring-Effective-and-Efficient-Agency-Logging-and-Network-Visibility-"
    "to-Defend-Against-Evolving-Cyber-Threats.pdf"
)
ZERO_PAPER = "https://arxiv.org/abs/1910.02054"
VDURA_INDEX = "VDURA Flash Volatility Index, Aug 1, 2026 update (https://www.vdura.com/?p=16714)"


@dataclass(frozen=True)
class Assumption:
    value: float
    unit: str
    description: str
    status: str = CONFIRM
    basis: str = ""


ASSUMPTIONS: dict[str, Assumption] = {
    # SIEM logs: hot days on SSD, the rest of the retention period on HDD.
    "siem_ingest_gb_per_day": Assumption(1_000, "GB/day", "SIEM raw log ingest"),
    "siem_stored_ratio": Assumption(
        0.5, "x ingest", "Bytes on disk per byte ingested, after compression and indexes"
    ),
    "siem_ssd_days": Assumption(30, "days", "SIEM days on the SSD hot tier"),
    "siem_retention_days": Assumption(
        365,
        "days",
        "SIEM total retention",
        basis=f"OMB M-26-14 minimum for federal civilian systems: retrievable for a year ({M_26_14})",
    ),
    # Full packet capture: a rolling window on HDD.
    "pcap_link_gbps": Assumption(10, "Gbit/s", "Monitored link rate"),
    "pcap_utilization": Assumption(0.10, "fraction", "Average utilization of the monitored link"),
    "pcap_window_days": Assumption(14, "days", "Rolling full-PCAP window"),
    # EDR telemetry, stored apart from the SIEM. Drop it if EDR already lands in the SIEM.
    "edr_endpoints": Assumption(5_000, "endpoints", "Endpoints reporting EDR telemetry"),
    "edr_mb_per_endpoint_day": Assumption(50, "MB/endpoint/day", "EDR telemetry as stored"),
    "edr_ssd_days": Assumption(30, "days", "EDR days on the SSD hot tier"),
    "edr_retention_days": Assumption(180, "days", "EDR total retention"),
    # AI layer: training and fine-tuning data. The current version on SSD, older versions on HDD.
    "dataset_tb": Assumption(
        20, "TB", "Curated training and fine-tuning corpus (labeled logs, PCAP slices, samples)"
    ),
    "dataset_versions": Assumption(3, "versions", "Dataset versions kept for reproducibility"),
    # AI layer: model checkpoints, all on SSD.
    "model_params_billion": Assumption(32, "billion", "Parameters in the fine-tuned model"),
    "checkpoint_bytes_per_param": Assumption(
        14,
        "bytes",
        "Full-state checkpoint: 2 (16-bit weights) + 12 (fp32 weights, momentum, variance)",
        basis=f"Mixed-precision Adam state per parameter, ZeRO paper Sec. 3.1 ({ZERO_PAPER})",
    ),
    "checkpoints_retained": Assumption(24, "checkpoints", "Checkpoints kept, e.g. 3 runs x 8 each"),
    # AI layer: embeddings and the vector store, on SSD.
    "vectors_million": Assumption(250, "million", "Embedded chunks (CTI, tickets, alerts, log summaries)"),
    "embedding_dims": Assumption(1_024, "dims", "Embedding dimensions"),
    "bytes_per_dim": Assumption(4, "bytes", "float32 vectors"),
    "vector_index_overhead": Assumption(
        2.0, "x vectors", "Index graph, metadata, and chunk text on top of the raw vectors"
    ),
    # AI layer: prompt and output logging for audit.
    "llm_calls_per_day": Assumption(250_000, "calls/day", "Model calls across all agents and pipelines"),
    "tokens_per_call": Assumption(12_000, "tokens", "Prompt plus output tokens per call"),
    "bytes_per_token": Assumption(4, "bytes", "Stored bytes per token of text"),
    "llm_log_overhead": Assumption(1.5, "x text", "JSON envelope, tool-call traces, and metadata"),
    "llm_log_ssd_days": Assumption(30, "days", "Prompt-log days on the SSD hot tier"),
    "llm_log_retention_days": Assumption(365, "days", "Prompt-log total retention"),
    # Protection: replicas, erasure-coding overhead, and backup copies.
    "protection_multiplier": Assumption(2.0, "x primary", "Raw capacity per usable byte, all categories"),
    # Media prices, USD per TB: 30TB drive prices from VDURA's Flash Volatility Index divided
    # by 30. VDURA does not publish its method. Replace with real quotes when available.
    "ssd_usd_per_tb_2025": Assumption(
        3_460 / 30, "USD/TB", "30TB TLC enterprise SSD, Q3 2025", SOURCED, VDURA_INDEX
    ),
    "ssd_usd_per_tb_2026": Assumption(
        22_600 / 30, "USD/TB", "30TB TLC enterprise SSD, Q3 2026", SOURCED, VDURA_INDEX
    ),
    "hdd_usd_per_tb_2025": Assumption(495 / 30, "USD/TB", "30TB HDD, Q3 2025", SOURCED, VDURA_INDEX),
    "hdd_usd_per_tb_2026": Assumption(1_216 / 30, "USD/TB", "30TB HDD, Q3 2026", SOURCED, VDURA_INDEX),
}


@dataclass(frozen=True)
class Row:
    category: str
    layer: str
    ssd_tb: float
    hdd_tb: float

    @property
    def total_tb(self) -> float:
        return self.ssd_tb + self.hdd_tb


def v(name: str) -> float:
    return ASSUMPTIONS[name].value


def validate() -> None:
    for name, a in ASSUMPTIONS.items():
        if a.value < 0:
            raise ValueError(f"{name} must not be negative")
    for prefix in ("siem", "edr", "llm_log"):
        if v(f"{prefix}_ssd_days") > v(f"{prefix}_retention_days"):
            raise ValueError(f"{prefix}_ssd_days exceeds {prefix}_retention_days")
    if not 0 <= v("pcap_utilization") <= 1:
        raise ValueError("pcap_utilization must be between 0 and 1")
    if v("dataset_versions") < 1 or v("protection_multiplier") < 1:
        raise ValueError("dataset_versions and protection_multiplier must be at least 1")


def retained(category: str, layer: str, gb_per_day: float, ssd_days: float, retention_days: float) -> Row:
    """A daily stream kept for retention_days, the newest ssd_days of it on SSD."""
    return Row(
        category,
        layer,
        ssd_tb=gb_per_day * ssd_days / 1_000,
        hdd_tb=gb_per_day * (retention_days - ssd_days) / 1_000,
    )


def estimate() -> list[Row]:
    siem_gb_day = v("siem_ingest_gb_per_day") * v("siem_stored_ratio")
    # Gbit/s x seconds per day / 8 bits per byte = GB/day.
    pcap_gb_day = v("pcap_link_gbps") * v("pcap_utilization") * 86_400 / 8
    edr_gb_day = v("edr_endpoints") * v("edr_mb_per_endpoint_day") / 1_000
    checkpoint_tb = v("model_params_billion") * 1e9 * v("checkpoint_bytes_per_param") / 1e12
    vector_tb = (
        v("vectors_million") * 1e6 * v("embedding_dims") * v("bytes_per_dim") * v("vector_index_overhead") / 1e12
    )
    llm_log_gb_day = (
        v("llm_calls_per_day") * v("tokens_per_call") * v("bytes_per_token") * v("llm_log_overhead") / 1e9
    )

    return [
        retained("SIEM logs", "Telemetry", siem_gb_day, v("siem_ssd_days"), v("siem_retention_days")),
        retained("Full PCAP", "Telemetry", pcap_gb_day, 0, v("pcap_window_days")),
        retained("EDR telemetry", "Telemetry", edr_gb_day, v("edr_ssd_days"), v("edr_retention_days")),
        Row(
            "Training and fine-tune data",
            "AI",
            ssd_tb=v("dataset_tb"),
            hdd_tb=v("dataset_tb") * (v("dataset_versions") - 1),
        ),
        Row("Model checkpoints", "AI", ssd_tb=checkpoint_tb * v("checkpoints_retained"), hdd_tb=0),
        Row("Embeddings and vector store", "AI", ssd_tb=vector_tb, hdd_tb=0),
        retained(
            "Prompt and output logs", "AI", llm_log_gb_day, v("llm_log_ssd_days"), v("llm_log_retention_days")
        ),
    ]


def subtotal(rows: list[Row], label: str, layer: str | None = None) -> Row:
    picked = [r for r in rows if layer is None or r.layer == layer]
    return Row(label, "", sum(r.ssd_tb for r in picked), sum(r.hdd_tb for r in picked))


def render(headers: list[str], rows: list[list[str]], markdown: bool, align: str) -> str:
    """Render a table. align holds one character per column: "l" for text, "r" for numbers."""
    if markdown:
        rule = "|" + "".join(" --- |" if a == "l" else " ---: |" for a in align)
        lines = ["| " + " | ".join(headers) + " |", rule]
        lines += ["| " + " | ".join(r) + " |" for r in rows]
        return "\n".join(lines)
    widths = [max(len(c) for c in col) for col in zip(headers, *rows)]

    def line(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) if a == "l" else c.rjust(w) for c, w, a in zip(cells, widths, align)).rstrip()

    return "\n".join([line(headers), line(["-" * w for w in widths])] + [line(r) for r in rows])


def tb(x: float) -> str:
    return f"{x:,.1f}"


def usd(x: float, cents: bool = False) -> str:
    return f"${x:,.2f}" if cents else f"${x:,.0f}"


def num(x: float) -> str:
    return f"{x:,.2f}".rstrip("0").rstrip(".")


def capacity_table(rows: list[Row], markdown: bool) -> str:
    mult = v("protection_multiplier")
    total = subtotal(rows, "Total, primary copy")
    body = [[r.category, r.layer, tb(r.ssd_tb), tb(r.hdd_tb), tb(r.total_tb)] for r in rows]
    for layer, label in (("Telemetry", "Subtotal, telemetry"), ("AI", "Subtotal, AI layer")):
        s = subtotal(rows, label, layer)
        body.append([s.category, "", tb(s.ssd_tb), tb(s.hdd_tb), tb(s.total_tb)])
    body.append([total.category, "", tb(total.ssd_tb), tb(total.hdd_tb), tb(total.total_tb)])
    body.append(
        [
            f"Total with protection (x{mult:g})",
            "",
            tb(total.ssd_tb * mult),
            tb(total.hdd_tb * mult),
            tb(total.total_tb * mult),
        ]
    )
    if markdown:
        for r in body[len(rows):]:
            r[0] = f"**{r[0]}**"
    return render(["Category", "Layer", "SSD TB", "HDD TB", "Total TB"], body, markdown, "llrrr")


def media_cost(row: Row, year: int) -> float:
    """Media cost of a row's protected capacity at one year's prices."""
    mult = v("protection_multiplier")
    return mult * (row.ssd_tb * v(f"ssd_usd_per_tb_{year}") + row.hdd_tb * v(f"hdd_usd_per_tb_{year}"))


def ratio(new: float, old: float) -> str:
    return f"{new / old:.1f}x" if old else "n/a"


def pct(part: float, whole: float) -> str:
    return f"{100 * part / whole:.0f}%" if whole else "n/a"


def cost_table(rows: list[Row], markdown: bool) -> str:
    mult = v("protection_multiplier")
    total = subtotal(rows, "")
    body = []
    for media, capacity in (("SSD", total.ssd_tb * mult), ("HDD", total.hdd_tb * mult)):
        p25, p26 = v(f"{media.lower()}_usd_per_tb_2025"), v(f"{media.lower()}_usd_per_tb_2026")
        body.append(
            [
                media,
                tb(capacity),
                usd(p25, cents=True),
                usd(p26, cents=True),
                usd(capacity * p25),
                usd(capacity * p26),
                ratio(p26, p25),
            ]
        )
    c25, c26 = media_cost(total, 2025), media_cost(total, 2026)
    label = "**Total**" if markdown else "Total"
    body.append([label, tb(total.total_tb * mult), "", "", usd(c25), usd(c26), ratio(c26, c25)])
    headers = ["Media", "Protected TB", "2025 $/TB", "2026 $/TB", "2025 cost", "2026 cost", "2026 vs 2025"]
    return render(headers, body, markdown, "lrrrrrr")


def layer_table(rows: list[Row], markdown: bool) -> str:
    mult = v("protection_multiplier")
    total = subtotal(rows, "")
    body = []
    for layer, label in (("Telemetry", "Telemetry"), ("AI", "AI layer")):
        s = subtotal(rows, label, layer)
        body.append(
            [
                label,
                tb(s.total_tb * mult),
                pct(s.total_tb, total.total_tb),
                pct(s.ssd_tb, total.ssd_tb),
                pct(media_cost(s, 2025), media_cost(total, 2025)),
                pct(media_cost(s, 2026), media_cost(total, 2026)),
            ]
        )
    headers = ["Layer", "Protected TB", "Share of TB", "Share of SSD TB", "Share of 2025 cost", "Share of 2026 cost"]
    return render(headers, body, markdown, "lrrrrr")


def assumption_table(markdown: bool) -> str:
    body = []
    for name, a in ASSUMPTIONS.items():
        status = f"{a.status}. Basis: {a.basis}" if a.basis else a.status
        body.append([f"`{name}`" if markdown else name, num(a.value), a.unit, a.description, status])
    return render(["Input", "Value", "Unit", "Description", "Status or source"], body, markdown, "lrlll")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--markdown", action="store_true", help="print GitHub-flavored Markdown tables")
    parser.add_argument("--assumptions", action="store_true", help="also print every input and its status")
    args = parser.parse_args()

    validate()
    rows = estimate()
    print(capacity_table(rows, args.markdown))
    print()
    print(cost_table(rows, args.markdown))
    print()
    print(layer_table(rows, args.markdown))
    if args.assumptions:
        print()
        print(assumption_table(args.markdown))
    unconfirmed = sum(a.status == CONFIRM for a in ASSUMPTIONS.values())
    if unconfirmed:
        print(f"\n{unconfirmed} inputs are still marked '{CONFIRM}'.")


if __name__ == "__main__":
    main()
