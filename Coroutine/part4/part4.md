从数据处理到并发编程
====================

> 目前为止的故事

+ 协程和生成器很相似
+ 你能够创建一组小的处理组件，然后把他们连接起来
+ 你能够通过设置管道线，数据流图等等来处理数据
+ 你能够在代码中使用协程来处理棘手的执行。(例如事件驱动系统)
+ 然而这里有更多的事情你可以做

> 一个通用的主题

+ 你能够发送数据到协程
+ 你能够发送数据到线程(经过队列)
+ 你能够发送数据到进程(经过消息)
+ 协程很自然地和那些包括线程和分布式系统的问题绑定到了一起

> 基础的并发

+ 你可以将协程打包到线程或者子进程中，通过添加额外的层级。

![](http://obmuedb3b.bkt.clouddn.com/p78.png)

+ 将会勾画一些基础的想法

> 一个线程目标

```python
@coroutine
def threaded(target):
    message = Queue()   # 一个消息队列
    def run_target():
        """ run_target

        一个永久循环的线程，从消息队列中拉取消息，将他们发送到目标之中
        """
        while True:
            item = message.get()
            if item is GeneratorExit:
                target.close()
                return
            else:
                target.send(item)
    Thread(target=run_target).start()
    # 接收消息，并把他们发送到线程之中
    try:
        while True:
            item = (yield)
            message.put(item)
    except GeneratorExit:
        # 通过 GeneratorExit 异常来让线程正确地关闭
        message.put(GeneratorExit)
```

```python
if __name__ == '__main__':
    xml.sax.parse("test.xml", EventHandler(
        emails_to_dicts(
            threaded(
                filter_on_field("title", "Test Mail",
                    filter_on_field("title", "Test Mail",
                        show_email_message()
                    )
                )
            )
        )
    ))
```

+ 注意，增加线程让这个例子慢了将近50%

> 一个图片

+ 这里有一个上个例子的直观图片:

![p85](http://obmuedb3b.bkt.clouddn.com/p85.png)

> 一个子进程目标

+ 也能够通过管道或者文件来桥接两个协程

```python
@coroutine
def sendto(f):
    try:
        while True:
            item = (yield)
            pickle.dump(item, f)
            f.flush()
    except StopIteration:
        f.close()

@coroutine
def recvfrom(f, target):
    try:
        while True:
            item = pickle.load(f)
            target.send(item)
    except EOFError:
        target.close()
```

+ 高等级的图片

![](http://obmuedb3b.bkt.clouddn.com/p87.png)

+ 当然，魔鬼在于细节
+ 你可以不实现这个例子，除非你能够回复底层通信的细节(比如你有多个CPU同时这里有足够多的进程来让这样做是值得的)

> 实现 VS 环境

+ 通过协程，你可以从任务的执行环境中分离它的实现。
+ 协程是被执行了的
+ 环境是你可以选择的(线程，子进程，网络等等)
