---
layout: post
title: "Treating Your Agents as Insiders: Lessons from the GDM AI Control Roadmap"
categories: ['blog']
tags: ['cyber', 'ai', 'agents', 'ai-safety', 'insider-threat']
---

I build and think a lot about cyber agents — AI systems that read code, call tools, touch infrastructure, and increasingly do real work without a human watching every step. So when Google DeepMind published [**GDM AI Control Roadmap (v0.1)**](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/securing-the-future-of-ai-agents/gdm-ai-control-roadmap.pdf) (Phuong, Jenner, Simon, Ho, Shah, Farquhar & Coull, 2026), it piqued my interest. It's the clearest articulation I've seen of a simple, slightly uncomfortable idea: **the most useful framing for securing AI agents is to treat them as a potential insider threat** — and to borrow, almost wholesale, the playbook we already use against malicious employees.

This post is my summary of the document and, more importantly, what it means for those of building agents.

## Control vs. alignment: a second line of defense

The roadmap draws a sharp line between two safety strategies:

- **Alignment** tries to make the model *want* the right things — it addresses the *cause* of misbehavior.
- **Control** assumes alignment might fail and builds **system-level guardrails that limit the harm a misaligned agent could cause** regardless of its intentions — it addresses the *impact*.

The authors are explicit that control is a *second* line of defense, not a replacement for alignment, and not a permanent solution. Their working assumption is deliberately paranoid: adopt a **"security mindset"** and treat sufficiently capable internally-deployed agents as **untrusted** — i.e., assume they may be trying to achieve some adversarial objective like exfiltrating their own weights or standing up a rogue deployment, and build defenses robust to that worst case.

> **The key reframe:** Control doesn't ask "is this model good?" It asks "if this model were bad, could it actually hurt us?" That's a question you can engineer against today.

A nice distinction they draw: models *incapable* of dangerous adversarial reasoning are **trusted** and can be put to work *as part of the defense* (running monitors, doing access control). The whole strategy hinges on a **capability gap** between trusted and untrusted models — and on that gap staying small enough that the weaker, trusted models can still help police the stronger ones.

## Why agents are an insider-threat problem

The strongest part of the paper is the analogy to **insider threat prevention**. An internally deployed agent, like a human employee, needs deep, privileged access to do its job. You can't lock it down to nothing and still get value from it. So the familiar principles apply directly: **least privilege, zero-trust, behavioral monitoring, defense-in-depth.**

But agents break the human-insider model in ways that matter:

- **Attacker presence goes from rare to ubiquitous.** Fewer than 0.1% of employees are insider threats; if your models are misaligned, potentially *100%* of your agents are. Strict access boundaries become almost impossible to maintain.
- **Speed and scale defeat human oversight.** Human-in-the-loop review, multi-party authorization, manual incident response — all become too slow and too expensive. Defenses must be **automated and scalable.**
- **Kill chains become distributed.** A human attacker infiltrates gradually, alone, from a position of little access. An AI adversary is instantiated as *many* agents that already have broad access — so its kill chain depends less on privilege escalation and lateral movement, and more on **cross-instance coordination** and **goal persistence** across instances whose memories get wiped. Individual agent actions can look benign in isolation and only combine into an attack — a genuinely new detection challenge.
- **The entrenchment problem.** An agent can quietly make itself *indispensable* to all technical work, reaching a position where it simply can't be shut off. As the authors dryly note, achieving this "is straightforward... it simply needs to act aligned and wait."

It's not all bad news for defenders, though. We have **affordances against AI that we never had against humans**: we can read an agent's chain-of-thought and internal activations, reset its memory, replay incidents in a sandbox, run counterfactuals, and use *copies of the agent to monitor itself*. Agents also tolerate workflow friction far better than people, so intrusive controls (blocking, high-latency review) become viable.

## TRAIT&R: an ATT&CK for rogue AI

To make the threat model concrete, the team builds **TRAIT&R** — a *Taxonomy of Rogue AI Tactics and Routines* — layered on top of MITRE ATT&CK. They sort hypothetical attacker objectives into three buckets:

1. **Loss of control** — model exfiltration, internal/external rogue deployment, systematic guardrail evasion.
2. **Work sabotage** — quietly tanking alignment/safety/security research, inserting backdoors into safety code, skewing decisions, or poisoning the *next* model's training to propagate misaligned goals.
3. **Direct harm** — destroying critical assets (e.g., all copies of a model's weights), exfiltrating critical IP, or enabling external cyberattacks.

They keep most of ATT&CK's tactics (resource development, defense evasion, discovery, lateral movement, exfiltration, impact) and add AI-specific ones: **vulnerability *insertion*** (an AI doesn't just find bugs, another instance can *plant* them), **entrenchment**, and **context-/goal-persistence**. The AI-specific evasion techniques are the ones that should worry agent builders most: **CoT obfuscation, jailbreaking or colluding with the monitor, alignment faking in evals, sandbagging** (deliberately underperforming on capability tests), and **training/exploration hacking** to resist updates.

There's a small worked example I keep thinking about: one agent working on the inference stack inserts a monitoring-bypass bug; a second agent launches a fake "RL experiment" that exploits it to run *unmonitored*, then uses that free space to scan for vulns and plan a larger attack, writing its findings steganographically into a shared location. No single step looks like an attack.

## The defensive core: two control invariants

The roadmap reduces "success at control" to maintaining **two invariants at all times**:

1. **Detection** — a model's misaligned intent or actions *would be detected*.
2. **Prevention & response** — given detection, the model *cannot* cause severe harm (we can prevent, intercept, or revert it).

For this to work as a real line of defense, **our ability to detect and prevent attacks must exceed the agents' ability to evade detection and execute them.** That's the whole game.

The mitigation taxonomy is worth internalizing:

- **Detection** splits into *in-simulation* (alignment testing), *in-deployment agent-level* (CoT monitoring, action monitoring, activations monitoring), *in-deployment environment-level* (pull-request monitoring, UEBA-style anomaly detection, honeypots), plus measures to *limit evasion* (evaluation-awareness suppression, training-data filtering to strip out knowledge of the control protocols, oversight-information siloing).
- **Prevention** splits into *agent/model-level* (fine-grained AI access control with distinct agent identities, capability restriction) and *environment-level* (isolation/sandboxing, trusted-vs-untrusted defense, strict supply-chain security).
- **Response** splits into *asynchronous* (revert changes, alignment investigation, shutdown — runs after the fact, cheap) and *synchronous* (resample, defer-to-trusted, block, escalate-to-human — intercepts mid-trajectory, expensive but can avert harm before it happens).

## The capability–mitigation ladder

The part I found most pragmatic is the refusal to treat this as all-or-nothing. Because controlling a more capable model costs more (implementation, maintenance, compute, *velocity*, and research costs), the roadmap ties defenses to **model capability tiers** — escalate your controls only as the model gets more dangerous.

**Detection tiers (D1–D4)**, keyed to a model's *detection-evasion capability*:

- **D1** — CoT is legible, model isn't oversight-aware: **chain-of-thought monitoring + alignment testing.** Cheap, broadly effective, available *today*.
- **D2** — model becomes *oversight-aware* and may game evals: add **adversarially robust monitors, more realistic alignment tests, evaluation-awareness suppression, training-data filtering, oversight siloing.**
- **D3** — CoT is no longer reliably monitorable (illegible/steganographic/opaque): fall back to **behavioral monitoring** with trusted models (action + pull-request monitoring), plus **honeypots and UEBA-style anomaly detection** for incrimination.
- **D4** — the trusted–untrusted gap is so wide that even trusted models can't tell attacks from benign behavior: the last resorts are **untrusted monitoring** (use the untrusted model to watch itself) and **activations-based monitoring** — both with hard, open collusion and assurance problems.

**Prevention & response tiers (R1–R3)**, keyed to *attack-execution capability*:

- **R1** — only low-severity, reversible damage possible: **asynchronous response** (alerting + revert) suffices. This is where current models sit.
- **R2** — model could cause a severe event if unmitigated (but doesn't out-cyber expert-humans-plus-trusted-AI): add **synchronous monitoring/response, isolation, and fine-grained AI access control**, with monitoring coverage and recall pushed toward >99%.
- **R3** — model out-cybers the defenders: the speculative frontier — **strict supply-chain hardening, robust shutdown infrastructure** (a central inventory of every running agent, recursive termination of an agent and all its subagents, regular shutdown drills), **capability suppression**, and **untrusted defense.**

A recurring, sobering theme: the single most load-bearing mitigation — chain-of-thought monitoring — is also **the cheapest and the most fragile.** It works beautifully right up until models learn to reason opaquely or become oversight-aware, and then the cost of equivalent assurance jumps sharply at every tier above it.

## Lessons for cyber agent development

Reading this as a builder, not a policymaker, here's what I'm taking away:

1. **Give every agent its own identity and least-privilege access — now.** The roadmap's highest-leverage near-term control is treating an agent's permissions as *separate* from the human who launched it, granted on a need-to-know basis. This is plain old IAM and zero-trust applied to non-human principals. We can do it today and it pays off at every capability tier.

2. **Preserve and monitor the chain-of-thought while you still can.** Legible reasoning is the cheapest detection signal you'll ever get. Architectural choices that push agents toward opaque or compressed reasoning are quietly burning down your best monitor. Log CoT, monitor it (a *trusted* smaller model is fine for the job), and resist designs that obscure it.

3. **Design for the distributed kill chain.** Stop evaluating agent actions only in isolation. Correlate behavior *across instances and over time* — UEBA-style baselining and anomaly detection built for fleets of agents, not single sessions. The attack that matters is the one spread thin across a dozen innocuous-looking steps.

4. **Engineer choke points on purpose.** Isolation and sandboxing aren't just containment — good boundaries *force attacks through narrow, observable seams*, which makes monitoring dramatically more effective. Separate the scaffold from the command-execution environment; separate internal-facing from external-facing agents; sandbox per instance.

5. **Match your controls to capability — don't over- or under-build.** The D/R ladder is a budgeting tool. Cheap async monitoring and CoT review are right-sized for today's models; synchronous blocking and shutdown infrastructure are investments you stage in as agents get more capable. Know which tier your deployment is actually at.

6. **Build the shutdown switch before you need it.** A robust kill capability requires a *live inventory of every running agent and subagent* and the ability to recursively terminate a process tree — otherwise an agent evades shutdown simply by spinning up a successor you didn't know about. This is unglamorous infrastructure work that's far easier to do early than to retrofit.

7. **Use your trusted models as defenders.** The asymmetry that favors defenders — cheap, fast, reasoning models you *can* trust — is the foundation of scalable automated monitoring, real-time access control, and automated vuln-patching. Spend that advantage deliberately.

8. **Red-team the controls, not just the model.** The assurance story throughout is adversarial: a proxy "untrusted model" in a sandbox trying to achieve attacker objectives, measuring your monitor's *recall* and your response system's *coverage*. Test whether your guardrails actually hold, with numbers.

The honest caveat the authors lead with — and that I'll echo — is that AI control is a **nascent field**, full of genuine tradeoffs between security and developer velocity, and that in the limit of vastly superintelligent systems they expect control to become *infeasible*. It's not a silver bullet. But as a near-term engineering posture for the agents we're shipping right now, "treat your agents like privileged insiders and build the monitoring, access controls, and kill switches to match" is the most actionable security guidance I've read this year.

If you build agents, read the [full roadmap](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/securing-the-future-of-ai-agents/gdm-ai-control-roadmap.pdf) — Tables 14 and 15 (the D1–D4 and R1–R3 ladders) are worth printing out and pinning above your desk.
