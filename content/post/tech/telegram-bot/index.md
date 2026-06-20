---
title: 关于telegram bot的琐碎
slug: telegram-bot
date: 2021-04-30T01:41:27+08:00
description: 后记：这玩意天天骂我
draft: true
categories:
    - tech
---

前因：

> Patchy 
> 隔壁之前有人弄个单纯随机复读的
>
> Patchy
> 已经通过了群友的人类认可
>
> Cedar
> 就是听了您的那个，觉得很有意思
>
> Cedar
> 所以手撸了一个

------

笑死，根本笑不死。

俺敲代码从来没有一个目标的，因为我就是门外汉（自豪）

之前听群友说，隔壁群曾经出了一个bot，是不是复读群友消息结果没有人发现这玩意是bot，我直接宣布这个bot通过图灵测试（迫真）

所以说，自己想搞一个自己的版本，不仅能复读，还能有其他生草功能。顺便一窥telegram的bot是怎么实现的。

# bot的出生

bot是从bot中生出来的，**生殖隔离确认**

这个生bot的bot是telegram的一个官方bot，名叫[@botfather](https://t.me/BotFather) .管生bot的人叫father无论如何都很奇怪吧。

当你向他输入/newbot指令的时候，一个bot的诞生就开始了。跟随他的指令，命名你的新bot。你输入的名字将会成为这个bot的用户名。

当bot生成之后，你可以通过/mybots来查看或者编辑这个bot的相关信息。

最重要的是，botfather在创建完这个bot之后，会给予一个独一无二的identifier,那就是这个bot的token。只有在token对应的时候，你才可以指挥你的bot。

# pytelegrambot相关

我是用pytelegrambot这个库写的，这个库十分优雅而强大，足够应付所有你想实现的功能。

```python
pip install pyTelegramBotAPI
```

安装方法如上。当你安装好了之后，新建一个python文件，在顶部写上：

```python
import telebot

bot = telebot.TeleBot("TOKEN", parse_mode=None)
```

这样，bot就以token的形式实例化出来了。

根据pytelegrambot的官方文件，一个bot的例子是：

```python
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")
```

这里定义了一个函数，对于/start和/help这两个指令，bot将会执行send_welcome这个函数，并发送信息"Howdy, how are you doing?“。

这里，pytelegrambot提供了一个十分友好的装饰器@bot.message_handler，可以对发给bot的消息进行筛查。查阅源码可知：

```python
    def message_handler(self, commands=None, regexp=None, func=None, content_types=None, ** kwargs):
        """
        Message handler decorator.
        This decorator can be used to decorate functions that must handle certain types of messages.
        All message handlers are tested in the order they were added.

        Example:

        bot = TeleBot('TOKEN')

        # Handles all messages which text matches regexp.
        @bot.message_handler(regexp='someregexp')
        def command_help(message):
            bot.send_message(message.chat.id, 'Did someone call for help?')

        # Handle all sent documents of type 'text/plain'.
        @bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])
        def command_handle_document(message):
            bot.send_message(message.chat.id, 'Document received, sir!')

        # Handle all other messages.
        @bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
        def default_command(message):
            bot.send_message(message.chat.id, "This is the default command handler.")

        :param commands: Optional list of strings (commands to handle).
        :param regexp: Optional regular expression.
        :param func: Optional lambda function. The lambda receives the message to test as the first parameter. It must return True if the command should handle the message.
        :param content_types: This commands' supported content types. Must be a list. Defaults to ['text'].
        """
```

这个装饰器可以用指令，正则，lamda函数以及内容的方式对发给bot的信息进行筛查，并确定是否执行你所定义的函数。

但是，当你执行这个python文件，bot并不会启动，这是因为这只是个定义性的代码文件，而并没有让bot跑起来。你需要在结尾加上：

```python
bot.polling()
```

这个polling方法可以让这个bot不断监听进入的消息，并按照不同情况执行上文所提到的message handler.但是这个方法实际上有坑；如果说进入的消息过多的话，服务器会认定受到了攻击，并停止这个bot。此时你的python文件会以”远程服务器强制终止了一个现有链接“停止。

为了避免这种情况的出现，pytelegrambot的api十分贴心地提供了另外一个方法：

```python
bot.infinity_polling()
```

从这个名字就可以看出来，当polling失败的时候，这个bot会重新建立连接，周而复始。

# what now?

在了解了这些基本的操作之后，你已经可以写一个复读机bot了。原理十分简单，如果要使复读是随机的话，你只需要求助于random库即可。

pytelegrambot还提供了其他好用的api，比如说发meme，发图片，甚至是让bot在群组中执行管理员权限，等等。限制你发挥的仅仅是你的想象力。

[我的bot](https://t.me/cedar_234_bot)能做到的事情有，时不时以*某种方式*复读，时不时发怪图，时不时说怪话。

你可以尝试和他对话，或者把他丢到某个群里。

你也可以在[我的github仓库](https://github.com/cedarsaigyouji/nonsense_chat_bot)里面找到这玩意。

以上。



# 题外话

对了，你如果要让这个bot一直开着，你就得让这个程序一直开着。如果你只有一台电脑的话，那就意味着你这台电脑没法关机。

而我直接整了个raspi4b，放在上面就跑这玩意。下次聊聊我还用树莓派干了些什么。

