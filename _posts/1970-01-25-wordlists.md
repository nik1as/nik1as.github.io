---
title: Wordlists
description: Wordlists cheatsheet
date: 1970-01-25
categories: [Cheatsheets]
tags: [cheatsheets,wordlists]
---

- [Munge](https://github.com/Th3S3cr3tAg3nt/Munge.git)
- [CUPP](https://github.com/Mebus/cupp)

```console
cewl -d <depth> -m <min-length> -w wordlist.txt <url>
```

```console
crunch <min> <max> <charset> -o wordlist.txt
crunch <min> <max> -t <pattern> -o wordlist.txt
@ -> lowercase alphabets
, -> uppercase alphabets
% -> numbers
^ -> special characters
```