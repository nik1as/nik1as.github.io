---
title: Forensics
description: Forensics cheatsheet
date: 1970-01-20
categories: [Cheatsheets]
tags: [cheatsheets,forensics]
---

- `file <file>`: determines the type of the file
- `binwalk -e <file>`: extracts hidden files
- `strings <file>`: prints the strings in the file
- `tar -xvf <file>`: untars the tar file
- `exiftool <file>`: prints metadata
- `extundelete`: recover deleted files
- `debsums`: verify the integrity of installed package files
- `chkrootkit` and `rkhunter`: examine the filesystem for rootkits
- `lsof`: files/resources connected with a process

## Images

```
stegseek -sf <file> -wl /usr/share/wordlists/rockyou.txt

steghide info <file>
```

## Binaries

- `strace`: trace system calls
- `ltrace`: trace library calls
- `strings`: extract printable strings from file
- `ghidra`: decompiler
