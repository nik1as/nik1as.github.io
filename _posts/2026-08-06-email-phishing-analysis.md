---
title: Email Phishing Analysis
description: Practical checklist for triaging suspicious emails, validating headers and authentication, inspecting URLs, and analyzing attachments safely.
date: 2026-08-08
categories: [Cheatsheets]
tags: [cheatsheets,email,phishing,incident-response]
---

## Overview

This guide provides a practical workflow for analyzing suspicious emails without clicking links or opening attachments in a normal workstation. The goal is to preserve evidence, identify sender inconsistencies, inspect URLs and attachments, and collect indicators of compromise (IOCs) that can be shared with others.

## Useful tools

- [MXToolbox](https://mxtoolbox.com/EmailHeaders.aspx): Inspect email headers, check SPF/DKIM/DMARC, and review sender reputation.
- [VirusTotal](https://www.virustotal.com): Check URLs, file hashes, and attachments for prior detections and context.
- [Hybrid Analysis](https://hybrid-analysis.com/): Submit suspicious files to a sandbox for behavioral analysis.
- [urlscan.io](https://urlscan.io/): Examine URLs, redirects, and screenshots of the rendered page.
- [DomainTools](https://whois.domaintools.com/): Investigate domain ownership, WHOIS history, and related infrastructure.
- [DidierStevensSuite](https://github.com/didierstevens/didierstevenssuite): Analyze Office documents, macros, and embedded content.

## Save the message source

From most mail clients, choose "View source" or "Download original" and save the output as `suspicious.eml`.

## Header & sender analysis

- Inspect the visible headers (`From`, `X-Sender-IP`, `Reply-To`, `To`) and the full `Received` chain. The first external `Received` header (the bottom-most entry) usually points to the originator or the last external hop.
- Common quick commands:

```bash
# show all Received headers (oldest last)
grep -i "^Received:" suspicious.eml | nl -ba | sed -n '1,200p'

# get the earliest (bottom-most) Received header
grep -i "^Received:" suspicious.eml | tail -n1
```

- Use the originating IP for reputation checks and a reverse DNS lookup:

```bash
dig -x <ip-address>
whois <ip-address>
```

- Check for display-name vs. envelope mismatches and small typos in domains (for example, `micr0soft.com` vs. `microsoft.com`).

## Authentication checks (SPF, DKIM, DMARC)

- Query DNS for SPF and DMARC records:

```bash
dig +short TXT example.com | sed -n '/v=spf1/p'
dig +short TXT _dmarc.example.com
```

- Check SPF and DKIM with MXToolbox.

- Interpretation tips:
  - SPF pass means the sending IP is authorized by the domain's SPF policy. SPF failures combined with a forged `From` address are highly suspicious.
  - DKIM pass indicates the message body and signature were not altered after signing.
  - DMARC policies tell receivers how to treat failing messages (`none`, `quarantine`, or `reject`).

## Content & URL analysis

- Extract URLs from the message safely (do not click):

```bash
grep -Eo "https?://[^\s\)\'\"]+" suspicious.eml | sed 's/[<>]//g' | sort -u
```

- Submit URLs to VirusTotal or urlscan.io for reputation checks and screenshots.
- Look for punycode, IP-based URLs, long redirect chains, URL shorteners, and domains that mimic trusted brands.

## Attachment analysis

- Extract attachments using a tool that understands MIME. Always analyze attachments in an air-gapped or sandboxed VM instead of a production machine.

```bash
# compute a file hash
sha256sum suspicious-attachment.docx

# basic macro checks
oledump.py suspicious-attachment.docx
oledump.py suspicious-attachment.docx -s <item> -S
oledump.py suspicious-attachment.docx -s <item> --vbadecompresscorrupt

# PDF checks
pdfid.py suspicious.pdf
pdf-parser.py suspicious.pdf | more
pdf-parser.py suspicious.pdf -s "/URI"
```

- Submit hashes to VirusTotal and search for prior reports or related submissions.
- If the file is executable or archive-like, consider sandbox detonation with Hybrid Analysis.
