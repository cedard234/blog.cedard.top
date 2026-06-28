---
title: 一台树莓派到底能拿来干什么？
slug: raspberry-pi
date: 2021-05-07T20:14:38+08:00
draft: true
categories:
    - tech
---

哪个年轻人不想拥有自己的一台树莓派呢？这是一个非常值得讨论的问题。截至2019年底，树莓派的销售量已经到达三千万台。虽然这玩意并不能真正意义上拿来当作办公用电脑，但是手握一台信用卡大小的单片机着实是一件很酷的事情，尤其是当这台机器可以完成大多数电脑也能干的事情的时候。套用那句非常非常老的话，就是用过树莓派基本不会失望，没用过树莓派不知道自己之后不会因此而失望。

我是今年年初的时候，因为要做arduino相关的一个项目，被朋友忽悠了入的。后来发现，我是用五百RMB换来一台属于自己的服务器！如果说IPV6推广的话，那么事实上我已经不需要购置其他厂商的VPS了，因为这玩意基本上可以完成所有VPS能干的事情，如果说他有公网IP的话。

# intro

树莓派是什么？简而言之，树莓派就是一台电脑，只不过非常之小，小到可以揣在口袋里带走。

它好在哪里？它好就好在他的CPU性能不俗，功耗低，便宜。你只要花上大概四百到五百人民币的价格，就能把这台小巧的卡片计算器带回家。也就是说，一台surface book2大概顶的上20台树莓派。如果说你买电脑只是为了一个文本编辑器，为什么不买一个树莓派呢？

它的另外一些好处有，你可以一直开着它，让他一直运行一些服务。普通的电脑你不用的时候通常会把他关机。

# 基本配置

当树莓派到手的时候，你需要干的事情有：

1. 买树莓派和对应的SD卡。一般来说32G的就已经很够用了。
2. 组装外壳。
3. 给你的SD卡刷好系统，并添加ssh文件（强烈建议）
4. 插入SD卡。
5. 通电。
6. 使用ssh登录你的树莓派。
7. 爱干嘛干嘛~

这样就完成了。是不是非常简单！

## 刷系统

树莓派是有属于自己的操作系统的。这个os被称作Raspberry Pi OS，之前也叫raspbian,因为是基于debian的类unix操作系统。从2015年开始，树莓派基金会就已经宣布raspberry pi os作为树莓派的首选系统。

这个系统最早是由Mike Thompson和Peter Green两位大佬在一个独立的项目里于2012年六月编译出来的。

为了把系统放进你的树莓派里充当软硬件的沟通媒介，你需要一个专有的写入程序。你可以在[这个界面](https://www.raspberrypi.org/software/)下载安装程序，里面会自带镜像文件。

用读卡器连接SD卡与你的电脑，并选择这个SD卡作为你的目标硬盘。选择你将要安装的操作系统，等待就OK。

### ssh文件

一般来说，搞定之后的树莓派里面是没有ssh文件的。但是如果要便捷地控制树莓派的话，ssh往往是最好的方式。没有人想把自己的显示屏拆下来再用hdmi线连上这台机器。

要激活树莓派的ssh功能也非常简单。直接在根目录里面新建一个ssh文件，问题就解决了。你也可以通过一些其他方式来打开树莓派本身的ssh，但是我觉得这个方法最简单。

事实上，这说明了raspberry pi os是自带openssh的，只是没有启用而已。

## 登录树莓派

要登录树莓派非常容易。前提条件是你需要知道你的树莓派的IP地址。

要使你的树莓派的ssh可用，你必须把他接上互联网。最简单的方法是插到路由器的LAN口，这样他就和你的电脑处于同一内网下……前提是你的电脑也连到了这个路由器。

查询路由器的IP表就可以知道树莓派的IP地址了。在个人PC上使用 ssh连接：

```
$ssh pi@${ip address}
pi@${ip address}'s password:
```

注意，一定要用pi用户登录。这是raspberry pi os的一个内置用户。用root是无法登录的。

当你没有做任何修改的时候，默认密码就是raspberry。

```
Linux raspberrypi 5.10.17-v7l+ #1403 SMP Mon Feb 22 11:33:35 GMT 2021 armv7l

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: -

SSH is enabled and the default password for the 'pi' user has not been changed.
This is a security risk - please login as the 'pi' user and type 'passwd' to set a new password.


Wi-Fi is currently blocked by rfkill.
Use raspi-config to set the country before use.

pi@raspberrypi:~ $
```

如果你可以看到这些提示信息，那么恭喜你。

# 你可以用它来干什么？

刚才说过，树莓派实际上和你的个人电脑没有什么区别，除了它小了点，运算效果差了点之外，操作系统不那么习惯而已。

实际上，如果你给他分配一个公网的IP地址，它可以胜任所有VPS能干的事情。比如说科学上网的服务器，只要你的公网IP不在合法区域。比如说你可以拿他来跑我上篇文章里写的机器人程序，或者用它来运行这个网站。

贴一张图~

![](/img/raspi.jpg)

这玩意竟然有RGB，真是让人感慨。