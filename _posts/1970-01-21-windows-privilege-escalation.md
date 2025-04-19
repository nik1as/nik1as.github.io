---
title: Windows Privilege Escalation
description: Windows Privilege Escalation cheatsheet
date: 1970-01-21
categories: [Cheatsheets]
tags: [cheatsheets,windows-privilege-escalation]
---

- [winPEAS](https://github.com/peass-ng/PEASS-ng/releases)
- connect to the target
```console
evil-winrm -i <rhost> -u <user> -p <password>
evil-winrm -i <rhost> -u <user> -H <hash-pass> 
```

## System Enumeration

```console
net users
net users <username>
whoami /priv
net localgroup
```

Find all important files:
```console
cd C:\Users
tree /F
```

## Network

- `ipconfig`
- `netstat -ab`
