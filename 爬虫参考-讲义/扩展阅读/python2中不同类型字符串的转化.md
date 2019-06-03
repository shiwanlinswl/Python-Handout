## python2中的字符串 
python2中字符串有两种类型 
- unicode类型 
- 字节类型

在Python2中，字符串无法完全地支持国际字符集和Unicode编码。为了解决这种限制，Python2对Unicode数据使用了单独的字符串类型。要输入Unicode字符串字面量，要在第一个引号前加上'u'。

Python2中普通字符串实际上就是已经编码(非Unicode)的**字节字符串**。

#### 1 python2中的字节类型字符串
python2 中定义字符串的时候，会自动将字符串转换为合适编码的字节字符串，比如中文：自动转换为utf-8编码的字节字符串

看下面的例子：

```
>>> a = "传智播客" #如此定义字符串的时候，其为字节类型
>>> a '\xe4\xbc\xa0\xe6\x99\xba\xe6\x92\xad\xe5\xae\xa2'
>>> type(a) <type 'str'>
```

上面的这种定义和在字符串前面加上b的效果一样

```
>>> c = b"传智播客"
>>> c
'\xe4\xbc\xa0\xe6\x99\xba\xe6\x92\xad\xe5\xae\xa2'
>>> type(c)
<type 'str'>
>>> c.decode("utf-8")
u'\u4f20\u667a\u64ad\u5ba2'
```

由于a已经是字节类型，所以只能对其进行解码，转化为str类型

```
>>> a.encode("utf-8")
Traceback
(most recent call last): File "<stdin>", line 1, in <module>

UnicodeDecodeError: 'ascii' codec can't decode byte 0xe4 in position 0: ordinal not in range(128)

>>> a.decode("utf-8")
u'\u4f20\u667a\u64ad\u5ba2'
```

#### 2 python2中的unicode类型字符串 
如果需要定义unicode字符串，即非字节类型的字符串的时候需要在前面加上u

```
>>> b = u"传智播客"
>>> b u'\u4f20\u667a\u64ad\u5ba2'
>>> type(b)
<type 'unicode'>
>>> b.encode("utf-8") '\xe4\xbc\xa0\xe6\x99\xba\xe6\x92\xad\xe5\xae\xa2'
```

#### 3 python2中字节类型和unicode类型的转化 
- 字节类型通过decode转化为unicode类型
- unciode类型通过encode方法转化为字节类型
- 方法的使用和python3相同，但是在方法中默认的编解码方式为`ascii`，对中文需要手动指定为`utf-8`

```
>>> b
u'\u4f20\u667a\u64ad\u5ba2'

>>> b.encode()
Traceback
(most recent call last): File "<stdin>", line 1, in <module>
UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-3: ordinal not in range(128)

>>> b.encode("utf-8") '\xe4\xbc\xa0\xe6\x99\xba\xe6\x92\xad\xe5\xae\xa2'
```


