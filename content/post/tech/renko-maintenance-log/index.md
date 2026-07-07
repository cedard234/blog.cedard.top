---
title: Renko Maintenance Log - Apr 18-19th 2026
slug: renko-maintenance-log
date: 2026-04-20T22:30:41+08:00
image: https://images.blog.cedard.top/post/tech/renko-maintenance-log/math20260420233237.png
description: yet another NAS maintenance log after one full year of idling
categories:
    - tech
tags:
    - renko
    - NAS
---

## Introduction
It's been a long while since I properly maintained my NAS. To remind our audience what I have:
```text
             .',;::::;,'.                 di_wang@renko
         .';:cccccccccccc:;,.             -------------
      .;cccccccccccccccccccccc;.          OS: Fedora Linux 43 (Server Edition) x86_64
    .:cccccccccccccccccccccccccc:.        Host: PR2285S1 (2.2)
  .;ccccccccccccc;.:dddl:.;ccccccc;.      Kernel: Linux 6.19.12-200.fc43.x86_64
 .:ccccccccccccc;OWMKOOXMWd;ccccccc:.     Uptime: 1 day, 4 hours, 14 mins
.:ccccccccccccc;KMMc;cc;xMMc;ccccccc:.    Packages: 1838 (rpm)
,cccccccccccccc;MMM.;cc;;WW:;cccccccc,    Shell: bash 5.3.0
:cccccccccccccc;MMM.;cccccccccccccccc:    Terminal: /dev/pts/0
:ccccccc;oxOOOo;MMM000k.;cccccccccccc:    CPU: Intel(R) Xeon(R) E3-1280 v5 (8) @ 4.00 GHz
cccccc;0MMKxdd:;MMMkddc.;cccccccccccc;    GPU: ASPEED Technology, Inc. ASPEED Graphics Family
ccccc;XMO';cccc;MMM.;cccccccccccccccc'    Memory: 37.72 GiB / 62.61 GiB (60%)
ccccc;MMo;ccccc;MMW.;ccccccccccccccc;     Swap: 2.85 GiB / 40.00 GiB (7%)
ccccc;0MNc.ccc.xMMd;ccccccccccccccc;      Disk (/): 64.06 GiB / 865.50 GiB (7%) - xfs
cccccc;dNMWXXXWM0:;cccccccccccccc:,       Disk (/storage): 8.23 TiB / 9.71 TiB (85%) - zfs
cccccccc;.:odl:.;cccccccccccccc:,.        Local IP (eno1): MANUALLY REDACTED
ccccccccccccccccccccccccccccc:'.          Locale: en_US.UTF-8
:ccccccccccccccccccccccc:;,..
 ':cccccccccccccccc::;,.
```
I still remember that it was back in late 2024 that I purchased all the parts for this NAS. I got 4 4T Seagate Skyhawks for roughly ¥CNY 400 each (roughly USD 57 each). It was quite a great deal back then, given that the price of HDDs has now gone up to around USD 30/Terabyte. I still remember last summer in Oregon when I was debating whether I should grab the USD 15/T deal from Best Buy (in hindsight I really should have, given OR doesn't have sales tax). Now it's 85% full and I'll have to seriously consider buying a bunch more.

It was funny when thinking about the motherboard supermicro X11SSH-F. All of its video outputs are essentially broken -- HDMI, VGA, etc. I don't know how to use serial ports. It was quite a bargain that I bought from 咸鱼 (basically the Chinese fb marketplace) for ¥200, whereas the listed price on Amazon was like:

![Wow, thank you Amazon](https://images.blog.cedard.top/post/tech/renko-maintenance-log/math20260420224403.png)

It was funny because the previous owner had no idea what the IPMI IP address was -- it was hard coded in BIOS; however, without video output, I wasn't able to reset the IP address, nor could I install a new OS. I spent a night writing a script on my openwrt router to try changing the subnet and pinging potential addresses, assuming it began with 192.168. I didn't manage to find one until the next day, when the owner messaged me saying that he recalled it was under 192.168.254.xxx, and I realized the IPMI was actually at 192.168.254.1. When I opened up IPMI, I saw the BIOS startup screen as "比特币挖矿系统" (BTC mining system) and I finally understood why it was so damn cheap. That was back when BTC mining was still pretty popular.

Anyways, I installed Fedora 40 back then and never worried about it again. I ran docker containers, my own chatbot, and reverse proxy services, but after last weekend reminded me of the Fedora 44 news, I thought it was time to actually try to upgrade the very broken system, since a lot of the "DevOps" things that I did were very, very ad hoc.

## Fedora 40 -> 43, RAM speed optimization

Fedora 40 was EOL like a year ago; therefore, upgrading the system was the first thing I did. It wasn't too hard to pull the prebuilt image and install it. For safety I did this in 3 steps: 40->41, 41->42, 42->43, each taking about half an hour.

Given I had to reboot the system anyway, I realized that all 4 DDR RAMs were running at 2133 instead of their rated speed of 2400. So I went into the BIOS settings to try to manually set the RAM speed to 2400.

![](https://images.blog.cedard.top/post/tech/renko-maintenance-log/math20260420225356.png)

However, I think it's pretty much a limitation of the motherboard not being able to support XMP; the E3-1280 V5 skylake CPU also blindly ties the memory bandwidth to 2133 (lame!), so setting the maximum frequency was the best thing I could do.

It was funny looking back at how long I spent dealing with IPMI once again. I have a custom nginx configuration where I assign the private domain name ipmi.renko.cedard.top to the IPMI port, but it wasn't connecting at the very beginning. It took me quite a while to troubleshoot whether this was a problem with some stale nginx setting, but it wasn't until I realized the IP wasn't up either that I found the IPMI port wasn't connected to an RJ45 cable, haha.

Once Fedora 43 booted up on the NAS, I finally caught up with the lifecycle of the system, and the kernel was also updated to 6.19.12.

```text
di_wang@renko:~$ cat /etc/os-release
NAME="Fedora Linux"
VERSION="43 (Server Edition)"
RELEASE_TYPE=stable
ID=fedora
VERSION_ID=43
VERSION_CODENAME=""
PRETTY_NAME="Fedora Linux 43 (Server Edition)"
ANSI_COLOR="0;38;2;60;110;180"
LOGO=fedora-logo-icon
CPE_NAME="cpe:/o:fedoraproject:fedora:43"
HOME_URL="https://fedoraproject.org/"
DOCUMENTATION_URL="https://docs.fedoraproject.org/en-US/fedora/f43/"
SUPPORT_URL="https://ask.fedoraproject.org/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=43
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=43
SUPPORT_END=2026-12-02
VARIANT="Server Edition"
VARIANT_ID=server
```

I set up a monthly reboot on Sunday morning at 3am to ensure the system is always up-to-date and running smoothly.

```config
# /var/spool/cron/root
0 3 * * 0 /sbin/reboot
```

## Docker Stuff
I have a few services on docker, but they were all running under my own home directory instead of being properly archived. Some of them were also running on really really old images, simply because I was too lazy to pull from dockerhub.

Docker runs as a systemd service under fedora, and any docker service that has the restart flag in `docker-compose.yml` will be automatically registered and restarted. This is pretty convenient since I don't really have to create separate systemd daemons for each one of these. Housekeeping: I put all of them under `/opt`.

I was trying to see if I could have them all automatically update themselves. Claude told me that there is a specific docker image `watchtower` that does this, only for me to realize that watchtower is no longer being maintained.

A simple script does this:

```bash
# update-containers.sh

#!/bin/bash
set -euo pipefail

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "Starting container update"

for dir in /opt/*/; do
    compose_file=""
    if [ -f "$dir/docker-compose.yml" ]; then
        compose_file="$dir/docker-compose.yml"
    elif [ -f "$dir/compose.yaml" ]; then
        compose_file="$dir/compose.yaml"
    else
        continue
    fi

    name=$(basename "$dir")
    log "Updating $name"
    docker compose -f "$compose_file" pull --quiet && \
        docker compose -f "$compose_file" up -d --remove-orphans || \
        log "WARNING: Failed to update $name"
done

docker image prune -f --filter "until=168h" > /dev/null
log "Container update complete"
```

I did realize the postgres image was a corner case, where pulling the latest image broke the split flow. It tried to pull PG18, and broke the PG16 data directory.

## Security
I turned off all password logins, only allowing SSH key-based authentication, and disabled unused firewall ports.

## ZFS

### RAIDZ1
Here comes the big deal. I use raidz1 for all 4 of my drives, but I do realize that if a drive fails, during rebuild I'll have no additional layer of protection, and rebuilding makes it pretty likely that other drives might fail too, especially if they all come from the same batch (mathematically, two independent Poisson processes can be summed in terms of fail rate. It gets even worse if they are correlated). However, I don't really have the luxury to do raidz2 right now, so I guess I'll have to live with it for some time.

### Some optimizations

`lz4` is better than `lzjb` in terms of data writes because it's faster and has a higher compression ratio.
`atime` is not necessary when doing writes. Therefore I made both changes:

```bash
zfs set compression=lz4 storage
zfs set atime=off storage
```

### Larger Record Size for media
I also created a separate dataset for my movies where sequential RW matters. Compared to 128K default chunk size, 1M reduces IO access counts significantly.

```bash
zfs set recordsize=1M /your/mount/point
```

### Auto ZFS snapshot
There is this nice [repo](https://github.com/zfsonlinux/zfs-auto-snapshot.git) from GitHub where we can keep continuous zfs auto snapshots. This is super useful if I ever need to roll back.

This actually did save me because I messed up postgres yesterday and I managed to recover in no time.

---
That's it. I will try to write up my learnings + sharings for future sysadmin stuff as separate blogs; this is just one of them. I'll probably try to update the system to Fedora 44 this upcoming weekend.

If you are using some of my services, I have a dedicated uppage (hopefully not a downpage) [here](https://status.cedard.top).

BTW if you don't know about this already, I drew the name "Renko" from the character "Renko Usami", a physics undergrad studying supernatural encounters.

![[by XUNSI](https://x.com/KXunsi17693/status/2045816705147142598?s=20)](math20260420232915.png)

It's funny that I named my NAS *Renko* because I named the reverse proxy VPS *Hearn*, who just so happens to be her bestie :)