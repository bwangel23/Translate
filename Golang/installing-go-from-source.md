从源码安装Go
=============

> + 原文地址： [https://golang.org/doc/install/source](https://golang.org/doc/install/source)

## 介绍

Go 是一个开源项目，基于 [BSD 风格](https://golang.org/LICENSE) 的 License 来发布的。这篇文档介绍了如何查看源代码，从你自己的机器上构建它们，运行它们。

大多数用户不需要做这个工作，可以用通过安装预编译好的二进制包来代替(这个在 [Get started](https://golang.org/doc/install) 中进行了介绍)，而且这也是一个更简单的过程。如果你想要去帮助开发那些预编译进包中的内容，请继续阅读下去。

这里有两种官方的 Go 编译工具链。这篇文档关注在 gc Go编译器和工具。如果想要获得如何通过 gccgo 进行工作的信息，这是一个传统的使用 GCC 后端的编译器，参考[Setting up and using gccgo](https://golang.org/doc/install/gccgo)章节。

Go 编译器支持7个指令集。不同架构的编译器的质量存在重要的不同。

+ amd64 (也叫做 x86-64)

  一个成熟的实现。在新的1.7版本中，它的基于 SSA 的后端生成了紧凑高效的代码

+ 386 (x86 或者 x86-32)

  兼容于 amd64 端，但是还没有使用基于 SSA 后端。它拥有有效的优化器(寄存器)而且能够生成良好的代码(尽管 gccgo 有时能够明显地做的更好)。

+ arm (ARM)

  支持 Linux, FreeBSD, NetBSD 和 Darwin 二进制包。比起其他端来使用地更少一些。

+ arm64 (AArch64)

  支持 Linux 和 Darwin 二进制包，在1.5版本中新添加的，同时也没有其他端使用地那么好。

+ ppc64, ppc64le (64位的 PowerPC 的大端和小端)

  支持 Linux 二进制包。在新的1.5版本中添加，没有其他端使用的那么好。

+ mips64, mips64le (64位的 MIPS 大端和小端)

  支持 Linux 二进制包，在新的1.6版本中添加，没有其他端使用地那么好。

+ s390x (IBM System z)

  支持 Linux 二进制包，在新的1.7版本中添加，没有其他端使用的那么好。

除了像低等级的操作系统接口代码的东西外，其他的运行时的支持在所有端上都是一样的，包括标记和扫描垃圾回收器，高效的数组和字符串切片，同时支持高效的 Go 协程，和按需求增长和收缩的栈。

编译器可以运行在 DragonFly BSD, FreeBSD, Linux, NetBSD, OS X(Darwin), Plan 9, Solaris 和 windows 操作系统上。在下面[环境变量](https://golang.org/doc/install/source#environment)的讨论中列出了全套支持的组合。

参考[整体系统需求](https://golang.org/doc/install#requirements)的主要安装页面，如下额外的应用到系统上的约束能够从源码构建。

  + 在 PowerPC 64位上运行的Linux，支持的最小版本的内核是 2.6.37。意味着 Go 不支持在这些系统上运行的 CentOS 6。
