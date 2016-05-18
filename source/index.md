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

1. 获取access token
打开个人设置页面可以看到用于调用接口的 access token

2. 使用 access token 访问api
access token可以让您直接访问API。
你可以在http的header中传入Token。`Authorization: token ACCESS-TOKEN`


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
      "src_provider": "github",
      "status": "Success",
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
src_provider | git 托管
status | 项目当前构建状态 "Pending|Started|Success|Failure|Error|Cancelled|Timeout"
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
src_provider | git 托管
status | 项目当前构建状态 "Pending, Started, Success, Failure, Error, Cancelled, Timeout"
src_origin_url | git 托管项目
package_id | build 成功后的镜像 id
created_at | 项目创建时间， iso8601 utc


## 手动构建项目

```shell
curl -X POST "https://openapi.daocloud.io/v1/build-flows/<build_flow_id>/builds" -H "Authorization: token <my token>" -H "Content-Type: application/json" -d '{"branch":"master"}'
```

```python
import requests
import json

result = requests.post('https://openapi.daocloud.io/v1/build-flows/{build_flow_id}/builds',
  headers={"Authorization": "token {token}", "Content-Type": "application/json"}, data=json.dumps({"branch":"master"}))

print(result.json())  
```

> 获取结果如下:


```json

{
    "status": "Pending", 
    "created_at": "2015-12-01T06:25:57+00:00", 
    "author": "DaoCloud", 
    "sha": "5785e42c7d6bfa754fc4765756e773ead6674as", 
    "tag": "master-init", 
    "branch": "master"
}

```

### HTTP 请求

`POST https://openapi.daocloud.io/v1/build-flows/<ID>/builds`

### 参数

字段 | 描述
--------- | -----------
branch | 需要构建的代码分支名

### 返回结果

字段 | 描述
--------- | -----------
branch | 分支名
status | 构建状态
tag  | 构建出来的镜像 tag 
sha| git 分支的 sha
created_at | 构建时间戳






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
        "id": "a849cdf2-c79e-4c29-83ca-50751cc388a5",
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
    "expose_ports": [
      {
        "publish_type": "not_publish",
        "protocol": "tcp",
        "external": "external",
        "container_port": 443
      },
      {
        "publish_type": "http",
        "protocol": "tcp",
        "external": "external",
        "container_port": 80
      }
    ],
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
config.expose_port(s) | Container内部端口，当只有一个内部端口，且可访问方式为http时，显示为expose_port
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


# 调用次数限制 Rate Limiting

不同的API会有不同的调用次数限制, 请检查返回 header 中的如下字段

header 字段 | 描述
--------- | -----------
X-RateLimit-Limit | 每小时的限制调用次数，超过后服务器会返回 403 错误
X-RateLimit-Remaining | 当前小时中还剩下的调用次数
X-RateLimit-Reset | 限制重置时间 unix time


# WebHook
 
WebHook 可以用于集成 DaoCloud 的项目管理，应用更新等。  
当 DaoCloud 平台有对应事件触发时，我们会给你发送一个 POST 请求。如果响应码不为`200`，我们会在一段时间间隔内重试`3`次 。 
如果你希望在本地调试 WebHook ，你可以使用 DaoCloud 应用的[云隧道](http://docs.daocloud.io/app-deploy-mgmt/tunnel) 功能 。

Webhook 设置页面：

`https://dashboard.daocloud.io/settings/profile`

## 事件
目前支持的 WebHook 事件有两种，镜像构建和持续集成。  

###镜像构建
这是镜像构建的事件，在返回结果中的`build_type` 为 `image_build` 。   
如果构建成功，`image`值将不为空。 此时你可以使用 `docker pull`来拉取该镜像。  
###持续集成
这是持续集成的事件，在返回结果中的`build_type` 为 `ci_build` 。

##Payloads:

``` json
{
	"repo":"daocloud/api",    
	"image":"daocloud.io/daocloud/api:master-init",    
	"build_flow_id":"8d7622ea-9323-4489-8c8e-fc4bed448961",     
	"name":"api",  
 	"build":
	 {  
	    "status":"Success",    
	   "duration_seconds":180,    
	   "author":"DaoCloud",  
	   "triggered_by":"tag",   
	   "sha":"a7c35d9dc7e93788ce81befbadeb0108de495e5e",    
	   "tag":"master-init",    
	   "branch":null,   
	   "pull_request":"",    
	   "message":"init build ",   
	   "started_at":"2015-01-01T08:20:00+00:00",   
	   "build_type":"image_build"}   
}
``` 

字段 | 描述
--------- | -----------
repo | 用户项目全名， 用户名/项目
image | 构建成功的镜像地址
build_flow_id | 项目 id
name| 项目名
build | 新触发的构建
status |构建的状态, Success,Failure,Error,Started
duration_seconds | 构建持续的时间
author | 触发构建的用户
triggered_by | 触发条件, 打tag还是手动构建
sha | 代码 sha
tag | 代码的tag
branch |代码的分支
pull_request |代码的pull request
message | 代码 commit 消息
started_at | 触发时间, iso8601 format
build_type | 构建类型, image_build,ci_build
