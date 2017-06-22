Table Panel
============

__摘要__:

> 原文地址：[http://docs.grafana.org/reference/table_panel/](http://docs.grafana.org/reference/table_panel/)

![](http://docs.grafana.org/assets/img/features/table-panel.png)

新的表格面板非常灵活，支持时序的多种模式，以及表格，注解和原始JSON数据等等。它也提供了数据格式化和值格式化和颜色选项等等。

## 选项概览

表格面板提供了多种方式来操作你的数据以达到最佳呈现效果。

![](http://docs.grafana.org/img/docs/v2/table-config2.png)

1. `Data`: 控制你的数据如何转换到表中
2. `Table Display`:  表显示选项
3. `Column Styles`: 列值格式化和显示选项

## 数据到表格

![](http://docs.grafana.org/img/docs/v2/table-data-options.png)

数据部分包含了 __To Table Transform(1)__ 。这是一个主要的选项用来控制你的数据/测量值，如何来转换成表格式。__Column (2)__ 选项允许你你想要在表格中显示的列，这仅仅适合某些转换。

### 时序到行

![](http://docs.grafana.org/img/docs/v2/table_ts_to_rows2.png)

在大多数的简单模式中，你可以将时序转换成行。这意味着你可以得到，`Time`，`Metric`，`Value`列。`Metric`是一个时序的名字。

### 时序到列

![](http://docs.grafana.org/img/docs/v2/table_ts_to_columns2.png)

这个转换允许你获取多个时序，然后由时间来进行分组。这将会让主要的列是`Time`，每个时序一个列。

### 时序聚合

![](http://docs.grafana.org/img/docs/v2/table_ts_to_aggregations2.png)

根据指标将表格转换成行，允许的列是`Avg`，`Min`，`Max`，`Current`和`Count`。超过一列能够被添加。

### 注解

![](http://docs.grafana.org/img/docs/v2/table_annotations.png)

如果你有一个在控制面板中开启了一个注解，你可以在表格中显示他们。如果你配置了这个模式，那么你在metric标签中的任意查询都会被忽略。

### JSON 数据

![](http://docs.grafana.org/img/docs/v2/table_json_data.png)

如果你有一个 Elasticseach 原始文档查询或者一个 Elasticsearch 查询没有`data histogram`参数，这个模式将会从 __Columns__ 部分中获取列名。

![](http://docs.grafana.org/img/docs/v2/elastic_raw_doc.png)
