Object Relational Tutorial
==========================

SQLAlchemy 的ORM代表了一种将用户定义的 Python 类关联到数据库表的方法，这些类的实例代表了他们所关联的数据库的表的一行。它代表了一种系统能够透明地将对象和关联的行之间的改变同步，这叫做 [unit of work](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-unit-of-work)，以及根据用户定义的类和他们定义这些类之间的关系，来表达数据库查询的系统。

ORM 和 SQLalchemy 表达式语言比起来，ORM是在其之上来构建框架的。而在 [SQL Expression Language Tutorial](http://docs.sqlalchemy.org/en/rel_1_1/core/tutorial.html) 中介绍的 SQL 表达式语言，介绍了一种直接表示相关数据库的没有添加其他意见原始构造。ORM 代表了一种高等级的，抽象的使用模式，它本身就是表达式语言应用的一个例子。

然而在 ORM 和表达式语言的使用模式上有一点重叠，相似之处是最先出现的更为浅显一点。从用户定义的 [domain model](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-domain-model) 的角度来看，它是被透明地持久化的，而且还能从它依赖的模型上刷新。另一种方法从文字模式和SQL表达式表示的，他们被精确地组合成了消息然后由独立的数据库进行构造。

一个成功的应用程序可能仅仅由 ORM 来构造。在高级的情况中，一个由ORM构造的应用程序可能由表达式语言在特定的区域中，需要和数据库交互的时候，偶尔直接使用。

如下的教程是在 doctest的格式中，`>>>`表示你可以在 Python 解释器中直接输入，而下方的文本代表了期望的返回值。

## 版本检查

一个快速的检查验证我们使用的至少是1.1版本的SQLalchemy:

```python
>>> import sqlalchemy
>>> sqlalchemy.__version__
1.1.0
```

## 连接

这个教程我们仅仅使用一个在内存中的 SQLite 数据库。连接数据库我们使用`create_engine()`:

```py
>>> from sqlalchemy import create_engine
>>> engine = create_engine('sqlite:///:memory:', echo=True)
```

`echo`标记是一个快捷方式去设置 SQLalchemy 的日志记录，它是通过 Python 标准库中的`logging`模块来实现的，当它开启的时候，我们能够看到所有的生成的SQL语句的输出。如果你正在按着本教程调试但是想要更少的输出，可以把它设置成`False`。在这个教程中，所有生成的SQL语句被放在一个弹出窗口后面所以它不会阻碍我们的表达；可以通过点击 “SQL” 连接去查看生成的 SQL 语句。

`create_engine`的返回值是`Engine`的一个实例，它代表了到数据库的核心接口。通过一个处理了数据库细节的方言和使用的[DBAPI](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-dbapi)来适配。在这个例子中，SQLlite的方言将会通过 Python 内建的模块`sqlite3`来解释。

当第一次调用像`Engine.execute()`或`Execute.connect()`这种方法的时候，`Engine`将会使用[DBAPI](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-dbapi)来和数据库建立一个真实的连接，它用来发射SQL语句。当使用 ORM 的时候，我们通常不直接地使用一次创建的`Engine`，而是`Engine`在背后被ORM使用，这个我们随后就会看到。

> __懒连接__
>
> 当我们第一次使用`create_engine`创建一个`Engine`的时候它并没有连接到数据库，而是当我们真正地去执行一个针对数据库的任务的时候它才会和数据库建立连接。

> 参见
> [Database Urls](http://docs.sqlalchemy.org/en/rel_1_1/core/engines.html#database-urls)。其中包括了使用`create_engine()`连接到各种数据库的例子，在其中有指向更多信息的链接。

## 声明一个映射

当我们使用 ORM 的时候，配置过程是从描述一个我们将会处理的表开始的，他们使用我们自己声明的类来定义，这些类将会被映射成数据库中的表。在现代 SQLalchemy 中，这两个任务通常一起执行，使用一个叫做[Declarative](http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/declarative/index.html)的系统来执行。它允许我们使用一些包括一些特殊指令的类来描述这些类将要被映射的真实的表。

使用 *Declarative* 系统来将类映射到数据库的表是基于一个基类来运行的，这个基类用来维护一组和这个基类相关的表和类，这个基类就叫做声明系统基类。我们的应用程序通常仅仅有这个在一个通用的导入模块中的基类的一个实例。我们可以通过使用`declarative_base()`函数来创建这个基类，如下：

```python
>>> from sqlalchemy.ext.declarative import declarative_base

>>> Base = declarative_base()
```

现在我们已经有了一个基类，我们可以基于它定义任意数量的映射类。我们将会通过一个简单的表`users`来开始，它将会存储使用我们的应用程序的终端用户的信息。一个新的类叫做`User`将会被创建来映射这个表。在类中，我们定义了将会被映射的表的细节，优先是表名，然后是 names 和数据类型列。

```python
>>> from sqlalchemy import Column, Integer, String
>>> class User(Base):
...     __tablename__ = 'users'
...
...     id = Column(Integer, primary_key=True)
...     name = Column(String)
...     fullname = Column(String)
...     password = Column(String)
...
...     def __repr__(self):
...        return "<User(name='%s', fullname='%s', password='%s')>" % (
...                             self.name, self.fullname, self.password)
```

一个使用 __Declarative__ 系统的类最少需要一个`__tablename__`属性了一列用来做主键的一部分。SQLalchemy 它自己不会对那个类所索引的表做任何的假设，同时它没有任何内建的名字，数据类型，或者约束的转换。但是这并不意味着需要样板，而是鼓励你用帮助函数和混合类来创建你自己的自动约定，这部分细节将在 [Mixin and Custom Base Classes](http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/declarative/mixins.html#declarative-mixins) 中描述。

当我们的类被构造了以后，__Declarative__ 系统将会使用特殊的 Python 访问器(比如 [descriptors](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-descriptors)) 来替换其中的列。这个过程叫做 [Instrumentation](http://docs.sqlalchemy.org/en/rel_1_1/glossary.html#term-instrumentation)。“Instrumented” 映射类将会为我们提供在SQL上下文中引用我们的表的方法，同时从数据库中存储和获取我们的数据的方法。

除了映射过程对我们的类所做的之外，类其他 Python 通用类相同，我们可以对其定义任意数量的普通成员和方法，当我们的应用程序需要的时候。

## 创建一个模式

我们的`User`类经过 __Declarative__ 系统的构造之后，我们已经定义了关于表的信息，这个信息叫做表的元数据。这个叫做`Table`的对象被SQLalchemy用来去代表一个指定的表的信息，而且这个对象 __Declarative__ 系统已经为我们生成好了。我们可以看见这个对象通过检查 `__table__` 属性。

```
>>> User.__table__
Table('users', MetaData(bind=None),
            Column('id', Integer(), table=<users>, primary_key=True, nullable=False),
            Column('name', String(), table=<users>),
            Column('fullname', String(), table=<users>),
            Column('password', String(), table=<users>), schema=None)python
```

当我们声明我的类的时候，__Declarative__ 系统使用了一个 Python 元类，以便在类声明完成以后能够执行额外的操作。在这个阶段，它根据我们的定义创建了一个`Table`对象，同时通过构造一个`Mapper`对象去关联它。这个对象是一个幕后的对象我们不需要直接去处理它(经管它在我们需要的时候能够提供许多关于映射的信息)。

这个`Table`对象是一个叫做`MetaData`的大的集合的一个成员。当我们使用 __Declarative__ 系统的时候，可以在我们声明的基类上使用`.metadata`对象去访问这个集合。

`MeatData`是一个注册表，它包括了向数据库发送一组有限的模式生成命令的能力。现在我们的 SQLlite 数据库实际并没有 `users`表，我们可以使用`MeatData`去发出`CREATE TABLE`语句来创建所有不存在的表。下面，我们可以使用`MetaData.create_all()`方法，传递一个`Engine`对象代表一个数据库连接的源，如下是实际的`CREATE TABLE`语句。

```python
>>> Base.metadata.create_all(engine)
SELECT ...
PRAGMA table_info("users")
()
CREATE TABLE users (
    id INTEGER NOT NULL, name VARCHAR,
    fullname VARCHAR,
    password VARCHAR,
    PRIMARY KEY (id)
)
()
COMMIT
```

> 最小化的表声明 vs 全描述
>
> 熟悉 CREATE TABLE 语法的用户可能会注意到 VARCHAR 列生成的时候没有使用长度；在 SQLite 和 PostgreSQL中，这是一个有效的数据类型，但是在其他数据库中，这是不被允许的。所以如果这些不被允许的数据库，你可能希望 SQLalchemy 在发布 CREATE TABLE 命令的时候，一个长度可以在 String 类型后面提供，比如下面这样：

> ` Columnt(String(50)) `

> String 域，以及这些相似的能够精确控制长度的类型，比如 Integer, Numeric等。他们的长度在创建表的时候并不会被 SQLalchemy 引用。
> 除此以外，Firebird 和 Oracle 需要一个序列值去生成主键标识符，而 SQLalchemy 没有去生成或者假设没有被指定，那时，你就需要使用 `Sequence` 构造函数。

```python
from sqlalchemy import Sequence
Column(Integer, Sequence('user_id_seq'), primary_key=True)
```

> 因此，一个完整的，万无一失的`Table`对象经过我们的声明映射是：

```py
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)
```
> 我们单独包含这个更详细的表定义，以突出面向Python内使用的最小构造与将用于更严格要求的特定后端上发出`CREATE TABLE`语句的最小构造之间的差异。

## 创建一个映射类的实例

当映射完成的时候，就可以去创建和查看`User`对象了。

```py
>>> ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
>>> ed_user.name
'ed'
>>> ed_user.password
'edspassword'
>>> str(ed_user.id)
'None'
```

尽管我们没有在构造函数中制定，`id`属性仍然被赋值为一个`None`当我们访问它的时候(而不是 Python 通常定义的抛出一个 AttributeError 的异常，对于未定义的属性)。SQLalchemy 的检测系统通常对于映射的列属性在第一次被访问的时候设置这个默认值，对于那些已经被赋值了的值，构建系统会跟踪这些值以遍在插入语句中使用，使之将值发送到数据库。

> `__init__()` 方法

> 我们的用户类，使用一个声明系统来创建的，已经默认提供了一个构造方法( `__init__()` 方法)，它将会接收匹配我们映射的列的名字的关键字参数。同时，我们也可以为我们的类定义任何显示的`__init__()`方法，它将会覆盖由声明系统提供的默认方法。

## 创建一个会话

我们现在开始准备去和数据库交流了，ORM对于数据库的处理器就是会话(`Session`)。当我们第一次设置应用程序的时候，和我们的`create_engine()`语句在同一等级，我们定义一个`Session`类，它将会像一个创建`Session`对象的工厂一样来运行。

```py
>>> from sqlalchemy.orm import sessionmaker
>>> Session = sessionmaker(bind=engine)
```

当你遇到在你的应用程序中还没有 Engine 这个模块等级的对象的时候，你可以像下面这个例子一样来设置：

```py
>>> Session = sessionmaker()
```

随后，你通过`create_engine()`语句创建了一个`engine`，可以通过`configure()`函数来连接到这个`Session`

```py
>>> Session.configure(bind=engine)  # 一旦engine是可用的
```

这个自定义的`Session`类将会创建新的绑定到我们数据库的`Session`对象。当调用`sessionmaker`的时候其他事务性的特性也可能会被定义，这部分内容将会在随后的章节中讲到。随后，无论何时你需要一个和数据库的对话的时候，可以实例化一个`Session`对象：

```py
>>> session = Session()
```

上述的`Session`对象就关联到了我们启动了 SQLite 的 `engine` 上，但是它目前还没有打开任何的连接。当它第一次被使用的时候，他从由`Engine`维护的连接池中取出一个连接，一直保持这个连接，直到我们提交了所有的改变，或者关闭了这个`session`对象。

> Session 生命周期模式
>
> 什么时候去创建一个`Session`，这个取决于应用程序的类型，记住，`Session`仅仅是你对象的工作空间，到一个特殊的数据库的连接的本地表示。如果你把你的应用程序线程想象成一个晚宴的客人的话，那么`Session`就是客人的盘子，你的对象就是盘子上的食物(数据库就可以想象成，厨房？)。关于这个主题的更多信息，请参看 [When do I construct a Session, when do I commit it, and when do I close it?](http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate)

## 添加和更新对象

为了持久化地存储我们的`User`对象，我们把它`add()`到了`Session`。

```py
>>> ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
>>> session.add(ed_user)
```

此时，我们说那个实例是阻塞( pending )的；还没有 SQL 语句被发送到了数据库，同时那个对象还不能代表数据库中的一条记录。一旦需要，`session`将会发送 SQL 语句，使用一个我们都知道的`flush`过程去持久化地存储`Ed Jones`。如果我们为`Ed Jones`查询数据库，所有阻塞的信息首先会被 flush，随后查询的 SQL 语句就会发出。

例如，下面我们创建了一个新的`Query`对象，它载入了`User`的实例。我们通过名字属性是`ed`来进行过滤，并只是我们只想获取行的完整列表中的第一个。此时一个用户实例被返回，且他们等价于我们刚刚添加的那个。

```py
>>> our_user = session.query(User).filter_by(name='ed').first()
>>> our_user
<User(name='ed', fullname='Ed Jones', password='edspassword')>
```

事实上，`Session`已经确定返回的行和它内部对象映射中表示的行是同一行，所以我们实际上获取的是和我们刚刚添加的对象相同的一个对象。

```py
>>> ed_user is our_user
True
```

这里工作的 ORM 的概念是身份映射，确保在一个 Session 中在一个行上的所有操作都是对一组数据进行操作。一旦一个有一个特定主键的对象在 Session 中存在，那个 Session 中的，在那个特定主键上的 SQL 查询将会返回同一个 Python 对象; 如果试图在 Session 中放置具有相同主键的第二个已经持久化的对象，它也会抛出一个异常。

我们可以通过`add_all()`语句来一次性地添加多个`User`对象：

```py
>>> session.add_all([
...     User(name='wendy', fullname='Wendy Williams', password='foobar'),
...     User(name='mary', fullname='Mary Contrary', password='xxg527'),
...     User(name='fred', fullname='Fred Flinstone', password='blah')])
])
```
同样，我们已经发现 Ed 的密码不是很安全，所以让我们来改变它：

```py
>>> ed_user.password = 'f8s7ccs'
```

Session 一直关注着这一切，例如，它知道 `Ed Jones` 已经被修改了：

```py
>>> session.dirty
IdentitySet([<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>])
```

同时那三个新的用户也一直被阻塞着:

```py
>>> session.new  # doctest: +SKIP
IdentitySet([<User(name='wendy', fullname='Wendy Williams', password='foobar')>,
<User(name='mary', fullname='Mary Contrary', password='xxg527')>,
<User(name='fred', fullname='Fred Flinstone', password='blah')>])
```

我们告诉 Session 我们想要将所有保留的改变同步到数据库，同时提交我们的已经一直在运行中的事务。我们通过`commit()`来完成了这个操作。`Session`发送`UPDATE`语句来改变 "ed" 的密码，同时发送 `INSERT` 语句来在数据库中添加那三个我们新添加的`User`对象。

```
>>> session.commit()
```

`commit()`清除所有剩余的更改，并将之同步到了数据库，同时也提交了事务。由 Session 引用的连接资源现在返回了连接池。操作这个 session 的后续操作将会在新的事务中出现，同时在它第一次需要的时候将会再次从连接池中申请一个连接资源。

如果我们来查看 Ed 的`id`属性的话，早期它的值为`None`，但是现在它有值了：

```py
>>> ed_user.id
1
```

在`Session`插入新行到数据库之后，所有新生成的标识符和数据库生成的默认值对于实例都变得可用了，它可能是立即变得可用，也可能是在第一次访问的时候(load-on-first-access)变得可用。在这个例子中，整个行都被重新载入了，因为在我们发出了`commit()`语句之后，新的事务开始了。SQLalchemy 在一个事务中第一次进行访问的时候，它默认索引前一个事务的数据，所以最近的状态是可用的。重新载入的等级是可配置的，这个会在 [Using the session](http://docs.sqlalchemy.org/en/latest/orm/session.html) 中描述。

> Session 对象状态
>
> 当我们的`User`对象在没有主键的情况下，从 Session 的外部移动到 Session 的内部的时候，它实际上被插入了，它会在四个可用的对象状态的三个中移动。transient, pending 和 persitent。无论如何，意识到这些状态的含义总是有好处的。一定要阅读 [Quickie Intro to Object States](http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html#session-object-states) 来进行一个概览。

## 回滚

因为`Session` 是在事务的基础上进行工作的，所以我们也能够回滚我们做出的操作。首先，让我们先做两个我们将要还原的两个操作;`ed_user`的用户名获取并设置成`Edwardo`:

```py
>>> ed_user.name = 'Edwardo'
```

同时我们将会添加一个错误的用户，`fake_user`:

```py
>>> fake_user = User(name='fakeuser', fullname='Invalid', password='12345')
>>> session.add(fake_user)
```

查询当前会话，我们可以看到它已经刷新到了当前会话中：

```py
>>> session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()
[<User(name='Edwardo', fullname='Ed Jones', password='f8s7ccs')>, <User(name='fakeuser', fullname='Invalid', password='12345')>]
```

执行回滚操作，我们可以看到`ed_user`的名字已经变回了`ed`，同时`fake_user`已经被踢出了会话中：

```py
>>> session.rollback()

>>> ed_user.name
u'ed'
>>> fake_user in session
False
```

执行`SELECT`操作来演示同步到了数据库的更改:

```py
>>> session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()
[<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>]
```

## 查询

一个`Query`对象是通过`session`中的`query()`对象来创建的。这个函数能够接收可变数量的参数，这些参数能够是任意类和构造类描述符的集合。下面，我们表明一个查询对象将会载入`User`实例。当在交互式的上下文中执行的时候，当前用户对象的列表会被返回。

```py
>>> for instance in session.query(User).order_by(User.id):
...     print(instance.name, instance.fullname)
ed Ed Jones
wendy Wendy Williams
mary Mary Contrary
fred Fred Flinstone
```

查询对象也可以接收 ORM 构造描述符作为一个参数。任何时间多个类实体或者基于列的实体被表达作为参数传递给`query()`函数的时候，返回的结果总是期待的元组值。

```py
>>> for name, fullname in session.query(User.name, User.fullname):
...     print(name, fullname)
ed Ed Jones
wendy Wendy Williams
mary Mary Contrary
fred Fred Flinstone
```

由`Query`返回的元组是一个命名元组，由`KeyedTuple`类来支持，能够以一个普通的Python对象来对待它。一个属性的名称和属性名相同，一个类的名称和类名相同(参考下面的例子来理解这句话)。

```py
>>> for row in session.query(User, User.name).all():
...    print(row.User, row.name)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')> ed
<User(name='wendy', fullname='Wendy Williams', password='foobar')> wendy
<User(name='mary', fullname='Mary Contrary', password='xxg527')> mary
<User(name='fred', fullname='Fred Flinstone', password='blah')> fred
```

你可以使用`lable()`构造函数来控制独立的列表达式的名字，它对于任何由`ColumnElement`继承来的对象和任何由一个类属性映射过来的对象都适用(比如`User.name`)。

```py
>>> for row in session.query(User.name.label('name_label')).all():
...    print(row.name_label)
ed
wendy
mary
fred
```

假设调用`query()`的时候有多个实体，能够通过`aliased()`函数来控制，通过一个给定名字来引用一个完整的实体，比如`User`。

```py
>>> from sqlalchemy.orm import aliased
>>> user_alias = aliased(User, name='user_alias')

>>> for row in session.query(user_alias, user_alias.name).all():
...    print(row.user_alias)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>
<User(name='wendy', fullname='Wendy Williams', password='foobar')>
<User(name='mary', fullname='Mary Contrary', password='xxg527')>
<User(name='fred', fullname='Fred Flinstone', password='blah')>
```

使用`Query`基础操作发出 LIMIT 和 OFFSET 命令，最方便的使用 Python 的数组切片，最典型的就是和`ORDER BY`结合使用：

```py
>>> for u in session.query(User).order_by(User.id)[1:3]:
...    print(u)
<User(name='wendy', fullname='Wendy Williams', password='foobar')>
<User(name='mary', fullname='Mary Contrary', password='xxg527')>
```

同时过滤结果也可以使用`filter_by()`函数来完成，这个函数使用关键字参数：

```py
>>> for name, in session.query(User.name).\
...             filter_by(fullname='Ed Jones'):
...    print(name)
ed
```

或者也可以使用`filter()`参数，它使用更灵活的 SQL 表达式语言构造。这个允许你在映射的类的类等级属性上中使用普通的 Python 操作符:

```py
>>> for name, in session.query(User.name).\
...             filter(User.fullname=='Ed Jones'):
...    print(name)
ed
```

`Query`对象是完全生成的，这意味着大多数调用的方法返回一个新的`Query`对象，你可以在上面添加更多的属性。例如，要查询一个名字为"ed"全名为"Ed Jones"的用户，你可以`filter()`两次，它们会使用`AND`进行标准连接：

```py
>>> for user in session.query(User).\
...          filter(User.name=='ed').\
...          filter(User.fullname=='Ed Jones'):
...    print(user)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>
```

### 通用过滤操作符

下面是`filter()`中使用的最常用的一些运算符:

+ equals:

  ```py
  query.filter(User.name == 'ed')
  ```

+ not equals:

  ```py
  query.filter(User.name != 'ed')
  ```

+ LIKE:

  ```py
  query.filter(User.name.like('%ed%'))
  ```

+ IN:

  ```py
  query.filter(User.name.in_(['ed', 'wendy', 'jack']))

  # 也可以和查询对象一起使用
  query.filter(User.name.in_(
          session.query(User.name).filter(User.name.like('%ed%'))
  ))
  ```

+ NOT IN:

  ```py
  query.filter(~User.name.in_(['ed', 'wendy', 'jack']))
  ```

+ IS NULL:

  ```py
  query.filter(User.name == None)

  # 或者，如果 pep8/linter 对上面的语法报出警告的话，可用下面的代替
  query.filter(User.name.is_(None))
  ```

+ IS NOT NULL:

  ```py
  query.filter(User.name != None)

  # 或者，如果 pep8/linter 对上面的语法报出警告的话，可用下面的代替
  query.filter(User.name.isnot(None))
  ```

+ AND:

  ```py
  # 使用 and_()
  from sqlalchemy import and_
  query.filter(and_(User.name == 'ed', User.fullname == 'Ed Jones'))

  # 或者发送多个表达式到 .filter() 函数
  query.filter(User.name == 'ed', User.fullname == 'Ed Jones')

  # 或者链接多个 filter()/filter_by() 调用
  query.filter(User.name == 'ed').filter(User.fullname == 'Ed Jones')
  ```
  > 注意
  >
  > 注意你使用的是`and_`函数而不是 Python 的与操作符

+ OR:

  ```py
  from sqlalchemy import or_
  query.filter(or_(User.name == 'ed', User.name == 'wendy'))
  ```
  > 注意
  >
  > 注意你使用的是`or_`函数而不是 Python 的或操作符

+ _MATCH:

  ```py
  query.filter(User.name.match('wendy'))
  ```

  > 注意
  >
  > match() 使用特定数据库的 MATCH 或者 CONTAINS 函数; 它的行为将会根据数据库后端的不同而变化，而且在一些数据库上(比如 SQLite )是不可使用的

### 返回列表和标量

在`Query`对象上的许多方法，会立即执行一个 SQL 语句同时返回一个包含着载入数据库结果的值。这里有一个简短的介绍：

+ `all()` 返回一个列表
  ```py
  >>> query = session.query(User).filter(User.name.like('%ed')).order_by(User.id)
  >>> query.all()
  [<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>,
      <User(name='fred', fullname='Fred Flinstone', password='blah')>]
  ```

+ `first()` 应用一个长度为1的限制，同时返回结果作为一个标量
  ```py
  >>> query.first()
  <User(name='ed', fullname='Ed Jones', password='f8s7ccs')>
  ```

+ `one()` 完全获取所有行，并且如果返回结果中不存在一个对象标识或者当前存在复合行，将会抛出错误
  多行返回的结果是这样的：
  ```py
  >>> user = query.one()
  Traceback (most recent call last):
  ...
  MultipleResultsFound: Multiple rows were found for one()
  ```

  没有一行数据找到的输出是这样的：
  ```py
  >>> user = query.filter(User.id == 99).one()
  Traceback (most recent call last):
  ...
  NoResultFound: No row was found for one()
  ```

  `one()`对于系统希望处理"没有找到结果"和"找到多个结果"不同，比如 RESTful web 服务，它想要抛出一个"404 not found"当结果没有找到的时候，当时将会抛出一个应用程序错误，当多个结果找到的时候。

+ `one_or_none()`相似于`one()`，但是当这个方法没有找到数据的时候，它不会抛出一个异常；它仅仅返回`None`。就像`one()`一样，当有多个结果找到的时候它将会抛出一个异常。

+ `scalar()` 它将会调用`one()`方法，而且在成功返回的第一行上返回第一列：

  ```py
  >>> query = session.query(User.id).filter(User.name == 'ed').\
  ...    order_by(User.id)
  >>> query.scalar()
  1
  ```

### 使用文本化的 SQL 语句

文本字符串能够和`Query`对象一起灵活地使用，通过`text()`构造函数来指定他们的使用，这个将会被大部分的适用方法所接受。例如：`filter()`和`order_by()`。

```py
>>> from sqlalchemy import text
>>> for user in session.query(User).\
...             filter(text("id<224")).\
...             order_by(text("id")).all():
...     print(user.name)
ed
wendy
mary
fred
```

绑定参数能够通过使用基于文本的字符串的冒号来实现。要去指定一个参数，可以使用`params()`方法：

```py
>>> session.query(User).filter(text("id<:value and name=:name")).\
...     params(value=224, name='fred').order_by(User.id).one()
<User(name='fred', fullname='Fred Flinstone', password='blah')>>"))
```

要使用一个完整的基于字符串的语句，一个`text()`构造代表了一个完整的语句，它能够被传递给`from_statement()`函数。如果没有额外的指定，它将会根据字符串 SQL 语句中的列的名称来匹配模型中的列，下面这个例子中我们仅仅用星号来表示载入所有的列：

```py
>>> session.query(User).from_statement(
...                     text("SELECT * FROM users where name=:name")).\
...                     params(name='ed').all()
[<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>]
```

名称匹配仅仅可以在简单的情况下工作，但是当处理包含重复列名的复杂语句或者使用不能够轻易匹配列名的复杂 ORM 构造的时候，它可能会变得难以处理。此外，当我们处理结果行的时候，我们可能发现在我们的结果行中的 *typing* 行为是必要的。在这种情况下，`text()`函数允许我们去链接它的文本SQL到核心或者 ORM 映射的列表达式的位置;我们可以实现这个，通过传递一个列表达式作为一个位置参数，到`TextClause.columns()`方法中：

```py
>>> stmt = text("SELECT name, id, fullname, password "
...             "FROM users where name=:name")
>>> stmt = stmt.columns(User.name, User.id, User.fullname, User.password)
>>> session.query(User).from_statement(stmt).params(name='ed').all()
[<User(name='ed', fullname='Ed Jones', password='f8s7ccs')>]
```

> *New in version 1.1*
> `TextClause.columns()`方法现在能够接收在文本 SQL 结果集中匹配位置的列表达式，消除了匹配的时候列名的需要，甚至消除了在 SQL 语句中是独一无二的需要。

当选择一个`text()`构造函数的时候，`Query`对象可能仍然指定返回的列和条目；而不是`query(User)`，我们也能够要求列是独立的，就像在其他情况中那样：

```py
>>> stmt = text("SELECT name, id FROM users where name=:name")
>>> stmt = stmt.columns(User.name, User.id)
>>> session.query(User.id, User.name).\
...          from_statement(stmt).params(name='ed').all()
[(1, u'ed')]
```
> 参见:
> [Using Textual SQL](http://docs.sqlalchemy.org/en/latest/core/tutorial.html#sqlexpression-text) - 从仅用核心查询的角度来解释`text()`构造函数

### 计数

`Query`对象包含一个方便的计数方法叫做`count()`:

```py
>>> session.query(User).filter(User.name.like('%ed')).count()
2

# -----------SQL-------------

SELECT count(*) AS count_1
FROM (SELECT users.id AS users_id,
                users.name AS users_name,
                users.fullname AS users_fullname,
                users.password AS users_password
FROM users
WHERE users.name LIKE ?) AS anon_1
('%ed',)
```

`count()`方法用来检测 SQL 语句将会返回多少行。参照上面生成的SQL语句，上面生成的SQL语句，SQLAlchemy 总是将我们正在进行的查询放到子查询中，然后从中计算行。在某些情况下这个可以简化成一个简单的`SELECT count(*) FROM table`，然而，SQLAlchemy 的现代版本并没有尝试去猜哪一种情况是合适的，尽管确切的 SQL 可以用更明确的方式完成。

在这种情况下，"要统计的事情"需要用特定的方式来表示，我们可以直接使用表达式`func.count`来指定"count"函数，这个函数可以从`func`构建中获取到。下面这个例子中，我们使用它去返回独一无二的用户名的总和：

```py
>>> from sqlalchemy import func
>>> session.query(func.count(User.name), User.name).group_by(User.name).all()
[(1, u'ed'), (1, u'fred'), (1, u'mary'), (1, u'wendy')]

# -------------SQL-----------------
SELECT count(users.name) AS count_1, users.name AS users_name
FROM users GROUP BY users.name
()
```

去实现我们简单的`SELECT count(*) FROM table,`语句，我们可以应用下面的方式：

```py
>>> session.query(func.count('*')).select_from(User).scalar()
4

# ---------------SQL--------------
ELECT count(?) AS count_1
FROM users
('*',)
```

如果我们就用户的主键来直接进行统计的话，`select_from`的用法能够删除：

```py
>>> session.query(func.count(User.id)).scalar()
4

# ----------------SQL----------------
SELECT count(users.id) AS count_1
FROM users
()
```

## 构建关系

让我们来考虑第二张表，和`User`表相关联的，能够被映射和查询的。用户在我们的系统中能够存储任意数量的和他们的用户名相关的邮件地址。这就在`user`表和一个新的存储邮件地址的表实现了一个基础的一对多的关联，我们可以称呼这个新的表为`address`。使用声明系统，我们定义了这个表它相关的映射类，`Address`：

```py
>>> from sqlalchemy import ForeignKey
>>> from sqlalchemy.orm import relationship

>>> class Address(Base):
...     __tablename__ = 'addresses'
...     id = Column(Integer, primary_key=True)
...     email_address = Column(String, nullable=False)
...     user_id = Column(Integer, ForeignKey('users.id'))
...
...     user = relationship("User", back_populates="addresses")
...
...     def __repr__(self):
...         return "<Address(email_address='%s')>" % self.email_address

>>> User.addresses = relationship(
...     "Address", order_by=Address.id, back_populates="user")
```

上述类介绍了`ForeignKey`构造函数，这是一个指令应用到`Column`函数中来表示这列值在当前列和一个远处的列中间应该有一个约束。这是关于关系型数据库的一个核心特征，它是一个“胶水”用来使没有关系的表集合去拥有丰富的关系。上述的`ForeignKey`表明，`address.user_id`列的值应该约束在`users.id`列中，即其主键。

第二条指令，也就是`relationship()`，告诉 ORM `Address` 类它自己应该通过属性`Address.user`链接到 `User` 类。`relationship()`通过两个表之间的的外键的关系来确定这种链接的性质，在这里检测到`Address.user`将会是多对一。一个额外的`relationship()`指令被放置到了`User()`映射类的`User.addresses`属性下。在两个`relationship()`指令中，参数`relationship.back_populates`被赋值用来索引互补的属性名；这个通过这样来做，每个`relationship()`能够做出一个智能地决定关于反向应该表达何种关系，`Address.user`索引一个用户实例，而另一边，`User.addresses`索引一个`Address`实例的列表。

> 注意:
>
> `relationship.back_populates`是一个过去非常常用的叫做`relationship.backref` SQLAlchemy 特性。`relationship.backref` 没有去任何地方，而且一直会保持可用。`relationship.back_populates` 和它是同样的东西，除了有更详细的输出和更好的可操作性。如果想对整个主题有一个概览，可以参考章节 [Linking Relationships with Backref](http://docs.sqlalchemy.org/en/latest/orm/backref.html#relationships-backref)。

多对一关系的反向总是一对多。一个完整的关于可用的`relationship()`的配置的目录在 [Basic Relationship Patterns](http://docs.sqlalchemy.org/en/latest/orm/backref.html#relationships-backref) 中。

两个完整的`Address.user`和`User.addresses`的关系称作是[双向关系](http://docs.sqlalchemy.org/en/latest/glossary.html#term-bidirectional-relationship)，而且这是 SQLAlchemy 的一个关键特征。章节 [Linking Relationships with Backref](http://docs.sqlalchemy.org/en/latest/orm/backref.html#relationships-backref) 详细讨论了 "backref" 特征的细节。

假设声明系统正在使用的时候，关系到远程类的`relationship()`的参数可以通过字符串来指定。一旦所有的映射都完成了，这些字符串等价于为了去实现真实参数的 Python 表达式，例如在上面例子中`Address`中的`User`类。在此评估期间，这个名字允许包括已经根据声明系统创建的所有类的名字除了一些其他事情。

参考`relationship()`的文档字符串获取参数风格的更多信息。

> 你知道吗？
>
> + 一个`FOREIGN KEY`约束在大多数关系型数据库中(尽管不是所有的)，都只能链接到一个数据库主键中，或者一个拥有`UNIQUE`约束的列。
> + 一个`FOREIGN KEY`约束引用了一个包含多列的主键，而且它自己也有多列的话，这就是一个"复合外键"。它也能够引用这些列的子集。
> + 一个`FOREIGN KEY`的列能够自动地更新，为了去响应它索引的那个列或者行的变化。这个就叫做`CASCADE`索引动作，而且这是关系型数据库的一个内建功能。
> + `FOREIGN KEY`能够索引它自己的表，这个就叫做"自索引"的外键。
> + 如果想要获取更多的关于外键的信息，请参考[Foreign Key - Wikipedia](http://en.wikipedia.org/wiki/Foreign_key)。

接下来，我们将会需要在数据库中新建一个`address`表，所以我们从我们的元数据从新发出另外一个 CREATE 命令。它将会跳过所有已经被创建的表：

```py
>>> Base.metadata.create_all(engine)

# -----------SQL-------------

PRAGMA...
CREATE TABLE addresses (
    id INTEGER NOT NULL,
    email_address VARCHAR NOT NULL,
    user_id INTEGER,
    PRIMARY KEY (id),
     FOREIGN KEY(user_id) REFERENCES users (id)
)
()
COMMIT
```

## 使用相关对象来工作

现在，当我们创建`User`对象的时候，一个空白的`address`集合也会跟着存在。各种集合类型，比如集合或者字典(参考：[自定义集合访问细节](http://docs.sqlalchemy.org/en/latest/orm/collections.html#custom-collections))，在这里都是可能的，但是在这里，默认的数据类型是一个 Python 的列表。

```py
>>> jack = User(name='jack', fullname='Jack Bean', password='gjffdd')
>>> jack.addresses
[]
```

我们能够自由地添加地址对象到我们的用户对象中。在下面这个例子中，我们将会直接赋值一个完全的列表：

```py
>>> jack.addresses = [
...                 Address(email_address='jack@google.com'),
...                 Address(email_address='j25@yahoo.com')]
```

当我们使用双向的关系的时候，元素在一个方向添加，也会自动在另外一个方向变得可见。这个行为是基于属相改变的事件发生的，这是在 Python 中评估实现的，没有使用任何 SQL 语句：

```py
>>> jack.addresses[1]
<Address(email_address='j25@yahoo.com')>

>>> jack.addresses[1].user
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
```

让我们添加一个提交`Jack Bean`到数据库中，`jack`将会有两个`Address`成员在合适的`addresses`集合中，而且也会在这次提交中被添加到数据库，这将会使用 **cascading** 的方式来处理。

```python
>>> session.add(jack)
>>> session.commit()

# ----------------SQL---------------
# INSERT INTO users (name, fullname, password) VALUES (?, ?, ?)
# ('jack', 'Jack Bean', 'gjffdd')
# INSERT INTO addresses (email_address, user_id) VALUES (?, ?)
# ('jack@google.com', 5)
# INSERT INTO addresses (email_address, user_id) VALUES (?, ?)
# ('j25@yahoo.com', 5)
# COMMIT
```

查询 Jack 的话，我们将会获得 Jack 的数据。但是没有 SQL 语句被发送来查询 Jack 的 Email 地址。

```py
>>> jack = session.query(User).\
... filter_by(name='jack').one()
>>> jack
<User(name='jack', fullname='Jack Bean', password='gjffdd')>

# ----------------SQL---------------
# BEGIN (implicit)
# SELECT users.id AS users_id,
#         users.name AS users_name,
#         users.fullname AS users_fullname,
#         users.password AS users_password
# FROM users
# WHERE users.name = ?
# ('jack',)
```

接下来我们来查看一下`address`集合，这里将会看到查询的 SQL 语句。

```py
>>> jack.addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]

# ---------------SQL-----------------
# SELECT addresses.id AS addresses_id,
#         addresses.email_address AS
#         addresses_email_address,
#         addresses.user_id AS addresses_user_id
# FROM addresses
# WHERE ? = addresses.user_id ORDER BY addresses.id
# (5,)
```

当我们访问`address`集合的时候，SQL 查询立刻就被发出了。这是一个懒载入关系的例子。`address`集合现在被载入了而且行为就像一个字典列表一样。我们将会介绍一些方式来优化此集合的加载。

## 使用 Joins 来查询

现在我们有了两个表，我们能够展示`Query`对象的更多特点了，特别是去创建如何同时处理两个表的查询。[SQL JOIN 的维基百科](http://en.wikipedia.org/wiki/Join_%28SQL%29)对于连接技术提供了一个很好的介绍，其中几个我们将在这里说明。

去构造一个隐含的在`User`和`Address`表之间的连接，我们可以使用`Query.filter()`去等同于它们一起的相关的列。下面我们将会使用这个方法来同时载入`User`和`Address`条目。

```py
>>> for u, a in session.query(User, Address).\
...                     filter(User.id==Address.user_id).\
...                     filter(Address.email_address=='jack@google.com').\
...                     all():
...     print(u)
...     print(a)
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
<Address(email_address='jack@google.com')>

# -------------------SQL----------------------
# SELECT users.id AS users_id,
#         users.name AS users_name,
#         users.fullname AS users_fullname,
#         users.password AS users_password,
#         addresses.id AS addresses_id,
#         addresses.email_address AS addresses_email_address,
#         addresses.user_id AS addresses_user_id
# FROM users, addresses
# WHERE users.id = addresses.user_id
#         AND addresses.email_address = ?
# ('jack@google.com',)
```

从另一方面来说，按照真实的`SQL JOIN`语法来写的话，最简单的实现恐怕就是`Query.join()`方法了：

```py
>>> session.query(User).join(Address).\
...         filter(Address.email_address=='jack@google.com').\
...         all()
[<User(name='jack', fullname='Jack Bean', password='gjffdd')>]

# -------------------SQL----------------------
# SELECT users.id AS users_id,
#         users.name AS users_name,
#         users.fullname AS users_fullname,
#         users.password AS users_password
# FROM users JOIN addresses ON users.id = addresses.user_id
# WHERE addresses.email_address = ?
# ('jack@google.com',)
```

`Query.join()`知道如何在`User`和`Address`之间进行连接，因为在他们直接仅仅有一个外键。如果这里没有外键，或者有多个外键，`Query.join()`以下面的一种方式来使用将会工作的更好：

```py
query.join(Address, User.id == Address.user_id)
query.join(User.address)
query.join(Address, User.addresses)              # same, with explicit target
query.join('addresses')                          # same, using a string
```

当你同样地想使用外连接的时候，使用`outerjoin()`函数：

```py
query.outerjoin(User.addresses)   # 左外连接
```

参考`join()`函数的文档来获取更多的细节信息，同时也可以通过例子查看这个方法接受的调用风格；`join()`在任何一个以 SQL 流为主的应用程序中都是一个重要的方法。

> 如果有多调记录的话，`Query` SELECT 将会返回什么？
>
> `Query.join()`方法将会典型地从所有记录列表中最左边的列表开始连接，当`ON`子句被发出的时候，或者`ON`子句在一个明文 SQL 表达式中。如果想要控制`JOIN`连接的结果集中的第一条记录(译者注：即左表)，使用`Query.select_from()`方法：
>
>      query = Session.query(User, Address).select_from(Address).join(User)

### 使用 Aliases

当查询多个表的时候，如果一个表需要被索引多次的话，SQL 通常需要那个表通过别名的方式来拥有另外一个名字，这样它就能过够和同时出现的自身区分开来了。`Query`对象通过`aliased`构造函数来明确支持这个特性。下面我们将会连接`Address`记录两次，去定位一个同时拥有两个不同的 Email 地址的用户：

```py
>>> from sqlalchemy.orm import aliased
>>> adalias1 = aliased(Address)
>>> adalias2 = aliased(Address)
>>> for username, email1, email2 in \
...     session.query(User.name, adalias1.email_address, adalias2.email_address).\
...     join(adalias1, User.addresses).\
...     join(adalias2, User.addresses).\
...     filter(adalias1.email_address=='jack@google.com').\
...     filter(adalias2.email_address=='j25@yahoo.com'):
...     print(username, email1, email2)
jack jack@google.com j25@yahoo.com
```

### 使用子查询

`Query`对象也适合用来生成能够被子查询使用的语句。假设我们想要载入`User`对象和每个用户相关的多个`Address`对象。最好的方法是像下面这个 SQL 的一样，获得由用户分组的地址对象的计数，然后和父查询连接起来。在下面这个例子中，我们使用了左外连接。所以我们得到的返回行是所有没有地址的用户，例子如下：

```sql
SELECT users.*, adr_count.address_count FROM users LEFT OUTER JOIN
    (SELECT user_id, count(*) AS address_count
        FROM addresses GROUP BY user_id) AS adr_count
    ON users.id=adr_count.user_id
```

使用`Query`对象，我们由内而外建立一个相似的语句。语句访问器返回一个 SQL 表达式，代表了由特定`Query`对象生成的语句 - 这是一个`select()`构造函数的实例，而它在 [SQL Expression Language Tutorial](http://docs.sqlalchemy.org/en/latest/core/tutorial.html) 中进行了解释。

```py
>>> from sqlalchemy.sql import func
>>> stmt = session.query(Address.user_id, func.count('*').\
...         label('address_count')).\
...         group_by(Address.user_id).subquery()
```

`func`关键字生成了 SQL 函数，`Query`对象上的`subquery()`函数代表了使用一个别名嵌入的 SELECT 语句(别名实际上是`query.statement.alias()`的快捷方式)。

一旦我们有了我们的语句，它的行为就像一个表结构一样，就比如我们这一小结一开始为`users`创建的表。这个语句上的列是能够通过叫做`c`的属性来访问的：

```
>>> for u, count in session.query(User, stmt.c.address_count).\
...     outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id):
...     print(u, count)
<User(name='ed', fullname='Ed Jones', password='f8s7ccs')> None
<User(name='wendy', fullname='Wendy Williams', password='foobar')> None
<User(name='mary', fullname='Mary Contrary', password='xxg527')> None
<User(name='fred', fullname='Fred Flinstone', password='blah')> None
<User(name='jack', fullname='Jack Bean', password='gjffdd')> 2
```

### 从子查询中选择实体

上面，我们仅仅从子查询中选择了一个包含一列的结果，如果我们想要将我们的子查询映射成一个实体的时候该怎么做呢？这里我们可以使用`aliased()`去关联一个映射类的别名到一个子查询上:

```py
>>> stmt = session.query(Address).\
...                 filter(Address.email_address != 'j25@yahoo.com').\
...                 subquery()
>>> adalias = aliased(Address, stmt)
>>> for user, address in session.query(User, adalias).\
...         join(adalias, User.addresses):
...     print(user)
...     print(address)
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
<Address(email_address='jack@google.com')>
```

## 使用 EXISTS

`EXISTS`关键字在 SQL 语句中是一个布尔操作符，如果给定的表达式包含任何行的话就返回真。它可能会在加入连接的许多场景下使用，也可以在关系型表中确定给定的一些行是否含有符合条件的行。

这里有一个明确的`EXISTS`结构，它看起来像下面这样:

```py
>>> from sqlalchemy.sql import exists
>>> stmt = exists().where(Address.user_id==User.id)
>>> for name, in session.query(User.name).filter(stmt):
...     print(name)
jack
```

`Query`对象包含几个查询操作符，它们将会自动使用`EXISTS`。例如上面的语句可以被表示成`User.addresses`使用`any()`的关系：

```py
>>> for name, in session.query(User.name).\
...         filter(User.addresses.any()):
...     print(name)
jack
```

`any()`也可以采用标准，来限制匹配的行。

```py
>>> for name, in session.query(User.name).\
...     filter(User.addresses.any(Address.email_address.like('%google%'))):
...     print(name)
jack
```

在多对一关系中，`has`和`any()`是同样的操作符(注意`~`操作符也是，它在这里意味着"NOT")：

```py
>>> session.query(Address).\
...         filter(~Address.user.has(User.name=='jack')).all()
[]
```

## 通用的关系操作符

这里所有的操作符都是基于关系型数据库，每个都有到它文档的链接，那里包括了它的用法和行为的更多细节：

+ `__eq__()`(多对一相等比较符):

> query.filter(Address.user == someuser)

+ `__ne__()`(多对一不等比较符)

> query.filter(Address.user != someuser)

+ IS NULL(多对一比较，也可以用`__eq__()`):

> query.filter(Address.user == None)

+ `contains()` (使用一对多的集合):

> query.filter(User.address.contains(someaddress))

+ `any()` (用于集合)

> ```
> query.filter(User.addresses.any(Address.email_address == 'bar'))
>
> # 也可以传入关键字参数：
> query.filter(User.addresses.any(email_address='bar'))
> ```

+ `has()` (用于标量引用)

> query.filter(Address.user.has(name='ed'))

+ `Query.with_parent()` (可以用于任何关系)

> session.query(Address).with_parent(someuser, 'addresses')

## 立即载入

回想早期我们讲过的一个懒加载操作，当我们访问一个`User`对象的`User.address`集合的时候，SQL 语句被发出了. 如果想要降低查询的数量(在我这里是戏剧性地需要),我们可以应用立即载入到查询语句上. SQLAlchemy 提供三种类型的立即载入,两种是自动的.第三种包括了自定义的标准.所有这三个类型都通过成为查询选项的函数调用,他们通过`Query.options()`方法查询提供有关如何加载各种属性的附加说明.

### 子查询载入

在这个例子中,我们想要去表示`User.addresses`应该被立即载入.载入一组对象和它们相关的集合的一个好的选择是`orm.subqueryload()`选项,它会立刻发送第二个 SQL 语句来载入和结果相关的集合."subquery"的名字起源于一个事实就是,直接由`Query`构造的 SELECT 查询语句被重用了,它会嵌入到相关表查询中作为一个子查询.这个有点啰嗦但是非常容易使用:

```py
>>> from sqlalchemy.orm import subqueryload
>>> jack = session.query(User).\
...                 options(subqueryload(User.addresses)).\
...                 filter_by(name='jack').one()
>>> jack
<User(name='jack', fullname='Jack Bean', password='gjffdd')>

>>> jack.addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]

# --------------- SQL ---------------

SELECT users.id AS users_id,
        users.name AS users_name,
        users.fullname AS users_fullname,
        users.password AS users_password
FROM users
WHERE users.name = ?
('jack',)
SELECT addresses.id AS addresses_id,
        addresses.email_address AS addresses_email_address,
        addresses.user_id AS addresses_user_id,
        anon_1.users_id AS anon_1_users_id
FROM (SELECT users.id AS users_id
    FROM users WHERE users.name = ?) AS anon_1
JOIN addresses ON anon_1.users_id = addresses.user_id
ORDER BY anon_1.users_id, addresses.id
('jack',)

```

> __注意:__
> 当在连词中使用`subqueryload()`的时候这里会有一点限制,比如`Query.first()`,`Query.limit()`或者`Query.offset()`应该也包括一个`Query.order_by()`连词在一个唯一的列上使用,以确保获得正确的结果.更多信息请参考: [The Importance of Ordering](http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#subqueryload-ordering).


### 连接载入

其他的自动立即载入的函数更加出名，它叫做`orm.joinedload()`。载入的风格是发送一个 JOIN 语句，默认是 LEFT OUTER JOIN，那样的话引导对象也会把相关对象或者集合一步载入的。下面我们将要以载入同样的`address`集合来说明。注意尽管`jack`用户上的`User.addresses`集合实际上已经被填充了，但是额外的 JOIN 语句仍然会被发出。

```py
>>> from sqlalchemy.orm import joinedload

>>> jack = session.query(User).\
...                        options(joinedload(User.addresses)).\
...                        filter_by(name='jack').one()
>>> jack
<User(name='jack', fullname='Jack Bean', password='gjffdd')>

>>> jack.addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]

# -------------- SQL ------------------ #

SELECT users.id AS users_id,
        users.name AS users_name,
        users.fullname AS users_fullname,
        users.password AS users_password,
        addresses_1.id AS addresses_1_id,
        addresses_1.email_address AS addresses_1_email_address,
        addresses_1.user_id AS addresses_1_user_id
FROM users
    LEFT OUTER JOIN addresses AS addresses_1 ON users.id = addresses_1.user_id
WHERE users.name = ? ORDER BY addresses_1.id
('jack',)

```

需要注意的是，尽管外连接的结果是两行，但我们仍然只得到了一个`User`。这是因为`Query`对象应用了一个"uniquing"的策略，基于对象标识，来返回实体。这个是有点特别的，所有连接查询的立即载入能够被应用到查询上而不影响查询结果。

然后`joinedload()`函数已经出现很久了，而`subqueryload()`函数是被新添加到立即载入中来的。`subqueryload()`更适合于载入相关的集合，而`joinedload()`更适合于载入多对一的关系，因为一个事实就是查询的目标对象和相关连的对象在`joinedload()`中只有一个被返回。

> `joinedload()`并不能够替换`join()`
>
> 由`joinedload()`函数创建的 JOIN 语句是一个匿名的别名，它实际上并不影响到查询结果。一个`Query.order_by()`或者一个`Query.filter()`函数并不能引用这个别名的表。所以被称为"用户空间"的连接是使用`Query.join()`函数来构造的。`joinedload()`函数被使用的理由就是为了去影响相关对象或者集合的载入情况，来作为一种优化细节存在的。它能够在不影响原有结果集的情况下被添加或者删除。参考 [The Zen of Eager Loading](http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#zen-of-eager-loading) 章节来获得这个函数被使用的更多的描述性的细节。

### 显式的 join + 立即载入

第三种风格的立即载入是当我们为了去定位主要行而显式地去构造`JOIN`，它看上去像是额外地去向一个主对象的相关对象或者集合额外地去应用额外的表。这个特点是通过`orm.contains_eager()`函数来支持的，这个函数最主要的场景就是在一个查询中需要去在相同的对象上过滤，用来提前载入一些多对一的对象。下面我们来说明在载入一个`Address`行的同时载入一个相关的`User`对象，同时过滤名字叫做 jack 的`User`对象，使用`orm.contains_eager()`去应用 "users" 列到`Address.user`属性上。

```py
>>> from sqlalchemy.orm import contains_eager
>>> jacks_addresses = session.query(Address).\
...                             join(Address.user).\
...                             filter(User.name=='jack').\
...                             options(contains_eager(Address.user)).\
...                             all()
>>> jacks_addresses
[<Address(email_address='jack@google.com')>, <Address(email_address='j25@yahoo.com')>]

>>> jacks_addresses[0].user
<User(name='jack', fullname='Jack Bean', password='gjffdd')>
```

想要参考更多的关于立即载入的信息，包括如何配置各种形式的载入的默认行为，请参考 [Relationship Loading Techniques](http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html) 章节。

## 删除

接下来让我们去删除`jack`对象，同时看看将会发生什么。我们将会在会话中标记那个对象为删除，然后我们将会发出一个`count`查询来看还有现在数据库中总共还有多少行。

```py
>>> session.delete(jack)
>>> session.query(User).filter_by(name='jack').count()
0

# ---------------- SQL ----------------

UPDATE addresses SET user_id=? WHERE addresses.id = ?
((None, 1), (None, 2))
DELETE FROM users WHERE users.id = ?
(5,)
SELECT count(*) AS count_1
FROM (SELECT users.id AS users_id,
        users.name AS users_name,
        users.fullname AS users_fullname,
        users.password AS users_password
FROM users
WHERE users.name = ?) AS anon_1
('jack',)
```

到目前为止，一切看起来都很好，那让我们看看和 jack 相关联的`Address`对象怎么样了：

```py
>>> session.query(Address).filter(
...     Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
...  ).count()
2
```

啊哦，它们依然在数据库中存在。分析刷新相关的 SQL 语句，我们可以看到相关的`Address`表中的每个`user_id`列都被设置成为了 NULL，但是 jack 代表的那一行却被删除了。SQLAlchemy 没有指定删除时的 cascade 行为，你必须告诉它它才会做这个动作。

### 配置级联删除/孤儿级联删除

我们将会配置 __cascade__ 选项在`User.relationship`关系上，去改变删除行为。虽然 SQLAlchemy 允许你在任何时刻添加属性和关系的映射，然而在这个例子中的已经存在的关系需要删除，所以我们需要完全解除映射关闭并且重新开始，我们将会关闭这个会话。

```py
session.close()
ROLLBACK
```

同时使用一个新的`declarative_base`，

```py
>>> Base = declarative_base()
```

接下来我们将会添加我们的`User`类，同时添加包括`cascade`配置的`addresses`关系，同时我们也将离开构造函数：

```py
>>> class User(Base):
...     __tablename__ = 'users'
...
...     id = Column(Integer, primary_key=True)
...     name = Column(String)
...     fullname = Column(String)
...     password = Column(String)
...
...     addresses = relationship("Address", back_populates='user',
...                     cascade="all, delete, delete-orphan")
...
...     def __repr__(self):
...        return "<User(name='%s', fullname='%s', password='%s')>" % (
...                                self.name, self.fullname, self.password)
```

然后我们将会创造`Address`类，注意在这个例子中我们将会通过已经存在的`User`对象来创造`Address.user`关系：

```py
>>> class Address(Base):
...     __tablename__ = 'addresses'
...     id = Column(Integer, primary_key=True)
...     email_address = Column(String, nullable=False)
...     user_id = Column(Integer, ForeignKey('users.id'))
...     user = relationship("User", back_populates="addresses")
...
...     def __repr__(self):
...         return "<Address(email_address='%s')>" % self.email_address
```

现在我们载入`jack`用户(下面代码中使用了`get()`来载入，它将会通过主键来载入)，从对应的`addresses`集合中删除地址将会导致所有相关的`Address`对象被删除：

```py
# load Jack by primary key
>>> jack = session.query(User).get(5)

# ----------------- SQL -----------------------
BEGIN (implicit)
SELECT users.id AS users_id,
        users.name AS users_name,
        users.fullname AS users_fullname,
        users.password AS users_password
FROM users
WHERE users.id = ?
(5,)

# remove one Address (lazy load fires off)
>>> del jack.addresses[1]

# only one address remains
>>> session.query(Address).filter(
...     Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
... ).count()
1
```

同时删除`jack`用户将会导致和`jack`相关联的所有`Address`条目被删除。

```py
>>> session.delete(jack)

# --------------------- SQL -------------------
DELETE FROM addresses WHERE addresses.id = ?
(1,)
DELETE FROM users WHERE users.id = ?
(5,)
SELECT count(*) AS count_1
FROM (SELECT users.id AS users_id,
                users.name AS users_name,
                users.fullname AS users_fullname,
                users.password AS users_password
FROM users
WHERE users.name = ?) AS anon_1
('jack',)

>>> session.query(User).filter_by(name='jack').count()
0

>>> session.query(Address).filter(
...    Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
... ).count()
0
```

> __关于 cascades 的更多信息__
>
> 关于 cascades 配置进一步的详细信息请参考 [Cascades 章节](http://docs.sqlalchemy.org/en/latest/orm/cascades.html#unitofwork-cascades)。cascades 函数在关系型数据库中也能够顺利地整合`ON DELETE CASCADE`功能。参考 [Using Passive Deletes 章节](http://docs.sqlalchemy.org/en/latest/orm/collections.html#passive-deletes)获取更多的信息。

## 建立多对多关系

我们正在进入这里的奖金轮，但是首先让我先炫耀一个多对多的关系。我们仍然将会使用到其他的一些特征，只是为了了解一下。我们将会制作我们的程序一个博客程序，这里用户能够写`BlogPost`项，它有一个`Keyword`属性和这个博客项关联。

为了使用多对多关系，我们需要去创建一个未映射的表结构，来作为一个相关表来进行工作。这看起来像下面这样：

```py
>>> from sqlalchemy import Table, Text
>>> # association table
>>> post_keywords = Table('post_keywords', Base.metadata,
...     Column('post_id', ForeignKey('posts.id'), primary_key=True),
...     Column('keyword_id', ForeignKey('keywords.id'), primary_key=True)
... )
```

在上面的代码中，我们能够看到直接声明一个表和通过一个映射类声明表有些不同。`Table`是一个构造函数，所以每个独立的`Column`参数通过逗号来分割。`Column`也被精确地给出了名字，而不是能够从关联的属性名那里能够获取到。

下面我们将会定义一个`BlogPost`和`Keyword`表，使用了附加的`relationship()`构造函数来定义，每个都通过索引`post_keyword`表来关联上一个表：

```py
>>> class BlogPost(Base):
...     __tablename__ = 'posts'
...
...     id = Column(Integer, primary_key=True)
...     user_id = Column(Integer, ForeignKey('users.id'))
...     headline = Column(String(255), nullable=False)
...     body = Column(Text)
...
...     # many to many BlogPost<->Keyword
...     keywords = relationship('Keyword',
...                             secondary=post_keywords,
...                             back_populates='posts')
...
...     def __init__(self, headline, body, author):
...         self.author = author
...         self.headline = headline
...         self.body = body
...
...     def __repr__(self):
...         return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


>>> class Keyword(Base):
...     __tablename__ = 'keywords'
...
...     id = Column(Integer, primary_key=True)
...     keyword = Column(String(50), nullable=False, unique=True)
...     posts = relationship('BlogPost',
...                          secondary=post_keywords,
...                          back_populates='keywords')
...
...     def __init__(self, keyword):
...         self.keyword = keyword
```

> __注意：__
>
> 上面的类声明精确地说明了`__init__()`方法，记住，当使用声明关系的时候，它是可选的。

如上所述，一个叫做`BlogPost.keywords`的多对多关系已经建立起来了。多对多关系的定义特征是通过`secondary`关键字来定义了，它索引了一个`Table`对象，代表它关联到了一张表上。这个表仅仅包含引用两边关系的列；如果想要让它有其他不同的列，比如它自己的主键，或者一个到其他表的外键，SQLAlchemy 需要不同的叫做“关联对象”的使用模式，这个在[关联对象](http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-pattern)章节中有详细描述。

同时，我们也想要让我们的`BlogPost`类能够拥有`author`域。我们将会添加这个作为另一个双向关系，除了一个问题，我们将会有一个单一的用户可能有多个博客页面。当我们访问`User.posts`的时候，我们将会想要去过滤结果而不是把整个集合都载入进来。为了完成这个功能，我们对`relationship()`设置了一个叫做`lazy='dynamic'`的参数，在这里，我们将会在属性上配置一个可替换的载入策略：

```py
>>> BlogPost.author = relationship(User, back_populates="posts")
>>> User.posts = relationship(BlogPost, back_populates="author", lazy="dynamic")
```

创建一个新的表格：

```py
>>> Base.metadata.create_all(engine)
```

用法和我们已经做过的没有太大的不同。让我们来给 Wendy 发表一些博客文章：

```
>>> wendy = session.query(User).\
...                 filter_by(name='wendy').\
...                 one()
>>> post = BlogPost("Wendy's Blog Post", "This is a test", wendy)
>>> session.add(post)
```

我们将会在数据库中存储唯一的关键字，但是我们知道现在还没有任何数据，所以让我们先来创建他们：

```py
>>> post.keywords.append(Keyword('wendy'))
>>> post.keywords.append(Keyword('firstpost'))
```

我们也能够查看所有拥有`firstpost`关键字的文章。我们将会使用`any`操作符去定位那些在关键字列表中拥有 "firstpost" 关键字的博客文章:

```py
>>> session.query(BlogPost).\
...             filter(BlogPost.keywords.any(keyword='firstpost')).\
...             all()
[BlogPost("Wendy's Blog Post", 'This is a test', <User(name='wendy', fullname='Wendy Williams', password='foobar')>)]
```

如果我们想要查询由用户`wendy`发布的所有文章，我们也能够缩小查询范围使用`User`对象作为父对象：

```py
>>> session.query(BlogPost).\
...             filter(BlogPost.author==wendy).\
...             filter(BlogPost.keywords.any(keyword='firstpost')).\
...             all()
[BlogPost("Wendy's Blog Post", 'This is a test', <User(name='wendy', fullname='Wendy Williams', password='foobar')>)]
```

或者我们也能够使用`wendy`自己的`posts`关系，它是一个动态的关系，查询直接来自这里：

```py
>>> wendy.posts.\
...         filter(BlogPost.keywords.any(keyword='firstpost')).\
...         all()
[BlogPost("Wendy's Blog Post", 'This is a test', <User(name='wendy', fullname='Wendy Williams', password='foobar')>)]
```

## 更多引用

+ 查询引用: query_api_toplevel
+ 映射引用: [Mapper Configuration](http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html)
+ 关系引用: [Relationship Configuration](http://docs.sqlalchemy.org/en/latest/orm/relationships.html)
+ 会话引用: [Using the Session](http://docs.sqlalchemy.org/en/latest/orm/session.html)
