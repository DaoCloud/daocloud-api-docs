---
title: DaoCloud 开放 API

language_tabs:
  - shell
  - python

toc_footers:
  - <a href='https://dashboard.daocloud.io'>控制台</a>

includes:
  - errors

search: true
---

# 介绍

欢迎使用 DaoCloud 开放 API

# 认证

```shell
curl -H "Authorization: token ACCESS-TOKEN" https://openapi.daocloud.io/v1/build-flows
```

1. 获取access token

打开个人设置页面可以看到用于调用接口的 access token

2. 使用 access token 访问api

access token可以让您直接访问API。

你可以在http的header中传入Token。`Authorization: token ACCESS-TOKEN`
	



# 代码构建

## 项目列表

```shell
curl "https://openapi.daocloud.io/v1/build-flows"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/build-flows',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 返回结果如下:

```json
{
  "build_flows": [
    {
      "id": "90d58d34-e1ca-4724-9d7c-9af7e3635f12",
      "name": "mongo_demo",
      "repo": "daocloud/mongo_demo",
      "src_language": "Go",
      "src_provider": "github",
      "status": "Success",
      "src_origin_url": "https://github.com/DaoCloud/golang-mongo-sample",
      "package_id": "e5033330-978f-4466-97d1-625c57a7943f",
      "created_at": "2015-12-01T06:25:57+00:00"
    }
  ]
}
```

获取用户的项目列表.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/build-flows`

### 返回结果

字段 | 描述
--------- | -----------
id | 项目 id
name | 项目名
repo | 项目 repo 名, 可以使用 docker pull 命令拉取
src_language | 编程语言
src_provider | git 托管
status | 项目当前构建状态 "Pending|Started|Success|Failure|Error|Cancelled|Timeout"
src_origin_url | git 托管项目
package_id | build 成功后的镜像 id
created_at | 项目创建时间， iso8601 utc


## 获取单个项目

```shell
curl "https://openapi.daocloud.io/v1/build-flows/<build_flow_id>"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/build-flows/{build_flow_id}',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "id": "90d58d34-e1ca-4724-9d7c-9af7e3635f12",
  "name": "mongo_demo",
  "repo": "daocloud/mongo_demo",
  "src_language": "Go",
  "src_provider": "github",
  "status": "Success",
  "src_origin_url": "https://github.com/DaoCloud/golang-mongo-sample",
  "package_id": "e5033330-978f-4466-97d1-625c57a7943f",
  "created_at": "2015-12-01T06:25:57+00:00"
}
```

获取用户的项目.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/build-flows/<ID>`

### 返回结果

字段 | 描述
--------- | -----------
id | 项目 id
name | 项目名
repo | 项目 repo 名, 可以使用 docker pull 命令拉取
src_language | 编程语言
src_provider | git 托管
status | 项目当前构建状态 "Pending|Started|Success|Failure|Error|Cancelled|Timeout"
src_origin_url | git 托管项目
package_id | build 成功后的镜像 id
created_at | 项目创建时间， iso8601 utc
