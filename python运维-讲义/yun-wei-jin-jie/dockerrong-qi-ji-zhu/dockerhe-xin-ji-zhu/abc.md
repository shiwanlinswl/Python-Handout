```
# 容器管理
```


    ## 1. 容器简介

    容器是什么? 容器就类似于我们运行起来的一个操作系统，而且这个操作系统启动了某些服务。 这里的容器指的是运行起来的一个Docker镜像。

    ## 2. 查看、启动

    ### 2.1 查看容器

    **命令格式：**

    ```Bash
    docker ps
    ```

    > **注意：**
    >
    > * 管理docker容器可以通过名称，也可以通过ID
    > * ps是显示正在运行的容器，-a是显示所有运行过的容器，包括已经不运行的容器

    ### 2.2 启动容器

    启动容器有三种方式：

    * 基于镜像新建一个容器并启动
    * 将关闭的容器重新启动
    * 守护进程方式启动docker

    #### 2.2.1 创建新容器并启动

    **命令格式：**

    ```Bash
    docker run <参数，可选> [docker_image] [执行的命令]
    ```

    启动一个镜像，输入信息后关闭容器

    ```Bash
    docker run nginx /bin/echo "hello docker"
    ```

    > **注意：**  
    > docker run其实是两个命令的集合体docker create + docker start

    #### 2.2.2 启动已终止的容器

    在生产过程中，常常会出现运行和不运行的容器，我们使用start命令开起一个已关闭的容器

    **命令格式：**

    ```Bash
    docker start [container_id] | 容器名称
    ```

    #### 2.2.3 守护进程方式启动容器

    更多的时候，需要让Docker容器在后台以守护形式运行。此时可以通过添加-d参数来实现

    **命令格式：**

    ```Bash
    docker run -d [image_name] command ...
    ```

    守护进程方式启动容器

    ```Bash
    docker run -d nginx
    ```

    ## 3. 关闭、删除

    ### 3.1 关闭容器

    在生产中，我们会以为临时情况，要关闭某些容器，我们使用stop命令来关闭某个容器 

    **命令格式：**

    ```Bash
    docker stop [container_id] | 容器名称
    ```

    关闭容器id

    ```Bash
    docker stop 8005c40a1d16
    ```

    ### 3.2 删除容器

    删除容器有两种方法：

    * 正常删除--删除已关闭的 

    * 强制删除--删除正在运行的

    #### 3.2.1 正常删除容器

    **命令格式：**

    ```Bash
    docker rm [container_id]
    ```

    删除已关闭的容器

    ```Bash
    docker rm 1a5f6a0c9443
    ```

    #### 3.2.2 强制删除运行容器

    **命令格式：**

    ```Bash
    docker rm -f [container_id]
    ```

    删除正在运行的容器

    ```Bash
    docker rm -f 8005c40a1d16
    ```

    **拓展：**批量关闭容器

    **命令格式：**

    ```Bash
    docker rm -f $(docker ps -a -q)
    ```

    ## 4. 进入、退出

    进入容器我们学习三种方法：

    * 创建容器的同时进入容器
    * 手工方式进入容器
    * 生产方式进入容器

    ### 4.1 创建并进入容器

    **命令格式：**

    ```Bash
    docker run --name [container_name] -it [docker_image] /bin/bash
    ```

    ```Bash
    [root@localhost ~]# docker run -it --name webserver nginx /bin/bash
    root@5721456ce1c6:/# echo "Hello World"
    Hello World
    root@5721456ce1c6:/# exit
    exit
    ```

    docker容器启动命令参数详解：

    * **--name：**给容器定义一个名称
    * **-i：**则让容器的标准输入保持打开
    * **-t：**让docker分配一个伪终端，并绑定到容器的标准输入上
    * **/bin/bash：**执行一个命令

    ### 4.2 退出容器

    * **方法一：**exit

    * **方法二：**Ctrl + D

    ### 4.3 手工方式进入容器

    **命令格式：**

    ```Bash
    docker exec -it 容器id /bin/bash
    ```

    **效果演示：**

    ```Bash
    docker exec -it d74fff341687 /bin/bash
    ```

    ### 4.4 生产方式进入容器

    我们生产中常用的进入容器方法是使用脚本，脚本内容如下：

    ```Bash
    #!/bin/bash

    # 定义进入仓库函数
    docker_in(){
        NAME_ID=$1
        PID=$(docker inspect -f "{{ .State.Pid }}" $NAME_ID)
        nsenter -t $PID -m -u -i -n -p
    }
    docker_in $1
    ```

    赋权执行

    ```Bash
    chmod +x docker_in.sh
    ```

    进入指定的容器，并测试

    ```Bash
    ./docker_in.sh b3fbcba852fd
    ```

    ## 5. 基于容器创建镜像

    ### 5.1 提交方式
    命令格式:

    docker commit -m '改动信息' -a "作者信息" \[container\_id\] \[new\_image:tag\]命令演示:

    ```
        进入一个容器，创建文件后并退出

    ```

    ./docker\_in.sh d74fff341687 mkdir /sswang  
     exit

    创建一个镜像

    docker commit -m 'mkdir /sswang' -a "sswang" d74fff341687 sswang-nginx:v0.2

    查看镜像

    docker images

    启动一个容器

    docker run -itd sswang-nginx:v0.2 /bin/bash

    进入容器进行查看

    ./docker\_in.sh ae63ab299a84 ls

    导出方式:命令格式:

    docker export \[容器id\] &gt;模板文件名.tar注意:

    docker export导出镜像的时候，会丢失很多历史记录和元数据信息。 命令演示:

    创建镜像

    docker export ae63ab299a84 &gt; gaoji.tar

    导入镜像

    cat gaoji.tar \| docker import - sswang-test

    2.2.6日志、信息这一节，我们从日志、详细信息两方面来学习。

    ```
    查看容器运行日志
      命令格式:

    ```

    docker logs \[容器id\]命令效果:

    docker logs 7c5a24a68f96

    ```
    查看容器详细信息
      命令格式:

    ```

    docker inspect \[容器id\]命令效果:

    查看容器全部信息

    docker inspect 930f29ccdf8a

    查看容器网络信息

    docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 930f29ccdf8a

    ```
    查看容器端口信息
    ```

    ```
      命令格式:

    ```

    docker port \[容器id\]命令效果:

    docker port 930f29ccdf8a

    2.1.7小结

    内容小结:  
     查看:docker ps

    内部架构文档

    ./docker\_in.sh ae63ab299a84 ls

    docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 930f29cc df8a

    12

    启动:docker run &lt;参数，可选&gt; \[docker\_image\] \[执行的命令\] docker start \[container\_id\]

    关闭:docker stop \[container\_id\]  
    删除:docker rm &lt;-f&gt; \[container\_id\]  
    进入:docker run --name \[container\_name\] -it \[docker\_image\] /bin/bash

    docker exec -it容器id /bin/bash退出:exit或者Ctrl + D

    创建:docker commit -m '改动信息' -a "作者信息" \[container\_id\] \[new\_image:tag\] docker export \[容器id\] &gt;模板文件名.tar

    日志:docker logs \[容器id\]信息:docker inspect \[容器id\]

    docker port \[容器id\]







