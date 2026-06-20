---
title: "手搓UART"
description: 关于UART协议的碎碎念
slug: uart
date: 2021-08-27 16:52:12+0800
categories:
    - tech
tags:
    - tech
---

## 起因

大三了。从原本的ISRL实验室里逃了出来，属实是喘不过气。没有人带+教授不好约+问题无法解决，在这样的实验室呆着怎么能做好项目呢（恼）

一次偶然的机会，发现了NBS里面隐藏的CICS实验室。环境非常好，并且supervisor非常和蔼可亲。总算能静下心来做点有意义的东西了。

进实验室做的第一个项目是用现有的FPGA板子，实现UART协议。每周去一次，大概三周把这玩意搞下来了，非常有趣。

本文部分参考于https://www.cnblogs.com/liujinggang/p/9535366.html

## 什么是UART

UART，即 **universal asynchronous receiver-transmitter**,是最简单也最常见的串口通信协议。从这个名字可以看出，这个协议是非同步的，并且支持全双工通信。

虽然说是非同步的，但是这不代表两个通信设备不需要时钟连接。时钟线，发送线，接收线，就构成了最基本的UART通讯线，只需要三根。因为是串行通讯设备，所以一般来说UART的速度很慢。但是对于简单的物联网IoT设备来说，一秒钟10kB/s级别的传输已经非常足够了。

对于UART协议而言，一个byte的数据会串行化之后，分成八份发送。通常，数据线是处于高电平状态的，在开始发送的时候会将电平拉低。之后会依次发送八个对应的bit，并在发送完成之后将电平拉高。这就是最基础的UART传输方式了。

而传输速度上，一个重要的参数是波特率（Baud Rate）。不同的波特率决定了不同的传输速率。标准的波特率包括了：9600，19200，38400，57600，115200. 波特率的单位是bps，即bit per second。如果说一秒钟能够发送115200bits的信息，那么信息的传输速率就是115200/1000/8=14.4kB/s。这一般也是UART协议能够达到的最高传输速率。然而，真实情况并不能达到这么高的速率。实际上，假如说波特率为115200bits，这就说明了一个bit的持续事件为1/115200=8.7us,那么发送一个byte所需的时间就是其的八倍，69us。但是，别忘了刚才提到的开始位和停止位；为了达成可靠的传输，需要加上两个bit位数的包头和包尾；这样发送一个byte就需要8.7us的十倍即87us的时间。因此，在一秒钟的时间内，这样的循环可以执行1s/87us=11,494.25次，也就是说最大传输速率降低到了11.49kB/s.实际情况下，传输速率可能会比这更低。

## verilog实现

接下来讨论如何使用verilog和Nexyz DDR4 FPGA来实现一个标准的UART协议。

### 时钟发生器

对于一块比较标准的FPGA板子来说，我们假设FPGA的基准频率是50MHz，即每秒钟完成五千万次时钟周期，每个周期20ns。那么要在一秒钟发送115200bits，就相当于说每个bit占用了8.7us.相除得到每个bit需要占用8.7us/20ns=435个周期。因此，如果要完成一次成功的发送，使能信号应该每隔435个周期置1.

我们的目标是实现这样的一个模块，他接收标准的时钟，重置信号，以及发送以及接收器的使能信号，产生发送器和接收器的发送与读取时钟信号。

```verilog
module baudrate_gen
(
    input   I_clk                  , // 系统50MHz时钟
    input   I_rst_n                , // 系统全局复位
    input   I_bps_tx_clk_en        , // 串口发送模块波特率时钟使能信号
    input   I_bps_rx_clk_en        , // 串口接收模块波特率时钟使能信号
    output  O_bps_tx_clk           , // 发送模块波特率产生时钟
    output  O_bps_rx_clk             // 接收模块波特率产生时钟
);

parameter       C_BPS9600         = 5207         ,    //波特率为9600bps
                C_BPS19200        = 2603         ,    //波特率为19200bps
                C_BPS38400        = 1301         ,    //波特率为38400bps
                C_BPS57600        = 867          ,    //波特率为57600bps
                C_BPS115200       = 433          ;    //波特率为115200bps
                
parameter       C_BPS_SELECT      = C_BPS115200  ;    //波特率选择
                
//计数器
reg [12:0]  R_bps_tx_cnt       ;
reg [12:0]  R_bps_rx_cnt       ;

//触发block，用于发送器计数器的启动
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        R_bps_tx_cnt <= 13'd0 ;
    //如果计数器的值为1，那么就重置计数器
    else if(I_bps_tx_clk_en == 1'b1)
        begin
            if(R_bps_tx_cnt == C_BPS_SELECT)
                R_bps_tx_cnt <= 13'd0 ;
            else
                R_bps_tx_cnt <= R_bps_tx_cnt + 1'b1 ;                 
        end    
    else
        R_bps_tx_cnt <= 13'd0 ;        
end

//如果计数器为1，那么输出一次发送信号的脉冲
assign O_bps_tx_clk = (R_bps_tx_cnt == 13'd1) ? 1'b1 : 1'b0 ;
//接收器也是同样的逻辑
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        R_bps_rx_cnt <= 13'd0 ;
    else if(I_bps_rx_clk_en == 1'b1)
        begin
            if(R_bps_rx_cnt == C_BPS_SELECT)
                R_bps_rx_cnt <= 13'd0 ;
            else
                R_bps_rx_cnt <= R_bps_rx_cnt + 1'b1 ;                 
        end    
    else
        R_bps_rx_cnt <= 13'd0 ;        
end

assign O_bps_rx_clk = (R_bps_rx_cnt == C_BPS_SELECT >> 1'b1) ? 1'b1 : 1'b0 ;

endmodule
```

这样就完成了接收和发送时钟的基本逻辑。

### 发送器

对于发送器而言，他要做的事情就是根据时钟发生器发来的信号来发送自己的bit。此外，还需要额外的使能信号来启动。

发送器有如下的输入和输出：

| 输入INPUT                                                    | 输出OUTPUT                                 |
| ------------------------------------------------------------ | ------------------------------------------ |
| 时钟信号<br />全局复位<br />发送使能信号<br />发送时钟<br />并行数据流 | 串行数据流<br />发送使能信号<br />发送结束 |

其中，输出部分的发送使能信号与时钟发生器的I_bps_tx_clk_en相连，即如果这个值不是高电平则时钟发生器无需为发送器产生发送时钟。这个逻辑也适用于接收器。

verilog代码如下：

```verilog
module uart_txd
(
    input          I_clk           , // 系统50MHz时钟
    input          I_rst_n         , // 系统全局复位
    input          I_tx_start      , // 发送使能信号
    input          I_bps_tx_clk    , // 发送波特率时钟
    input   [7:0]  I_para_data     , // 要发送的并行数据
    output  reg    O_rs232_txd     , // 发送的串行数据，在硬件上与串口相连
    output  reg    O_bps_tx_clk_en , // 波特率时钟使能信号
    output  reg    O_tx_done         // 发送完成的标志
);

reg  [3:0]  R_state ;

reg R_transmiting ; // 数据正在发送标志

/////////////////////////////////////////////////////////////////////////////
// 产生发送 R_transmiting 标志位
/////////////////////////////////////////////////////////////////////////////
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        R_transmiting <= 1'b0 ;
    else if(O_tx_done)
        R_transmiting <= 1'b0 ;
    else if(I_tx_start)
        R_transmiting <= 1'b1 ;          
end

/////////////////////////////////////////////////////////////////////////////
// 发送数据状态机
/////////////////////////////////////////////////////////////////////////////
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        begin
            R_state      <= 4'd0 ;
            O_rs232_txd  <= 1'b1 ; 
            O_tx_done    <= 1'b0 ;
            O_bps_tx_clk_en <= 1'b0 ;  // 关掉波特率时钟使能信号
        end 
    else if(R_transmiting) // 检测发送标志被拉高，准备发送数据
        begin
            O_bps_tx_clk_en <= 1'b1 ;  // 发送数据前的第一件事就是打开波特率时钟使能信号
            if(I_bps_tx_clk) // 在波特率时钟的控制下把数据通过一个状态机发送出去，并产生发送完成信号
                begin
                    case(R_state)
                        4'd0  : // 发送起始位
                            begin
                                O_rs232_txd  <= 1'b0            ;
                                O_tx_done    <= 1'b0            ; 
                                R_state      <= R_state + 1'b1  ;
                            end
                        4'd1  : // 发送 I_para_data[0]
                            begin
                                O_rs232_txd  <= I_para_data[0]  ;
                                O_tx_done    <= 1'b0            ; 
                                R_state      <= R_state + 1'b1  ;
                            end 
                        4'd2  : // 发送 I_para_data[1]
                            begin
                                O_rs232_txd  <= I_para_data[1]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end
                        4'd3  : // 发送 I_para_data[2]
                            begin
                                O_rs232_txd  <= I_para_data[2]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end
                        4'd4  : // 发送 I_para_data[3]
                            begin
                                O_rs232_txd  <= I_para_data[3]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end 
                        4'd5  : // 发送 I_para_data[4]
                            begin
                                O_rs232_txd  <= I_para_data[4]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end
                        4'd6  : // 发送 I_para_data[5]
                            begin
                                O_rs232_txd  <= I_para_data[5]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end
                        4'd7  : // 发送 I_para_data[6]
                            begin
                                O_rs232_txd  <= I_para_data[6]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end
                        4'd8  : // 发送 I_para_data[7]
                            begin
                                O_rs232_txd  <= I_para_data[7]   ;
                                O_tx_done    <= 1'b0             ; 
                                R_state      <= R_state + 1'b1   ;
                            end 
                        4'd9  : // 发送 停止位
                            begin
                                O_rs232_txd  <= 1'b1             ;
                                O_tx_done    <= 1'b1             ; 
                                R_state      <= 4'd0             ;
                            end
                        default :R_state      <= 4'd0            ;
                    endcase
                end
        end
    else
        begin 
            O_bps_tx_clk_en  <= 1'b0  ; // 一帧数据发送完毕以后就关掉波特率时钟使能信号 
            R_state          <= 4'd0  ; 
            O_tx_done        <= 1'b0  ; 
            O_rs232_txd      <= 1'b1  ;  
        end 
end 

endmodule
```

### 接收器

对于接收器而言，它需要这些IO:

| 输入INPUT                                                    | 输出OUTPUT                                 |
| ------------------------------------------------------------ | ------------------------------------------ |
| 时钟信号<br />全局复位<br />接收使能信号<br />接收时钟<br />串行数据流 | 并行数据流<br />接收使能信号<br />发送结束 |

可以看到，发送器和接收器是对称的，在串并行的程度上，以及在信号处理的方面。

然而，对于接收器而言，还有一段逻辑需要处理。接收使能信号并不像发送使能信号那样，想发就置1.还记得关于UART设定的讨论吗？在没有发送信息的时候，接收线是高电平。在开始接收到信息时，电平置0.所以对于接收器来说，需要一个逻辑模块来判断接收使能信号是否为1.

```verilog
////////////////////////////////////////////////////////////////////////////////
// 功能：把 I_rs232_rxd 打的前两拍，是为了消除亚稳态
//      把 I_rs232_rxd 打的后两拍，是为了产生下降沿标志位
////////////////////////////////////////////////////////////////////////////////
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        begin
            R_rs232_rx_reg0 <= 1'b0 ;
            R_rs232_rx_reg1 <= 1'b0 ;
            R_rs232_rx_reg2 <= 1'b0 ;
            R_rs232_rx_reg3 <= 1'b0 ;
        end 
    else
        begin  
            R_rs232_rx_reg0 <= I_rs232_rxd      ;
            R_rs232_rx_reg1 <= R_rs232_rx_reg0  ; 
            R_rs232_rx_reg2 <= R_rs232_rx_reg1  ; 
            R_rs232_rx_reg3 <= R_rs232_rx_reg2  ; 
        end   
end
// 产生I_rs232_rxd信号的下降沿标志位
assign W_rs232_rxd_neg    =    (~R_rs232_rx_reg2) & R_rs232_rx_reg3 ;
```

如果接收使能信号一直是高电平，那么要开启接收器的方法就是观察这里的W_rs232_rxd_neg是否被置1.由于一个bit占用的周期数相比四个周期大得多，所以中间产生的时钟偏移可以忽略不计。

完整的接收器代码如下。

```verilog
module uart_rxd
(
    input                       I_clk               , // 系统50MHz时钟
    input                       I_rst_n             , // 系统全局复位
    input                       I_rx_start          , // 接收使能信号
    input                       I_bps_rx_clk        , // 接收波特率时钟
    input                       I_rs232_rxd         , // 接收的串行数据，在硬件上与串口相连  
    output    reg               O_bps_rx_clk_en     , // 波特率时钟使能信号
    output    reg               O_rx_done           , // 接收完成标志
    output    reg   [7:0]       O_para_data           // 接收到的8-bit并行数据
);

reg         R_rs232_rx_reg0 ;
reg         R_rs232_rx_reg1 ;
reg         R_rs232_rx_reg2 ;
reg         R_rs232_rx_reg3 ;

reg         R_receiving     ;

reg [3:0]   R_state         ;
reg [7:0]   R_para_data_reg ;

wire        W_rs232_rxd_neg ;

////////////////////////////////////////////////////////////////////////////////
// 功能：把 I_rs232_rxd 打的前两拍，是为了消除亚稳态
//          把 I_rs232_rxd 打的后两拍，是为了产生下降沿标志位
////////////////////////////////////////////////////////////////////////////////
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        begin
            R_rs232_rx_reg0 <= 1'b0 ;
            R_rs232_rx_reg1 <= 1'b0 ;
            R_rs232_rx_reg2 <= 1'b0 ;
            R_rs232_rx_reg3 <= 1'b0 ;
        end 
    else
        begin  
            R_rs232_rx_reg0 <= I_rs232_rxd      ;
            R_rs232_rx_reg1 <= R_rs232_rx_reg0  ; 
            R_rs232_rx_reg2 <= R_rs232_rx_reg1  ; 
            R_rs232_rx_reg3 <= R_rs232_rx_reg2  ; 
        end   
end
// 产生I_rs232_rxd信号的下降沿标志位
assign W_rs232_rxd_neg    =    (~R_rs232_rx_reg2) & R_rs232_rx_reg3 ;

////////////////////////////////////////////////////////////////////////////////
// 功能：产生发送信号R_receiving
////////////////////////////////////////////////////////////////////////////////
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        R_receiving <= 1'b0 ;
    else if(O_rx_done)
        R_receiving <= 1'b0 ;
    else if(I_rx_start && W_rs232_rxd_neg)
        R_receiving <= 1'b1 ;          
end

////////////////////////////////////////////////////////////////////////////////
// 功能：用状态机把串行的输入数据接收，并转化为并行数据输出
////////////////////////////////////////////////////////////////////////////////
always @(posedge I_clk or negedge I_rst_n)
begin
    if(!I_rst_n)
        begin
            O_rx_done       <= 1'b0 ; 
            R_state         <= 4'd0 ;
            R_para_data_reg <= 8'd0 ;
            O_bps_rx_clk_en <= 1'b0 ;
        end 
    else if(R_receiving)
        begin
            O_bps_rx_clk_en <= 1'b1 ; // 打开波特率时钟使能信号
            if(I_bps_rx_clk)
                begin
                    case(R_state)
                        4'd0  : // 接收起始位，但不保存
                            begin
                                R_para_data_reg     <= 8'd0             ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end
                        4'd1  : // 接收第0位，保存到R_para_data_reg[0]
                            begin
                                R_para_data_reg[0]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end
                        4'd2  : // 接收第1位，保存到R_para_data_reg[1]
                            begin
                                R_para_data_reg[1]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end
                        4'd3  : // 接收第2位，保存到R_para_data_reg[2]
                            begin
                                R_para_data_reg[2]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end 
                        4'd4  : // 接收第3位，保存到R_para_data_reg[3]
                            begin
                                R_para_data_reg[3]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end 
                        4'd5  : // 接收第4位，保存到R_para_data_reg[4]
                            begin
                                R_para_data_reg[4]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end
                        4'd6  : // 接收第5位，保存到R_para_data_reg[5]
                            begin
                                R_para_data_reg[5]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end
                        4'd7  :// 接收第6位，保存到R_para_data_reg[6]
                            begin
                                R_para_data_reg[6]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end
                        4'd8  : // 接收第7位，保存到R_para_data_reg[7]
                            begin
                                R_para_data_reg[7]  <= I_rs232_rxd      ;
                                O_rx_done           <= 1'b0             ; 
                                R_state             <= R_state + 1'b1   ;
                            end 
                        4'd9  : // 接收停止位，但不保存，并把R_para_data_reg给输出
                            begin
                                O_para_data         <= R_para_data_reg  ;
                                O_rx_done           <= 1'b1             ; 
                                R_state             <= 4'd0             ;
                            end 
                            
                        default:R_state <= 4'd0                         ;                                                      
                    endcase 
                end
        end
    else
        begin
            O_rx_done           <= 1'b0 ;
            R_state             <= 4'd0 ;
            R_para_data_reg     <= 8'd0 ;
            O_bps_rx_clk_en     <= 1'b0 ; // 接收完毕以后关闭波特率时钟使能信号
        end          
end

endmodule
```

对于接收到的并行信号，可以对其做写入or打印的处理。

## what after？

verilog的基本实现已经完成了。我们可以例化一个顶层模块，把这三个东西都放进去，然后连接输入输出。现实中，我们将用FPGA开发板实现这一点。但是在完成这一步之前，我们可以使用vivado的仿真工具先验证一下我们的猜想和代码是否正确。这一块我会再下一个博客中写出。
