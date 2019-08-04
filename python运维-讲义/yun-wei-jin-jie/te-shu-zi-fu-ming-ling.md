# 特殊字符命令

## 1. “?”和“\*”

* **?：**代表任意1个字符

* **\*：**代表零到多个任意字符

**例1：**查看/bin目录下面只有两个字符的命令

```Bash
[root@localhost ~]# ls /bin/??
/bin/ar  /bin/bg  /bin/cp  /bin/df  /bin/ex  /bin/fg  /bin/ld  /bin/ls  /bin/nl  /bin/od  /bin/ps  /bin/sg  /bin/su  /bin/ul  /bin/wc
/bin/as  /bin/cd  /bin/dd  /bin/du  /bin/fc  /bin/id  /bin/ln  /bin/mv  /bin/nm  /bin/pr  /bin/rm  /bin/sh  /bin/tr  /bin/vi  /bin/xz
```

**例2：**查看/root目录下以.txt结尾的文件

```Bash
[root@localhost ~]# ls
anaconda-ks.cfg  itcast  python.txt
[root@localhost ~]# ls *.txt
python.txt
```

## 2. “ \| ”：管道符号

**作用：**

把前一个命令结果的输出交给后一个命令继续处理

![](/assets/pipe.png)

**例1：**分页查看/etc目录下面的文件（包含目录）

```Bash
[root@localhost ~]# ls /etc | more
adjtime
aliases
aliases.db
alternatives
anacrontab
asound.conf
audisp
audit
bash_completion.d
bashrc
binfmt.d
centos-release
centos-release-upstream
chkconfig.d
chrony.conf
chrony.keys
cron.d
cron.daily
cron.deny
cron.hourly
cron.monthly
crontab
cron.weekly
crypttab
csh.cshrc
csh.login
dbus-1
default
depmod.d
dhcp
DIR_COLORS
DIR_COLORS.256color
DIR_COLORS.lightbgcolor
dracut.conf
--More--
```

## 3. 数据流及重定向

* **输入流：**从键盘或者文件中读取内容到内存中

* **输出流：**从计算机内存中把数据写入到文件或者显示到显示器上

![](/assets/data_stream.png)

* **重定向：**改变数据的流向

![](/assets/redirect.png)

Linux中有三种流：标准输出流、标准错误输出流、标准输入流。

* **标准输入（stdin）：**代码为0，使用&lt;或&lt;&lt;；数据流向，从右向左。
* **标准输出（stdout）：**代码为1，使用&gt;或&gt;&gt;；数据流向，从左向右。
* **标准错误输出（stderr）：**代码为2，使用2&gt;或2&gt;&gt;；

### 3.1 标准输出（&gt;或&gt;&gt;）与标准错误输出（2&gt;或2&gt;&gt;）

**例1：**观察/目录下的所有内容，并记录下来

```Bash
[root@localhost ~]# ls -l /
总用量 16
lrwxrwxrwx.   1 root root    7 1月  21 21:33 bin -> usr/bin
dr-xr-xr-x.   5 root root 4096 1月  21 21:49 boot
drwxr-xr-x.  21 root root 3300 1月  23 11:42 dev
drwxr-xr-x.  75 root root 8192 1月  23 21:20 etc
drwxr-xr-x.   2 root root    6 4月  11 2018 home
lrwxrwxrwx.   1 root root    7 1月  21 21:33 lib -> usr/lib
lrwxrwxrwx.   1 root root    9 1月  21 21:33 lib64 -> usr/lib64
drwxr-xr-x.   2 root root    6 4月  11 2018 media
drwxr-xr-x.   2 root root    6 4月  11 2018 mnt
drwxr-xr-x.   2 root root    6 4月  11 2018 opt
dr-xr-xr-x. 124 root root    0 1月  23 11:42 proc
dr-xr-x---.   4 root root  217 1月  23 20:47 root
drwxr-xr-x.  24 root root  740 1月  23 21:20 run
lrwxrwxrwx.   1 root root    8 1月  21 21:33 sbin -> usr/sbin
drwxr-xr-x.   2 root root    6 4月  11 2018 srv
dr-xr-xr-x.  13 root root    0 1月  23 11:42 sys
drwxrwxrwt.   9 root root  230 1月  23 20:42 tmp
drwxr-xr-x.  13 root root  155 1月  21 21:33 usr
drwxr-xr-x.  19 root root  267 1月  21 21:49 var

# 将ls -l的输出重定向到roofile文件里面
[root@localhost ~]# ls -l / > rootfile

[root@localhost ~]# ls -l rootfile
-rw-r--r--. 1 root root 1014 1月  23 21:36 rootfile
# rootfile文件创建了

# 查看rootfile文件内容
[root@localhost ~]# cat rootfile
总用量 16
lrwxrwxrwx.   1 root root    7 1月  21 21:33 bin -> usr/bin
dr-xr-xr-x.   5 root root 4096 1月  21 21:49 boot
drwxr-xr-x.  21 root root 3300 1月  23 11:42 dev
drwxr-xr-x.  75 root root 8192 1月  23 21:20 etc
drwxr-xr-x.   2 root root    6 4月  11 2018 home
lrwxrwxrwx.   1 root root    7 1月  21 21:33 lib -> usr/lib
lrwxrwxrwx.   1 root root    9 1月  21 21:33 lib64 -> usr/lib64
drwxr-xr-x.   2 root root    6 4月  11 2018 media
drwxr-xr-x.   2 root root    6 4月  11 2018 mnt
drwxr-xr-x.   2 root root    6 4月  11 2018 opt
dr-xr-xr-x. 124 root root    0 1月  23 11:42 proc
dr-xr-x---.   4 root root  233 1月  23 21:36 root
drwxr-xr-x.  24 root root  740 1月  23 21:20 run
lrwxrwxrwx.   1 root root    8 1月  21 21:33 sbin -> usr/sbin
drwxr-xr-x.   2 root root    6 4月  11 2018 srv
dr-xr-xr-x.  13 root root    0 1月  23 11:42 sys
drwxrwxrwt.   9 root root  230 1月  23 20:42 tmp
drwxr-xr-x.  13 root root  155 1月  21 21:33 usr
drwxr-xr-x.  19 root root  267 1月  21 21:49 var
```

**例2：**查看一个不存在的文件，并记录下来

```Bash
[root@localhost ~]# ls hahaha 2> error.log
[root@localhost ~]# cat error.log
ls: 无法访问hahaha: 没有那个文件或目录
```

**例3：**将ls -l /结果输出追加重定向到rootfile文件

```Bash
# 两个>>就是追加重定向
[root@localhost ~]# ls -l >> rootfile

# 查看rootfile文件内容
[root@localhost ~]# cat rootfile
总用量 16
lrwxrwxrwx.   1 root root    7 1月  21 21:33 bin -> usr/bin
dr-xr-xr-x.   5 root root 4096 1月  21 21:49 boot
drwxr-xr-x.  21 root root 3300 1月  23 11:42 dev
drwxr-xr-x.  75 root root 8192 1月  23 21:20 etc
drwxr-xr-x.   2 root root    6 4月  11 2018 home
lrwxrwxrwx.   1 root root    7 1月  21 21:33 lib -> usr/lib
lrwxrwxrwx.   1 root root    9 1月  21 21:33 lib64 -> usr/lib64
drwxr-xr-x.   2 root root    6 4月  11 2018 media
drwxr-xr-x.   2 root root    6 4月  11 2018 mnt
drwxr-xr-x.   2 root root    6 4月  11 2018 opt
dr-xr-xr-x. 124 root root    0 1月  23 11:42 proc
dr-xr-x---.   4 root root  233 1月  23 21:36 root
drwxr-xr-x.  24 root root  740 1月  23 21:20 run
lrwxrwxrwx.   1 root root    8 1月  21 21:33 sbin -> usr/sbin
drwxr-xr-x.   2 root root    6 4月  11 2018 srv
dr-xr-xr-x.  13 root root    0 1月  23 11:42 sys
drwxrwxrwt.   9 root root  230 1月  23 20:42 tmp
drwxr-xr-x.  13 root root  155 1月  21 21:33 usr
drwxr-xr-x.  19 root root  267 1月  21 21:49 var
总用量 24
-rw-------. 1 root root 1257 1月  21 21:37 anaconda-ks.cfg
-rw-r--r--. 1 root root   52 1月  23 21:44 error.log
-rw-r--r--. 2 root root  158 6月   7 2013 hosts_hard_link
drwxr-xr-x. 3 root root   19 1月  22 17:59 itcast
drwxr-xr-x. 2 root root 4096 1月  22 00:00 log
-rw-r--r--. 1 root root    6 1月  23 19:09 python.txt
-rw-r--r--. 1 root root 1014 1月  23 21:36 rootfile
```

* **1&gt;：**以覆盖的方法将**正确的数据**输出到指定的文件或装置上；
* **1&gt;&gt;：**以追加的方法**将正确的数据**输出到指定的文件或装置上；
* **2&gt;：**以覆盖的方法**将错误的数据**输出到指定的文件或装置上；
* **2&gt;&gt;：**以追加的方法**将错误的数据**输出到指定的文件或装置上；

> **注意：**标准输出中1可以省略不写，标准错误输出2一定不能省略

### 3.2 标准输入（&lt;与&lt;&lt;）

* **&lt;：**将原来本需要由键盘输入的数据，改由文件内容来取代。

**例1：**利用cat指令来建立一个文件的简单流程

```Bash
# cat > 可以创建文件
[root@localhost ~]# cat > catfile
abcdef
123456
<==这里按下ctrl+d来离开

# 查看文件catfile内容
[root@localhost ~]# cat catfile
abcdef
123456
```

**例2：**用标准输入取代键盘的输入以建立新文件的简单流程

```Bash
[root@localhost ~]# cat > catfile < .bashrc

# 查看catfile文件内容
[root@localhost ~]# cat catfile
# .bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# 查看.bashrc文件内容
[root@localhost ~]# cat .bashrc
# .bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi
```

* **&lt;&lt;：**结束的输入字符的意思，例如：我要让键盘输入EOF时，该次输入就结束，可以这样做：

```Bash
[root@localhost ~]# cat > catfile << EOF
> hello world
> hello python
> EOF
# 输入EOF这关键词，立刻就结束而不需要输入ctrl+d

# 查看catfile文件内容
[root@localhost ~]# cat catfile
hello world
hello python
# 只有这两行，不会存在关键词那一行
```

> **注意：**EOF可以用任意字符替代

## 4. 命令排列

如果希望一次执行多个命令，shell允许在不同的命令之间，放上特殊的排列字符。命令排列可以使用两种排列字符：**“;”和“&&”。**

### 4.1 使用“;”

先执行命令1，不管命令1是否出错，接下来就执行命令2。

**语法格式：**

```Bash
命令1;命令2;命令...
```

### 4.2 使用“&&”

使用“&&”命令时，只有当命令1正确运行完毕后，才能执行命令2。

**语法格式：**

```Bash
命令1&&命令2&&命令...
```

## 5. 命令替换

命令替换可以使用两种替换字符，**“$\(\)”和“\`\`”。**

**使用“$\(\)”**

```Bash
命令1 $(命令2)
```

**使用“\`\`”**

```Bash
命令1 `命令2`
```



