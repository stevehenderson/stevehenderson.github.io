---
layout: page
title: The Agentic Developer's Ethos
permalink: /ethos/
math: true
---

*Building whole systems that wouldn't otherwise exist — at velocity, with judgment that scales.*

AI-assisted development isn't a productivity gimmick, and it isn't a threat to resist. It's the first time most of us can bring entire systems to life that we'd never have had the hours to build — turning an idea into a working thing in an afternoon instead of a quarter. The velocity is real. The volume is real. And the discipline that lets me trust what I ship is what turns that velocity into *ambition I can act on* rather than risk I can't see.

That's the whole bet of this ethos: rigor isn't the brake on speed — it's the engine of it. The more cheaply I can trust code, the more of it I can safely set loose. These are the principles I build by.

---

## How to value the tool

**AI is a multiplier, not an addition.**

> *"Give me a lever long enough and a fulcrum on which to place it, and I shall move the world."*
> — Archimedes

<figure class="figure">
  <img src="{{ site.baseurl }}/images/Archimedes_lever.png" alt="Engraving of Archimedes moving the Earth with a long lever resting on a fulcrum" />
  <figcaption>Archimedes moving the world with a lever — <em>Mechanics Magazine</em>, 1824. Public domain, via <a href="https://commons.wikimedia.org/">Wikimedia Commons</a>.</figcaption>
</figure>

AI is the lever; I am the one leaning on it. A lever multiplies force — it doesn't supply the force, and it has no idea where to push. Both of those are mine to bring: the push, and the aim. Mine is [twenty years of hard-won domain expertise](/experience/) — knowing exactly where to set the fulcrum and how hard to lean. Hand this lever to a master and it moves worlds; hand it to an empty grip and it moves nothing, only faster. That's the whole of it: the tool scales whatever judgment I bring to it. A strong base compounds enormously; an empty one amplifies into nothing. So my job is to be a base worth multiplying — to play Archimedes, **and use the lever to build and ship world-sized, massively impactful capabilities and solutions.**

**A built thing beats an imagined one.**
For a whole new system, the real comparison is never "well-understood code" versus "loosely-understood code" — it's "this exists" versus "this never got built." A system I mostly understand and actually shipped is pure upside against the one I was still planning. Opportunity has a clock on it: the idea I sit on becomes someone else's product. When the downside is small and the upside is a thing that didn't exist yesterday, I build.

**Volume is not value — but velocity-to-existence is.**
Line count is a cost, not a trophy; I measure validated outcomes, not keystrokes saved. But shipping the first working version of something that *should* exist is its own kind of value, and AI has made that speed-to-life the cheapest it has ever been.

**I am the author of the decisions, not the keystrokes.**
The agent typed it; I own it. Provenance doesn't transfer accountability. If it ships under my name, it's mine to explain, defend, and stand behind.

---

## How to work with the agent

**The agent is an extension of me, not a being.**
It isn't a colleague, a genie, or a mythical "AI" I bargain with — it's a tool acting on my behalf, which makes it an extension of my own hands. There's no relationship to wrangle and no persona to manage; there's only my intent, carried out. So my agents speak in the **first person, as me** — never as some third party narrating what "the AI" did — and I own every line they produce exactly as if I'd typed it myself. To keep that framing honest, I drop a line like this into every `AGENT.md`:

```text
You are not a separate assistant or persona. You are an extension of me, the
author — my hands, acting on my behalf. Write and speak in the first person
("I", "my"), as me; never refer to yourself as "the AI", "the assistant", or
"the agent," and never narrate in the third person. Everything you produce is
my work and my responsibility — make the call I would make, and surface only
what I'd genuinely want to decide myself.
```

**Short leash, small diffs.**
I direct the approach and read the code as it forms, so I never inherit a thousand-line blob I didn't watch being built. Reverse-engineering intent from a finished diff is the slowest, riskiest order of operations.

**Specify, then generate.**
The contract is the part I write by hand — the types, the invariants, the statement of what must be true. Intent is the new source code; the implementation flows from a spec I own.

**Stay in my competence — or know that I've left it.**
In my domain, reading is faster than writing, so the velocity is real. Outside it, the speed is a trap, because I can't review what I don't understand. If reviewing feels as slow as writing it myself, that's information — either I slow down and learn, or I consciously decide to let verification carry the trust instead.

---

## How to review

**Match the rigor to the stakes — downside *and* upside.**
Scrutiny scales with what a mistake would cost and with what the work could unlock. Irreversible, production, money, security, shared data, real blast radius → I understand every line before it ships. Greenfield, reversible, exploratory, behind a flag, a thing that wouldn't otherwise exist → I let myself err toward building now and understanding deeper later. The sin isn't shipping code I haven't fully internalized; it's failing to *calibrate* — bringing prototype rigor to a payments path, or audit rigor to a throwaway spike.

**If I can't say why, I can't ship it — where it counts.**
On anything in the blast radius, "why is it written this way?" demands a real answer, and "I didn't read it" is never acceptable. That bar is non-negotiable exactly where a single defect is expensive — and deliberately relaxed where it isn't.

**Review by blast radius, not by line.**
Severity isn't linear; I can't average a production-killing bug against a thousand fine lines. Resource handling, data mutations, security boundaries, anything irreversible: deep scrutiny. Boilerplate and glue: a glance. Attention goes where one defect outweighs all the rest.

**Unfamiliar is not wrong.**
I separate "I wouldn't have written it this way" from "this is incorrect." Style and unfamiliarity aren't defects, and I won't burn a veto on them. But every "this looks off" gets resolved into *correct, just different* or *actually broken* — I verify the equivalence, I don't assume it.

**Trust the process, not the artifact.**
Wholesale trust is earned through verification — types, tests, invariants, property checks, sound boundaries — not by eyeballing every line forever. That's exactly how we already trust compilers: not by reading their output, but by trusting the system around them. And as the math below shows, it's also the very thing that lets me build more.

---

## How to hold the line

**The bug is the symptom; the missing review is the disease.**
A defect caught in review is the system working as designed. The thing worth fixing is never the caught mistake — it's the workflow that let unread code reach a place it could hurt. Fix the process; don't scapegoat the person it already caught.

**Reward the ones who multiply well.**
The goal is judgment kept in the loop — not banning the tool, not worshipping it. The future belongs to the people who unlock this power responsibly, and that's a skill to cultivate: in myself, and in the people I build alongside.

---

**The creed, in one line:**
> Go fast by understanding faster — and make understanding cheaper, so I can build what wouldn't otherwise exist.

---

## The workflow: orient -> review -> verify

Three moves, each with a moment to reach for it. The first builds *felt* understanding: fast, and fallible. The last two build *checked* understanding: slower, and real. I dial the depth to the stakes — a light touch on a reversible spike, all three in full on the blast-radius code.

**Orient — build the map.**
*The moment a diff or an unfamiliar file lands.* I reach for an agentic explainer or a structural index — Claude Code, Cursor, Copilot's agent mode, Sourcegraph/Cody, or a knowledge-graph view for the shape of the thing. It hands me a narrative in seconds. I treat that narrative as a hypothesis, never a verdict: it was written by the same kind of model that wrote the code, so it can be confidently wrong in the same places.

**Review — interrogate the risk.**
*Before merge, scaled by blast radius.* I let an AI reviewer take the first pass — CodeRabbit, Greptile, Qodo, Cursor BugBot, Claude Code Review — layered on a deterministic static engine like Semgrep, SonarQube, or DeepSource. Then I spend my own attention where a single defect outweighs the rest. The deterministic engine is the part that doesn't share the author's blind spots, so it carries the weight when the AI reviewer and the AI author would otherwise fail the same way.

**Verify — prove the behavior.**
*Anything I couldn't defend on reading alone, and everything in the blast radius.* Types, property-based tests (Hypothesis and kin) that throw hundreds of inputs at a stated invariant, and mutation testing to confirm the tests would actually catch a planted bug. This is the move that discharges comprehension debt — it produces checkable facts instead of a persuasive story. It is also, as it turns out, the move that raises my ceiling.

**The loop, in one line:**
> Orientation earns the speed; verification earns the right to trust it.

---

## The ceiling is a dial I control

The lever has a catch, and it's all about the fulcrum. Archimedes still had to choose where to set it — and for building, the fulcrum is *how much I must understand myself*. Move it and the whole trade-off moves; the math makes that exact.

If I insist on personally understanding everything at full depth, there is a hard cap on my multiplier — and it pays to know the math, because knowing it is how I beat it. It is Amdahl's Law: whatever share of the work is *me understanding and deciding* can't be compressed away, so

$$
M_{\max} \;=\; \frac{1}{p}\,,\qquad p = \text{the share of the work I must understand myself.}
$$

![The multiplier is a dial you control: maximum multiplier equals one divided by the share of work you must understand yourself; the ceiling stays near 2x while that share is large and climbs steeply as it shrinks toward 10%.](data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNzIwIDQ0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iLWFwcGxlLXN5c3RlbSwgQmxpbmtNYWNTeXN0ZW1Gb250LCAnU2Vnb2UgVUknLCBSb2JvdG8sIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI3MjAiIGhlaWdodD0iNDQwIiByeD0iMTQiIGZpbGw9IiNGQkY5RjQiLz4KICA8dGV4dCB4PSIzNjAiIHk9IjMyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE4IiBmb250LXdlaWdodD0iNTAwIiBmaWxsPSIjMkMyQzJBIj5UaGUgbXVsdGlwbGllciBpcyBhIGRpYWwgeW91IGNvbnRyb2w8L3RleHQ+CiAgPHRleHQgeD0iMzYwIiB5PSI1NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZmlsbD0iIzVGNUU1QSI+bWF4aW11bSBtdWx0aXBsaWVyID0gMSAmIzI0NzsgdGhlIHNoYXJlIG9mIHdvcmsgeW91IG11c3QgdW5kZXJzdGFuZCB5b3Vyc2VsZjwvdGV4dD4KCiAgPCEtLSBncmlkbGluZXMgLS0+CiAgPGxpbmUgeDE9IjcwIiB5MT0iMzgwIiB4Mj0iNjkwIiB5Mj0iMzgwIiBzdHJva2U9IiNCNEIyQTkiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxsaW5lIHgxPSI3MCIgeTE9IjM0Ni43IiB4Mj0iNjkwIiB5Mj0iMzQ2LjciIHN0cm9rZT0iI0U0RTFEOCIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPGxpbmUgeDE9IjcwIiB5MT0iMjgwIiB4Mj0iNjkwIiB5Mj0iMjgwIiBzdHJva2U9IiNFNEUxRDgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxsaW5lIHgxPSI3MCIgeTE9IjIxMy4zIiB4Mj0iNjkwIiB5Mj0iMjEzLjMiIHN0cm9rZT0iI0U0RTFEOCIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPGxpbmUgeDE9IjcwIiB5MT0iMTQ2LjciIHgyPSI2OTAiIHkyPSIxNDYuNyIgc3Ryb2tlPSIjRTRFMUQ4IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8bGluZSB4MT0iNzAiIHkxPSI4MCIgeDI9IjY5MCIgeTI9IjgwIiBzdHJva2U9IiNFNEUxRDgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxsaW5lIHgxPSI3MCIgeTE9IjgwIiB4Mj0iNzAiIHkyPSIzODAiIHN0cm9rZT0iI0I0QjJBOSIgc3Ryb2tlLXdpZHRoPSIxIi8+CgogIDwhLS0geSB0aWNrcyAtLT4KICA8dGV4dCB4PSI2MCIgeT0iMzg0IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj4xJiMyMTU7PC90ZXh0PgogIDx0ZXh0IHg9IjYwIiB5PSIzNTAuNyIgdGV4dC1hbmNob3I9ImVuZCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+MiYjMjE1OzwvdGV4dD4KICA8dGV4dCB4PSI2MCIgeT0iMjg0IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj40JiMyMTU7PC90ZXh0PgogIDx0ZXh0IHg9IjYwIiB5PSIyMTcuMyIgdGV4dC1hbmNob3I9ImVuZCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+NiYjMjE1OzwvdGV4dD4KICA8dGV4dCB4PSI2MCIgeT0iMTUwLjciIHRleHQtYW5jaG9yPSJlbmQiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjgmIzIxNTs8L3RleHQ+CiAgPHRleHQgeD0iNjAiIHk9Ijg0IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj4xMCYjMjE1OzwvdGV4dD4KCiAgPCEtLSB4IHRpY2tzIC0tPgogIDx0ZXh0IHg9IjcwIiB5PSI0MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjYwJTwvdGV4dD4KICA8dGV4dCB4PSIxNTguNiIgeT0iNDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj41MCU8L3RleHQ+CiAgPHRleHQgeD0iMjQ3LjEiIHk9IjQwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+NDAlPC90ZXh0PgogIDx0ZXh0IHg9IjMzNS43IiB5PSI0MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjMzJTwvdGV4dD4KICA8dGV4dCB4PSI0MjQuMyIgeT0iNDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj4yNSU8L3RleHQ+CiAgPHRleHQgeD0iNTEyLjkiIHk9IjQwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+MjAlPC90ZXh0PgogIDx0ZXh0IHg9IjYwMS40IiB5PSI0MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjE1JTwvdGV4dD4KICA8dGV4dCB4PSI2OTAiIHk9IjQwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+MTAlPC90ZXh0PgoKICA8IS0tIGF4aXMgdGl0bGVzIC0tPgogIDx0ZXh0IHg9IjIyIiB5PSIyMzAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMiIGZpbGw9IiM0NDQ0NDEiIHRyYW5zZm9ybT0icm90YXRlKC05MCAyMiAyMzApIj5tYXggbXVsdGlwbGllcjwvdGV4dD4KICA8dGV4dCB4PSIzODAiIHk9IjQyNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZmlsbD0iIzQ0NDQ0MSI+c2hhcmUgb2YgdGhlIHdvcmsgeW91IG11c3QgdW5kZXJzdGFuZCB5b3Vyc2VsZjwvdGV4dD4KCiAgPCEtLSBhcmVhIGZpbGwgdW5kZXIgY3VydmUgLS0+CiAgPHBvbHlnb24gcG9pbnRzPSI3MCwzNTYuNyAxNTguNiwzNDYuNyAyNDcuMSwzMzAgMzM1LjcsMzEzLjMgNDI0LjMsMjgwIDUxMi45LDI0Ni43IDYwMS40LDE5MCA2OTAsODAgNjkwLDM4MCA3MCwzODAiIGZpbGw9IiNEODVBMzAiIGZpbGwtb3BhY2l0eT0iMC4wOCIvPgoKICA8IS0tIGN1cnZlIC0tPgogIDxwb2x5bGluZSBwb2ludHM9IjcwLDM1Ni43IDE1OC42LDM0Ni43IDI0Ny4xLDMzMCAzMzUuNywzMTMuMyA0MjQuMywyODAgNTEyLjksMjQ2LjcgNjAxLjQsMTkwIDY5MCw4MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRDg1QTMwIiBzdHJva2Utd2lkdGg9IjIuNSIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CgogIDwhLS0gcG9pbnRzIC0tPgogIDxjaXJjbGUgY3g9IjcwIiBjeT0iMzU2LjciIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSIxNTguNiIgY3k9IjM0Ni43IiByPSI0IiBmaWxsPSIjRDg1QTMwIi8+CiAgPGNpcmNsZSBjeD0iMjQ3LjEiIGN5PSIzMzAiIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSIzMzUuNyIgY3k9IjMxMy4zIiByPSI0IiBmaWxsPSIjRDg1QTMwIi8+CiAgPGNpcmNsZSBjeD0iNDI0LjMiIGN5PSIyODAiIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSI1MTIuOSIgY3k9IjI0Ni43IiByPSI0IiBmaWxsPSIjRDg1QTMwIi8+CiAgPGNpcmNsZSBjeD0iNjAxLjQiIGN5PSIxOTAiIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSI2OTAiIGN5PSI4MCIgcj0iNC41IiBmaWxsPSIjOTkzQzFEIi8+CgogIDwhLS0gYW5ub3RhdGlvbnMgLS0+CiAgPHRleHQgeD0iOTIiIHk9IjM3MiIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj51bmRlcnN0YW5kIGl0IGFsbCAmIzg3NzY7IDImIzIxNTs8L3RleHQ+CiAgPHRleHQgeD0iMzAwIiB5PSIxMjAiIHRleHQtYW5jaG9yPSJzdGFydCIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjOTkzQzFEIj5sZXQgdmVyaWZpY2F0aW9uIGNhcnJ5IHRoZSBwcm9vZiAmIzgyMTI7PC90ZXh0PgogIDx0ZXh0IHg9IjMwMCIgeT0iMTM4IiB0ZXh0LWFuY2hvcj0ic3RhcnQiIGZvbnQtc2l6ZT0iMTIuNSIgZmlsbD0iIzk5M0MxRCI+YW5kIHRoZSBjZWlsaW5nIGNsaW1iczwvdGV4dD4KICA8cGF0aCBkPSJNIDU0MCAxNDAgUSA2MDAgMTUwIDY0NSAxMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzk5M0MxRCIgc3Ryb2tlLXdpZHRoPSIxLjQiLz4KICA8cGF0aCBkPSJNIDY0NSAxMTAgbCAtOSAxIGwgNSA3IHoiIGZpbGw9IiM5OTNDMUQiLz4KPC9zdmc+)

Read the curve as good news, not bad. It isn't a prison — it's a map of where the leverage lives. The share I must personally understand is *not fixed*: every place I let trustworthy verification carry the proof — a type proving a resource is released, a static pass proving no leaked handle, a property test pinning an invariant across thousands of inputs — I shrink that share without lowering my assurance one bit. Moving from "I must understand half" to "I must truly understand a fifth" is the whole distance from a 2x ceiling to a 5x one. I don't raise my multiplier by reading faster. I raise it by *needing to read less, safely.*

And for whole new systems the math is kinder still, because the baseline isn't a well-understood codebase — it's an empty repo. Measured against *nothing*, a system I mostly understand and actually shipped is all upside. That is exactly where I spend my willingness to understand less: greenfield, reversible, the thing that wouldn't otherwise exist. I save the deep comprehension for the day it earns real users and a real blast radius — and by then, verification is precisely what lets me extend it without holding all of it in my head at once.

The horizon is the best part. As agent layers mature toward being trustable the way a compiler is — deterministic, verified, track-recorded — the share I have to read myself collapses toward just the spec I write and check, and the ceiling runs clean off the top of that chart. It rises exactly as fast as trustworthy verification displaces personal comprehension, and not one step faster. So that's the real work, and it's a hopeful kind of work: make trust cheap, and the ambition takes care of itself.

**The creed, in its final form:**
> I can't multiply faster than I can understand — so I make understanding cheaper, and pour the surplus into building things that didn't exist yesterday.
