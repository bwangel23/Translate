Plugin architecture
===================

这篇文章描述了插件架构，它面向那些想要用C去写插件的人群。

插件的结构本身并不是很复杂，但无论如何还是很容易去忘记一些事情。我们建议去复制一个简单的插件(例如 [Load plugin](https://collectd.org/wiki/index.php/Plugin:Load))然后从这里开始。

这里由一个步骤或者插件需要事项的列表。

<!-- toc -->

## 版权信息

所有的 \*.c 文件必须包含一个版权注意和授权信息。授权信息必须兼容于 collectd 它自己的授权信息，GPL 2。除非你有一个好的注意去分离你的插件到多个文件中，否则请把所有的内容放到一个 .c 文件中。

## 包含的头文件

通常插件包含至少如下的头文件：

```c
#include "collectd.h"
#include "common.h" /* 辅助函数 */
#include "plugin.h" /* plugin_register_*, plugin_dispatch_values */
```

## 回调函数

插件的第一步是去注册一个或者多个回调函数，在共享对象已经被载入之后，服务将会调用函数：
```c
void module_register (void);
```
那个函数已经被插件导出了。这个函数的目标是去注册一个回调函数给服务(除此以外就没有其他功能了)。除了`module_register`之外的所有函数，尤其是所有的回调函数，都应该使用`static`声明。

这有如下几种类型的回调函数，它们都能够被注册。当然，他们都是可选的。

### 配置回调函数

如果一个插件需要一个配置块，它必须提供一个配置回调函数。这里实际上有两种类型的配置回调函数："简单" 或者 "复杂"。这两种回调函数都声明在`src/plugin.h`中。

#### 简单配置回调函数

简单配置回调函数在每个配置项(例如，从配置文件中读取的每个键值对)被应用的时候都会被调用。

接收到的选项(键)必须被传递到注册函数。通常，这些选项是在文件的开头被定义，像下面这样：

```c
satic const char *config_keys[] = {
    "OptionOne",
    "OptionTwo",
    "SomethingElse",
}
static int config_keys_num = STATIC_ARRAY_SIZE(config_keys);
```

回调函数必须有如下的声明：
```c
static int my_config(const char *keym const char *value);
```

返回值必须是0代表成功，大于0代表失败，小于0代表配置项有一个无效的值。

可以像下面这样使用`plugin_register_config`去注册一个回调函数：

```c
void module_register(void)
{
    plugin_register_config("my_plugin", my_config,
        config_keys, config_keys_num);
}
```

每个配置项找到的时候，这个回调函数就被调用一次。这里并不能保证针对每个配置项仅仅调用一次这个函数，或者它总是被调用。

#### 复杂配置回调函数

为那个插件解析每个<Plugin />块的时候复杂配置文件就会被调用。它将会传递整个树，这样来允许插件配置使用嵌套的块，同时提供对已解析的数据类型的访问权限。

回调函数必须有如下的声明：
```c
static int my_config (oconfig_item_t *ci);
```

返回值必须是0(代表成功)，非0(代表失败)。
可以像下面这样使用`plugin_register_complex_config`函数去注册一个回调函数：

```
void module_register (void)
{
    plugin_register_complex_config("my_plugin", my_config)
}
```

想要查找如何解析配置树的示例代码，请参考[SNMP 插件](https://github.com/collectd/collectd/blob/master/src/snmp.c)的源码。


### 初始化回调函数

初始化函数用来去设置一个插件。它在配置文件被读取后(例如，所有配置文件的回调函数都已经陪执行完了)首先调用，在任何读写函数调用之前调用。然而，由于历史原因，他可能会在进程的生命周期中再次被调用，插件也需要一种方式来优雅地处理这个。[#911](https://github.com/collectd/collectd/issues/911)在跟踪这个情况，所以初始函数需要被仅仅调用一次，就像全世界期望的那样(额。。)。

这个回调函数必须有如下的声明：

```
static init my_init (void);
```

函数比如返回一个0代表成功，或者返回非0代表其他情况。如果非0返回了，所有插件注册的函数将会被取消注册。
可以像下面这样使用`plugin_regiser_init`函数来注册这个回调函数：

```c
void module_register (void)
{
    plugin_regiser_init("my_plugin", my_init);
}
```

### 读回调函数

> 参见：[Category:Calback read](https://collectd.org/wiki/index.php/Category:Callback_read)

读回调函数有两个变种：“simple”和“complex”读回调函数
这两个回调函数都被周期性地调用，但是每个注册的插件仅仅有一个。所以他们必须是线程安全的但不一定是可重入安全的(除非注册了两次或者多次)。

#### 简单读回调函数

回调函数必须有如下的声明：
```c
static int my_read (void);
```
函数必须返回0代表成功或者非0代表其他请求。如果非0返回了，这个值将会导致以更长的时间间隔来暂停，但是不会超过86,400秒（一天）。
可以像下面这样使用`plugin_register_read`函数去注册回调函数：
```c
void module_register (void)
{
    plugin_register_read("my_plugin", my_read)
}
```

#### 复杂读回调函数

复杂读回调函数和简单读回调函数在给他们传入的`user_data_t`指针上有不同。这个通常被 Java 插件(也应该被 Perl 插件使用)使用来确定哪个注册程序已经被调用了，同时调用合适的操作码或者脚本实现。

回调函数必须有如下的原型:
```c
static int plugin_read_c (user_data_t *ud);
```
这个函数必须返回0代表成功，返回非0代表其他情况。如果非0被返回了，这个值导致以一个更长的时间间隔来休眠，但是不会超出86,400秒(一天)。

使用`plugin_register_complex_read`函数来注册回调函数。你可以传递一个`struct timespec`去注册函数，让回调函数以指定的时间间隔来调用。如果你传递了一个`NULL`，全局的`Interval`设置将会被使用。

```c
void module_register (void)
{
    struct timespec ts = { 13, 370000000 }; /* 每13.37秒调用一次 */
    plugin_register_complex_read("my_plugin", my_read
        /* interval = */ &ts, /* user data = */ NULL);
}
```

### 写回调函数

插件通过注册一个写入函数可以实现将值写入到某些地方。当一个读函数调用调用`plugin_dispatch_values`函数的时候，一个有数据集的值列表将会被传递到所有写函数。参考[data_set_t](https://collectd.org/wiki/index.php/Data_set_t)，[value_list_t](https://collectd.org/wiki/index.php/Value_list_t)，[user_data_t](https://collectd.org/wiki/index.php/User_data_t)来查看数据类型的描述。请注意这个函数需要是线程安全的。

回调函数必须有如下的声明：
```c
static int my_write (const data_set_t *ds, const value_list_t *vl, user_data_t *ud);
```
这个函数必须返回0来代表成功，返回非0来代表其他情况。
可以像下面这样使用`plugin_register_write`函数来注册写回调函数：
```c
void module_register (void)
{
    plugin_register_write ("my_plugin"m my_write, /* user data = */ NULL);
}
```

### 刷新回调参数

许多写回调函数做了某种缓存来提升IO性能。例如RRDtool 插件是一个这种情况特别突出的例子。如果可能的话，实现了写函数应该提供一个*flush*回调函数来清空这些缓冲/缓存。

这个回调函数必须有如下的原型：
```c
static int my_flush (int timeout, const char *identifier, user_data_t *ud);
```
这个回调函数期望去刷新那些比`timeout`秒后更旧的值。小于或者等于0的值表示年龄不应该被检查。如果`identifier`是`NULL`的话，那就可以用来仅仅刷新一部分数据。最后的参数是一个可选的状态信息的指针。参考如下的注册函数。

这个函数必须返回0代表成功，返回非0代表其他情况。
可以像下面这样使用`plugin_register_flush`函数去注册回调函数：
```c
void module_register (void)
{
    plugin_register_flush ("my_plugin", my_flush, /* user data = */ NULL);
}
```

### 关闭回调函数

许多插件希望在他们之后清除。关闭函数能够用来去实现它同时终止线程，在退出之前关闭文件或者执行一些相似的任务。

回调函数必须有如下的声明：

```c
static int my_shutdown (void);
```

函数必须返回0代表成功，返回非0代表其他的情况。

可以像下面这样使用`plugin_register_shutdown`函数来注册回调函数：
```c
void module_register (void)
{
    plugin_regiser_shutdown ("my_plugin", my_shutdown);
}
```

### 日志回调函数

实现了`logging`的插件可能注册一个日志回调函数。严重性的常量`LOG_ERR`, `LOG_WARNING`, `LOG_NOTICE`, `LOG_INFO`, `LOG_DEBUG`定义在[src/plugin.h](http://git.verplant.org/?p=collectd.git;a=blob;hb=master;f=src/plugin.h)中。最后的参数是一个可选的指针指向状态信息，参考[user_data_t](https://collectd.org/wiki/index.php/User_data_t)来查找关于数据类型的描述。请注意日志函数需要可重入安全的。

回调函数必须包含如下的声明：
```
static void my_log (int serverity, const char *message, user_data_t *ud);
```
可以像下面这样来使用`plugin_register_log()`函数来注册回调函数：
```
void module_register (void)
{
    plugin_register_log ("my_plugin", my_log, /* user data = */ NULL);
}
```

### 提醒回调函数

__TODO__

## 数据类型

这里有两种复杂的数据类型插件可能会遇到。第一个是，[value_list_t](https://collectd.org/wiki/index.php/Value_list_t)，用于将值从插件接口传递到`plugin_dispatch_values`函数。第二个，[data_set_t](https://collectd.org/wiki/index.php/Data_set_t)会在写函数的声明中遇到，可能在动态加载数据集定义的时候出现。这个声明可以在[src/plugin.h](http://git.verplant.org/?p=collectd.git;a=blob;hb=master;f=src/plugin.h)中找到。

## 接口的稳定性

请意识到，插件接口没有被认为是新的镜像版本的向后兼容的一部分。即，它可以在任何时候变得更漂亮。它将会在下一个主要版本中进行一些改变。

这里并不确定插件会在每个版本上兼容，如果你想让你的插件在明年工作，请把它发送给我们，我们会照顾它且让他做出适当的改变来适应接口。
