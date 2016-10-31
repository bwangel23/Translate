Simple statements
=================

## 7.7 The yield statement

> yield_stmt ::= yield_expression

一个 yield 语句在语义上等于[yield 表达式](https://docs.python.org/3/reference/expressions.html#yieldexpr)。yield语句能够用来忽略在 yield 表达式中需要的括号。例如，如下的 yield 语句：

```python
yield <expr>
yield from <expr>
```

等价于如下的 yield 表达式语句：

```python
(yield <expr>)
(yield from <expr>)
```

yield 表达式和语句仅仅用于在定义一个生成器函数的时候，而且仅仅用于生成器函数内部。在一个函数定义中使用 yield 关键字足够去定义一个生成器函数而不是一个普通函数。

想要了解 yield 语义的细节，请参考 [yield 表达式](https://docs.python.org/3/reference/expressions.html#yieldexpr) 部分。
