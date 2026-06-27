---
title: "Infrastructure"
slug: "infrastructure"
date: 2026-06-20 15:47:23
menu:
    main:
        name: Infrastructure
        weight: 6
        params:
            icon: server
---

I own the domain [cedard.top](https://cedard.top), so all of my services live on its subdomains.

## VPS

[hearn.cedard.top](https://hearn.cedard.top) is a DigitalOcean VPS in San Jose, used solely as a reverse proxy.

## NAS — "Renko"

My home NAS, **Renko**, runs the following configuration:

```
             .',;::::;,'.                di_wang@renko
         .';:cccccccccccc:;,.            -------------
      .;cccccccccccccccccccccc;.         OS: Fedora Linux 44 (Server Edition) x86_64
    .:cccccccccccccccccccccccccc:.       Host: PR2285S1 2.2
  .;ccccccccccccc;.:dddl:.;ccccccc;.     Kernel: 7.0.12-201.fc44.x86_64
 .:ccccccccccccc;OWMKOOXMWd;ccccccc:.    Uptime: 5 days, 10 hours, 53 mins
.:ccccccccccccc;KMMc;cc;xMMc:ccccccc:.   Packages: 1906 (rpm)
,cccccccccccccc;MMM.;cc;;WW::cccccccc,   Shell: bash 5.3.9
:cccccccccccccc;MMM.;cccccccccccccccc:   Resolution: 1024x768
:ccccccc;oxOOOo;MMM0OOk.;cccccccccccc:   Terminal: /dev/pts/0
cccccc:0MMKxdd:;MMMkddc.;cccccccccccc;   CPU: Intel Xeon E3-1280 v5 (8) @ 4.000GHz
ccccc:XM0';cccc;MMM.;cccccccccccccccc'   GPU: 05:00.0 ASPEED Technology, Inc. ASPEED Graphics Family
ccccc;MMo;ccccc;MMW.;ccccccccccccccc;    Memory: 29625MiB / 64110MiB
ccccc;0MNc.ccc.xMMd:ccccccccccccccc;
cccccc;dNMWXXXWM0::cccccccccccccc:,
cccccccc;.:odl:.;cccccccccccccc:,.
:cccccccccccccccccccccccccccc:'.
.:cccccccccccccccccccccc:;,..
  '::cccccccccccccc::;,.
```

Renko reboots every Monday at 3:00 AM Pacific Time.

It hosts the following services:
- **Nextcloud**: [nextcloud.renko.cedard.top](https://nextcloud.renko.cedard.top)
- **Emby**: [emby.renko.cedard.top](https://emby.renko.cedard.top)
- **Navidrome**: [navidrome.renko.cedard.top](https://navidrome.renko.cedard.top)
- **Spliit**: [spliit.renko.cedard.top](https://spliit.renko.cedard.top)
- **Telegram bot**: "cedar_the_misleading" (@cedar_234_bot)
- I host the following two internet radio stations. 
  - **Cedar's Classical**: [My own taste of classical music](https://radio.renko.cedard.top/classical)
  - **[凋叶棕](https://en.touhouwiki.net/wiki/%E5%87%8B%E5%8F%B6%E6%A3%95)**: from my fav musician RD-Sound and vocalist [めらみぽっぷ](https://remywiki.com/Meramipop), [all album touhou music](https://radio.renko.cedard.top/touhou)

All services are monitored via [UptimeRobot](https://status.cedard.top/).

## Contact

If you would like to use any of my services, or want to report an issue, reach me on [Telegram](https://t.me/cedar_234) or by [email](mailto:wangdi1310@gmail.com).