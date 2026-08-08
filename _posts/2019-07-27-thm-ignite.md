---
title: Ignite
description: Writeup for the TryHackMe machine Ignite
date: 2019-07-27
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds one open port: HTTP (80).
```
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
| http-robots.txt: 1 disallowed entry
|_/fuel/
|_http-title: Welcome to FUEL CMS
|_http-server-header: Apache/2.4.18 (Ubuntu)
```

### HTTP - TCP 80

The website is running Fuel CMS version 1.4. A quick search for known vulnerabilities leads to [this](https://www.exploit-db.com/exploits/50477) Remote Code Execution (RCE) exploit.

## Shell as www-data

I use the script from ExploitDB to obtain a shell as the `www-data` user.
```console
$ python3 50477.py -u "http://ignite.thm/"
```

## Shell as root

I inspect the application files and find database credentials in `/var/www/html/fuel/application/config/database.php`:

```
'hostname' => 'localhost',
'username' => 'root',
'password' => '<REDACTED>',
'database' => 'fuel_schema',
```
I use the database password to switch to the `root` user.
