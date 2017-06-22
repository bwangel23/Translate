collcted.conf(5)
================

__摘要__:

> 1. 原文地址：https://collectd.org/documentation/manpages/collectd.conf.5.shtml#name

## 名字

collectd.conf -- 系统静态信息收集服务collectd的配置文件

## 概要

```xml
BaseDir "/var/lib/collectd"
PIDFile "/run/collectd.pid"
Interval 10.0

LoadPlugin cpu
LoadPlugin load

<LoadPlugin df>
    Interval 3600
</LoadPlugin>

<Plugin df>
    ValuesPercentage true
</Plugin>

LoadPlugin ping
<Plugin ping>
    Host "example.org"
    Host "provider.net"
</Plugin>
```

## 描述

这个配置文件控制着系统信息收集服务 __collectd__ 的行为。最重要的选项是 __LoadPlugin__ ，它控制着哪个插件被载入。这些插件最终定义了 collectd 的行为。如果 __AutoLoadPlugin__ 选项被开启了，在所有的插件配置块(例如，一个<Plugin ...>块)中的显式的 __LoadPlugin__ 行可能被忽略。

这个配置文件的语法很像著名的 Web 服务器 *Apache webserver* 的配置语法。每个行包含一个选项(一个关键字和一个或多个值的列表)或者一个章节开始或结束。空行和非引号的哈希符号(#)后面的内容都会被忽略。关键字是独一无二的字符串，由字母，数字和下划线字符组成。关键字由 collectd 处理成大小写不敏感的，同时它所载入的所有插件也是大小写不敏感的。值可以是一个非引用的字符串，一个引用字符串(由双引号包裹起来)，一个数字或者一个布尔表达式。非引用的字符串由字母数字下划线组成，而且不需要引号。引用字符串由双引号包裹(")。你可以使用转义字符(\)来在字符串中包含一个双引号。数字能够使用十进制和浮点数的格式(使用点.来作为进制分隔符)。十六进制使用0x开头，八进制使用0开头。二进制的值是 __true__ 或者 __false__。

行能够在最后一个字符后，新行之前使用`\`来包裹。这允许一个长行被分割成多行。引用字符串也能够被这样包裹。然而，有个特殊的情况是新行之前的空白会被忽略掉，这样来让被包裹的行被漂亮地缩进。

配置是被按顺序地从上到下的读取和处理。所以插件是按照它们在配置文件中的列出的顺序来载入的。所以最好先加载日志插件，为了能够获取插件配置过程中的信息。同样的，除非 __AutoLoadPlugin__ 配置被开启了，否则 __LoadPlugin__ 选项就要写在对应的`<Plugin ...>`配置块之前。

## 全局选项

+ BaseDir *Directory*
> 设置根目录，在这个目录下面 RRD-files 文件被创建。同时可能有更多的子目录被创建。这个目录也是服务的工作目录。
+ LoadPlugin *Plugin*
> 载入 *Plugin* 插件，除非 __AutoLoadPlugin__ 选项已经开启，否则在载入插件的时候，需要用到这个指令。如果没有载入任何插件的话，*collectd* 将不会有太大的用处。
> 针对给定插件仅仅第一个__LoadPlugin__语句或者插件块配置是生效的。这是有用的如果你想讲配置分割到多个小文件，而且想让每个小文件是自包含的。例如，它包含了 __Plugin__ 插件块和合适的 __LoadPlugin__ 语句。在下面如果你想指定多个冲突的 __LoadPlugin__ 块，例如，它们指定不同的时间间隔，然后它们中仅仅会有一个生效(第一次遇到的那个)，其他的将会被静默地忽略。
> __LoadPlugin__ 可能是一个简单的配置语句或者是有会影响到 __LoadPlugin__ 行为的额外配置块。一个简单的语句看起来是这样的：

> `LoadPlugin "cpu"`

> 插入 __LoadPlugin__ 块中的选项能够覆盖默认的设置同时影响插件载入的方式，例如：

> ```xml
> <LoadPlugin perl>
>   Interval 60
> </LoadPlugin>
> ```

> 如下的选项可以放入到 __LoadPlugin__ 块中：
> + Global true|false
>> 如果开启的话，将会导出这个插件的所有全局符号(同时还有作为插件的依赖的所有载入的库)。同时，如果系统支持的话，这些符号可用于解析后续载入的插件中的未解析符号。

>> 这个是很有用的，甚至可以说是必须的。例如，当加载一个插件将一些脚本语言嵌入到服务中时(例如， Python 或者 Perl 插件)。脚本语言通常提供一些加载C扩展的工具。这些扩展需要由解释器提供的符号，它将会作为 collectd 各自插件的依赖来载入。请参考相关文档([collectd-perl(5)](https://collectd.org/documentation/manpages/collectd-perl.5.shtml) 或者 [collectd-python(5)](https://collectd.org/documentation/manpages/collectd-python.5.shtml))来了解更多的细节。

>> 默认情况情况下这个选项是被关闭的。但当使用名为 Python 或 Perl 的插件的时候，这个选项默认开启来让平均用户不必关注这个低级别的链接内容。

> + Interval *Seconds*

>> 设定插件收集指标时的时间间隔。这个将会覆盖全局 __Interval__ 设置。如果一个插件用指定时间间隔来提供自己的支持，这个设置(插件指定的)将会被优先采用。

> + AutoLoadPlugin false|true

>> 当设置成 __false__ 的时候(默认情况)，每个插件需要精确地导入，通过上面文档中提到的 __LoadPlugin__ 语句。如果一个 __<Plugin ...>__ 块已经遇到了，但是没有为这个已经被注册的插件设置处理回调函数，一个警告将会被记录同时这个块会被忽略。

>> 当设置成 __true__ 的时候，精确的 __LoadPlugin__ 语句不再需要了。每个 __<Plugin ...>__ 块的行为看起来像被用 __LoadPlugin__ 语句立即处理了一样。__LoadPlugin__ 语句仍然需要当一个插件需要被载入但是没有提供任何配置的时候，例如 *Load Plugin*。

> + CollectInternalStats false|true

>> 当被设置成 __true__ 的时候，各种关于 collectd 服务的指标将会被收集，同时使用 "collectd" 作为插件名。默认为 __false__。

>> 如下的指标将会被报告：

>> + collectd-write_queue/queue_length
>>> 指标的值是当前写入队列的长度。你通过 __WriteQueueLimitLow__ 和 __WriteQueueLimitHigh__ 选项可以限制队列长度。
>> + collectd-write_queue/derived-dropped
>>> 指标的值是由于超出队列长度丢弃的元素个数。如果这个值是非0的话，你的系统不能处理所有输入的指标，为了防止它自己过载而丢弃了一些指标。
>> + collectd-cache/cache_size
>>> 元素指标缓存的数量(或者你能够使用 [collectd-unixsock(5)](https://collectd.org/documentation/manpages/collectd-unixsock.5.shtml) 交互的缓存)。

## 插件选项

一些插件注册的时候可能有它自己的选项。这些选项必须被包裹在`Pulgin-` 部分中。这些选项存在依赖于插件是否被使用，一些插件也需要额外的配置。例如`apache plugin`，需要在你想要收集数据的 Web 服务器中配置 `mod_status` 模块。

这些插件被列在下面，即使他们不需要在 collectd 的配置文件中写任何配置。

所有插件的列表和每个插件简短的描述能够在源码附带的`README`文件中找到，希望二进制安装包也能做到这样。

### Plugin logfile

+ LogLevel debug|info|notice|warning|err

> 设置日志等级。例如，如果设置成`notice`的话，那么所有事件严重性为`notice`，`warning`或者`err`将会被提交到 syslog 服务。
> 注意，调试等级仅仅当 collectd 服务编译进了调试支持的时候才能被使用

+ File *File*

> 设置写日志信息的文件。特殊的字符 __stdout__ 或者 __stderr__ 能够被用来分别写到标准输出或者标准错误频道。当然这个只有在*collectd* 在前台或者非服务模式下运行时才有效。

+ Timestamp true | false
> 在所有行首打印当前时间。默认是 __true__。

+ PrintSeverity true | false
> 当开启的时候，默认在日志消息的行首打印严重性，例如"warning"。默认为 __false__。

### Plugin syslog

+ LogLevel debug|info|notice|warning|err

> 设置日志等级。例如，如果设置成`notice`的话，那么所有事件严重性为`notice`，`warning`或者`err`将会被提交到 syslog 服务。
> 注意，调试等级仅仅当 collectd 服务编译进了调试支持的时候才能被使用

+ NotifyLevel OKAY|WARNING|FAILURE

> 控制哪些提示应该被发送到syslog。默认的行为是不发送任何东西。设置为程度较轻的值意味着会记录程度更严重的提醒：设置这个值为 __OKAY__ 意味着会发送所有的提醒到 syslog，将这个值设置为 __WARNING__ 意味着会发送 __WARNING__ 和 __FAILURE__ 提醒同时丢弃 __OKAY__ 提醒。设置这个选项为 __FAILURE__ 讲仅仅会发送 failure 信息到 syslog。

### Pulgin network

网络插件能够从远端的 collectd 实例上同时发送和接收数据。一般从网络上接收到的数据通常不会再被转发，但是这个能够通过下面的 __Forward__ 选项来激活。

默认的 IPv6 多播组是 ff18::efc0:4a42 ，默认的 IPv4 多播组是 239.192.74.66。默认的 UDP 端口是 __25826__ 。

__Server__ 和  __Listen__ 选项能够被用来作为一个单个选项或者一个块。当作为一个块的时候，给出的选项仅仅对这些套接字有效。如下的例子将会到处这些指标两次：一次发送到一个“内部”服务器(没有加密和签名) ,一次发送到一个外部的服务器(经过加密和签名)。

```xml
<Plugin "network">
    # Export to an internal server
    # (demonstrates usage without additional options)
    Server "collectd.internal.tld"

    # Export to an external server
    # (demonstrates usage with additional options)
    <Server "collectd.external.tld">
        SecurityLevel "sign"
        Username "myhostname"
        Password "ohl0eQue"
    </Server>
</Plugin>
```

+ <Server Host[Port]>

> __Server__ 语句块设置发送数据报的服务器。这个语句为了发送多个报文给不同的服务器，可能会多次发生。
> 参数 *Host* 可以是一个主机名或者是一个 IPv4 或者 IPv6 的地址。可选的第二个参数指定了端口号或者服务的名称。如果没有给出的话，第二个参数默认是 __25826__
> 如下的选项将会在 __Server__ 块内部被识别：
> + SecurityLevel Encrypt|Sign|None
>> 设置在网络通信上你需要的安全等级。当安全等级被设置成 __Encrypt__ 的时候，在网络上发送的数据将会通过 *AES-256* 来安装。确保包的完整性使用的是*SHA-1*算法。当设置成 __Sign__ 的时候，在网络上传输的数据将会使用 *HMAC-SHA-256* 消息认证码来进行签名。当设置成None的时候，数据将会在没有任何安全措施的情况下发送。
> + Username *Username*
>> 设置要传输的用户名。这个由服务器用来查找密码。参见下面的 __AuthFile__。除了 __None__ ，所有的安全等级都需要这个设置。
>> 只有当网络插件被 *libgcrypt* 被链接的时候，这个特性才可用。
> + Password *Password*
>> 为这个套接字连接设置密码(共享秘钥)。除了 __None__ ，所有的安全等级都需要这个设置。
>> 只有当网络插件被 *libgcrypt* 被链接的时候，这个特性才可用。
> + Interface *Interface name*
>> 设置 IP 包的网络出口。这个至少适用于 IPv6，也可能试用与 IPv4。如果这个选项不适用的话，未定义的或者不存在的接口名会被使用，默认的行为是让内核去选择合适的接口。请注意，手动选择单播流量只有在极少数的情况下才需要。
> + ResolveInterval *Seconds*
>> 设置为了默认主机重新解析 DNS 的间隔秒数。这个用来强制使用定期的DNS查询来支持高可用的特性。如果没有指定的话，不会尝试去重新解析。

+ <Listen Host[Port]>

> 监听语句设置绑定的接口，如果在服务中设置中找到了多个语句，将会绑定多个接口。

> 参数 *Host* 可以是一个主机名，一个 IPv4 或者 IPv6 地址。如果参数是一个多播地址，服务将会加入那个多播组。可选的第二个参数是指定服务监听的端口号，如果没有给出的话，默认使用25826。

> 如下的选项将会被在 __<Listen>__ 块内识别：

> + SecurityLevel Encrypt|Sign|None

>> 为网络通信设置你需要的安全等级。当安全等级设置成 __Encrypt__ 的时候，只有被加密的数据才会被接受。包的完整性加密使用的是 *SHA-1* 算法。当设置成 *Sign* 的时候，只有被加密的数据才会被接受。当设置成 __None__ 的时候，所有的数据都会被接受。只有当 __AuthFile__ 选项设置的时候，加密数据才可能被解密。

>> 只有当网络插件被 *libgcrypt* 被链接的时候，这个特性才可用。

> + AuthFile *Filename*

>> 设置一个文件去映射用户名和密码。这些密码用来去验证签名和解密网络包。如果 __SecurityLevel__ 选项设置为 __None__ 的时候，这个选项就是可选的。如果给出的话，签名将会被验证同时加密的数据也会被解密。否则的话，签名数据就会在没有经过验证的情况下被接受，加密的数据也不会被解密。对于其他的安全等级是强制性的。

>> 文件格式的检验非常简单：每个行由用户名，冒号，任意数量的空格，密码组成。为了去演示，一个文件例子能够像下面这样使用：
>> ```
>>  user0: foo
>>  user1: bar
>> ```

>> 每次一个包被接受了以后，文件的修改时间将会通过 *stat(2)* 来检查，如果文件被更改过了，它的内容将会被重新读。当文件被读取的时候，它将会使用 *fcntl(2)* 来锁定。

> + Interface *Interface Name*

>> 明确地指定 IP 包的入口网卡。这个至少可以在 IPv6 上使用，在 IPv4 上也可以使用。如果这个选项没有被应用，未定义的或者不存在的网卡名将会被指定，默认的行为是，让内核去选择合适的接口。这样的话，如果它到达了给定的接口，进入的流量将会被接受。

+ TimeToLive 1-255

> 设置发送包的生存时间，这个将会应用到所有的 IPv4，IPv6的广播和单播包。默认是不会改变这个值，这意味着在大多数的操作系统上多播包将会使用`TTL = 1`来发送。

+ MaxPacketSize 1024-65535

> TODO

+ Forward *true|false*

> TODO

+ ReportStatus true|false

> 网络插件不仅能够接收和发送统计指标，它也能创建关于它自己的统计值。收集的数据包括接受和发送的包的字节长度和数量，接收队列的长度和处理值的数量。当这个设置为 __true__ 的时候，网络插件将会使这些统计指标可用，默认为 __false__ 。
