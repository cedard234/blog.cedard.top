---
title: zsh踩坑记
slug: zsh-pitfalls
date: 2021-08-21T22:20:24+08:00
description: 代码可以写的烂，终端不能不好看
draft: true
categories:
    - tech
tags:
    - tech
---

## 草，原来除了bash还有其他的壳程序啊

暑假去公司写了大概三个月的java，其中一半以上的时间在改shell的参数，跑测试，etc。不得不说，shell这玩意的语法真的邪门，终于知道为什么那么多工程师喜欢用python写脚本了，写了半天./xxx.sh之后告诉你command not found真的很折磨.jpg

不过体验最深的是，bash太丑了，不行！但是只能说以前的自己实在是too young too simple, sometimes naive，需要学习一个；到了今天我才知道，除了bash，还有这么多好康的壳程序，实在是离了大谱了。总的来说，bash之所以叫“bash”，并不说因为这个壳程序想要揍你一拳，而是bash这个词是**B** ourne-**A** gain **SH** ell的acronym。bourne shell，即“伯恩壳”（没错，就是谍影重重的那个男主角的名字，当然不是同一个人），是由[AT&T](https://zh.wikipedia.org/wiki/AT%26T)[贝尔实验室](https://zh.wikipedia.org/wiki/贝尔实验室)的[史蒂夫·伯恩](https://zh.wikipedia.org/wiki/史蒂夫·伯恩)在1977年在[Version 7 Unix](https://zh.wikipedia.org/wiki/Version_7_Unix)中针对大学与学院发布的，也是先行各种linux的distro的默认shell。

当然，除了bash之外，还有很多shell程序，它们都是以-sh结尾的（shell）。比如说，sh,bash,**zsh**,fish(?),etcsh...

嗯，没错。今天就是要来使用一下zsh。

## zsh是什么

zsh，即Z shell的缩写，是保罗·弗斯塔德在1990年纪念他的老师邵中（**Z** hong **Sh** ao）而写的，很明显的一个中文名字。而zsh的发扬光大，是github上的一个社区项目oh-my-zsh发扬光大的，有了oh-my-zsh，这个shell包含了上百种主题，加上许多可执行插件，如vim一样充满生命力。

## 安装和使用

想要使用oh-my-zsh的美观主题和各种插件，步骤是这样的：

```
git clone https://github.com/robbyrussell/oh-my-zsh.git ~/.oh-my-zsh
cp ~/.oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc
chsh -s /bin/zsh
```

克隆，复制.zshrc文件，更改主题，完事。

可惜的是，因为我是尝试在我们学校的HPC节点上运转（which uses LDAP login），我估计没有权限更改系统的shell，所以也许只能在.bashrc里面添加一条zsh

.zshrc是zsh的用户定义配置文件，在里面可以更改主题。记住oh-my-zsh已经提供了许多美观耐用的主题，修改名字并source一下就能奏效了。

在.zshrc里面同样放着plugins的定义描述，对其修改也能起到对应的效果。

## command not found: compdef

这是我在使用过程中踩到的一个坑点。实际上，compdef是zsh内置的一个function，如果冒出这种情况多半是因为zsh的函数环境变量改了，可以在.zshrc里面添加fpath来修改这个问题。

对于我来说：

```
fpath=(/usr/share/zsh/$ZSH_VERSION/functions/ $fpath)
```



在fpath里面加上/usr/share/zsh/$ZSH_VERSION/functions/，这个问题就解决了。