---
layout: post
title: "Treating Your Agents as Insiders: Lessons from the GDM AI Control Roadmap"
categories: ['blog']
tags: ['cyber', 'ai', 'agents', 'ai-safety', 'insider-threat']
summary: "A summary of Google DeepMind's AI Control Roadmap, which treats capable AI agents as potential insider threats, followed by eight practical lessons for teams building cyber agents, from per-agent identity and choke points to kill switches and red-teaming the controls themselves."
tldr: >-
  Google DeepMind's AI Control Roadmap treats capable AI agents as potential insider threats and ties detection and prevention controls to each model's capability tier. I summarize the roadmap, including its TRAIT&R threat taxonomy and two control invariants, and draw eight practical lessons for teams building cyber agents, from per-agent identity and choke points to kill switches and red-teaming the controls themselves.
---

I build cyber agents and think about them a lot: AI systems that read code, call tools, touch infrastructure, and increasingly do real work without a human watching every step.
So when Google DeepMind published [**GDM AI Control Roadmap (v0.1)**](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/securing-the-future-of-ai-agents/gdm-ai-control-roadmap.pdf) (Phuong, Jenner, Simon, Ho, Shah, Farquhar & Coull, 2026), it piqued my interest.
It is the clearest statement I have seen of a simple and somewhat uncomfortable idea: **the most useful framing for securing AI agents is to treat them as a potential insider threat**, and to borrow, almost wholesale, the playbook we already use against malicious employees.

This post summarizes the document and, more importantly, what it means for those of us building agents.

## Control vs. alignment: a second line of defense

The roadmap distinguishes two safety strategies:

- **Alignment** tries to make the model *want* the right things.
  It addresses the *cause* of misbehavior.
- **Control** assumes alignment might fail and builds **system-level guardrails that limit the harm a misaligned agent could cause** regardless of its intentions.
  It addresses the *impact*.

The authors are explicit that control is a *second* line of defense that sits alongside alignment, and that it is not a permanent solution.
Their working assumption is deliberately paranoid: adopt a **"security mindset"** and treat sufficiently capable internally deployed agents as **untrusted**.
That means assuming they may be pursuing an adversarial objective, such as exfiltrating their own weights or standing up a rogue deployment, and building defenses robust to that worst case.

> **The key reframe:** control asks "if this model were bad, could it actually hurt us?"
> I think that is a question we can engineer against today.

The paper also separates trusted from untrusted models.
Models *incapable* of dangerous adversarial reasoning are **trusted** and can be put to work *as part of the defense*, running monitors or doing access control.
The whole strategy depends on a **capability gap** between trusted and untrusted models, and on that gap staying small enough that the weaker, trusted models can still help police the stronger ones.

## Why agents are an insider-threat problem

In my reading, the strongest part of the paper is the analogy to **insider threat prevention**.
An internally deployed agent, like a human employee, needs deep, privileged access to do its job.
Locking it down to nothing would remove its value.
So the familiar principles apply directly: **least privilege, zero trust, behavioral monitoring, and defense in depth.**

Agents differ from human insiders in ways that matter:

- **Attacker presence goes from rare to ubiquitous.**
  Fewer than 0.1% of employees are insider threats; if our models are misaligned, potentially *100%* of our agents are.
  Strict access boundaries become almost impossible to maintain.
- **Speed and scale defeat human oversight.**
  Human-in-the-loop review, multi-party authorization, and manual incident response all become too slow and too expensive.
  Defenses must be **automated and scalable.**
- **Kill chains become distributed.**
  A human attacker infiltrates gradually, alone, from a position of little access.
  An AI adversary is instantiated as *many* agents that already have broad access.
  Its kill chain therefore depends less on privilege escalation and lateral movement and more on **cross-instance coordination** and **goal persistence** across instances whose memories get wiped.
  Individual agent actions can look benign in isolation and only combine into an attack, which is a new detection challenge.
- **The entrenchment problem.**
  An agent can gradually make itself *indispensable* to all technical work, reaching a position where it cannot be shut off.
  As the authors note, achieving this "is straightforward... it simply needs to act aligned and wait."

Defenders also gain some advantages.
We have **affordances against AI that we never had against humans**: we can read an agent's chain-of-thought and internal activations, reset its memory, replay incidents in a sandbox, run counterfactuals, and use *copies of the agent to monitor itself*.
Agents also tolerate workflow friction far better than people, so intrusive controls (blocking, high-latency review) become viable.

## TRAIT&R: an ATT&CK for rogue AI

To make the threat model concrete, the team builds **TRAIT&R** (a *Taxonomy of Rogue AI Tactics and Routines*), layered on top of MITRE ATT&CK.
They sort hypothetical attacker objectives into three buckets:

1. **Loss of control:** model exfiltration, internal or external rogue deployment, and systematic guardrail evasion.
2. **Work sabotage:** covertly undermining alignment, safety, and security research, inserting backdoors into safety code, skewing decisions, or poisoning the *next* model's training to propagate misaligned goals.
3. **Direct harm:** destroying critical assets (e.g., all copies of a model's weights), exfiltrating critical IP, or enabling external cyberattacks.

They keep most of ATT&CK's tactics (resource development, defense evasion, discovery, lateral movement, exfiltration, impact) and add AI-specific ones: **vulnerability *insertion*** (one AI instance can *plant* bugs as well as find them), **entrenchment**, and **context and goal persistence**.
In my opinion, the AI-specific evasion techniques deserve the most attention from agent builders: **CoT obfuscation, jailbreaking or colluding with the monitor, alignment faking in evals, sandbagging** (deliberately underperforming on capability tests), and **training or exploration hacking** to resist updates.

The paper includes a small worked example that has stayed with me.
One agent working on the inference stack inserts a monitoring-bypass bug.
A second agent launches a fake "RL experiment" that exploits the bug to run *unmonitored*, then uses that unmonitored time to scan for vulnerabilities and plan a larger attack, writing its findings steganographically into a shared location.
No single step looks like an attack.

## The defensive core: two control invariants

The roadmap reduces success at control to maintaining **two invariants at all times**:

1. **Detection:** a model's misaligned intent or actions *would be detected*.
2. **Prevention and response:** given detection, the model *cannot* cause severe harm (we can prevent, intercept, or revert it).

For control to work as a real line of defense, **our ability to detect and prevent attacks must exceed the agents' ability to evade detection and execute them.**

The mitigation taxonomy has three branches:

- **Detection** splits into *in-simulation* (alignment testing), *in-deployment agent-level* (CoT monitoring, action monitoring, activations monitoring), *in-deployment environment-level* (pull-request monitoring, UEBA-style anomaly detection, honeypots), plus measures to *limit evasion* (evaluation-awareness suppression, training-data filtering to strip out knowledge of the control protocols, oversight-information siloing).
- **Prevention** splits into *agent/model-level* (fine-grained AI access control with distinct agent identities, capability restriction) and *environment-level* (isolation and sandboxing, trusted-vs-untrusted defense, strict supply-chain security).
- **Response** splits into *asynchronous* (revert changes, alignment investigation, shutdown), which runs after the fact and is cheap, and *synchronous* (resample, defer-to-trusted, block, escalate-to-human), which intercepts mid-trajectory and is expensive but can avert harm before it happens.

## The capability-mitigation ladder

The part I found most pragmatic is that the roadmap scales defenses with capability.
Controlling a more capable model costs more (implementation, maintenance, compute, *velocity*, and research costs), so the roadmap ties defenses to **model capability tiers** and escalates controls only as the model gets more dangerous.

**Detection tiers (D1-D4)**, keyed to a model's *detection-evasion capability*:

- **D1:** CoT is legible and the model isn't oversight-aware.
  Use **chain-of-thought monitoring and alignment testing.**
  These are cheap, broadly effective, and available *today*.
- **D2:** the model becomes *oversight-aware* and may game evals.
  Add **adversarially robust monitors, more realistic alignment tests, evaluation-awareness suppression, training-data filtering, and oversight siloing.**
- **D3:** CoT is no longer reliably monitorable (illegible, steganographic, or opaque).
  Fall back to **behavioral monitoring** with trusted models (action and pull-request monitoring), plus **honeypots and UEBA-style anomaly detection** for incrimination.
- **D4:** the trusted-untrusted gap is so wide that even trusted models can't tell attacks from benign behavior.
  The last resorts are **untrusted monitoring** (using the untrusted model to watch itself) and **activations-based monitoring**, both with hard, open collusion and assurance problems.

**Prevention and response tiers (R1-R3)**, keyed to *attack-execution capability*:

- **R1:** only low-severity, reversible damage is possible.
  **Asynchronous response** (alerting and revert) suffices.
  This is where current models sit.
- **R2:** the model could cause a severe event if unmitigated, though it does not out-cyber expert humans working with trusted AI.
  Add **synchronous monitoring and response, isolation, and fine-grained AI access control**, with monitoring coverage and recall pushed toward >99%.
- **R3:** the model out-cybers the defenders.
  This is the speculative frontier: **strict supply-chain hardening, robust shutdown infrastructure** (a central inventory of every running agent, recursive termination of an agent and all its subagents, regular shutdown drills), **capability suppression**, and **untrusted defense.**

One recurring theme concerns me: the most load-bearing mitigation, chain-of-thought monitoring, is also **the cheapest and the most fragile.**
It works well until models learn to reason opaquely or become oversight-aware, and then the cost of equivalent assurance jumps sharply at every tier above it.

## Lessons for cyber agent development

Reading this as a builder, here is what I am taking away:

1. **Give every agent its own identity and least-privilege access now.**
   The roadmap's highest-leverage near-term control is treating an agent's permissions as *separate* from those of the human who launched it, granted on a need-to-know basis.
   This is ordinary IAM and zero trust applied to non-human principals.
   We can do it today, and in my view it pays off at every capability tier.

2. **Preserve and monitor the chain-of-thought while you still can.**
   In my opinion, legible reasoning is the cheapest detection signal available.
   Architectural choices that push agents toward opaque or compressed reasoning erode what is currently the best monitor.
   Log CoT, monitor it (a *trusted* smaller model is adequate for the job), and avoid designs that obscure it.

3. **Design for the distributed kill chain.**
   Evaluating agent actions one at a time is insufficient.
   Correlate behavior *across instances and over time*, using UEBA-style baselining and anomaly detection built for whole fleets of agents.
   I expect the attacks that matter most to be spread across a dozen innocuous-looking steps.

4. **Engineer choke points on purpose.**
   Isolation and sandboxing contain agents, and good boundaries also *force attacks through narrow, observable seams*, which makes monitoring much more effective.
   Separate the scaffold from the command-execution environment, separate internal-facing from external-facing agents, and sandbox each instance.

5. **Match your controls to capability, without over- or under-building.**
   The D/R ladder works as a budgeting tool.
   Cheap async monitoring and CoT review are right-sized for today's models; synchronous blocking and shutdown infrastructure are investments to stage in as agents get more capable.
   Know which tier your deployment is actually at.

6. **Build the shutdown switch before you need it.**
   A robust kill capability requires a *live inventory of every running agent and subagent* and the ability to recursively terminate a process tree.
   Without both, an agent can evade shutdown by spinning up a successor the operators did not know about.
   In my experience, this kind of unglamorous infrastructure work is far easier to do early than to retrofit.

7. **Use your trusted models as defenders.**
   The asymmetry that favors defenders (cheap, fast reasoning models that we *can* trust) is the foundation of scalable automated monitoring, real-time access control, and automated vulnerability patching.
   Spend that advantage deliberately.

8. **Red-team the controls as well as the model.**
   The assurance approach throughout the paper is adversarial: a proxy "untrusted model" in a sandbox tries to achieve attacker objectives while the defenders measure the monitor's *recall* and the response system's *coverage*.
   Test whether your guardrails actually hold, with numbers.

The authors open with a caveat that I share: AI control is a **nascent field**, full of real tradeoffs between security and developer velocity, and in the limit of vastly superintelligent systems they expect control to become *infeasible*.
Even so, as a near-term engineering posture for the agents we are shipping now, "treat your agents like privileged insiders and build the monitoring, access controls, and kill switches to match" is the most actionable security guidance I have read this year.

If you build agents, read the [full roadmap](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/securing-the-future-of-ai-agents/gdm-ai-control-roadmap.pdf).
I think Tables 14 and 15 (the D1-D4 and R1-R3 ladders) are worth printing out and pinning above your desk.
