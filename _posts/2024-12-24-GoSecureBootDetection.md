---
layout: post
title: The Importance of Secure Boot
categories: ['blog']
tags: ['cyber', 'secureboot']
---

Secure Boot is a rather cryptic and opaque security setting on your computer.  In most circumstances, it's something you or your computer's vendor will configure in your machine's BIOS, and then forget about.  Occasionally, you might be tempted to disable this setting to facilitate custom boot scenarios, install certain hardware, or peform botique configurations to your machine.  However, Secure Boot is an essential protection mechanism to help keep your computer safe from the most dangerous and sophisticated cyber security threats.

## Overview of secure boot

Secure Boot is a security standard developed by the Unified Extensible Firmware Interface (UEFI) Forum. 
It is used to ensure that a device boots using only software that is trusted by the manufacturer. During the boot process, the firmware checks each piece of software against a database of known good code. If any software is found to be untrusted or tampered with, the boot process is halted. This mechanism helps prevent unauthorized code from running at startup, effectively mitigating risks associated with rootkits, bootkits, and other forms of malware that attempt to compromise a system before the operating system has a chance to load.

## Adding Legitimate User Applications, Operating System Files, and Kernel Modules with Secure Boot

While Secure Boot provides an essential layer of protection against malicious code, it can also pose challenges when adding your legitimate user applications, operating system files, and kernel modules. To ensure that these components are trusted by the system, developers and administrators must follow specific procedures.

### Adding Legitimate User Applications

To add a legitimate user application with Secure Boot enabled, the application must be signed with a trusted certificate. This certificate is typically obtained from a trusted Certificate Authority (CA). With modern operating systems, this is handled automatically by the package management system.  For example, on Linux Ubuntu, apt will handle isntalling applications with a trusted certificate.  **It is important when adding apt-keys that you always ensure they are trusted -- if you allow sketchy repos, you can get burnt**.   The packagage manager will add the signed application is then added to the system's whitelist, allowing it to run without being blocked by Secure Boot.  Windows works the same way, with Microsoft only allowing application to be install for which it has a trusted CA relationship built-in to Windows.

### Adding Operating System Files

When adding new operating system files, such as device drivers or system libraries, these files must also be signed with a trusted certificate. Again, a **properly configured** Operating System will handle this as part of its update syetem.  In addition, the operating system's package manager will typically  be configured to verify the integrity of these files during installation. This ensures that only trusted operating system files are installed on the system.

### Adding Kernel Modules

Kernel modules, which provide additional functionality to the operating system kernel, must also be signed with a trusted certificate. In Linux, kernel modules can be signed using the sign-file tool, which generates a digital signature for the module. The signed module is then loaded into the kernel, allowing it to function without being blocked by Secure Boot.

Here is an example:

```
sign-file -v -k /path/to/private/key -c /path/to/certificate.crt -t /path/to/kernel/module.ko
```

## Detecting Secure Boot

As a developer, it's often helpful to audit the machine your code is running on to determine if secureboot is enabled.  

### Linux

In Linux you can write a go program that does just that:


```go
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// checkSecureBoot checks if Secure Boot is enabled by reading the appropriate EFI variable.
func checkSecureBoot() (bool, error) {
	secureBootPath := "/sys/firmware/efi/efivars/SecureBoot-*"

	files, err := filepath.Glob(secureBootPath)
	if err != nil {
		return false, fmt.Errorf("failed to read Secure Boot variable: %v", err)
	}

	for _, file := range files {
		data, err := os.ReadFile(file)
		if err != nil {
			return false, fmt.Errorf("failed to read file %s: %v", file, err)
		}

		// Check the contents to determine if Secure Boot is enabled
		if strings.Contains(string(data), "1") {
			return true, nil
		}
	}

	return false, nil
}

func main() {
	enabled, err := checkSecureBoot()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	if enabled {
		fmt.Println("Secure Boot is enabled.")
	} else {
		fmt.Println("Secure Boot is not enabled.")
	}
}
```

### Windows Powershell

On Windows, you can detect SecureBoot with a simple Powershell command

```
Confirm-SecureBootUEFI
```

### Windows Go

You can also write some go code to detect the same:

```go
package main

import (
	"fmt"
	"golang.org/x/sys/windows"
)

const (	
	secureBootVariableName = "SecureBoot"
)

func main() {
	// Get the firmware environment variable value
	value, err := getFirmwareEnvironmentVariable(secureBootVariableName)
	if err != nil {
		fmt.Println(err)
		return
	}

	// Check the Secure Boot status
	if value == 1 {
		fmt.Println("Secure Boot is enabled")
	} else {
		fmt.Println("Secure Boot is disabled")
	}
}

func getFirmwareEnvironmentVariable(name string) (uint32, error) {
	// Get the firmware environment variable value using the Windows API
	var value uint32
	var size uint32
	err := windows.GetFirmwareEnvironmentVariableEx(windows.StringToUTF16Ptr(name), &value, &size)
	if err != nil {
		return 0, err
	}
	return value, nil
}
```
