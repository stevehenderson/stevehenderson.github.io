---
layout: post
title: "Storage Is the Hidden AI Bottleneck (and Cyber Teams Feel It First)"
categories: ['blog']
tags: ['cyber', 'ai', 'storage', 'infrastructure', 'siem', 'air-gapped']
summary: "AI demand absorbed enterprise flash and nearline disk supply through 2026, and data center power limits are squeezing the same budgets. Security teams already retain large volumes of SIEM, PCAP, and EDR data and now add AI pipelines on top. A worked estimate for a mid-size AI-for-cyber project shows where the bytes and the money go, followed by what I would do now."
tldr: >-
  GPUs get most of the attention in AI planning, and in 2026 storage is the constraint I see deciding whether projects ship. Enterprise SSD contract prices rose about 80% in the first quarter alone, Seagate has most of its nearline HDD output allocated into 2028, and the flash makers expect tight supply through 2027. Security teams already keep large volumes of logs, packets, and endpoint telemetry, and AI pipelines add training data, checkpoints, embeddings, and prompt logs on top. In my worked estimate the AI layer is a small share of the bytes and most of the flash, and the post closes with what I would do about it now.
---

Most AI infrastructure conversations I take part in start with GPUs: how many we can get and when they arrive.
Storage usually comes up later, when someone asks where the training data, checkpoints, and logs will live.
This year that question got much harder to answer, and in my experience it is now the one that decides whether a project ships on schedule.

Flash and high-capacity disk both tightened through 2026 as AI demand absorbed supply, and power limits at data centers are pressing on the same budgets.
Security teams feel this earlier than most, because we already keep large volumes of telemetry and are now adding AI pipelines on top of it.

## The crunch is already here

### Flash

TrendForce reported that enterprise SSD contract prices rose [about 80% in the first quarter of 2026](https://www.trendforce.com/presscenter/news/20260611-13092.html) as vendors raised prices into tight supply.
In August it put the [cumulative rise in enterprise SSD prices for 2026 at 235%](https://www.trendforce.com/presscenter/news/20260825-13198.html), after about 35% in the second half of 2025.
Its [fourth-quarter forecast](https://www.trendforce.com/presscenter/news/20260930-13258.html) has NAND contract prices up another 15-20% and notes that "most incremental supply has already been committed, leaving little available on the open market."

Micron's [fiscal 2026 annual report](https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000023/mu-20260903.htm) cites "an approximate 200% increase in average selling prices" for NAND over fiscal 2025.

### Disk

In July, Seagate's CEO said that ["the vast majority of our nearline exabytes are now allocated into calendar 2028."](https://www.marketbeat.com/earnings/reports/2026-7-28-seagate-technology-plc-stock/)
In April, Western Digital's CFO said that ["Manufacturing lead times are now about a year, and so most of the purchase orders are being placed a year in advance."](https://www.fool.com/earnings/call-transcripts/2026/04/30/western-digital-wdc-q3-2026-earnings-transcript/)
WD's blended price per terabyte in the quarter that ended July 3 was [up by a high-teens percentage year over year](https://stockanalysis.com/stocks/wdc/transcripts/658556-q4-2026/).
As of October 12, TrendForce reported nearline HDD lead times [still at 50 weeks](https://insights.trendforce.com/p/weekly-radar-005).

### What is driving it

TrendForce attributes the flash increases to [AI applications driven by inference](https://www.trendforce.com/presscenter/news/20260202-12911.html).
Micron points to [KV cache offload and SSDs replacing HDDs](https://investors.micron.com/files/doc_financials/2026/q4/Q4-FY26-Prepared-Remarks.pdf) as new demand for flash.
TrendForce [estimates](https://www.trendforce.com/presscenter/news/20260825-13198.html) that DRAM and NAND together will take 47% of the major cloud providers' capital spending in 2026 and 68% in 2027.

### How long it lasts

The forecasts disagree on when this eases.
TrendForce [expects](https://www.trendforce.com/presscenter/news/20260721-13148.html) a 4-5% NAND supply deficit in 2026, with supply and demand coming back into balance in the second half of 2027.
The suppliers are more cautious.
Micron [expects](https://investors.micron.com/files/doc_financials/2026/q4/Q4-FY26-Prepared-Remarks.pdf) industry NAND bit shipments to grow in the mid-20s percent in 2027 and 2028 and the industry "to remain supply constrained in both years."
Kioxia [sees](https://www.kioxia-holdings.com/content/dam/kioxia-hd/en-jp/ir/library/event/asset/Kioxia_Investor_Day_2026_en_script.pdf) the market staying tight throughout 2027, and SanDisk [told analysts](https://www.investing.com/news/transcripts/earnings-call-transcript-sandisk-beats-q4-2026-forecasts-shares-slide-93CH-4839552) it expects its bits "to remain on allocation beyond calendar year 2027."

New fabs arrive late: Micron's Singapore NAND facility is [scheduled](https://investors.micron.com/files/doc_financials/2026/q4/Q4-FY26-Prepared-Remarks.pdf) to begin output in the second half of 2028, and SK hynix [plans](https://news.skhynix.com/en/fab-facility-investment-2026/) to open the first cleanroom of its Cheongju NAND fab in December 2028.
I plan for prices to stay high through 2027 and treat any easing late in the year as upside.

### Who pays the open-market price

The biggest buyers have long-term agreements, and TrendForce [reports](https://www.trendforce.com/presscenter/news/20260825-13198.html) that some signed from the second quarter of 2026 onward include price ceilings.
In my experience most security teams buy on the open market, where TrendForce says little supply is left.

VDURA, which sells hybrid flash and disk systems and so has an interest in the comparison, publishes a [price index](https://www.vdura.com/?p=16714) for 30 TB enterprise drives.
It puts a TLC SSD at $3,460 in Q3 2025 and $22,600 in Q3 2026, and an HDD at $495 and $1,216.
VDURA does not publish its method, and its index has risen faster than TrendForce's contract figures.
I read it as closer to what a buyer without a long-term agreement pays, and I use it for the prices in the estimate below.

## AI uses storage at every layer

For an AI-for-cyber project I count four layers of storage, covering everything that persists between training and inference runs.

**Training and fine-tuning data.**
For cyber work it includes labeled logs, PCAP slices, detection outputs, and sometimes malware samples.
I keep every dataset version used to train a model so it can be reproduced and audited.

**Model checkpoints.**
The [ZeRO paper](https://arxiv.org/abs/1910.02054) works out that mixed-precision Adam training holds 16 bytes per parameter: 2 for 16-bit weights, 2 for gradients, and 12 for the fp32 weights, momentum, and variance.
A checkpoint that can resume training saves the weights and the optimizer state, so I budget about 14 bytes per parameter.
For a 32-billion-parameter model, that is about 450 GB per checkpoint, and keeping eight checkpoints from each of three runs is about 11 TB of fast storage.
LoRA and other parameter-efficient fine-tunes are far smaller.

**Embeddings and vector stores.**
A 1,024-dimension float32 embedding is 4,096 bytes.
250 million chunks of CTI reports, tickets, alerts, and log summaries come to about 1 TB of raw vectors, before the index graph, metadata, and chunk text.
I keep these on SSD because analysts and agents wait on retrieval.

**Prompt and output logs.**
Agents need audit trails, and I have found security teams want every prompt, tool call, and output kept at least as long as the alerts the agent touched.
Agent prompts are long because each call re-sends its context, so these logs grow faster than the alert count.

## Power is the second squeeze

- Gartner [predicted](https://www.gartner.com/en/newsroom/press-releases/2024-11-12-gartner-predicts-power-shortages-will-restrict-40-percent-of-ai-data-centers-by-20270) in November 2024 that 40% of existing AI data centers would be operationally constrained by power availability by 2027.
- Lawrence Berkeley National Laboratory's [2025 update](https://eta-publications.lbl.gov/publications/united-states-data-center-energy-2025) projects that data centers could use 11.8% of US electricity by 2030, within a range of 9.5% to 15.3%.
- PJM's [2028/29 capacity auction](https://www.pjm.com/-/media/DotCom/about-pjm/newsroom/2026-releases/20260714-pjm-capacity-auction-procures-138318-mw-of-generation-resources.pdf) cleared at the $325/MW-day price cap for the third auction in a row and came in 6,831 MW short of the reliability requirement.
  PJM's independent market monitor [attributes](https://www.pjm.com/-/media/DotCom/committees-groups/committees/mc/2026/20260727-web/item-02---marketing-monitoring-report---presentation.pdf) $6.3 billion of the $16.4 billion in capacity charges, 38.2%, to data center load.
- ERCOT is [tracking about 474 GW](https://www.ercot.com/files/docs/2026/07/29/ERCOT-Senate-July-29-Panel-1-Assessing-The-Grid.pdf) of large loads seeking interconnection, about 90% of them data centers.
  In August it [paused approvals](https://www.ercot.com/files/docs/2026/09/11/14-Batch-Zero-Update.pdf) to energize data centers of 75 MW or more.

The effect on storage is indirect: in a power-capped facility I have found that new watts go to compute first, and storage gets the space and power left over.
TrendForce [notes](https://www.trendforce.com/presscenter/news/20250915-12714.html) that QLC SSDs use about 30% less power than nearline HDDs, which favors flash in a power-limited room, and 2026 prices make that trade harder to justify.

## Why cyber teams get hit twice

Security teams already run some of the largest data stores in most organizations: months of SIEM data, EDR telemetry from every endpoint, and full packet capture.
PCAP is the heaviest; a 10 Gbit/s link at 10% average utilization writes about 10.8 TB a day, so a two-week rolling window is about 150 TB.

In May, OMB Memorandum [M-26-14](https://www.whitehouse.gov/wp-content/uploads/2026/05/M-26-14-Ensuring-Effective-and-Efficient-Agency-Logging-and-Network-Visibility-to-Defend-Against-Evolving-Cyber-Threats.pdf) rescinded M-21-31, stating that some of its requirements, "such as the retention of vast quantities of logging data without clear utility, proved neither operationally feasible nor cost-effective for most agencies."
The new minimum is six months actively searchable and a year retrievable.
M-26-14 does not apply to national security systems or to Defense and Intelligence Community systems, which set their own requirements.

The AI layer then lands on top: training data drawn from the same logs and packets, a vector store over threat intelligence and tickets, and agent audit logs as one more retained stream.

Air-gapped and classified environments feel this first.
As I wrote in my [AthenaBench post]({% post_url 2026-07-09-AthenaBench-Local-CTI %}), a lot of my work happens in places cloud services cannot reach, so those teams cannot burst to cloud storage when a project grows.
Their hardware comes through approved supply chains, on procurement cycles that in my experience can match the drive makers' year-long lead times, and without the long-term agreements that cap hyperscaler prices.

## A worked estimate

To put numbers on this, I wrote a small standard-library Python script, [`scripts/storage_estimate.py`](https://github.com/stevehenderson/stevehenderson.github.io/blob/main/scripts/storage_estimate.py), that estimates one year of storage for a mid-size AI-for-cyber project.
Every input sits in one labeled block at the top of the file.
Inputs marked as assumptions are placeholders until I replace them with numbers from a real program.

| Category | Inputs | Status |
| --- | --- | --- |
| SIEM logs | 1,000 GB/day, stored at 50% of raw, 30 days SSD, 365 days total | ASSUMPTION - Steve to confirm (365 days matches the M-26-14 minimum) |
| Full PCAP | 10 Gbit/s link, 10% utilization, 14-day window on HDD | ASSUMPTION - Steve to confirm |
| EDR telemetry | 5,000 endpoints, 50 MB each per day, 30 days SSD, 180 days total | ASSUMPTION - Steve to confirm |
| Training and fine-tune data | 20 TB corpus, 3 versions kept, current version on SSD | ASSUMPTION - Steve to confirm |
| Model checkpoints | 32 billion parameters, 14 bytes per parameter, 24 checkpoints kept on SSD | ASSUMPTION - Steve to confirm (bytes per parameter from [ZeRO](https://arxiv.org/abs/1910.02054)) |
| Embeddings and vector store | 250 million chunks, 1,024 dimensions, float32, 2x for index and metadata | ASSUMPTION - Steve to confirm |
| Prompt and output logs | 250,000 calls/day, 12,000 tokens each, 4 bytes per token, 1.5x for traces, 30 days SSD, 365 days total | ASSUMPTION - Steve to confirm |
| Protection | 2x raw per usable byte for replicas, erasure coding, and backup | ASSUMPTION - Steve to confirm |
| Media prices | VDURA index, 30 TB TLC SSD and 30 TB HDD, Q3 2025 and Q3 2026 | Sourced ([VDURA](https://www.vdura.com/?p=16714)) |

The capacity result, in decimal terabytes:

| Category | Layer | SSD TB | HDD TB | Total TB |
| --- | --- | ---: | ---: | ---: |
| SIEM logs | Telemetry | 15.0 | 167.5 | 182.5 |
| Full PCAP | Telemetry | 0.0 | 151.2 | 151.2 |
| EDR telemetry | Telemetry | 7.5 | 37.5 | 45.0 |
| Training and fine-tune data | AI | 20.0 | 40.0 | 60.0 |
| Model checkpoints | AI | 10.8 | 0.0 | 10.8 |
| Embeddings and vector store | AI | 2.0 | 0.0 | 2.0 |
| Prompt and output logs | AI | 0.5 | 6.0 | 6.6 |
| **Subtotal, telemetry** |  | 22.5 | 356.2 | 378.7 |
| **Subtotal, AI layer** |  | 33.3 | 46.0 | 79.4 |
| **Total, primary copy** |  | 55.8 | 402.2 | 458.1 |
| **Total with protection (x2)** |  | 111.7 | 804.5 | 916.1 |

The media cost of that protected capacity at each year's prices:

| Media | Protected TB | 2025 $/TB | 2026 $/TB | 2025 cost | 2026 cost | 2026 vs 2025 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SSD | 111.7 | $115.33 | $753.33 | $12,880 | $84,132 | 6.5x |
| HDD | 804.5 | $16.50 | $40.53 | $13,274 | $32,607 | 2.5x |
| **Total** | 916.1 |  |  | $26,154 | $116,740 | 4.5x |

Rows may not sum exactly because of rounding.

The telemetry we already keep is most of the bytes: SIEM and PCAP alone are about 73% of the primary capacity, which makes retention policy the largest lever on the total.

The AI layer is small in bytes and heavy in flash.
Checkpoints, the active training set, and the vector store all want fast storage, so the AI layer is 17% of the capacity and 60% of the SSD, and its share of media cost goes from 35% at 2025 prices to 46% at 2026 prices.

At 2026 prices the same capacity costs about 4.5 times as much, and that covers drives only.
Servers, networking, power, and licenses come on top.
The estimate also applies one protection multiplier to every category, though many teams keep PCAP without a replica, and it holds ingest flat for the year, although in my experience ingest grows.

## What I'd do now

**Put storage on the AI budget as its own line.**
Size it with the GPUs, break out the four AI layers, and rerun the estimate when the model size, agent call volume, or retention policy changes.
I have found storage is the line most often discovered after the GPU order is placed.

**Set retention by detection value.**
M-26-14 moved federal civilian logging toward a risk-based approach, and I think the reasoning applies everywhere.
I would keep the sources that detections and hunts query, and shorten retention on the ones nobody has searched in months; SIEM query history makes this measurable.

**Tier by access pattern.**
I keep flash for hot SIEM data, the vector index, the current training set, and active checkpoints, and put warm telemetry, older dataset versions, and rollback checkpoints on disk.

**Reduce bytes before they land.**
For PCAP, I would keep full packets for a short window and Zeek or Suricata metadata for longer, and truncate encrypted flows that cannot be inspected anyway.
Storing repeated system prompts and shared context once, keyed by hash, removes most of the duplication in prompt logs.
Storing embeddings as float16 halves the raw vectors, and int8 halves them again, if retrieval quality holds up in testing.

**Decide between buying ahead and cloud on purpose.**
For air-gapped and classified programs, I see one realistic option: order 2027 capacity now, and price QLC flash where disk lead times block the schedule.
Cloud object storage absorbs growth without a hardware lead time, but cloud providers buy the same components, and I would not assume their storage prices hold.

## Closing

In my experience the AI projects that ship on time are the ones that sized storage early and bought it before they needed it.
For security teams, that sizing starts with the telemetry we already keep, because it is most of the bytes before any model arrives.

If your numbers look very different from mine, I would like to hear which ones.

