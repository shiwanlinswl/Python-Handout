# ls、cd、pwd命令

## 1. ls（List Directory Contents）：显示目录下的内容及相关属性信息

**语法格式：**

```bash
ls [选项] [文件或目录]
```

**选项：**

* **-l：**使用长格式列出文件及目录信息

* **-a：**显示目录下的所有文件，包括以“.”字符开始的隐藏文件

* **-h：**以人类可读的信息显示文件或目录大小（需要结合-l选项）

* **-d：**当遇到目录时，列出目录本身而不是目录内的内容（结合-l选项可以查看目录的详细信息）

* **-t：**根据最后的修改时间（mtime）排序，默认是以文件名排序

* **-F：**在条目后加上文件类型的指示符号（\*、/、＝、@、\|、其中的一个）

  * **/：**表示目录

  * **@：**表示符号链接文件。

  * **★：**表示可执行文件。

  * **\|：**表示管道文件。

  * **=：**表示socket文件

  * **@：**表示符号链接

**例1：**列出当前工作目录下的文件和目录

```Bash
[root@localhost ~]# ls
anaconda-ks.cfg
```

**例2：**列出/下的文件和目录

```Bash
[root@localhost ~]# ls /
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

**例3：**使用长格式方式列出/下的文件和目录

```Bash
[root@localhost ~]# ls -l /
总用量 16
lrwxrwxrwx.   1 root root    7 1月  21 21:33 bin -> usr/bin
dr-xr-xr-x.   5 root root 4096 1月  21 21:49 boot
drwxr-xr-x.  21 root root 3300 1月  22 2019 dev
drwxr-xr-x.  75 root root 8192 1月  22 2019 etc
drwxr-xr-x.   2 root root    6 4月  11 2018 home
lrwxrwxrwx.   1 root root    7 1月  21 21:33 lib -> usr/lib
lrwxrwxrwx.   1 root root    9 1月  21 21:33 lib64 -> usr/lib64
drwxr-xr-x.   2 root root    6 4月  11 2018 media
drwxr-xr-x.   2 root root    6 4月  11 2018 mnt
drwxr-xr-x.   2 root root    6 4月  11 2018 opt
dr-xr-xr-x. 120 root root    0 1月  22 2019 proc
dr-xr-x---.   2 root root  135 1月  21 22:34 root
drwxr-xr-x.  24 root root  740 1月  22 2019 run
lrwxrwxrwx.   1 root root    8 1月  21 21:33 sbin -> usr/sbin
drwxr-xr-x.   2 root root    6 4月  11 2018 srv
dr-xr-xr-x.  13 root root    0 1月  22 2019 sys
drwxrwxrwt.   9 root root  230 1月  22 14:16 tmp
drwxr-xr-x.  13 root root  155 1月  21 21:33 usr
drwxr-xr-x.  19 root root  267 1月  21 21:49 var
```

## 2. cd（Change Directory）：切换目录

### 2.1 绝对路径和相对路径

* **绝对路径：**路径的写法一定从根目录/写起，例如：/root这个目录。
* **相对路径：**路径的写法不是从跟写起，例如从/usr/share/doc要到/usr/share/man底下时，可以写成：`cd ../man`这就是相对路径的写法。

**命令作用：**

从当前目录切换到指定的工作目录

**语法格式：**

```Bash
cd [选项] [目录]
```

**选项：**

* **-：**当只使用“－”选项时，代表的是切换到当前用户上一次所在的目录路径 

* **~：**当只使用“~”选项时，代表的是切换到当前用户的家目录所在的路径 

* **..：**当只使用“..”选项时，将会从当前目录切换到当前目录的上一级目录所在的路径

> **注意：**.和..的区别，.代表的是当前目录，..代表的是上一层目录

**例1：**切换到/etc目录下

```Bash
[root@localhost ~]# cd /etc
[root@localhost etc]#
```

**例2：**回到当前用户上一次所在的目录

```Bash
[root@localhost etc]# cd -
/root
[root@localhost ~]#
```

## 3. pwd（Print Working Directory）：显示当前所在的位置

**命令作用： **

显示当前工作目录的绝对路径 

**语法格式：**

```Bash
pwd [选项]
```

**选项：**

无常用选项

**例1：**显示当前工作目录路径

```Bash
[root@localhost ~]# pwd
/root
```



