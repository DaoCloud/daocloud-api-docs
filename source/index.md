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

打开个人设置页面可以看到用于调用接口的 access token

# 代码构建 Build Flow

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
status | 项目当前构建状态 "Pending, Started, Success, Failure, Error, Cancelled, Timeout"
src_origin_url | git 托管项目
package_id | build 成功后的镜像 id
created_at | 项目创建时间， iso8601 utc


# 应用程序 App

## App 列表

```shell
curl "https://openapi.daocloud.io/v1/apps"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/apps',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 返回结果如下:

```json
{
  "app": [
    {
      "package": {
        "id": "1b6b9e72-f127-41fe-8290-cc3df8dfdf19",
        "image": "daocloud.io/daocloud/daocloud"
      },
      "state": "RUNNING",
      "created_at": "2015-12-19T07:55:10+00:00",
      "last_operated_at": "2015-12-14T08:46:11+00:00",
      "release_name": "v1.0.0",
      "app_runtime": {
        "name": "S0",
        "display_name": "自有集群"
      },
      "id": "a5fad5a6-b967-4436-bcfd-1978110ea8cb",
      "name": "open-api",
      "enable_auto_redeploy": true
    }
  ]
}
```

获取用户的 app 列表.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/apps`

### 返回结果

字段 | 描述
--------- | -----------
id | App id
name | App 名称
state | App 状态
release_name | App 镜像版本
package | Package 信息
app_runtime | App 运行时信息
enable_auto_redeploy | 是否启用自动发布
created_at | 创建时间 iso8601 utc
last_operated_at | 最后操作时间 iso8601 utc


## 获取单个 App

```shell
curl "https://openapi.daocloud.io/v1/apps/<app_id>"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/apps/{app_id}',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "last_operated_at": "2015-12-14T10:01:39+00:00",
  "name": "open-api",
  "release_name": "master-20ec560",
  "app_runtime": {
    "name": "S0",
    "display_name": "自有集群"
  },
  "state": "RUNNING",
  "package": {
    "id": "ab6f0727-ba60-4166-8bc6-7012e61303e8",
    "image": "daocloud.io/daocloud/open-api"
  },
  "created_at": "2015-12-01T10:45:29+00:00",
  "config": {
    "instances": 1,
    "expose_port": 8881,
    "command": null
  },
  "id": "d535ca76-b388-4356-8ad8-990e488fc1eb",
  "enable_auto_redeploy": true
}
```

获取用户的 app 列表.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/apps/{app_id}`

### 返回结果

字段 | 描述
--------- | -----------
id | App id
name | App 名称
state | App 状态
release_name | App 镜像版本
package | Package 信息
app_runtime | App 运行时信息
config.instances | 实例数
config.expose_port | Container内部端口
config.command | 启动命令
enable_auto_redeploy | 是否启用自动发布
created_at | 创建时间 iso8601 utc
last_operated_at | 最后操作时间 iso8601 utc

## 启动 App

```shell
curl -X POST "https://openapi.daocloud.io/v1/apps/<app_id>/actions/start"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/apps/{app_id}/actions/start',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

启动 App.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/apps/{app_id}/actions/start`

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id

## 停止 App

```shell
curl -X POST "https://openapi.daocloud.io/v1/apps/<app_id>/actions/stop"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/apps/{app_id}/actions/stop',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

启动 App.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/apps/{app_id}/actions/stop`

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id

## 重启 App

```shell
curl -X POST "https://openapi.daocloud.io/v1/apps/<app_id>/actions/restart"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/apps/{app_id}/actions/restart',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

启动 App.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/apps/{app_id}/actions/restart`

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id

## 重新发布 App

```shell
curl -X POST "https://openapi.daocloud.io/v1/apps/<app_id>/actions/redeploy"
  -H "Authorization: token <my token>" -H "Content-Type: application/json" -d '{"release_name": "v1.0.0"}'
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/apps/{app_id}/actions/redeploy',
  data={"release_name": "v1.0.0"},
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

发布 App 到指定版本.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/apps/{app_id}/actions/redeploy`

### 参数

字段 | 描述
--------- | -----------
release_name | 要发布的版本名称

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id


## 获取事件 Action

```shell
curl "https://openapi.daocloud.io/v1/apps/<app_id>/actions/<action_id>"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/apps/{app_id}/actions/{action_id}',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "end_date": "2015-12-14T10:16:23+00:00",
  "action_name": "start_app",
  "state": "SUCCESS",
  "app_id": "d535ca76-b388-4356-8ad8-990e488fc1eb",
  "start_date": "2015-12-14T10:16:21+00:00",
  "error_info": {
    "message": null
  },
  "id": "8e3e490e-54ae-4214-924c-b7dcf3c33454",
  "time_cost_seconds": 2
}
```

获取事件信息.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/apps/{app_id}/actions/{action_id}`

### 返回结果

字段 | 描述
--------- | -----------
id | Action id
action_name | Action 名称
state | App 状态, SUCCESS -> 成功, FAILED -> 失败, IN_PROCESS -> 正在执行
app_id | App id
start_date | 事件开始时间 iso8601 utc
end_date | 事件开始时间 iso8601 utc
error_info | 错误信息
time_cost_seconds | 耗费时间(秒)
