# 1. 特殊字符命令

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

## 2. “\|”：管道符号



