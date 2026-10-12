---
layout: page
title: The Agentic Developer's Ethos
permalink: /ethos/
math: true
---

*Building whole systems that wouldn't otherwise exist, at velocity, with judgment that scales.*

AI-assisted development is the first time most of us can bring entire systems to life that we'd otherwise never have the hours to build.
It can turn an idea into a working thing in an afternoon instead of a quarter.
The velocity is real, and so is the volume.
What makes it usable is the discipline to trust what I ship.
That discipline is what lets me act on the speed while keeping the risk visible.

The bet of this ethos is that rigor makes speed possible.
In my experience, the more cheaply I can trust code, the more of it I can safely put to work, and the stakes of each system set how much rigor it gets.
These are the principles I build by.

---

## How to value the tool

**AI is a multiplier on my judgment.**

> *"Give me a lever long enough and a fulcrum on which to place it, and I shall move the world."*
>
> Attributed to Archimedes

<figure class="figure">
  <img src="{{ site.baseurl }}/images/Archimedes_lever.png" alt="Engraving of Archimedes moving the Earth with a long lever resting on a fulcrum" />
  <figcaption>Archimedes moving the world with a lever. <em>Mechanics Magazine</em>, 1824. Public domain, via <a href="https://commons.wikimedia.org/">Wikimedia Commons</a>.</figcaption>
</figure>

AI is the lever, and I am the one leaning on it.
A lever multiplies force, but it supplies none of its own and does not know where to push.
Both the push and the aim are mine to bring.
Mine come from [twenty years of hard-won domain expertise](/experience/): knowing where to set the fulcrum and how hard to lean.
In my experience, the tool scales whatever judgment I bring to it: deep expertise compounds, and without expertise the tool produces little of value, only faster.
So my job is to be a base worth multiplying: to play Archimedes and **use the lever to build and ship capabilities with real impact, at a level of rigor set by what each one could break.**

**I favor a built thing over an imagined one.**
For a whole new system, the comparison I find honest is between a thing that exists and a thing that never got built; at that stage, how completely I understand each line matters less, as long as the stakes are low.
When the stakes are low, a system I mostly understand and actually shipped is a clear gain over the one I was still planning, and as its blast radius grows, so does the rigor I apply to it.
In my experience, opportunity has a clock on it, and an idea I sit on can become someone else's product.
When the downside is small and the upside is a thing that didn't exist yesterday, I build.

**I measure speed to a first working version, and I treat volume as a cost.**
Line count is a cost to be managed.
I measure validated outcomes, and keystrokes saved are not one of them.
Shipping the first working version of something that *should* exist has its own value, at a level of rigor matched to its blast radius.
AI has made reaching that first version cheaper than it has ever been.

**I author the decisions; the agent types.**
The agent typed it, and I own it.
In my view, where the code came from does not change who is accountable for it.
If it ships under my name, it's mine to explain, defend, and stand behind.

---

## How to work with the agent

**The agent is an extension of me.**
It is a tool acting on my behalf, an extension of my own hands.
I do not treat it as a colleague, a genie, or a mythical "AI" to bargain with.
There is no relationship or persona to manage; the agent carries out my intent.
So my agents speak in the **first person, as me**, and never narrate as a third party describing what "the AI" did.
I own every line they produce exactly as if I'd typed it myself.
To keep that framing consistent, I put a passage like this into every `AGENT.md`:

```text
You are not a separate assistant or persona. You are an extension of me, the
author — my hands, acting on my behalf. Write and speak in the first person
("I", "my"), as me; never refer to yourself as "the AI", "the assistant", or
"the agent," and never narrate in the third person. Everything you produce is
my work and my responsibility — make the call I would make, and surface only
what I'd genuinely want to decide myself.
```

**Short leash, small diffs.**
I direct the approach and read the code as it forms, so I never inherit a thousand-line blob I didn't watch being built.
In my experience, reverse-engineering intent from a finished diff is the slowest and riskiest order of operations.

**Specify, then generate.**
The contract is the part I write by hand: the types, the invariants, and the statement of what must be true.
I treat that statement of intent as the real source code, and the implementation follows from a spec I own.

**Stay in my competence, or know when I've left it.**
In my domain, reading is faster than writing, so the velocity is real.
Outside it, the speed works against me, because I can't review what I don't understand.
If reviewing feels as slow as writing the code myself, I take that as a signal.
Either I slow down and learn, or I consciously decide to let verification carry the trust.

---

## How to review

**Match the rigor to the stakes, downside *and* upside.**
Scrutiny scales with what a mistake would cost and with what the work could unlock.
For work that is irreversible, in production, or touches money, security, shared data, or anything else with a real blast radius, I understand every line before it ships.
For work that is greenfield, reversible, exploratory, behind a flag, or something that wouldn't otherwise exist, I let myself err toward building now and understanding more deeply later.
Shipping low-stakes code I haven't fully internalized is acceptable to me.
The failure I guard against is failing to *calibrate*: bringing prototype rigor to a payments path, or audit rigor to a throwaway spike.

**Where it counts, if I can't say why, I can't ship it.**
On anything in the blast radius, "why is it written this way?" demands a real answer, and "I didn't read it" is never acceptable.
That bar is non-negotiable where a single defect is expensive, and deliberately relaxed where it isn't.

**Review by blast radius.**
Severity isn't linear, and I can't average a production-killing bug against a thousand fine lines.
Resource handling, data mutations, security boundaries, and anything irreversible get deep scrutiny.
Boilerplate and glue get a glance.
My attention goes where one defect would outweigh all the rest.

**Unfamiliar code is not necessarily wrong.**
I separate "I wouldn't have written it this way" from "this is incorrect."
Style and unfamiliarity aren't defects, and I won't spend a veto on them.
But I resolve every "this looks off" into *correct, just different* or *actually broken*, and I verify the equivalence before accepting it.

**Trust the verification around the code.**
I earn wholesale trust through verification (types, tests, invariants, property checks, sound boundaries) and stop depending on eyeballing every line forever.
That is how we already trust compilers: we trust the system around them and do not read their output.
As the math below shows, the same verification is what lets me build more.

---

## How to hold the line

**I treat the bug as the symptom and the missing review as the cause.**
A defect caught in review means the system worked as designed.
What I fix is the workflow that let unread code reach a place where it could cause harm.
I fix the process and do not blame the person whose mistake the review caught.

**Reward the people who multiply well.**
The goal is to keep judgment in the loop, without banning the tool or worshipping it.
I believe the people who use this capability responsibly will do the most with it.
That is a skill I cultivate in myself and in the people I build alongside.

---

**The creed, in one line:**
> Go fast by understanding faster, and make understanding cheaper, so I can build what wouldn't otherwise exist.

---

## The workflow: orient, review, verify

The workflow has three moves, each with a moment to reach for it.
The first builds *felt* understanding, which is fast and fallible.
The last two build *checked* understanding, which is slower and real.
I set the depth by the stakes: a light touch on a reversible spike, and all three in full on blast-radius code.

**Orient: build the map.**
*The moment a diff or an unfamiliar file lands.*
I reach for an agentic explainer or a structural index, such as Claude Code, Cursor, Copilot's agent mode, Sourcegraph/Cody, or a knowledge-graph view for the shape of the thing.
It hands me a narrative in seconds.
I treat that narrative as a hypothesis to check.
The same kind of model that wrote the code wrote the narrative, so it can be confidently wrong in the same places.

**Review: interrogate the risk.**
*Before merge, scaled by blast radius.*
I let an AI reviewer (CodeRabbit, Greptile, Qodo, Cursor BugBot, Claude Code Review) take the first pass, layered on a deterministic static engine such as Semgrep, SonarQube, or DeepSource.
Then I spend my own attention where a single defect outweighs the rest.
The deterministic engine is the part that doesn't share the author's blind spots, so it carries the weight when the AI reviewer and the AI author would otherwise fail the same way.

**Verify: prove the behavior.**
*Anything I couldn't defend on reading alone, and everything in the blast radius.*
I use types, property-based tests (Hypothesis and similar tools) that throw hundreds of inputs at a stated invariant, and mutation testing to confirm the tests would actually catch a planted bug.
This move pays down comprehension debt by producing facts I can check, where orientation produced only a persuasive story.
It is also the move that raises my ceiling, as the next section shows.

**The loop:**
> Orientation earns the speed; verification earns the right to trust it.

---

## The ceiling is a dial I control

Archimedes still had to choose where to set the fulcrum.
For building, the fulcrum is *how much I must understand myself*.
Moving it moves the whole trade-off, and the math makes that exact.

If I insist on personally understanding everything at full depth, my multiplier has a hard cap.
Knowing the math is how I raise it.
The cap is Amdahl's Law: whatever share of the work is *me understanding and deciding* can't be compressed away, so

$$
M_{\max} \;=\; \frac{1}{p}\,,\qquad p = \text{the share of the work I must understand myself.}
$$

![The multiplier is a dial you control: maximum multiplier equals one divided by the share of work you must understand yourself; the ceiling stays near 2x while that share is large and climbs steeply as it shrinks toward 10%.](data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNzIwIDQ0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iLWFwcGxlLXN5c3RlbSwgQmxpbmtNYWNTeXN0ZW1Gb250LCAnU2Vnb2UgVUknLCBSb2JvdG8sIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI3MjAiIGhlaWdodD0iNDQwIiByeD0iMTQiIGZpbGw9IiNGQkY5RjQiLz4KICA8dGV4dCB4PSIzNjAiIHk9IjMyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE4IiBmb250LXdlaWdodD0iNTAwIiBmaWxsPSIjMkMyQzJBIj5UaGUgbXVsdGlwbGllciBpcyBhIGRpYWwgeW91IGNvbnRyb2w8L3RleHQ+CiAgPHRleHQgeD0iMzYwIiB5PSI1NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZmlsbD0iIzVGNUU1QSI+bWF4aW11bSBtdWx0aXBsaWVyID0gMSAmIzI0NzsgdGhlIHNoYXJlIG9mIHdvcmsgeW91IG11c3QgdW5kZXJzdGFuZCB5b3Vyc2VsZjwvdGV4dD4KCiAgPCEtLSBncmlkbGluZXMgLS0+CiAgPGxpbmUgeDE9IjcwIiB5MT0iMzgwIiB4Mj0iNjkwIiB5Mj0iMzgwIiBzdHJva2U9IiNCNEIyQTkiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxsaW5lIHgxPSI3MCIgeTE9IjM0Ni43IiB4Mj0iNjkwIiB5Mj0iMzQ2LjciIHN0cm9rZT0iI0U0RTFEOCIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPGxpbmUgeDE9IjcwIiB5MT0iMjgwIiB4Mj0iNjkwIiB5Mj0iMjgwIiBzdHJva2U9IiNFNEUxRDgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxsaW5lIHgxPSI3MCIgeTE9IjIxMy4zIiB4Mj0iNjkwIiB5Mj0iMjEzLjMiIHN0cm9rZT0iI0U0RTFEOCIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPGxpbmUgeDE9IjcwIiB5MT0iMTQ2LjciIHgyPSI2OTAiIHkyPSIxNDYuNyIgc3Ryb2tlPSIjRTRFMUQ4IiBzdHJva2Utd2lkdGg9IjEiLz4KICA8bGluZSB4MT0iNzAiIHkxPSI4MCIgeDI9IjY5MCIgeTI9IjgwIiBzdHJva2U9IiNFNEUxRDgiIHN0cm9rZS13aWR0aD0iMSIvPgogIDxsaW5lIHgxPSI3MCIgeTE9IjgwIiB4Mj0iNzAiIHkyPSIzODAiIHN0cm9rZT0iI0I0QjJBOSIgc3Ryb2tlLXdpZHRoPSIxIi8+CgogIDwhLS0geSB0aWNrcyAtLT4KICA8dGV4dCB4PSI2MCIgeT0iMzg0IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj4xJiMyMTU7PC90ZXh0PgogIDx0ZXh0IHg9IjYwIiB5PSIzNTAuNyIgdGV4dC1hbmNob3I9ImVuZCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+MiYjMjE1OzwvdGV4dD4KICA8dGV4dCB4PSI2MCIgeT0iMjg0IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj40JiMyMTU7PC90ZXh0PgogIDx0ZXh0IHg9IjYwIiB5PSIyMTcuMyIgdGV4dC1hbmNob3I9ImVuZCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+NiYjMjE1OzwvdGV4dD4KICA8dGV4dCB4PSI2MCIgeT0iMTUwLjciIHRleHQtYW5jaG9yPSJlbmQiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjgmIzIxNTs8L3RleHQ+CiAgPHRleHQgeD0iNjAiIHk9Ijg0IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj4xMCYjMjE1OzwvdGV4dD4KCiAgPCEtLSB4IHRpY2tzIC0tPgogIDx0ZXh0IHg9IjcwIiB5PSI0MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjYwJTwvdGV4dD4KICA8dGV4dCB4PSIxNTguNiIgeT0iNDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj41MCU8L3RleHQ+CiAgPHRleHQgeD0iMjQ3LjEiIHk9IjQwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+NDAlPC90ZXh0PgogIDx0ZXh0IHg9IjMzNS43IiB5PSI0MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjMzJTwvdGV4dD4KICA8dGV4dCB4PSI0MjQuMyIgeT0iNDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj4yNSU8L3RleHQ+CiAgPHRleHQgeD0iNTEyLjkiIHk9IjQwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+MjAlPC90ZXh0PgogIDx0ZXh0IHg9IjYwMS40IiB5PSI0MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPjE1JTwvdGV4dD4KICA8dGV4dCB4PSI2OTAiIHk9IjQwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+MTAlPC90ZXh0PgoKICA8IS0tIGF4aXMgdGl0bGVzIC0tPgogIDx0ZXh0IHg9IjIyIiB5PSIyMzAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMiIGZpbGw9IiM0NDQ0NDEiIHRyYW5zZm9ybT0icm90YXRlKC05MCAyMiAyMzApIj5tYXggbXVsdGlwbGllcjwvdGV4dD4KICA8dGV4dCB4PSIzODAiIHk9IjQyNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZmlsbD0iIzQ0NDQ0MSI+c2hhcmUgb2YgdGhlIHdvcmsgeW91IG11c3QgdW5kZXJzdGFuZCB5b3Vyc2VsZjwvdGV4dD4KCiAgPCEtLSBhcmVhIGZpbGwgdW5kZXIgY3VydmUgLS0+CiAgPHBvbHlnb24gcG9pbnRzPSI3MCwzNTYuNyAxNTguNiwzNDYuNyAyNDcuMSwzMzAgMzM1LjcsMzEzLjMgNDI0LjMsMjgwIDUxMi45LDI0Ni43IDYwMS40LDE5MCA2OTAsODAgNjkwLDM4MCA3MCwzODAiIGZpbGw9IiNEODVBMzAiIGZpbGwtb3BhY2l0eT0iMC4wOCIvPgoKICA8IS0tIGN1cnZlIC0tPgogIDxwb2x5bGluZSBwb2ludHM9IjcwLDM1Ni43IDE1OC42LDM0Ni43IDI0Ny4xLDMzMCAzMzUuNywzMTMuMyA0MjQuMywyODAgNTEyLjksMjQ2LjcgNjAxLjQsMTkwIDY5MCw4MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRDg1QTMwIiBzdHJva2Utd2lkdGg9IjIuNSIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CgogIDwhLS0gcG9pbnRzIC0tPgogIDxjaXJjbGUgY3g9IjcwIiBjeT0iMzU2LjciIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSIxNTguNiIgY3k9IjM0Ni43IiByPSI0IiBmaWxsPSIjRDg1QTMwIi8+CiAgPGNpcmNsZSBjeD0iMjQ3LjEiIGN5PSIzMzAiIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSIzMzUuNyIgY3k9IjMxMy4zIiByPSI0IiBmaWxsPSIjRDg1QTMwIi8+CiAgPGNpcmNsZSBjeD0iNDI0LjMiIGN5PSIyODAiIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSI1MTIuOSIgY3k9IjI0Ni43IiByPSI0IiBmaWxsPSIjRDg1QTMwIi8+CiAgPGNpcmNsZSBjeD0iNjAxLjQiIGN5PSIxOTAiIHI9IjQiIGZpbGw9IiNEODVBMzAiLz4KICA8Y2lyY2xlIGN4PSI2OTAiIGN5PSI4MCIgcj0iNC41IiBmaWxsPSIjOTkzQzFEIi8+CgogIDwhLS0gYW5ub3RhdGlvbnMgLS0+CiAgPHRleHQgeD0iOTIiIHk9IjM3MiIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj51bmRlcnN0YW5kIGl0IGFsbCAmIzg3NzY7IDImIzIxNTs8L3RleHQ+CiAgPHRleHQgeD0iMzAwIiB5PSIxMjAiIHRleHQtYW5jaG9yPSJzdGFydCIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjOTkzQzFEIj5sZXQgdmVyaWZpY2F0aW9uIGNhcnJ5IHRoZSBwcm9vZiAmIzgyMTI7PC90ZXh0PgogIDx0ZXh0IHg9IjMwMCIgeT0iMTM4IiB0ZXh0LWFuY2hvcj0ic3RhcnQiIGZvbnQtc2l6ZT0iMTIuNSIgZmlsbD0iIzk5M0MxRCI+YW5kIHRoZSBjZWlsaW5nIGNsaW1iczwvdGV4dD4KICA8cGF0aCBkPSJNIDU0MCAxNDAgUSA2MDAgMTUwIDY0NSAxMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzk5M0MxRCIgc3Ryb2tlLXdpZHRoPSIxLjQiLz4KICA8cGF0aCBkPSJNIDY0NSAxMTAgbCAtOSAxIGwgNSA3IHoiIGZpbGw9IiM5OTNDMUQiLz4KPC9zdmc+)

I read the curve as a map of where the leverage lives.
The share I must personally understand is *not fixed*.
Every place I let trustworthy verification carry the proof shrinks that share without lowering my assurance: a type proving a resource is released, a static pass proving no leaked handle, a property test pinning an invariant across thousands of inputs.
Moving from "I must understand half" to "I must truly understand a fifth" is the whole distance from a 2x ceiling to a 5x one.
Reading faster helps little; *needing to read less, safely* is what raises my multiplier.

For whole new systems the math is more favorable, because the baseline is an empty repo.
Measured against *nothing*, a low-stakes system I mostly understand and actually shipped is a clear gain.
That is where I accept understanding less: greenfield, reversible work that wouldn't otherwise exist.
I save deep comprehension for the point when the system earns real users and a real blast radius.
By then, verification is what lets me extend it without holding all of it in my head at once.

I think the longer-term trend makes this worth betting on.
As agent layers mature toward being trustworthy the way a compiler is (deterministic, verified, with a track record), I expect the share I have to read myself to shrink toward the spec I write and check, and the ceiling to rise well past the top of that chart.
The ceiling rises only as fast as trustworthy verification replaces personal comprehension.
That is the work I focus on, and I find it hopeful: in my view, making trust cheap is what makes larger ambitions safe to pursue.

**The creed, in its final form:**
> I can't multiply faster than I can understand, so I make understanding cheaper and put the surplus into building things that didn't exist yesterday.
