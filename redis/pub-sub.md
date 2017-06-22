Pub/Sub
=======

__摘要__:

> 1. 原文地址: http://redis.io/topics/pubsub

SUBSCRIBE，UNSUBSCRIBE 和 PUBLISH 实现了一个消息发布订阅范式，在这个范式中，发送者(publisher)不需要通过程序去发送他们的消息给特定的接收者(subscriber)。相反，发送字符化的消息到频道中，不需要事先知道哪个订阅者(如果存在的话)在频道中。订阅者可能对一个或者多个频道感兴趣，仅仅订阅他们感兴趣的频道就可以了，不需要知道这个频道中有哪些发布者(如果存在的话)。这个在发布者和订阅者之间解耦，可以有更好的可扩展性和更灵活的网络拓扑。
例如为了订阅频道 foo 和 bar，客户端发出了一个 SUBSCRIBE 命令同时提供了频道的名字：

```
SUBSCRIBE foo bar
```

由其他客户端发送到这个频道的消息将会由 redis 推送到订阅了这些频道的客户端。
一个订阅了一个或者多个频道的客户端应该不能发送命令了，尽管它能够从其他频道中订阅或者取消订阅。订阅和取消订阅操作的回复是以消息的形式发送的，所以客户端能够通过消息的第一个元素来知道消息的类型，从而仅仅读相关的消息流。在一个订阅了的客户端的上下文中允许的命令是 SUBSCRIBE, PSUBSCRIBE, UNSUBSCRIBE, PUNSUBSCRIBE, PING 和 QUIT。

## 推送消息的格式

一个消息是一个数组相应包括三个元素：

第一个元素是消息的类型：

> + subscribe: 表示我们成功地订阅了以响应第二个元素命名的频道。第三个参数表示我们当前订阅的频道的数量。
> + unsubscribe: 表示我们成功地取消订阅了以响应第二个元素命名的频道。第三个参数表示我们当前订阅的频道的数量。当最后一个参数为0的时候，表示我们没有再订阅任何频道。当我们在 Pub/Sub 状态之外的时候，客户端可以发送任何类型的 Redis 命令。
> + message: 作为由另外一个客户端发送 PUBLISH 命令的结果，它是一个消息。第二个参数是发起的频道的名字，第三个参数是实际的消息内容。

## 数据库和作用域

Pub/Sub 没有任何相关的键空间，它被设计的在任何等级上都不会被干扰，包括数据库数。
在数据库10上发布的消息，将会被数据库1上的订阅者收到。
如果你需要某种程度上的命名空间，使用环境名称为通道添加前缀(test, staging, production, ...)。

## 有线协议的例子

```
SUBSCRIBE first second
*3
$9
subscribe
$5
first
:1
*3
$9
subscribe
$6
second
:2
```

在此时，我们使用另外一个客户端在名字为 sencond 的频道上执行了一个发布操作。

```
PUBLISH second hello
```

第一个客户端将会接收到：

```
*3
$7
message
$6
second
$5
Hello
```

现在客户端使用 UNSUBSCRIBE 命令(没有额外的参数)取消订阅所有的频道。

```
UNSUBSCRIBE
*3
$11
unsubscribe
$6
second
:1
*3
$11
unsubscribe
$5
first
:0
```

## 模式匹配的例子

Redis 的 Pub/Sub 系统支持模式匹配。客户端可能会订阅一个`glob`风格的模式，为了去接收所有名字符合给出模式的频道的消息。

例如:

```
PSUBSCRIBE news.*
```

上面的命令执行后，客户端将会接收`news.arg.figurative`，`news.music.jazz`等频道的消息。所有`glob`风格的模式都是有效的，所以多个通配符也是支持的。(译者注：`glob`模式并不是正则表达式，而是Unix Shell中的通配符，[参考地址](https://en.wikipedia.org/wiki/Glob_(programming)))

```
PUNSUBSCRIBE news.*
```

当客户端从上述`glob`模式中取消订阅的时候。其他的订阅将不会被这个调用所影响。
作为一个匹配模式的结果接收的消息，在发送时将会以不同的模式发送。
> + 消息的类型是`pmessage`: 作为其他客户端在模式匹配的频道上发出`PUBLISH`命令的结果，它是一个接收到的消息。第二个元素是原始的匹配模式，第三个元素是发出消息的频道的名字，最后一个元素是真实消息的有效载荷。

和`SUBSCRIBE`和`UNSUBSCRIBE`类似，`PSUBSCRIBE`和`PUNSUBSCRIBE`命令由系统确认来发送一种`psubscribe`和`punsubscribe`类型的消息，这种消息和`subscribe`和`unsubscribe`消息使用相同的格式。

## 消息匹配模式和频道订阅

一个客户端可能一次接收多个消息，如果它订阅的多个模式都匹配发布的消息的话。或者它既订阅了模式，也订阅了频道，这两个都匹配这个消息，就像如下的例子：

```
SUBSCRIBE foo
PSUBSCRIBE f*
```

在上面的例子中，如果如果一个消息发送给了频道foo，那么客户端将会接收两个消息，一种类型的消息来自频道订阅，一种类型的消息来自模式订阅。

## 模式匹配的订阅计数的含义

在 `subscribe`，`unsubscribe`, `psubscribe`, `punsubscribe`这几种消息类型中，最后一个参数是仍然活跃的订阅的数量。这个数字其实是客户端仍然订阅的频道和模式的总数。所以客户端只有会在这个数为0的时候，退出 Pub/Sub 模式，作为从所有频道和模式取消订阅的结果。

## 编程例子

Pieter Noordhuis 使用事件机制和Redis创建了一个非常好的例子，[a multi user high performace web chat](https://gist.github.com/pietern/348262)

## 客户端库实现提示

因为所有接收到的消息都会包含一个造成消息发布的原始订阅(频道或者模式)。客户端库可能会绑定原始订阅到回调函数(匿名函数，函数块，函数指针等)，使用哈希表来绑定。

当一个消息接收以后可以进行O(1)的查找，以便将消息送到注册的回调。
