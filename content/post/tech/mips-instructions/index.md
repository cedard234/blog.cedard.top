---
title: 编译第一条MIPS指令
slug: mips-instructions
date: 2021-02-16T20:05:35+08:00
draft: true
categories:
    - tech
---

本文摘自https://blog.csdn.net/qq_42650988/article/details/103532682



------





## Linux学习的点点滴滴（二）

其实本文跟Linux关系并不是那么大，是我在自己写CPU的过程中总结的东西，之前只用Word写在自己电脑里了，想着哪天放到博客上。
本文是在写CPU进行测试的时候需要将汇编翻译成机器码的过程，刚开始学的时候，也遇到了一些小问题，在此记录。

### 一、安装GNU工具链

gcc编译器使用的是龙芯公司的，使用了MIPS架构。[下载地址](http://ftp.loongnix.org/toolchain/gcc/release/gcc-4.3-ls232.tar.gz)
进入Linux虚拟机的`/opt`文件夹（其实哪个都无所谓），在终端输入`tar -zxvf gcc-4.3-ls232.tar.gz`，这里`tar -zxvf`是`.tar.gz`文件的解压缩命令，后面会详细介绍其他的[解压缩命令](https://blog.csdn.net/qq_42650988/article/details/103532682#tar)
解压缩之后，首先配置环境变量，找到当前用户的文件夹下的隐藏文件`.bashrc`，如果遇到权限不够，用`chmod`修改权限之后，打开文件，在文件最后一行加上
`export PATH=”$PATH:password/opt/gcc-4.3-ls232/bin”`
在终端输入`echo $PATH`查看已经配好的环境变量，（echo是回显命令，是常见的脚本命令）
![echo](https://img-blog.csdnimg.cn/20191213201547316.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
然后输入`mipsel-linux-gcc -v`，如下图表示GNU工具链安装完成：
![GNU](https://img-blog.csdnimg.cn/20191213201800255.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
有个很坑的地方，如果提示：bash ./ 没有那个文件或目录，是因为Ubuntu是64位的，没有32位的运行库，安装一个32位运行库即可：`apt-get install lib32z1`
至此基本的准备工作就完成了，但是在此过程中不熟悉Linux系统会导致一些列问题，在此总结一下。

### 二、解压缩命令

常见的解压缩命令

```shell
tar
-c: 建立压缩档案
-x：解压
-t：查看内容
-r：向压缩归档文件末尾追加文件
-u：更新原压缩包中的文件
这五个是独立的命令，压缩解压都要用到其中一个，可以和别的命令连用但只能用其中一个。下面的参数是根据需要在压缩或解压档案时可选的。

-z：有gzip属性的
-j：有bz2属性的
-Z：有compress属性的
-v：显示所有过程
-O：将文件解开到标准输出
下面的参数-f是必须的
-f: 使用档案名字，切记，这个参数是最后一个参数，后面只能接档案名。
tar -cf all.tar *.jpg
这条命令是将所有.jpg的文件打成一个名为all.tar的包。-c是表示产生新的包，-f指定包的文件名。
tar -rf all.tar *.gif
这条命令是将所有.gif的文件增加到all.tar的包里面去。-r是表示增加文件的意思。
tar -uf all.tar logo.gif
这条命令是更新原来tar包all.tar中logo.gif文件，-u是表示更新文件的意思。
tar -tf all.tar
这条命令是列出all.tar包中所有文件，-t是列出文件的意思
tar -xf all.tar
这条命令是解出all.tar包中所有文件，-t是解开的意思

//压缩
tar -cvf jpg.tar *.jpg //将目录里所有jpg文件打包成tar.jpg 
tar -czf jpg.tar.gz *.jpg   //将目录里所有jpg文件打包成jpg.tar后，并且将其用gzip压缩，生成一个gzip压缩过的包，命名为jpg.tar.gz
tar -cjf jpg.tar.bz2 *.jpg //将目录里所有jpg文件打包成jpg.tar后，并且将其用bzip2压缩，生成一个bzip2压缩过的包，命名为jpg.tar.bz2
tar -cZf jpg.tar.Z *.jpg   //将目录里所有jpg文件打包成jpg.tar后，并且将其用compress压缩，生成一个umcompress压缩过的包，命名为jpg.tar.Z
rar a jpg.rar *.jpg //rar格式的压缩，需要先下载rar for linux
zip jpg.zip *.jpg //zip格式的压缩，需要先下载zip for linux

//解压
tar -xvf file.tar 			//解压 tar包
tar -xzvf file.tar.gz 		//解压tar.gz
tar -xjvf file.tar.bz2   	//解压 tar.bz2
tar -xZvf file.tar.Z   		//解压tar.Z
unrar e file.rar 			//解压rar
unzip file.zip				//解压zip

//总结
1、*.tar 用 tar -xvf 解压
2、*.gz 用 gzip -d 或者gunzip 解压
3、*.tar.gz 和 *.tgz 用 tar -xzf 解压
4、*.bz2 用 bzip2 -d或者用bunzip2 解压
5、*.tar.bz2 用 tar -xjf 解压
6、*.Z 用 uncompress 解压
7、*.tar.Z 用tar -xZf 解压
8、*.rar 用 unrar e解压
9、*.zip 用 unzip 解压*
12345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152
```

### 三、关于环境变量

类似于Windows下的环境变量，本质含义就是让系统运行一个程序时，不仅仅要在当前目录下面寻找，还要到PATH指定的路径下寻找，此操作实际简化了程序执行的复杂度，提高了效率。
以上面的GCC路径为例，我们写入的PATH路径为：`export PATH=”$PATH:/opt/gcc-4.3-ls232/bin”`
什么意思？可以把PATH看成一个字符串，用`“/”、“：”、“\$”` 等符号进行划分，系统根据划分的字符串寻找目标地址。因为PATH是一个字符串，用“$PATH”表示引用这个字符串，就是表示PATH所指的内容；`：`是Linux中分隔符，相当于Windows中的`；`，因此该语句表示在原有的PATH路径下再加上`/opt/gcc-4.3-ls232/bin`路径，我们在终端中检验一下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203136581.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
实际上，若要仅仅配置GCC，不需要加上之前的PATH路径，因此只要这样写即可：
`export PATH=”/opt/gcc-4.3-ls232/bin"`.我们在终端中再次输入echo $PATH，结果证明是正确的，gcc安装无误：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203218185.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)

### 四、编译汇编指令

我们先编写一组汇编指令，命名为`inst_rom.S`
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203317375.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
然后我们在终端中输入指令:
`mipsel-linux-as -mips32 inst_rom.S -o inst_rom.o`，表示用as工具将inst_rom.S文件编译成`inst_rom.o`文件再输入：
`mipsel-linux-ld -T ram.ld inst_rom.o -o inst_ram.om`，表示将`inst_rom.o`文件链接成`inst_rom.om`文件。再输入：
`mipsel-linux-objcopy -O binary inst_rom.om inst_ram.bin`，根据.om文件得到了bin文件，再输入：
`mipsel-linux-objdump -D inst_rom.om > inst_ram.asm`，对汇编指令进行反汇编，得到与机器指令对应的二进制字。
最后将Bin2MEM.exe拷贝到与inst_rom系列文件相同的目录下，执行
`./Bin2Mem.exe -f inst_rom.bin -o inst_rom.data`
第一次执行应该需要修改Bin2Mem.exe文件的权限，输入：
`Chmod 777 Bin2Mem.exe`，最终转化为与Vivado程序中读入的文件类型（.data），执行结果如图：
![没有描述~~~](https://img-blog.csdnimg.cn/20191213203518724.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
生成的文件：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203550517.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
我们打开inst_rom.data文件查看：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203609232.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
这便是我们一开始那几条汇编指令的机器指令。

### 五、大小端地址

大端（存储）模式：是指一个数据的低位字节序的内容放在高地址处，高位字节序存的内容放在低地址处。
小端（存储）模式：是指一个数据的低位字节序内容存放在低地址处，高位字节序的内容存放在高地址处。（可以总结为“小小小”即低位、低地址、小端）
在上述的例子中，我们发现原来的机器指令34011100变成了00110134，高位数据放在了地址的高位，是小端存储，这样看上去不是很方便，我们可以修改编译指令改变最终编译的结果，输入`mipsel-linux-as -help`查看帮助：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203859994.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203906390.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
我们修改指令：
![在这里插入图片描述](https://img-blog.csdnimg.cn/2019121320391995.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
查看inst_rom.data文件：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213203929149.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
已经修改为大端模式了。我们需要修改为大端模式，因为该OpenMIPS就是大端模式。

### 六、Make工具

每次都输入四个（加上.asm一共五个）指令显得很麻烦，我们可以编写一个脚本来自动执行命令。
make便是Linux上的一个脚本，当我们只输入make命令的工作流程是：

1. make会在当前目录下找名字叫“Makefile”或“makefile”的文件；
2. 如果找到，它会找文件中的第一个目标文件（target），在上面的例子中，他会找到“inst_rom.data”这个文件，并把这个文件作为最终的目标文件；
3. 如果inst_rom.data文件不存在，或是.data所依赖的后面的 .om 文件的文件修改时间要比.data这个文件新，那么make会执行下面定义的命令来生成.data文件；
4. 如果.data所依赖的.om文件也存在，那么make会在当前文件中找目标为.om文件的依赖性，如果找到再根据命令生成.om文件（这是一个递归的过程）；

如果在找寻的过程中，出现了被依赖的文件找不到的错误，那么make就会直接退出，并报错。
如果在一条依赖链中，比如：A依赖B，B依赖C，C依赖D。那么当D更新后，make发现D比C新则会重新构建C，以此类推，最终A也会被更新。
简单的说，makefile带来的好处就是——自动化编译，只要一个make命令，所有工程和文件自动编译，类似于Shell的.sh和cmd的.bat

我们编写如下代码：

```shell
ifndef CROSS_COMPILE
	CROSS_COMPILE = mipsel-linux-
endif
CC = $(CROSS_COMPILE)as
LD = $(CROSS_COMPILE)ld

OBJCOPY = $(CROSS_COMPILE)objcopy
OBJDUMP = $(CROSS_COMPILE)objdump

OBJECTS = inst_rom.o
export CROSS_COMPILE
all:inst_rom.data inst_rom.om inst_rom.o inst_rom.bin inst_rom.asm

%.o:%.S
	$(CC) -mips32 -EB $< -o $@

inst_rom.om:ram.ld $(OBJECTS) 
	$(LD) -EB -T ram.ld $(OBJECTS) -o $@

inst_rom.bin:inst_rom.om
	$(OBJCOPY) -O binary $< $@

inst_rom.asm:inst_rom.om
	$(OBJDUMP) -D $< >$@

inst_rom.data:inst_rom.bin
	./Bin2Mem.exe -f $< -o $@

clean:
	rm -f *.o *.om *.bin *.data
123456789101112131415161718192021222324252627282930
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20191213204254687.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyNjUwOTg4,size_16,color_FFFFFF,t_70)
其中 `$<` 表示第一个依赖文件的名称，`$@` 表示目标的完整名称

至此，我们用gcc编译汇编指令生成机器码的过程就做完了。

### 七、ram.ld链接代码

```shell
MEMORY
        {      
        ram(RW)    : ORIGIN = 0x00000000, LENGTH = 0x00001000
        }
SECTIONS
{
	  /*
	  For some reason the linker script can't see the _reset_vector symbol 
	  (even if we declare it global), so we explicitly set it. */
	.text :
        {
        *(.text)
        } > ram

        .data :
        {
        *(.data)
        } > ram
        .bss :
        {
        *(.bss)
        } > ram
        .stack  ALIGN(0x10) (NOLOAD):
        {
        *(.stack)
        _ram_end = .;
        } > ram
}
ENTRY (_start)
1234567891011121314151617181920212223242526272829
```

### 八、Bin2Mem.c代码

```c
#include <stdlib.h>
#include <stdio.h>

char *option_invalid  = NULL;
char *option_file_in  = NULL;
char *option_file_out = NULL;

FILE *file_in_descriptor  = NULL;
FILE *file_out_descriptor = NULL;

void exception_handler(int code) {
    switch (code) {
        case 0:
            break;
        case 10001:
            printf("Error (10001): No option recognized.\n");
            printf("Please specify at least one valid option.\n");
            break;
        case 10002:
            printf("Error (10002): Invalid option: %s\n", option_invalid);
            break;
        case 10003:
            printf("Error (10003): No input Binary file specified.\n");
            break;
        case 10004:
            printf("Error (10004): Cannot open file: %s\n", option_file_in);
            break;
        case 10005:
            printf("Error (10005): Cannot create file: %s\n", option_file_out);
            break;
        default:
            break;
    }

    if (file_in_descriptor  != NULL) {
        fclose(file_in_descriptor);
    }
    if (file_out_descriptor != NULL) {
        fclose(file_out_descriptor);
    }
    exit(0);
}

int main(int argc, char **argv) {
 
    int i=0,j=0;
    unsigned char temp1,temp2,temp3,temp4;
    unsigned int option_flag = 0;

    while (argc > 0) {
        if (** argv == '-') {
            (*argv) ++;
            switch (**argv) {
                case 'f':
                    option_flag |= 0x4;
                    argv ++;
                    option_file_in = *argv;
                    argc --;
                    break;
                case 'o':
                    option_flag |= 0x8;
                    argv ++;
                    option_file_out = *argv;
                    argc --;
                    break;
                default:
                    option_flag |= 0x1;
                    (*argv) --;
                    option_invalid = *argv;
                    break;
            }
        }
        argv ++;
        argc --;
    }

    file_in_descriptor = fopen(option_file_in, "rb");
    if (file_in_descriptor == NULL) {
        exception_handler(10004);
    }

    file_out_descriptor = fopen(option_file_out, "w");
    if (file_out_descriptor == NULL) {
        exception_handler(10005);
    }
    
    while (!feof(file_in_descriptor)) {
         
            fscanf(file_in_descriptor, "%c", &temp1);
            fscanf(file_in_descriptor, "%c", &temp2);
            fscanf(file_in_descriptor, "%c", &temp3);
            fscanf(file_in_descriptor, "%c", &temp4);

            if(!feof(file_in_descriptor)) {
             fprintf(file_out_descriptor, "%02x", temp1);
             fprintf(file_out_descriptor, "%02x", temp2);
             fprintf(file_out_descriptor, "%02x", temp3);
             fprintf(file_out_descriptor, "%02x", temp4);
             fprintf(file_out_descriptor, "\n");
            } 
    }

    exception_handler(0);
    return 0;
}
```