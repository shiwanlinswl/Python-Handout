# DNS服务器搭建

## 

### 4.1 新建正向查找区域

**步骤1：**打开“DNS”管理器

![](/assets/dns_conf.png)**步骤2：**鼠标右键单击“正向查找区域”，然后选择“新建区域”

![](/assets/dns_conf2.png)

**步骤3：**选择“下一步”![](/assets/dns_conf3.png)**步骤4：**选择创建的区域类型为“主要区域”，然后选择“下一步”

![](/assets/dns_conf4.png)**步骤5：**输入“区域名称”（域名），然后选择“下一步”

![](/assets/dns_conf5.png)**步骤6：**区域文件名保持默认，然后选择“下一步”

![](/assets/dns_conf6.png)**步骤7：**保持默认“不允许更新”，然后选择“下一步”

![](/assets/dns_conf7.png)**步骤8：**“完成”正向查找区域的创建

### ![](/assets/dns_conf8.png)4.2 新建主机记录

假设公司现在有一台web服务器，web服务器的IP地址为：192.168.10.200，现在需要让用户能够输入www.itcast.itcast这个网址就能访问该web服务器，这个时候我就需要新建主机记录

**步骤1：**鼠标右键单击前面新建的“itcast.itcast”正向查找区域，然后选择“新建主机（A或AAAA）”

![](/assets/dns_conf9.png)

**步骤2：添加主机**

![](/assets/dns_conf10.png)

**步骤3：**查看新建的主机记录

![](/assets/dns_conf11.png)

### 4.3 新建反向查找区域

**步骤1：**鼠标右键单击“反向查找区域”，然后选择“新建区域”

![](/assets/dns_conf12.png)

**步骤2：**选择“下一步”

![](/assets/dns_conf13.png)**步骤3：**新建“主要区域”，然后选择“下一步”

![](/assets/dns_conf14.png)**步骤4：**选择“IPv4反向查找区域”，然后选择“下一步”

![](/assets/dns_conf15.png)**步骤5：**输入“网络ID”，然后选择“下一步”

![](/assets/dns_conf16.png)**步骤6：**文件名保持默认，然后选择“下一步”

![](/assets/dns_conf17.png)**步骤7：**保持默认“不允许动态更新”，然后选择“下一步”

![](/assets/dns_conf18.png)**步骤8：**完成“反向查找区域的创建”

### ![](/assets/dns_conf19.png)4.4 添加反向解析记录

添加反向解析记录：192.168.10.200可以解析成www.itcast.itcast

**步骤1：**鼠标右键单击前面创建的反向查找区域，然后选择“新建指针（PTR）”

![](/assets/dns_reverse1.png)

**步骤2：**添加反向解析记录

![](/assets/dns_reverse2.png)**步骤3：**查看反向解析记录

## ![](/assets/dns_reverse3.png)5. 



