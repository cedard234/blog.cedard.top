---
title: 编写module file
slug: module-file
date: 2022-04-03T14:18:05+08:00
description: 小心运维人
draft: true
categories:
    - tech
tags:
    - tech
---

本文介绍的是lua based lmod环境变量模组。如果你用的是一台小型私人服务器，那么你根本不需要这种玩意。

也就是说，Lmod只有在大型服务器，有非常多用户使用，并且还需要非常多不同版本或者不同种类的基本编译套件时，可以发挥最大用处。如果你只是用一台私人服务器跑东西，那么你要做的只是把所有的binary文件目录都加入环境变量PATH里，再把所有load library加到环境变量LD_LIBRARY_PATH里面。

这两天开始苦逼地当学校超算的运维，于是需要搞定这种玩意。稍微写一下博客。学校超算组的链接：https://ntuhpc.org/

# 什么是Lmod

Lmod is a Lua based module system that easily handles the MODULEPATH Hierarchical problem. Environment Modules provide a convenient way to dynamically change the users’ environment through modulefiles. This includes easily adding or removing directories to the PATH environment variable. Modulefiles for Library packages provide environment variables that specify where the library and header files can be found.

（小学二年级英语）：Lmod是一个基于Lua的模组系统，可以简单解决modulepath的等级分划问题（dependency）。Lmod提供了一种简便的方法来修改用户的运行环境，通过编写modulefiles的方法。这包括了对环境变量PATH的增删。而Modulefile则提供了对于库文件和头文件的说明。

那么，Lmod有多方便呢？举个例子：假如说你把python3.8安装在了自己的家目录，但是忘了加到PATH里面去；那么你在terminal里面敲一个python3，就会有这种提示：

```
[root@fedora ~]# python3
-bash: python3: command not found
```

你感到不解，于是你尝试echo $PATH，才发现python原来没有被加到自己的环境变量里去。你感到很恼火，于是修改了一下自己的.bashrc，加了一条export。

但是在将来的一天，你把这件事忘了；但是python3.9更新了！于是你在自己的服务器上安装了python3.9，仍然安装在自己的家目录；当你在terminal里敲击python3，冒出来的却是python3.8的interactive session。你这才想起来自己的环境变量里面写的是python3.8，于是你十分恼火，再进到.bashrc里，把3.8改了。

当然，这说的是一件特殊的例子，也许python3.8并不影响你的运行效率；但是如果，你在编译一个大型项目，里面提供了N套编译方案，可以使用N套不同的，互相不兼容的编译套件呢？（比如gcc和icc）

没有Lmod的话，你就只能不停地修改PATH，或者高明一点，写一个脚本帮你解决，每次都要运行，每次有新的模组进来都要修改。于是聪明的程序员们用lua写了Lmod，一劳永逸地彻底解决这个问题。

有了Lmod，你在terminal里面就只需要敲击module av(ailable)，就会有以下的东西蹦出来：

```
[root@fedora ~]# module av

--------------------------------------------------- /opt/modulefile ----------------------------------------------------
   python3/3.8				python3/3.9
```

那么接下来的事情就轻松很多。如果你想要使用3.8，那么你就可以module load python3/3.8；如果你想要换成3.9，那么你就可以module load python3/3.9.

如何让module av显示出所有系统中，系统管理员想让你看到的所有module呢？这要通过编写modulefile来解决。

## 编写modulefile

modulefile不难写：https://lmod.readthedocs.io/en/latest/015_writing_modules.html

简而言之，modulefile的位置可以放在任何位置，只要它也被包括进module本身的查询list中。举个例子，我们将cuda安装在/usr/local/cuda-11.4中，我们就可以在/opt/modulefile里mkdir一个新的目录cuda，里面再写一个文件11.4.lua，这表示这是module cuda下属的版本11.4.

```
[root@fedora cuda]# cat 11.4.lua
help([[
https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html
]])
prepend_path( "PATH",           "/usr/local/cuda-11.4/bin")
prepend_path( "LD_LIBRARY_PATH","/usr/local/cuda-11.4/lib64")
[root@fedora cuda]#
```

help语句在module help的时候比较有用，他会告诉你，这个module的用处是什么。这里是直接的来自nvidia的url。

prepend_path就很好理解了。第一个slot放的是变量名，第二个则是需要prepend的path。也就是说，在执行module load cuda的时候，会执行这两行命令。

除去prepend_path之外，还有一个API可能会比较有用，setenv。当然也很好理解，这种可能在gcc的modulepath中比较有用。

当然，在编写完modulefile之后，不要忘了把modulepath添加进module自己，否则module av不会显示这个目录。添加的方法是，module use $(需要添加的目录)

以上。
