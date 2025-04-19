---
title: Active Directory
description: Active Directory cheatsheet
date: 1970-01-24
categories: [Cheatsheets]
tags: [cheatsheets,active-directory]
---

```console
smbclient -L //<rhost>/ -U <user>
smbclient //<rhost>/<share> -U <user>

enum4linux -a <ip>

ldapdomaindump ldap://<rhost> -u '<domain>\<user>' -p '<password>'

netexec smb <rhost> -u guest -p '<password>' --rid-brute
netexec smb <rhost> -u users.txt -p '<password>' 
```
