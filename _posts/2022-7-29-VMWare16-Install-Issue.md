I'm installing VMWare Workstation on Linux Ubuntu 20, and had trouble with it not starting.  The issues was related to Linux not being able to compile and install `vmmon` and `vmnet` kernel modules.

```
2022-07-29T08:55:47.901-04:00| host-220593| I005:       | 
2022-07-29T08:55:47.901-04:00| host-220593| I005: make[1]: *** [Makefile:1875: /tmp/modconfig-wOXCH0/vmnet-only] Error 2
2022-07-29T08:55:47.901-04:00| host-220593| I005: make: *** [Makefile:117: vmnet.ko] Error 2
2022-07-29T08:55:47.901-04:00| host-220593| I005: Unable to install all modules.  See log for details.
```

I needed to install some kernel modules to get VMWare Workstation to work.

There are some [kind souls](https://github.com/mkubecek) that manage a very nice repo for ptaching the kernel.

This is how I used it

```
cd ~/tmp
git clone https://github.com/mkubecek/vmware-host-modules.git
```

Once checked out, you need to find your kernel version

```
uname -a
```

Yields:

```
Linux coolbox 5.15.0-41-generic #44~20.04.1-Ubuntu SMP Fri Jun 24 13:27:29 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
```

So this kernel is `5.15`

If you search the tags for the vmware-host_modules repo:

```
git fetch --tags
git tag -l w15*
```

(Or use the web console)

I find the tag I need:

```
git tag -l w16*k5.15*
w16.1.2-k5.15
w16.2.0-k5.15
w16.2.1-k5.15
w16.2.3-k5.15
w16.2.4-k5.15
```

And check it out:

```
git checkout w16.2.4-k5.15
```

I used the most up-to-date version for workstation that matched my kernel.

Then build it:

```
make
sudo make install
```

Workstation then starts up!
