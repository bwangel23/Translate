Moduel ngx_http_rewrite_module
==============================

## rewrite 指令

```
Syntax: rewrite regex replacement [flag];
Default: -
Content: Server, Location, Default
```
如果指定的正则表达式匹配请求的 URI，URI 按照 *replacement* 字符串中指定的方式来改变。rewrite 指令按照他们在配置文件中出现的顺序来执行。可以使用指令来终结指令的进一步处理。如果替换字符串以`http://`或者`https://`开头，那么处理程序就会结束然后给客户端返回一个重定向。

可选的`flag`参数可以是下面这些值：

+ last

    停止处理当前的 ngx_http_rewrite_module 指令集的处理，同时开始搜索新的匹配更改后的URI的 location

+ break

    停止处理当前的 ngx_http_rewrite_module 指令集的处理，就好像 [break](http://nginx.org/en/docs/http/ngx_http_rewrite_module.html#break) 指令一样

+ redirect

    返回一个临时的重定向，返回码是 302；这个使用在如果替换字符串没有以`http://`或者`https://`开头

+ permanent

    返回一个永久的重定向，返回码是 301;

完整的重定向指令是根据请求的方案(schema, $schema)，和 [server_name_in_redirect](http://nginx.org/en/docs/http/ngx_http_core_module.html#server_name_in_redirect) 指令和 [port_in_redirect](http://nginx.org/en/docs/http/ngx_http_core_module.html#port_in_redirect) 指令一起生成的。

例子：

```
server {
    ...
    rewrite ^(/download/.*)/media/(.*)\..*$ $1/mp3/$2.mp3 last;
    rewrite ^(/download/.*)/audio/(.*)\..*$ $1/mp3/$2.ra last;
    return 403;
    ...
}
```

但是如果这些指令放在了 "/download" location 的内部，那么`last`标志就应该被替换成`break`，否则的话 Nginx 就会运行10次循环同时返回一个 500 错误。

```
location /download/ {
    rewrite ^(/downlaod/.*)/media/(.*)\..*$ $1/mp3/$2.mp3 break;
    rewrite ^(/download/.*)/audio/(.*)\..*$ $1/mp3/$2.ra break;
    return 403;
}
```

如果替换字符串包括了一个新的请求参数，原来的请求参数被添加到了他们的末尾。如果这是不期望的，在替换字符串的末尾放置一个问号标记来避免添加原来的参数，比如像下面这样:

```
rewrite ^/users/(.*)$ /show?user=$1? last;
```

如果正则表达式包括了 "}" 或者 ";" 字符串，整个表达式应该用单引号或者双引号包裹起来。
