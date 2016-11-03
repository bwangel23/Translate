构建系统
========

这页描述了 collectd 的构建系统，它是基于[autoconf](http://www.gnu.org/software/autoconf/)和[automake](http://www.gnu.org/software/automake/)。

从版本4.1开始依赖检查是在*configure*脚本中做的。插件是否被自动开启或者关闭取决于它的依赖是否被找到，或者可以通过`--enable-plugin`参数来强制地开启或者关闭插件。

## autoconf

将你的插件包括到构建过程中的第一步是将插件添加到*configure*脚本中。编辑[configure.ac](http://git.verplant.org/?p=collectd.git;a=blob;hb=master;f=configure.ac)文件来实现这个任务。你需要去添加一行`AC_PLUGIN`宏，它将会添加：

+ `--enable-plugin`参数到*configure*脚本
+ `BUILD_PLUGIN_PLUGIN`条件到 Makefile
+ `HAVE_PLUGIN_PLUGIN`定义到`config.h`

宏需要像被下面的方式来调用：

`AC_PLUGIN([name], $with_dependency, [description])`

第二个参数是决定的插件是被被构建的变量的值。如果你的插件没有任何 C99/POSIX 之外的依赖，你可以简单地传递一个"yes"值。否则的话，就来检测是否存在依赖性，当然，这是一个棘手的部分。变量`$with_dependency`应该被设置成"yes"，如果依赖被满足且没有其他的东西的话。第一个参数应该是插件的名字，第三个插件仅仅是`./configure --help`命令的描述。
那是一个好主意仅仅搜索宏且去赋值已经存在的行。如果你计划去发送你的补丁到邮件列表，请注意插件是按照字母顺序排列的。

## automake

上文中的`AC_PLUGIN`宏可以在[src/Makefile.am](http://git.verplant.org/?p=collectd.git;a=blob;hb=master;f=src/Makefile.am)设置条件，设置*automake*的输入文件。这里有多个`Makefile.am`，每个目录都有一个。如果你想要添加你自己的插件到`src/`，在那个目录中的文件是你想要编辑的。条件被命名成了`BUILD_PLUGIN_PLUGIN`。条件类似于C语言中的`#ifdef`预处理语句。他们包围的块定义了插件，所以只有在条件为True的时候这个才会被构建。一个典型的块看起来像是下面这样的：

```
if BUILD_PLUGIN_FOOBAR
pkglib_LTLIBRARIES += foobar.la
foo_la_SOURCES = foobar.c
foobar_la_LDFLAGS = -module -avoid-version
collectd_LOADD += "-dlopen" foobar.la
collectd_DEPENDENCIES += foobar.la
endif
```

再次强调，你最好的方法就是复制一个已经存在的块，然后根据你的需求来修改它。

## 生成 configure 和 Makefile.in

在你做出了你的改变之后，你需要去重新生成配置脚本和一些 Makefile.in。在你已经有一个配置脚本以后，可以通过键入make来实现。(生成的配置文件将会检查需求同时重新生成auto{conf, make}工作文件)。或者可以通过git仓库中的`build.sh`来完成这个功能。在那以后你就可以准备安装了。
