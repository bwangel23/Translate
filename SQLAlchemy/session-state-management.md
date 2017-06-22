状态管理
========

__摘要__:

> 1. 原文地址：[State Management](http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html#quickie-intro-to-object-states)

## 对于对象状态的快速介绍

了解一个 Session 中的实例能够拥有的状态是非常有用的：

+ Transient 这代表了一个实例没有在一个 Session 中，同时它也没有被保存到数据库中；既，它也没有数据库标识。这样的一个实例和 ORM 的唯一关系就是它的类有一个`mapper()`方法和它关联着。

+ Pending 当你`add()`一个 transient 实例的时候，它就变成了 pending 状态。它实际上仍然没有刷新到数据库中，但是当下一次刷新发生的时候它就会进行刷新

+ Persistent 一个实例它现在在一个 Session 中，同时在数据库中也有一条记录了。你可以通过刷新一个 Pending 实例来使它变成 Persistent 的，或者通过查询数据库来获取已经存在的实例来获取一个 Persistent 实例(或者移动其他 Session 中的 Persistent 实例到你当前的 Session 中)。

+ Deleted 在一次刷新中一个实例已经被删除了，但是事务还没有完成。在这个状态上的对象实际上与 "pending" 状态的实例在相反的状态，当 Session 事务被提交了以后，对象将会被移动到 detached 状态。或者，当 Session 事务回滚的时候，一个 deleted 的对象会回退到 Persistent 状态。

> `Changed in version 1.1`: 'delete' 状态新添加到了 session 对象状态中，不同于 'persistent' 状态

+ Detached 一个实例代表着，或者先前代表着数据库中的一条记录，但是它现在不存在于任何一个 Session 中。Detached 对象将会包含一个数据库标识标记，然而由于它没有关联到任何一个 Session 中，我们无法确定这个数据库标识对于目标数据库来说是否还可用。Detached 对象可以安全地正常使用，除了它们没有能力去载入未载入的属性或者是先前已经标记为"过期"的属性。

想要更深地挖掘所有可能的状态转换，参考[ Object Lifecycle Events ](http://docs.sqlalchemy.org/en/latest/orm/session_events.html#session-lifecycle-events)部分，它将会描述每个可能的状态转换，以及如何使用编程来跟踪这些状态转换。

### 得到一个对象的当前状态

一个映射对象的实际状态能够在任何时候通过[`inspect()`](http://docs.sqlalchemy.org/en/latest/core/inspection.html#sqlalchemy.inspection.inspect)系统来查看

```py
>>> from sqlalchemy import inspect
>>> insp = inspect(my_object)
>>> insp.persistent
```

> 参考
> 
> [InstanceState.transient](http://docs.sqlalchemy.org/en/latest/orm/internals.html#sqlalchemy.orm.state.InstanceState.transient)
> 
> [InstanceState.pending](http://docs.sqlalchemy.org/en/latest/orm/internals.html#sqlalchemy.orm.state.InstanceState.pending)
> 
> [InstanceState.persistent](http://docs.sqlalchemy.org/en/latest/orm/internals.html#sqlalchemy.orm.state.InstanceState.persistent)
> 
> [InstanceState.deleted](http://docs.sqlalchemy.org/en/latest/orm/internals.html#sqlalchemy.orm.state.InstanceState.deleted)
> 
> [InstanceState.detached](http://docs.sqlalchemy.org/en/latest/orm/internals.html#sqlalchemy.orm.state.InstanceState.detached)
