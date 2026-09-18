#!/usr/bin/env python3
"""Generate a complete English OpenAPI documentation tree and navigation."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from deep_translator import GoogleTranslator, MyMemoryTranslator
from deep_translator.exceptions import TranslationNotFound


ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCE_OPENAPI_DIR = ROOT_DIR / "docs" / "openapi"
TARGET_OPENAPI_DIR = ROOT_DIR / "docs" / "en" / "openapi"
SOURCE_NAV_FILE = ROOT_DIR / "openapi-nav.yml"
TARGET_NAV_FILE = ROOT_DIR / "openapi-nav.en.yml"
TRANSLATION_CACHE_FILE = ROOT_DIR / ".translation-cache-openapi-en.json"


MANUAL_TRANSLATIONS = {
    "OpenAPI 文档": "OpenAPI Documentation",
    "OpenAPI 文档索引": "OpenAPI Documentation Index",
    "工作台": "Workbench",
    "应用工作台 OpenAPI": "Workbench OpenAPI",
    "容器": "Containers",
    "容器管理 OpenAPI": "Container Management OpenAPI",
    "多云编排 OpenAPI": "Multi-Cloud Orchestration OpenAPI",
    "镜像仓库 OpenAPI": "Image Registry OpenAPI",
    "网络 OpenAPI": "Networking OpenAPI",
    "虚拟机 OpenAPI": "Virtual Machine OpenAPI",
    "可观测性 OpenAPI": "Observability OpenAPI",
    "微服务引擎 OpenAPI": "Microservice Engine OpenAPI",
    "服务网格 OpenAPI": "Service Mesh OpenAPI",
    "数据服务": "Data Services",
    "中间件 OpenAPI": "Middleware OpenAPI",
    "中间件 OpenAPI 之一": "Middleware OpenAPI I",
    "中间件 OpenAPI 之二": "Middleware OpenAPI II",
    "中间件 OpenAPI 文档索引": "Middleware OpenAPI Index",
    "Elasticsearch 搜索服务": "Elasticsearch Search Service",
    "Kafka 消息队列": "Kafka Message Queue",
    "RabbitMQ 消息队列": "RabbitMQ Message Queue",
    "RocketMQ 消息队列": "RocketMQ Message Queue",
    "MinIO 对象存储": "MinIO Object Storage",
    "MongoDB 数据库": "MongoDB Database",
    "MySQL 数据库": "MySQL Database",
    "PostgreSQL 数据库": "PostgreSQL Database",
    "Redis 数据库": "Redis Database",
    "云原生 AI": "Cloud-Native AI",
    "AI Lab OpenAPI": "AI Lab OpenAPI",
    "算力云 OpenAPI": "Compute Cloud OpenAPI",
    "边缘计算": "Edge Computing",
    "云边协同 OpenAPI": "Cloud-Edge Collaboration OpenAPI",
    "管理": "Management",
    "设备管理 OpenAPI": "Device Management OpenAPI",
    "全局管理 OpenAPI": "Global Management OpenAPI",
    "早期版本": "Earlier Versions",
    "Index": "Index",
    "访问密钥": "Access Key",
    "个人中心": "Personal Center",
}


CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
NON_TRANSLATABLE_KEYS = {
    "$ref",
    "name",
    "operationId",
    "example",
    "examples",
    "enum",
    "default",
    "pattern",
    "format",
    "type",
    "required",
}
TRANSLATABLE_KEYS = {
    "title",
    "summary",
    "description",
    "x-displayName",
}


INDEX_TEMPLATE = """---
hide:
  - toc
---

# OpenAPI Documentation Overview

This page lists the OpenAPI documentation for DCE 5.0 related modules so that you can call the APIs programmatically.
You need an **[Access Key](#access-key)** to call OpenAPI endpoints.

<div class="grid cards" markdown>

-   :material-microsoft-azure-devops:{ .lg .middle } __Workbench OpenAPI__

    ---

    - [v0.131.0](./amamba/v0.131.0.md), [v0.130.0](./amamba/v0.130.0.md), [v0.129.0](./amamba/v0.129.0.md), [v0.128.0](./amamba/v0.128.0.md)
    - [v0.127.0](./amamba/v0.127.0.md), [v0.126.0](./amamba/v0.126.0.md), [v0.125.0](./amamba/v0.125.0.md), [v0.124.1](./amamba/v0.124.1.md)
    - [v0.123.x](./amamba/v0.123.0.md), [v0.122.x](./amamba/v0.122.0.md), [v0.121.0](./amamba/v0.121.0.md), [v0.120.0](./amamba/v0.120.0.md)
    - [v0.119.0](./amamba/v0.119.0.md), [v0.118.x](./amamba/v0.118.0.md), [v0.117.x](./amamba/v0.117.0.md), [v0.116.0](./amamba/v0.116.0.md)

-   :octicons-container-16:{ .lg .middle } __Container Management OpenAPI__

    ---

    - [v0.45.0](./kpanda/v0.45.0.md), [v0.44.0](./kpanda/v0.44.0.md), [v0.43.x](./kpanda/v0.43.0.md), [v0.42.x](./kpanda/v0.42.0.md)
    - [v0.41.0](./kpanda/v0.41.0.md), [v0.40.x](./kpanda/v0.40.0.md), [v0.39.0](./kpanda/v0.39.0.md), [v0.38.0](./kpanda/v0.38.0.md)
    - [v0.37.0](./kpanda/v0.37.0.md), [v0.34.0](./kpanda/v0.34.0.md), [v0.33.x](./kpanda/v0.33.0.md), [v0.32.x](./kpanda/v0.32.0.md)
    - [v0.31.1](./kpanda/v0.31.1.md), [v0.30.x](./kpanda/v0.30.1.md), [v0.29.x](./kpanda/v0.29.0.md), [v0.28.x](./kpanda/v0.28.0.md)

-   :material-cloud-check:{ .lg .middle } __Multi-Cloud Orchestration OpenAPI__

    ---

    - [v0.23.0](./kairship/v0.23.0.md), [v0.22.0](./kairship/v0.22.0.md), [v0.21.x](./kairship/v0.21.0.md), [v0.20.x](./kairship/v0.20.0.md)
    - [v0.18.0](./kairship/v0.18.0.md), [v0.17.0](./kairship/v0.17.0.md), [v0.16.0](./kairship/v0.16.0.md), [v0.15.0](./kairship/v0.15.0.md)
    - [v0.14.0](./kairship/v0.14.0.md), [v0.13.x](./kairship/v0.13.0.md), [v0.12.0](./kairship/v0.12.0.md), [v0.11.x](./kairship/v0.11.0.md)
    - [v0.10.x](./kairship/v0.10.0.md), [v0.9.x](./kairship/v0.9.0.md), [v0.8.x](./kairship/v0.8.0.md)

-   :material-warehouse:{ .lg .middle } __Image Registry OpenAPI__

    ---

    - [v0.22.0](./kangaroo/v0.22.0.md), [v0.21.0](./kangaroo/v0.21.0.md), [v0.18.0](./kangaroo/v0.18.0.md), [v0.17.0](./kangaroo/v0.17.0.md)
    - [v0.15.0](./kangaroo/v0.15.0.md), [v0.14.0](./kangaroo/v0.14.0.md), [v0.13.x](./kangaroo/v0.13.0.md), [v0.12.x](./kangaroo/v0.12.0.md)
    - [v0.11.0](./kangaroo/v0.11.0.md), [v0.10.x](./kangaroo/v0.10.0.md), [v0.9.1](./kangaroo/v0.9.1.md), [v0.8.0](./kangaroo/v0.8.0.md)

-   :material-dot-net:{ .lg .middle } __Networking OpenAPI__

    ---

    - [v0.16.x](./spidernet/v0.16.0.md), [v0.15.x](./spidernet/v0.15.0.md), [v0.14.x](./spidernet/v0.14.0.md), [v0.13.0](./spidernet/v0.13.0.md)
    - [v0.12.x](./spidernet/v0.12.0.md), [v0.10.x](./spidernet/v0.10.0.md), [v0.9.0](./spidernet/v0.9.0.md), [v0.8.x](./spidernet/v0.8.0.md)
    - [v0.7.0](./spidernet/v0.7.0.md), [v0.6.0](./spidernet/v0.6.0.md), [v0.5.0](./spidernet/v0.5.0.md)

-   :material-train-car-container:{ .lg .middle } __Virtual Machine OpenAPI__

    ---

    - [v0.19.0](./virtnest/v0.19.0.md), [v0.18.x](./virtnest/v0.18.0.md), [v0.17.0](./virtnest/v0.17.0.md), [v0.16.0](./virtnest/v0.16.0.md)
    - [v0.15.0](./virtnest/v0.15.0.md), [v0.13.0](./virtnest/v0.13.0.md), [v0.12.0](./virtnest/v0.12.0.md), [v0.9.x](./virtnest/v0.8.0.md)
    - [v0.8.x](./virtnest/v0.8.0.md), [v0.7.x](./virtnest/v0.7.0.md), [v0.6.0](./virtnest/v0.6.0.md)

-   :material-monitor-dashboard:{ .lg .middle } __Observability OpenAPI__

    ---

    - [v0.41.0](./insight/v0.41.0.md), [v0.40.x](./insight/v0.40.0.md), [v0.39.x](./insight/v0.39.0.md), [v0.38.x](./insight/v0.38.0.md)
    - [v0.37.x](./insight/v0.37.0.md), [v0.36.x](./insight/v0.36.0.md), [v0.35.x](./insight/v0.35.0.md), [v0.34.x](./insight/v0.34.0.md)
    - [v0.33.1](./insight/v0.33.1.md), [v0.31.3](./insight/v0.31.3.md), [v0.28.0](./insight/v0.28.0.md), [v0.27.x](./insight/v0.27.0.md)
    - [v0.26.0](./insight/v0.26.0.md), [v0.25.2](./insight/v0.25.2.md), [v0.24.0](./insight/v0.24.0.md), [v0.22.x](./insight/v0.22.0.md)

-   :material-engine:{ .lg .middle } __Microservice Engine OpenAPI__

    ---

    - [v0.54.0](./skoala/v0.54.0.md), [v0.53.0](./skoala/v0.53.0.md), [v0.51.0](./skoala/v0.51.0.md), [v0.50.x](./skoala/v0.50.0.md)
    - [v0.49.0](./skoala/v0.49.0.md), [v0.48.x](./skoala/v0.48.0.md), [v0.47.1](./skoala/v0.47.1.md), [v0.43.x](./skoala/v0.43.0.md)
    - [v0.42.x](./skoala/v0.42.0.md), [v0.41.x](./skoala/v0.41.1.md), [v0.40.1](./skoala/v0.40.1.md), [v0.39.4](./skoala/v0.39.4.md)
    - [v0.38.x](./skoala/v0.38.1.md), [v0.37.x](./skoala/v0.37.0.md), [v0.36.x](./skoala/v0.36.0.md), [v0.35.x](./skoala/v0.35.0.md)

-   :material-table-refresh:{ .lg .middle } __Service Mesh OpenAPI__

    ---

    - [v0.116.0](./mspider/v0.116.0.md), [v0.109.0](./mspider/v0.109.0.md)
    - [v0.108.3](./mspider/v0.108.3.md), [v0.106.2](./mspider/v0.106.2.md)
    - [v0.105.1](./mspider/v0.105.1.md)

-   :fontawesome-brands-edge:{ .lg .middle } __Cloud-Edge Collaboration OpenAPI__

    ---

    - [v0.21.0](./kant/v0.21.0.md), [v0.20.0](./kant/v0.20.0.md), [v0.17.0](./kant/v0.17.0.md), [v0.16.1](./kant/v0.16.1.md)
    - [v0.15.0](./kant/v0.15.0.md), [v0.14.0](./kant/v0.14.0.md), [v0.13.0](./kant/v0.13.0.md), [v0.12.0](./kant/v0.12.0.md)
    - [v0.11.0](./kant/v0.11.0.md), [v0.10.0](./kant/v0.10.0.md), [v0.9.0](./kant/v0.9.0.md), [v0.8.0](./kant/v0.8.0.md)

-   :octicons-devices-16:{ .lg .middle } __Device Management OpenAPI__

    ---

    - [v0.5.0](./topohub/v0.5.0.md), [v0.4.1](./topohub/v0.4.1.md), [v0.3.0](./topohub/v0.3.0.md), [v0.2.0](./topohub/v0.2.0.md)

-   :robot:{ .lg .middle } __AI Lab OpenAPI__

    ---

    - [v0.111.2](./baize/v0.111.2.md), [v0.107.4](./baize/v0.107.4.md)

-   :computer:{ .lg .middle } __Compute Cloud OpenAPI__

    ---

    - [v0.14.0](./zestu/v0.14.0.md), [v0.13.0](./zestu/v0.13.0.md), [v0.12.0](./zestu/v0.12.0.md), [v0.11.0](./zestu/v0.11.0.md)
    - [v0.10.x](./zestu/v0.10.0.md), [v0.9.0](./zestu/v0.9.0.md), [v0.8.0](./zestu/v0.8.0.md), [v0.7.0](./zestu/v0.7.0.md)

-   :fontawesome-solid-user-group:{ .lg .middle } __Global Management OpenAPI__

    ---

    - [v0.45.x](./ghippo/v0.45.0.md), [v0.43.0](./ghippo/v0.43.0.md), [v0.42.2](./ghippo/v0.42.2.md), [v0.41.3](./ghippo/v0.41.3.md)
    - [v0.40.x](./ghippo/v0.40.0.md), [v0.37.0](./ghippo/v0.37.0.md), [v0.36.0](./ghippo/v0.36.0.md), [v0.35.x](./ghippo/v0.35.0.md)
    - [v0.34.0](./ghippo/v0.34.0.md), [v0.33.0](./ghippo/v0.33.0.md), [v0.31.0](./ghippo/v0.31.0.md), [v0.30.0](./ghippo/v0.30.0.md)
    - [v0.28.0](./ghippo/v0.28.0.md), [v0.27.0](./ghippo/v0.27.0.md), [v0.26.0](./ghippo/v0.26.0.md), [v0.25.x](./ghippo/v0.25.0.md)

-   :material-middleware:{ .lg .middle } __Middleware OpenAPI I__

    ---

    [:octicons-arrow-right-24: Middleware OpenAPI Index](./midware.md)

    - Search service: [Elasticsearch](./mcamel/elasticsearch/elasticsearch-v0.24.0.md)
    - Message queue: [Kafka](./mcamel/kafka/kafka-v0.22.0.md),
      [RabbitMQ](./mcamel/rabbitmq/rabbitmq-v0.27.0.md),
      [RocketMQ](./mcamel/rocketmq/rocketmq-v0.13.0.md)

-   :material-middleware:{ .lg .middle } __Middleware OpenAPI II__

    ---

    [:octicons-arrow-right-24: Middleware OpenAPI Index](./midware.md)

    - Object storage: [MinIO](./mcamel/minio/minio-v0.21.0.md)
    - Database: [MongoDB](./mcamel/mongodb/mongodb-v0.16.0.md),
      [MySQL](./mcamel/mysql/mysql-v0.26.0.md),
      [PostgreSQL](./mcamel/postgresql/postgresql-v0.18.0.md),
      [Redis](./mcamel/redis/redis-v0.26.0.md)

</div>

## Access Key

An Access Key can be used to access OpenAPI and continuous delivery. In DCE 5.0, you can get a key from the **Personal Center** and then use it to access the API.

### Get a Key

Log in to DCE 5.0. In the drop-down menu at the upper-right corner, open **Personal Center** and manage your account access keys on the **Access Key** tab.

![ak list](./images/platform02.png)

![created a key](./images/platform03.png)

!!! info

    Access key information is shown only once. If you lose it, create a new access key.

### Use the Key to Access the API

When you call a DCE 5.0 OpenAPI, add the request header `Authorization:Bearer ${token}` to identify the caller, where `${token}` is the key obtained in the previous step.

**Request example**

```bash
curl -X GET -H 'Authorization:Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkRKVjlBTHRBLXZ4MmtQUC1TQnVGS0dCSWc1cnBfdkxiQVVqM2U3RVByWnMiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE2NjE0MTU5NjksImlhdCI6MTY2MDgxMTE2OSwiaXNzIjoiZ2hpcHBvLmlvIiwic3ViIjoiZjdjOGIxZjUtMTc2MS00NjYwLTg2MWQtOWI3MmI0MzJmNGViIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWRtaW4iLCJncm91cHMiOltdfQ.RsUcrAYkQQ7C6BxMOrdD3qbBRUt0VVxynIGeq4wyIgye6R8Ma4cjxG5CbU1WyiHKpvIKJDJbeFQHro2euQyVde3ygA672ozkwLTnx3Tu-_mB1BubvWCBsDdUjIhCQfT39rk6EQozMjb-1X1sbLwzkfzKMls-oxkjagI_RFrYlTVPwT3Oaw-qOyulRSw7Dxd7jb0vINPq84vmlQIsI3UuTZSNO5BCgHpubcWwBss-Aon_DmYA-Et_-QtmPBA3k8E2hzDSzc7eqK0I68P25r9rwQ3DeKwD1dbRyndqWORRnz8TLEXSiCFXdZT2oiMrcJtO188Ph4eLGut1-4PzKhwgrQ' https://demo-dev.daocloud.io/apis/ghippo.io/v1alpha1/users?page=1&pageSize=10 -k
```

**Response**

```json
{
    "items": [
        {
            "id": "a7cfd010-ebbe-4601-987f-d098d9ef766e",
            "name": "a",
            "email": "",
            "description": "",
            "firstname": "",
            "lastname": "",
            "source": "locale",
            "enabled": true,
            "createdAt": "1660632794800",
            "updatedAt": "0",
            "lastLoginAt": ""
        }
    ],
    "pagination": {
        "page": 1,
        "pageSize": 10,
        "total": 1
    }
}
```
"""


MIDWARE_TEMPLATE = """---
hide:
  - toc
---

# Middleware OpenAPI Documentation

This page lists all middleware OpenAPI documents so that you can call the APIs programmatically.

<div class="grid cards" markdown>

-   :simple-elasticsearch:{ .lg .middle } __Elasticsearch OpenAPI__

    ---

    - [v0.27.0](mcamel/elasticsearch/elasticsearch-v0.27.0.md), [v0.26.x](mcamel/elasticsearch/elasticsearch-v0.26.0.md), [v0.25.x](mcamel/elasticsearch/elasticsearch-v0.25.0.md), [v0.24.x](mcamel/elasticsearch/elasticsearch-v0.24.0.md)
    - [v0.23.0](mcamel/elasticsearch/elasticsearch-v0.23.0.md), [v0.21.x](mcamel/elasticsearch/elasticsearch-v0.21.0.md), [v0.20.0](mcamel/elasticsearch/elasticsearch-v0.20.0.md), [v0.18.0](mcamel/elasticsearch/elasticsearch-v0.18.0.md)
    - [v0.17.0](mcamel/elasticsearch/elasticsearch-v0.17.0.md), [v0.16.0](mcamel/elasticsearch/elasticsearch-v0.16.0.md), [v0.15.0](mcamel/elasticsearch/elasticsearch-v0.15.0.md), [v0.14.0](mcamel/elasticsearch/elasticsearch-v0.14.0.md)
    - [v0.13.0](mcamel/elasticsearch/elasticsearch-v0.13.0.md), [v0.12.0](mcamel/elasticsearch/elasticsearch-v0.12.0.md), [v0.11.0](mcamel/elasticsearch/elasticsearch-v0.11.0.md), [v0.10.x](mcamel/elasticsearch/elasticsearch-v0.10.0.md)

-   :simple-apachekafka:{ .lg .middle } __Kafka OpenAPI__

    ---

    - [v0.29.0](mcamel/kafka/kafka-v0.29.0.md), [v0.28.x](mcamel/kafka/kafka-v0.28.0.md), [v0.27.0](mcamel/kafka/kafka-v0.27.0.md), [v0.26.0](mcamel/kafka/kafka-v0.26.0.md)
    - [v0.25.0](mcamel/kafka/kafka-v0.25.0.md), [v0.24.x](mcamel/kafka/kafka-v0.24.0.md), [v0.22.0](mcamel/kafka/kafka-v0.22.0.md), [v0.21.0](mcamel/kafka/kafka-v0.21.0.md)
    - [v0.19.0](mcamel/kafka/kafka-v0.19.0.md), [v0.18.0](mcamel/kafka/kafka-v0.18.0.md), [v0.17.0](mcamel/kafka/kafka-v0.17.0.md), [v0.16.0](mcamel/kafka/kafka-v0.16.0.md)
    - [v0.15.0](mcamel/kafka/kafka-v0.15.0.md), [v0.14.0](mcamel/kafka/kafka-v0.14.0.md), [v0.13.0](mcamel/kafka/kafka-v0.13.0.md), [v0.12.0](mcamel/kafka/kafka-v0.12.0.md)

-   :material-database:{ .lg .middle } __MinIO OpenAPI__

    ---

    - [v0.24.0](mcamel/minio/minio-v0.24.0.md), [v0.23.x](mcamel/minio/minio-v0.23.0.md), [v0.22.0](mcamel/minio/minio-v0.22.0.md), [v0.21.0](mcamel/minio/minio-v0.21.0.md)
    - [v0.20.0](mcamel/minio/minio-v0.20.0.md), [v0.19.0](mcamel/minio/minio-v0.19.0.md), [v0.18.x](mcamel/minio/minio-v0.18.0.md), [v0.16.0](mcamel/minio/minio-v0.16.0.md)
    - [v0.15.0](mcamel/minio/minio-v0.15.0.md), [v0.13.0](mcamel/minio/minio-v0.13.0.md), [v0.12.0](mcamel/minio/minio-v0.12.0.md), [v0.11.0](mcamel/minio/minio-v0.11.0.md)
    - [v0.10.0](mcamel/minio/minio-v0.10.0.md), [v0.9.0](mcamel/minio/minio-v0.9.0.md), [v0.8.x](mcamel/minio/minio-v0.8.0.md), [v0.7.x](mcamel/minio/minio-v0.7.0.md)

-   :simple-mongodb:{ .lg .middle } __MongoDB OpenAPI__

    ---

    - [v0.19.0](mcamel/mongodb/mongodb-v0.19.0.md), [v0.18.0](mcamel/mongodb/mongodb-v0.18.0.md), [v0.17.0](mcamel/mongodb/mongodb-v0.17.0.md), [v0.16.x](mcamel/mongodb/mongodb-v0.16.0.md)
    - [v0.15.0](mcamel/mongodb/mongodb-v0.15.0.md), [v0.14.0](mcamel/mongodb/mongodb-v0.14.0.md), [v0.13.x](mcamel/mongodb/mongodb-v0.13.0.md), [v0.12.0](mcamel/mongodb/mongodb-v0.12.0.md)
    - [v0.11.0](mcamel/mongodb/mongodb-v0.11.0.md), [v0.9.0](mcamel/mongodb/mongodb-v0.9.0.md), [v0.8.0](mcamel/mongodb/mongodb-v0.8.0.md), [v0.7.0](mcamel/mongodb/mongodb-v0.7.0.md)
    - [v0.6.0](mcamel/mongodb/mongodb-v0.6.0.md), [v0.5.0](mcamel/mongodb/mongodb-v0.5.0.md), [v0.4.0](mcamel/mongodb/mongodb-v0.4.0.md), [v0.3.x](mcamel/mongodb/mongodb-v0.3.0.md)

-   :simple-mysql:{ .lg .middle } __MySQL OpenAPI__

    ---

    - [v0.29.0](mcamel/mysql/mysql-v0.29.0.md), [v0.28.x](mcamel/mysql/mysql-v0.28.0.md), [v0.27.x](mcamel/mysql/mysql-v0.27.0.md), [v0.26.x](mcamel/mysql/mysql-v0.26.0.md)
    - [v0.25.0](mcamel/mysql/mysql-v0.25.0.md), [v0.24.0](mcamel/mysql/mysql-v0.24.0.md), [v0.23.0](mcamel/mysql/mysql-v0.23.0.md), [v0.22.0](mcamel/mysql/mysql-v0.22.0.md)
    - [v0.21.0](mcamel/mysql/mysql-v0.21.0.md), [v0.19.0](mcamel/mysql/mysql-v0.19.0.md), [v0.18.0](mcamel/mysql/mysql-v0.18.0.md), [v0.17.1](mcamel/mysql/mysql-v0.17.1.md)
    - [v0.16.0](mcamel/mysql/mysql-v0.16.0.md), [v0.15.0](mcamel/mysql/mysql-v0.15.0.md), [v0.14.0](mcamel/mysql/mysql-v0.14.0.md), [v0.13.0](mcamel/mysql/mysql-v0.13.0.md)

-   :simple-postgresql:{ .lg .middle } __PostgreSQL OpenAPI__

    ---

    - [v0.21.0](mcamel/postgresql/postgresql-v0.21.0.md), [v0.20.x](mcamel/postgresql/postgresql-v0.20.0.md), [v0.19.0](mcamel/postgresql/postgresql-v0.19.0.md), [v0.18.x](mcamel/postgresql/postgresql-v0.18.4.md)
    - [v0.17.0](mcamel/postgresql/postgresql-v0.17.0.md), [v0.16.0](mcamel/postgresql/postgresql-v0.16.0.md), [v0.15.0](mcamel/postgresql/postgresql-v0.15.0.md), [v0.14.0](mcamel/postgresql/postgresql-v0.14.0.md)
    - [v0.13.0](mcamel/postgresql/postgresql-v0.13.0.md), [v0.10.0](mcamel/postgresql/postgresql-v0.10.0.md), [v0.9.0](mcamel/postgresql/postgresql-v0.9.0.md), [v0.8.0](mcamel/postgresql/postgresql-v0.8.0.md)
    - [v0.7.0](mcamel/postgresql/postgresql-v0.7.0.md), [v0.6.0](mcamel/postgresql/postgresql-v0.6.0.md), [v0.5.x](mcamel/postgresql/postgresql-v0.5.1.md), [v0.4.0](mcamel/postgresql/postgresql-v0.4.0.md)

-   :simple-rabbitmq:{ .lg .middle } __RabbitMQ OpenAPI__

    ---

    - [v0.31.0](mcamel/rabbitmq/rabbitmq-v0.31.0.md), [v0.30.0](mcamel/rabbitmq/rabbitmq-v0.30.0.md), [v0.29.0](mcamel/rabbitmq/rabbitmq-v0.29.0.md), [v0.28.0](mcamel/rabbitmq/rabbitmq-v0.28.0.md)
    - [v0.27.x](mcamel/rabbitmq/rabbitmq-v0.27.0.md), [v0.26.0](mcamel/rabbitmq/rabbitmq-v0.26.0.md), [v0.25.0](mcamel/rabbitmq/rabbitmq-v0.25.0.md), [v0.24.0](mcamel/rabbitmq/rabbitmq-v0.24.0.md)
    - [v0.23.0](mcamel/rabbitmq/rabbitmq-v0.23.0.md), [v0.22.0](mcamel/rabbitmq/rabbitmq-v0.22.0.md), [v0.21.0](mcamel/rabbitmq/rabbitmq-v0.21.0.md), [v0.20.0](mcamel/rabbitmq/rabbitmq-v0.20.0.md)
    - [v0.18.0](mcamel/rabbitmq/rabbitmq-v0.18.0.md), [v0.17.0](mcamel/rabbitmq/rabbitmq-v0.17.0.md), [v0.16.0](mcamel/rabbitmq/rabbitmq-v0.16.0.md), [v0.15.0](mcamel/rabbitmq/rabbitmq-v0.15.0.md)

-   :simple-redis:{ .lg .middle } __Redis OpenAPI__

    ---

    - [v0.30.0](mcamel/redis/redis-v0.30.0.md), [v0.29.x](mcamel/redis/redis-v0.29.0.md), [v0.28.0](mcamel/redis/redis-v0.28.0.md), [v0.27.x](mcamel/redis/redis-v0.27.2.md)
    - [v0.26.0](mcamel/redis/redis-v0.26.0.md), [v0.25.0](mcamel/redis/redis-v0.25.0.md), [v0.23.0](mcamel/redis/redis-v0.23.0.md), [v0.22.0](mcamel/redis/redis-v0.22.0.md)
    - [v0.21.0](mcamel/redis/redis-v0.21.0.md), [v0.19.0](mcamel/redis/redis-v0.19.0.md), [v0.18.0](mcamel/redis/redis-v0.18.0.md), [v0.17.0](mcamel/redis/redis-v0.17.0.md)
    - [v0.16.0](mcamel/redis/redis-v0.16.0.md), [v0.15.0](mcamel/redis/redis-v0.15.0.md), [v0.14.0](mcamel/redis/redis-v0.14.0.md), [v0.13.0](mcamel/redis/redis-v0.13.0.md)

-   :simple-apacherocketmq:{ .lg .middle } __RocketMQ OpenAPI__

    ---

    - [v0.18.0](mcamel/rocketmq/rocketmq-v0.18.0.md), [v0.17.0](mcamel/rocketmq/rocketmq-v0.17.0.md), [v0.16.0](mcamel/rocketmq/rocketmq-v0.16.0.md), [v0.15.x](mcamel/rocketmq/rocketmq-v0.15.2.md)
    - [v0.13.0](mcamel/rocketmq/rocketmq-v0.13.0.md), [v0.12.0](mcamel/rocketmq/rocketmq-v0.12.0.md), [v0.11.0](mcamel/rocketmq/rocketmq-v0.11.0.md), [v0.10.0](mcamel/rocketmq/rocketmq-v0.10.0.md)
    - [v0.8.0](mcamel/rocketmq/rocketmq-v0.8.0.md), [v0.7.0](mcamel/rocketmq/rocketmq-v0.7.0.md), [v0.5.0](mcamel/rocketmq/rocketmq-v0.5.0.md), [v0.4.0](mcamel/rocketmq/rocketmq-v0.4.0.md)

</div>

!!! info

    More middleware OpenAPI documents are being prepared.

![what is midware](https://docs.daocloud.io/daocloud-docs-images/docs/openapi/images/middleware02.jpeg)
"""


API_DOC_FLOW_TEMPLATE = """---
hide:
  - toc
---

# OpenAPI Documentation Generation Flow

This page uses Ghippo as an example to explain how OpenAPI documentation is produced.
The main idea is to generate a Swagger JSON file and then automatically submit a PR to the documentation repository.

1. Add the following target to `Makefile`:

    ```go title="Makefile"
    .PHONY += doc.openapi
    doc.openapi:
        $(eval swagger_path ?= swagger)
        @bash hack/gen-openapi-json.sh ghippo $(GHIPPO_VERSION) $(swagger_path)
    ```

1. Write the script that generates the Swagger JSON file.

1. Write the script that opens a PR against the documentation repository.

1. Update the GitLab CI configuration so that the OpenAPI documentation is published automatically for tagged releases.
"""


@dataclass
class TranslationState:
    """Keep a reusable translator and a persistent translation cache."""

    translator: GoogleTranslator
    fallback_translator: MyMemoryTranslator
    cache: dict[str, str]


def load_translation_cache() -> dict[str, str]:
    """Load the persistent translation cache from disk if it exists."""
    if TRANSLATION_CACHE_FILE.exists():
        return json.loads(TRANSLATION_CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_translation_cache(cache: dict[str, str]) -> None:
    """Persist the translation cache to disk in a stable JSON format."""
    TRANSLATION_CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def contains_chinese(text: str) -> bool:
    """Return whether the input string contains Chinese characters."""
    return bool(CHINESE_PATTERN.search(text))


def should_translate_string(key: str | None, value: str) -> bool:
    """Return whether a string value should be translated."""
    if not value or not contains_chinese(value):
        return False
    if key in NON_TRANSLATABLE_KEYS:
        return False
    if key in TRANSLATABLE_KEYS:
        return True
    if len(value) <= 1:
        return False
    return True


def normalize_whitespace(text: str) -> str:
    """Normalize repeated whitespace before sending text to the translator."""
    return re.sub(r"\s+", " ", text).strip()


def split_for_translation(text: str) -> list[str]:
    """Split complex strings into smaller chunks that translators can handle better."""
    parts = re.split(r"(\s+|-->|->|=>|[:：;,，。()（）/\[\]])", text)
    return [part for part in parts if part]


def translate_with_fallback(text: str, state: TranslationState) -> str:
    """Translate text with primary and fallback translators."""
    try:
        return state.translator.translate(text)
    except TranslationNotFound:
        return state.fallback_translator.translate(text)
    except Exception:
        return state.fallback_translator.translate(text)


def translate_text(text: str, state: TranslationState) -> str:
    """Translate a Chinese string into English with manual overrides and cache."""
    if text in MANUAL_TRANSLATIONS:
        return MANUAL_TRANSLATIONS[text]

    normalized = normalize_whitespace(text)
    if normalized in MANUAL_TRANSLATIONS:
        return MANUAL_TRANSLATIONS[normalized]

    if normalized in state.cache:
        return state.cache[normalized]

    try:
        translated = translate_with_fallback(normalized, state)
    except Exception:
        segments = split_for_translation(normalized)
        translated_parts: list[str] = []
        for segment in segments:
            if contains_chinese(segment):
                try:
                    translated_parts.append(translate_with_fallback(segment, state))
                except Exception:
                    translated_parts.append(segment)
            else:
                translated_parts.append(segment)
        translated = "".join(translated_parts)
    state.cache[normalized] = translated
    return translated


def translate_json_node(node: Any, state: TranslationState, parent_key: str | None = None) -> Any:
    """Recursively translate OpenAPI JSON fields that are meant for human readers."""
    if isinstance(node, dict):
        translated: dict[str, Any] = {}
        for key, value in node.items():
            translated[key] = translate_json_node(value, state, key)
        return translated

    if isinstance(node, list):
        return [translate_json_node(item, state, parent_key) for item in node]

    if isinstance(node, str) and should_translate_string(parent_key, node):
        return translate_text(node, state)

    return node


def collect_translatable_strings(node: Any, bucket: set[str], parent_key: str | None = None) -> None:
    """Collect unique human-facing strings from a JSON node for batch translation."""
    if isinstance(node, dict):
        for key, value in node.items():
            collect_translatable_strings(value, bucket, key)
        return

    if isinstance(node, list):
        for item in node:
            collect_translatable_strings(item, bucket, parent_key)
        return

    if isinstance(node, str) and should_translate_string(parent_key, node):
        bucket.add(normalize_whitespace(node))


def chunked(items: list[str], size: int) -> list[list[str]]:
    """Split a list into fixed-size chunks."""
    return [items[index:index + size] for index in range(0, len(items), size)]


def prime_cache_for_strings(strings: set[str], state: TranslationState) -> None:
    """Translate unknown strings in batches before walking the JSON tree."""
    pending = [
        text for text in sorted(strings)
        if text not in MANUAL_TRANSLATIONS and text not in state.cache
    ]

    for batch in chunked(pending, 50):
        try:
            translated_batch = state.translator.translate_batch(batch)
            if translated_batch and len(translated_batch) == len(batch):
                for source, translated in zip(batch, translated_batch):
                    state.cache[source] = translated
                save_translation_cache(state.cache)
                continue
        except Exception:
            pass

        for item in batch:
            if item in state.cache:
                continue
            state.cache[item] = translate_text(item, state)
        save_translation_cache(state.cache)


def translate_nav_node(node: Any, state: TranslationState) -> Any:
    """Translate navigation labels and rewrite paths into the English tree."""
    if isinstance(node, dict):
        translated: dict[str, Any] = {}
        for key, value in node.items():
            new_key = translate_text(key, state) if contains_chinese(key) else key
            if isinstance(value, str) and value.startswith("openapi/"):
                translated[new_key] = f"en/{value}"
            else:
                translated[new_key] = translate_nav_node(value, state)
        return translated

    if isinstance(node, list):
        return [translate_nav_node(item, state) for item in node]

    return node


def copy_shared_images() -> None:
    """Copy shared OpenAPI image assets into the English documentation tree."""
    source_images_dir = SOURCE_OPENAPI_DIR / "images"
    target_images_dir = TARGET_OPENAPI_DIR / "images"
    if target_images_dir.exists():
        shutil.rmtree(target_images_dir)
    shutil.copytree(source_images_dir, target_images_dir)


def ensure_target_directory() -> None:
    """Recreate the English OpenAPI output directory from scratch."""
    TARGET_OPENAPI_DIR.mkdir(parents=True, exist_ok=True)


def generate_manual_pages() -> None:
    """Write the English landing pages that are authored manually."""
    (TARGET_OPENAPI_DIR / "index.md").write_text(INDEX_TEMPLATE, encoding="utf-8")
    (TARGET_OPENAPI_DIR / "midware.md").write_text(MIDWARE_TEMPLATE, encoding="utf-8")
    (TARGET_OPENAPI_DIR / "api-doc-flow.md").write_text(API_DOC_FLOW_TEMPLATE, encoding="utf-8")


def iter_source_files(products: set[str] | None = None) -> list[Path]:
    """Collect all OpenAPI source files that need to be mirrored into English."""
    def matches_product(path: Path) -> bool:
        if not products:
            return True
        relative_path = path.relative_to(SOURCE_OPENAPI_DIR)
        return relative_path.parts[0] in products

    return sorted(
        path for path in SOURCE_OPENAPI_DIR.rglob("*")
        if path.is_file() and "images" not in path.parts and matches_product(path)
    )


def filter_source_files_by_prefixes(source_files: list[Path], path_prefixes: list[str] | None) -> list[Path]:
    """Filter source files by relative path prefixes when targeted reruns are needed."""
    if not path_prefixes:
        return source_files

    normalized_prefixes = [prefix.strip("/") for prefix in path_prefixes]
    filtered: list[Path] = []
    for path in source_files:
        relative_path = path.relative_to(SOURCE_OPENAPI_DIR).as_posix()
        if any(relative_path.startswith(prefix) for prefix in normalized_prefixes):
            filtered.append(path)
    return filtered


def build_target_path(source_path: Path) -> Path:
    """Map a Chinese OpenAPI file path into its English counterpart."""
    relative_path = source_path.relative_to(SOURCE_OPENAPI_DIR)
    return TARGET_OPENAPI_DIR / relative_path


def resolve_swagger_json_name(source_markdown_path: Path) -> str:
    """Resolve the Swagger JSON file name for a Markdown wrapper with patch-version fallback."""
    direct_match = source_markdown_path.with_suffix(".json")
    if direct_match.exists():
        return direct_match.name

    version_match = re.match(r"^(v\d+\.\d+)\.\d+$", source_markdown_path.stem)
    if version_match:
        version_prefix = version_match.group(1)
        candidates = sorted(source_markdown_path.parent.glob(f"{version_prefix}.*.json"))
        if candidates:
            return candidates[-1].name

    return direct_match.name


def generate_english_openapi_files(
    state: TranslationState,
    products: set[str] | None = None,
    path_prefixes: list[str] | None = None,
) -> None:
    """Generate English Markdown wrappers and translated JSON files."""
    source_files = iter_source_files(products)
    source_files = filter_source_files_by_prefixes(source_files, path_prefixes)
    for source_path in source_files:
        if source_path.name in {"index.md", "midware.md", "api-doc-flow.md"}:
            continue

        target_path = build_target_path(source_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.suffix == ".md":
            if target_path.exists():
                continue
            json_name = resolve_swagger_json_name(source_path)
            target_path.write_text(f"# <swagger-ui src={json_name}>\n", encoding="utf-8")
            continue

        if source_path.suffix == ".json":
            if target_path.exists():
                continue
            source_data = json.loads(source_path.read_text(encoding="utf-8"))
            strings_to_translate: set[str] = set()
            collect_translatable_strings(source_data, strings_to_translate)
            prime_cache_for_strings(strings_to_translate, state)
            translated_data = translate_json_node(source_data, state)
            target_path.write_text(
                json.dumps(translated_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            save_translation_cache(state.cache)
            continue

        shutil.copy2(source_path, target_path)


def generate_english_nav(state: TranslationState) -> None:
    """Generate an English navigation file that points to the English tree."""
    source_nav = yaml.safe_load(SOURCE_NAV_FILE.read_text(encoding="utf-8"))
    translated_nav = translate_nav_node(source_nav, state)
    TARGET_NAV_FILE.write_text(
        yaml.safe_dump(translated_nav, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for incremental English OpenAPI generation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--products",
        nargs="+",
        help="Only generate the specified top-level OpenAPI product directories.",
    )
    parser.add_argument(
        "--skip-nav",
        action="store_true",
        help="Skip regenerating shared navigation and manual landing pages.",
    )
    parser.add_argument(
        "--path-prefixes",
        nargs="+",
        help="Only generate files whose relative path starts with one of these prefixes.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate the complete English OpenAPI site assets and navigation."""
    args = parse_args()
    products = set(args.products) if args.products else None
    state = TranslationState(
        translator=GoogleTranslator(source="zh-CN", target="en"),
        fallback_translator=MyMemoryTranslator(source="zh-CN", target="en-US"),
        cache=load_translation_cache(),
    )
    ensure_target_directory()
    if not args.skip_nav:
        copy_shared_images()
        generate_manual_pages()
        generate_english_nav(state)
    generate_english_openapi_files(state, products, args.path_prefixes)
    save_translation_cache(state.cache)


if __name__ == "__main__":
    main()
