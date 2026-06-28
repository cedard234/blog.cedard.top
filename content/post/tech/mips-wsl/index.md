---
title: 在wsl上搭建MIPS交叉编译环境
slug: mips-wsl
date: 2021-02-13T17:24:47+08:00
draft: true
categories:
    - tech
---

年初一晚上吃完饭回来想继续搞自己写了一丁点的MIPS32架构的CPU，看了一下教材想自己搞定一下GNU工具链完成对MIPS32架构汇编的编译。但是昨天把源码下到wsl里面跑了一下发现报错：

```
-bash: /home/cedar/GNUworkfile/mips-2014.05/bin/mips-sde-elf-as: cannot execute binary file: Exec format error
```

一拍脑袋，自己的PC是x86架构的，没法对MIPS进行编译。查了一下万能的stackoverflow，给我指了一条死路，让我去下一个ubuntu64 for arm试试看。今天早上起来丢进vmware，果然挂了；vmware也没法搞定arm架构的虚拟机。

下午甚至试了一下把树莓派装起来看看能不能跑，结果是同样报错。最后试了一下gcc和qemu交叉编译环境搭建，成功了，也是折腾的不行。

最后想了一下原因，树莓派是64位的，PC也是，但是目标CPU是32位base。

# 配置环境

先把qemu和配置的binfmt搞定：

```
sudo apt install qemu-user-static
sudo update-binfmts --install i386 /usr/bin/qemu-i386-static --magic '\x7fELF\x01\x01\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x03\x00\x01\x00\x00\x00' --mask '\xff\xff\xff\xff\xff\xff\xff\xfc\xff\xff\xff\xff\xff\xff\xff\xff\xf8\xff\xff\xff\xff\xff\xff\xff'
```

然后启动binfmt服务：

```
sudo service binfmt-support start
```

配置i386(32位)内核包：

```
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install gcc:i386
```

这一步很重要，因为实际上是从64位到32位出问题的。一会可以看到结果。

现在来试试。

```
cedar@cedar-grandArchive:~/assembly$ mips-sde-elf-as -mips32 inst_rom.S -o inst_rom.o
cedar@cedar-grandArchive:~/assembly$ ls
inst_rom.S  inst_rom.o
```

非常nice.

试试把i386 support关了，然后再来一次；

```
cedar@cedar-grandArchive:~/assembly$ sudo service binfmt-support stop
[sudo] password for cedar:
 * Disabling additional executable binary formats binfmt-support                                                 [ OK ]
cedar@cedar-grandArchive:~/assembly$ mips-sde-elf-as -mips32 inst_rom.S -o inst_rom.o
-bash: /home/cedar/GNUworkfile/mips-2014.05/bin/mips-sde-elf-as: cannot execute binary file: Exec format error
```

和预期一致。

# 缺少32位库

当然你还有可能出现这种情况：

```
/lib/ld-linux.so.2: bad ELF interpreter: No such file or directory
```

这个报错是因为缺少ld-linux.so.2引起的，如果是用ubuntu的话可以用apt-get来安装。

```
apt-get update
apt-get install ia32-libs
```

这样就搞定了。nice job!