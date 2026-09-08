---
layout: post
title: "MAVLink Has No Idea Who You Are: Drone Autonomy on an Unauthenticated Link (Part 1)"
categories: ['blog']
tags: ['cyber', 'drones', 'mavlink', 'ardupilot', 'gazebo', 'ai', 'simulation', 'series']
---

Every drone fleet I have looked at from a security angle has the same uncomfortable property: the protocol that flies the aircraft was designed for a world where the worst thing that happened to a packet was radio noise.
[MAVLink](https://mavlink.io/en/), the lingua franca of ArduPilot, PX4, and most commercial companion computers, ships by default with **no authentication, no encryption, and no integrity protection** beyond a CRC that exists to catch corrupted bytes rather than a deliberate forgery.
Anyone who can reach the telemetry radio can ask the vehicle for its parameters.
Anyone who can reach it can tell the vehicle to go somewhere else.

None of that is a new discovery.
MAVLink's trust model has been picked apart in academic papers and conference talks for the better part of a decade, and both ArduPilot and PX4 document the gaps themselves.
What I wanted was not another finding but a bench: a reproducible place to *measure* the gaps rather than cite them, and to see what they look like once an autonomy stack is the thing on the other end of the link.

Because that is the part that has changed.
The consumer of drone telemetry is increasingly not a human with a joystick.
It is a software stack of mission planners, vision pipelines, and increasingly LLM-based decision layers, consuming telemetry and emitting commands.
Every one of those systems inherits MAVLink's trust model whether its designers thought about it or not.
An attacker does not need to defeat the autonomy. They only need to lie to it.

This post is part 1 of a short series: the build log for the lab, and the security notes I took while building it.
Part 2 moves the same traffic onto an isolated container network, where a MAVLink link behaves like a link, with distinct endpoints, real packet boundaries, and deliberate damage.

## The bug that framed the whole project

An hour into bringing up the physics simulator, I had a simulation that looked alive and was doing nothing.
ArduPilot's SITL binary emitted heartbeats, the Gazebo plugin reported a connected peer, and the EKF never fused a thing.

The root cause was mundane.
**Two `arducopter` processes were alive at once**, because a `sim_vehicle.py` launch had orphaned its child.
Both were talking to the physics plugin's single-client lockstep with clashing frame counters, and the plugin latched onto the wrong peer.

The security translation is what kept me on this project.
This ecosystem has no concept of endpoint identity.
Two controllers fighting over one vehicle is a *normal* failure mode, it is indistinguishable from an attack, and nothing anywhere in the stack objects to it.
If you have ever wondered what "the ground station is dual-homed" or "a second telemetry radio came online" looks like on the wire, it looks exactly like my bug looked.
The autopilot cannot tell the difference, and neither can anything downstream of it.

## The second thing worth knowing before the build log

SITL refuses to stream most telemetry until something heartbeats at it as a ground station.
That sounds like a gate. It is not.

A MAVLink 2 `HEARTBEAT` is 21 bytes: a 10-byte header, a 9-byte payload, and a 2-byte CRC.
No key, no handshake, no nonce, nothing that varies per sender.
Any process that can emit those 21 cleartext bytes unlocks the richest data path on the vehicle, which includes attitude, position, servo outputs, EKF status, and the command channel that arms the motors.

So the vehicle does gate its telemetry, and the credential for that gate is a constant that anyone can type.
There is no pairing, no allow list, and no audit record on the vehicle side that it ever happened.

## Why simulate instead of buying hardware

Cost is the obvious reason. A bricked quadcopter is expensive and a bricked process is a Ctrl-C.

Reproducibility matters more.
A SITL instance pinned to a Git commit behaves identically tomorrow, which is the only condition under which security measurements mean anything.

Then there is legality.
Fuzzing a radio link over the air is a fast way to meet your regulator.
Doing the same work inside an isolated network is an ordinary afternoon.

The tradeoff is fidelity, and it is real.
Bootloaders, UARTs, radio firmware, and hardware timing are all things SITL cannot show, and I keep a separate hardware bench list for exactly that reason.

## The lab

Everything on loopback, every process tracked by an exact PID, every port with exactly one owner:

- **ArduPilot SITL** (`arducopter` at `Copter-4.7.0`) as the autopilot under test
- **Gazebo Harmonic** as the 3D physics world, via the official `ardupilot_gazebo` plugin
- **[MAVIO](https://github.com/jaggedmountain/mavio)** as the MAVLink client, recorder, and Foxglove bridge
- **Foxglove** for telemetry, map, and 3D visualization
- A **MAVProxy** router owning the SITL-facing link on UDP 14560 and forwarding to the tooling on 14550 and a dedicated ground-station port on 14551

The ground rule from the start: nothing binds `0.0.0.0`.
A lab that exposes an unauthenticated drone-control protocol to the local network has stopped being a lab.

That rule turned out to matter immediately, because **SITL's default does not follow it**.
Left alone, `arducopter`'s serial0 is `tcp:5760:wait`, a listener on all interfaces.
The setup documented in most wikis quietly exposes an unauthenticated vehicle-command socket to whatever network the host is sitting on.
My lab overrides it to a loopback UDP client. On a corporate network the default is a finding worth writing up.
Worth confirming against whichever version you are running, since this is exactly the sort of default that changes quietly between releases.

## The workbench: MAVIO

One tool runs on my side of the wire for the whole lab.
[MAVIO](https://github.com/jaggedmountain/mavio) is an async Python MAVLink client that is simultaneously a diagnostics CLI and an embeddable library, with the same engine under both:

```bash
mavio console <url>             # interactive REPL (the default)
mavio stream  <url>             # decoded frames to stdout, then exit
mavio probe   <url>             # what is this board?
mavio ftp     <url> ls|get|put  # read/write the vehicle's filesystem
mavio convert <capture> [out]   # capture -> MCAP for Foxglove
mavio bridge  <url>             # live link -> Foxglove websocket
mavio flash   info|upload       # identify/flash a board via its bootloader
```

A security review of a protocol is mostly an honest description of its normal use, so here is what each verb does and what each one hands an attacker.

**`probe` is unauthenticated host identification.**
Point it at an endpoint and it answers with firmware version, git hash, sensor inventory, capability bitmaps, power rails, and mounted filesystems.
That is the entire reconnaissance phase of a drone compromise in one command, with no handshake, no credential, and no consent record on the vehicle side:

```
link       udp://127.0.0.1:14551
system     1:1    QUADROTOR / ArduPilot   MAVLink 2   STANDBY, disarmed
firmware   ArduPilot 4.7.0             git 1511f271
sensors    21 present · 19 enabled · 19 healthy
capability MISSION_INT COMMAND_INT FTP SET_ATTITUDE_TARGET TERRAIN …
```

That reading is from the full stack with Gazebo attached.
Bare SITL with no physics backend reports `19 present · 15 enabled · 15 healthy`, since the simulated sensors the plugin provides are simply absent.
The delta is a useful reminder that the probe describes a configuration and not a model of aircraft.

**`stream` makes the wire greppable and recordable.**
`stream --log sim.tlog` records post-filter traffic, `stream file://sim.tlog` replays it later with no vehicle attached, and `convert sim.tlog` turns it into MCAP for Foxglove with original timestamps preserved.
The captured link is functionally the whole link, which means anyone who records telemetry keeps a permanent, replayable transcript of the flight.
Whether that transcript is also a working *control* replay depends on the vehicle accepting it, which unsigned MAVLink will and signed MAVLink is specifically designed to refuse.

**`console` is where read-only ends.**
The console's `rate` command issues `MAV_CMD_SET_MESSAGE_INTERVAL`, and the `COMMAND_ACK cmd=511` comes back to prove it.
`param SYSID_THISMAV` reads the config and `param <tag> <value>` writes it.
`send <msg>` builds arbitrary frames.
`ftp ls @SYS/` returns the autopilot's live introspection filesystem, including `tasks.txt`, `threads.txt`, `memory.txt`, `uarts.txt`, and `crash_dump.bin`, and `ftp get` pulls them over the link.
Unauthenticated read of a flight controller's running task list, thread list, serial port configuration, heap statistics, and crash dumps is a documented feature of the protocol rather than an exploit.
The console is excellent for bring-up and it is a complete takeover kit for anyone in RF range of a real aircraft.

**`ftp put` writes.**
Firmware update over MAVFTP is board and configuration dependent rather than universal, so I am not going to claim the write channel is a turnkey firmware implant.
An unauthenticated write path into the vehicle's filesystem is a serious finding on its own terms.

**`bridge` pushes the live link to Foxglove** over a loopback websocket while recording the same traffic to MCAP.
Verified channels include the raw MAVLink firehose at roughly 30 message types, plus synthesized `pose`, `tf`, `odom`, and `location`:

![Foxglove rendering the live MAVLink link](/images/drone-cyber/foxglove-live-link.png)

**`flash` talks to a bootloader rather than to MAVLink**, which makes it the one verb SITL cannot exercise.
SITL skips precisely the parts of a real vehicle that attacks like most, so `flash` stays on the hardware bench list.

## The threat model

MAVLink was born in 2009 as a telemetry protocol for a trusted party line: one autopilot, one ground station, one hobbyist, and a threat model of RF noise.
Its defaults never grew out of that.
On a standard MAVLink 2 link today:

**Passive reach buys complete reconnaissance.**
Identity, firmware version, git hash, board IDs, capabilities, the full parameter set, every waypoint of the loaded mission, and live position, attitude and health, continuously.
The parameter set alone is the interesting part, and I will come back to it.

**Active reach buys the aircraft.**
Parameter writes, mission replacement, mode changes, arm and disarm, takeoff, landing and kill commands, plus the filesystem access above.
The protocol does not distinguish the owner's ground station from whoever is loudest on 433 MHz.

**The protocol's own defense is MAVLink 2 signing**, and it is worth being precise about what it is.
Each frame carries a 13-byte trailer: a 1-byte link ID, a 6-byte timestamp, and a 6-byte truncated HMAC-SHA256 over a shared 32-byte secret.
It authenticates frames and it is genuinely useful, particularly against the replay case above, where the timestamp window is the whole point.
It also does not encrypt anything, it distributes one symmetric key by hand, it says nothing about identity or authorization beyond "holder of the key," and in every fleet I have looked at it was switched off.

Signing is not the only thing available, and I want to be fair about that.
SiK radios support AES-128 link encryption.
LTE and WiFi companion links can be tunneled over WireGuard or DTLS.
ArduPilot has signed firmware and `SecureCommand` work for the bootloader path.
Each of those defends one layer, none of them gives MAVLink a concept of *who is talking*, and the composition is left entirely to the integrator.
That gap is the subject of part 2.

## What the parameter stream gives away

The moment a client behaves like a ground station, the vehicle volunteers its **entire parameter set**.
On this stock copter that is 1,370 parameters, streamed at roughly 10 Hz, so about 2.3 minutes for a full dump on a default configuration.

Those parameters are a reconnaissance goldmine: failsafe thresholds, geofence geometry, RC channel mappings, companion-computer routing, serial port assignments, and arming checks.
An attacker who reads them knows where the geofence is before deciding where to push the aircraft, and knows which failsafe will fire before triggering it.

MAVLink has no concept of a read-only guest.
The same link that streams attitude also accepts parameter writes, mission uploads, and arm and disarm commands.
Nothing in the protocol distinguishes my diagnostics tool from an attacker's implant, because there is no field in which that distinction could be expressed.

## The first flight

With the link healthy, a small pymavlink ground-station client on its own dedicated port issued the standard sequence: GUIDED mode, arm, takeoff to 5 m.
The virtual airframe climbed to 5.05 m and settled to a steady 5.00 m hover, streaming into Foxglove while the bridge recorded every frame to MCAP.
A scripted LAND set it down a minute later with auto-disarm.

The commands that armed the motors and lifted the aircraft were ordinary unsigned MAVLink `command_long` frames from a process any user on the host could start.
Nothing authenticated them.
The protocol's answer to "who are you, and may you fly this aircraft" is silence followed immediately by takeoff.

Getting there was instructive in a smaller way too.
`MAV_CMD_NAV_TAKEOFF` in LAND or STABILIZE mode fails with a plain `MAV_RESULT_FAILED`, which means the mode machine is part of the attack surface and a ground station that does not watch `COMMAND_ACK` is flying blind.

## Moving the world

For the acceptance test that a controlled simulator action changes telemetry, I called Gazebo's `set_pose` service and slid the airframe 35 m sideways.
The autopilot reported a new GPS position through the simulated NavSat:

```
before:  lat=-353633248  lon=1491657330
after:   lat=-353633248  lon=1491661186   # +35.0 m, exactly as commanded
```

The arithmetic checks out: 0.0003856 degrees of longitude at this latitude is 111320 × cos(35.363°) × 0.0003856, which is 35.0 m.

I want to be careful about what this does and does not demonstrate, because it is easy to oversell.
`set_pose` moves Gazebo's **ground truth**, so the simulated GPS and the simulated inertial sensors move together and stay consistent with each other.
The estimator had nothing inconsistent to detect, and a well-behaved EKF handed a self-consistent world is supposed to follow it.
This is the simulator working correctly rather than an estimator being deceived.

What the test actually proves is that the injection path is wired up end to end: an external process can change what the autopilot believes about the world, and the change propagates through the EKF into position reports, mission logic, and everything downstream.
The interesting experiment is the next one, where GPS and inertial are made to *disagree*, and the measurement to publish is `EKF_STATUS_REPORT` innovations and GPS glitch status across the injection.
That is a part 2 measurement and I am not going to claim its result in advance.

The axiom underneath is still the right one.
Whoever controls sensor truth controls every decision made downstream of it: the estimator, the geofence, the mission logic, and any autonomy bolted on top.
My follow-up work on this bench is about what happens when "physics" is an attacker-controlled JSON socket.

## Reading our own traffic

A loopback `tcpdump` across the lab ports during a second full flight, takeoff through a 25 s hover to land and disarm, produced **739 k packets and 199 MB in 310 s**.
Almost all of that is the Gazebo to SITL JSON physics channel, which is a useful reminder that even one drone is several protocols talking at once.
Filtering to just the three MAVLink segments shrinks the story to 98 k packets and 7.5 MB:

```
sitl->mavproxy       32609 packets  105 pkt/s  ATTITUDE=1240 GLOBAL_POSITION_INT=1240 VFR_HUD=1240 SYS_STATUS=1240 AHRS=1240 …
mavproxy->mavio      32609 packets  105 pkt/s  (byte-identical mirror)
mavproxy->gcs-port   32609 packets  105 pkt/s  (byte-identical mirror)
upstream commands    645 packets    HEARTBEAT=620  REQUEST_DATA_STREAM=21  SET_MODE=2  COMMAND_LONG=2
```

Two readings are worth writing down.

**The whole mission is visible and signed by nobody.**
`SET_MODE` twice, to GUIDED and then to LAND, and `COMMAND_LONG` twice, to arm and to take off, are plainly readable in the capture with message ID, ordering, and parameters intact.
No key exchange, no handshake, no per-command authorization.
Against an unsigned link that capture is a replay recipe.

**Broadcast redundancy multiplies exposure.**
MAVProxy forwards the entire firehose verbatim to every attached consumer at about 105 packets per second each.
Every additional listener is free, and every additional listener is an exfiltration channel the autopilot never accounts for.
On a radio link that is invisible. On a shared network segment it is worse than invisible.

One correction to the advice I would have given before running this.
Wireshark does not dissect these frames out of the box, because its MAVLink dissector is not registered on the ports this lab uses.
The capture opens as plain UDP with an undissected payload, which is exactly what the screenshot below shows.
The fix is **Decode As… → MAVLink** on UDP 14550, 14551 and 14560, after which `mavlink` works as a display filter and `udp.port == 14560` drills into a single segment:

![Wireshark showing the lab MAVLink capture as undissected UDP](/images/drone-cyber/wireshark-mavlink-pcap.png)

### The honest limit of a loopback capture

Before the next part, the caveat that governs it: one host means no link layer, no distinct endpoint identities, and no impairment.
Everything above is a single machine talking to itself, and that destroys most of what network analysis is for.

I uploaded the capture to a fantastic hosted analysis product, [Teleseer](go.teleseer.com), to get a second opinion.
It parsed the traffic correctly, resolved the ports, and accounted for all 7.5 MB of UDP:

![Teleseer's packet view of the same capture](/images/drone-cyber/teleseer-packets.png)

Then it reported what a loopback capture actually contains, which is one host, `127.0.0.1`, "Unknown Hostname," no MAC available:

![Teleseer's host inventory: a single loopback host](/images/drone-cyber/teleseer-external-hosts.png)

This is exactly as expected.

The result is a good illustration of how loopback can mask MAC.  I will re-run it against the part 2 container network, where there will actually be something to map.

## What an autonomy stack inherits

Everything above is a protocol story, and it becomes an AI story the moment the ground station stops being a person.

An autonomy stack sits exactly where my tooling sits in this lab.
It consumes the same unsigned telemetry, it emits the same unsigned commands, and it has the same total inability to tell the vehicle's real state from a plausible fiction injected by anyone within reach of the link.
Every property established in this post is inherited by the planner, the vision pipeline, and the decision layer, without any of them opting in.

Three consequences seem worth stating plainly.

**Sensor truth is the whole attack surface.**
A classical ground station shows a human a position and that human has independent context, including the aircraft they can see and the mission they remember planning.
An autonomy stack has only the telemetry.
Corrupting the estimator's inputs corrupts every decision made on top of them, and there is no second opinion anywhere in the loop.

**Reconnaissance is free and it is now targeting logic rather than an operator.**
The 1,370-parameter dump tells an attacker the geofence geometry and the failsafe thresholds.
Against a human operator that is useful.
Against a deterministic planner that reacts to those same thresholds in a documented way, it approaches a specification for how to steer the aircraft without ever sending it a flight command.

**Telemetry that reaches a language model is an injection surface nobody models.**
MAVLink carries operator-controlled text.
`STATUSTEXT` is a free-text field, mission items carry names, and both flow into logs, dashboards, and increasingly into the context window of an LLM-based decision layer summarizing vehicle state.
Anyone who can write to the link can write into that context.
The security literature has spent two years on prompt injection through documents and web pages, and I have seen nothing on prompt injection through an unauthenticated telemetry field on an aircraft.
That is a gap worth closing before somebody demonstrates it for us.

## What to actually do about it

Concrete and boring, in rough order of return:

- **Turn signing on and understand its limits.** It authenticates frames and defeats replay. It is not encryption, the key distribution is manual, and it says nothing about authorization.
- **Never expose 5760, 14550 or their neighbors beyond loopback or a tunnel.** Check the default rather than assuming it; SITL's is wrong for any network you did not build.
- **Treat the companion-computer link as untrusted and tunnel it.** WireGuard on the LTE or WiFi path costs little and moves the problem to a layer that has actual identity.
- **Watch `COMMAND_ACK`.** A ground station or autonomy stack that fires commands without checking results is blind to both failure and interference, and this one is free.
- **Sanitize telemetry text before it reaches a model.** If `STATUSTEXT` or a mission item name can reach an LLM's context, it is untrusted input from anyone in RF range.

## What's next

Part 2 moves this stack onto an isolated rootless-container network, so the traffic stops being localhost and starts being a network with real link layers, distinct endpoints, and controlled damage:

- MAVLink 2 signing on one port, the same flight signed and unsigned, measuring the 13-byte overhead, what forged frames do, and where the timestamp window helps and where it does not
- Bounded delay, loss, duplication and reordering on lab-owned virtual links, and how the stack recovers
- The GPS-versus-inertial disagreement test the `set_pose` work set up, with `EKF_STATUS_REPORT` innovations published rather than asserted
- Identity and multi-peer isolation, which is the two-`arducopter` bug turned into a deliberate experiment

All keys synthetic, all captures inside the box, podman rootless, nothing bound wider than loopback.

## Colophon

ArduPilot pinned at `Copter-4.7.0`, commit `1511f271`, built with its own `waf` inside a lab-local venv.
Gazebo Harmonic with `ardupilot_gazebo` pinned to a commit and built out of tree.

One note for anyone reproducing this on Ubuntu 24.04: **do not run ArduPilot's `install-prereqs-ubuntu.sh` without reading it first**.
It is a well-meaning script for getting roboticists flying quickly rather than a security baseline.
It unconditionally adds the invoking user to the `dialout` group, runs `apt-get remove` on `modemmanager` and `brltty`, writes PATH exports into `~/.profile`, and installs an STM32 ARM cross-compiler that x86 SITL does not need, with no flags to decline some of that.
Everything SITL actually needs is a dozen pip packages in a venv plus `build-essential`.

Launch detached with `setsid`, write the PID file from inside the new session, and capture the exit code.
A simulator that cannot be stopped by exact PID is a simulator that cannot be trusted during a fuzzing session, which is why there is no `pkill` anywhere in this lab.

The scripts, configs, topology manifest, and the MAVLink-only pcap all live in the companion repository, [**cyberdrone**](https://github.com/stevehenderson/cyberdrone).
The capture is the same 98,786 packets summarized above, so the numbers in this post can be checked rather than taken on faith.

That repository went through the same review this post argues for, and it was worth doing.
The first pass turned up absolute home paths in six files, a detailed hardware and installed-software fingerprint of the workstation in two more, and full-resolution originals of screenshots that had already been pulled from this post for leaking unrelated cloud identifiers.
None of that was interesting to an attacker on its own. All of it was free reconnaissance that a lab about free reconnaissance had no business shipping.

