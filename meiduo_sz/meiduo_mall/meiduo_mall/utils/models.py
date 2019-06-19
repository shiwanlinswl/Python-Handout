from django.db import models


class BaseModel(models.Model):
    """创建模型基类:为模型补充字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类，用于继承，执行数据库迁移时不会创建BaseModel表

