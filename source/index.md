---
title: DaoCloud Services 开放 API

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

欢迎使用 DaoCloud Services 开放 API

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
  headers={"Authorization": "token {token}"}, json={"branch":"master"})

print(result.json())  
```

> 获取结果如下:


```json

{
    "id": 345786,
    "status": "Pending", 
    "created_at": "2015-12-01T06:25:57+00:00", 
    "author": "DaoCloud", 
    "sha": "5785e42c7d6bfa754fc4765756e773ead6674as", 
    "tag": "master-init", 
    "ref": "master",
    "ref_is_tag": "false",
    "ref_is_branch": "true"
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
id     | 构建ID
ref | 代码的 ref, 如 master, v1.0
ref_is_branch | ref 代表 branch
ref_is_tag | ref 代表 tag
status | 构建状态
tag  | 构建出来的镜像 tag 
sha| git 分支的 sha
created_at | 构建时间戳


## 获取构建信息

```shell
curl "https://openapi.daocloud.io/v1/build-flows/<build_flow_id>/builds/<build_id>" -H "Authorization: token <my token>" -H "Content-Type: application/json"
```

```python
import requests
import json

result = requests.get('https://openapi.daocloud.io/v1/build-flows/{build_flow_id}/builds/{build_id}',
  headers={"Authorization": "token {token}"})

print(result.json())  
```

> 获取结果如下:


```json

{
    "id": 345786,
    "status": "Pending", 
    "created_at": "2015-12-01T06:25:57+00:00", 
    "author": "DaoCloud", 
    "sha": "5785e42c7d6bfa754fc4765756e773ead6674as", 
    "tag": "master-init", 
    "ref": "master",
    "ref_is_tag": "false",
    "ref_is_branch": "true"
}

```

### HTTP 请求

`GET https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/builds/<build_id>`

### 参数

字段 | 描述
--------- | -----------
build_flow_id | 项目ID
build_id   | 构建ID

### 返回结果

字段 | 描述
--------- | -----------
id     | 构建ID
ref | 代码的 ref, 如 master, v1.0
ref_is_branch | ref 代表 branch
ref_is_tag | ref 代表 tag
status | 构建状态
tag  | 构建出来的镜像 tag 
sha| git 分支的 sha
created_at | 构建时间戳


## 创建项目持续集成私有环境变量
```shell
curl -X POST "https://openapi.daocloud.io/v1/build-flows/<build_flow_id>/private-ci-envs" -H "Authorization: token <my token>" -H "Content-Type: application/json" -d '{"name":"passwxxord", "value": "thisispassword",  "visible": false}'
```

```python
import requests
import json

result = requests.post('https://openapi.daocloud.io/v1/build-flows/<build_flow_id>/private-ci-envs',
  headers={"Authorization": "token {token}"}, json={"name":"password", "value": "thisispassword",  "visible": false})

print(result.json())
```

> 获取结果如下:


```json
{
    "visible": false,
    "buildflow_id": "24b63b93-9bc0-4e29-8da0-930e3c3d46f0",
    "id": "e18a3e8b-1113-422d-83b3-f4c02e396181",
    "value": "",
    "name": "password"
}

```

### HTTP 请求

`POST https://openapi.daocloud.io/v1/build-flows/<build_flow_id>/private-ci-envs`

### 参数

字段 | 描述
--------- | -----------
name | 环境变量名
value | 环境变量值
visible | 是否网页可见

### 返回结果

字段 | 描述
--------- | -----------
name | 环境变量名
value | 环境变量值，网页不可见时值为空
visible | 是否网页可见
buildflow_id | 项目 ID
id | 环境变量 ID


## 列出所有持续集成私有环境变量
```shell
curl "https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/private-ci-envs" -H "Authorization: token <my token>" -H "Content-Type: application/json"
```

```python
import requests
import json

result = requests.get('https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/private-ci-envs',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:


```json
[
    {
        "visible": false,
        "buildflow_id": "24b63b93-9bc0-4e29-8da0-930e3c3d46f0",
        "id": "e18a3e8b-1113-422d-83b3-f4c02e396181",
        "value": "",
        "name": "password"
    }
]
```

### HTTP 请求

`GET https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/private-ci-envs`

### 返回结果

字段 | 描述
--------- | -----------
name | 环境变量名
value | 环境变量值，网页不可见时值为空
visible | 是否网页可见
buildflow_id | 项目 ID
id | 环境变量 ID

## 删除持续集成私有环境变量
```shell
curl -X DELETE "https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/private-ci-envs/<id>" -H "Authorization: token <my token>" -H "Content-Type: application/json"
```

```python
import requests
import json

result = requests.delete('https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/private-ci-envs/<id>',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:


HTTP 状态码 204

### HTTP 请求

`DELETE https://openapi.daocloud.io/v1/build-flows/<buildflow_id>/private-ci-envs/<id>`

### 返回结果

HTTP 状态码 204



## 构建机器 IP 列表

```shell
curl "https://openapi.daocloud.io/v1/ship/iplist" -H "Authorization: token <my token>" -H "Content-Type: application/json"
```

```python
import requests
import json

result = requests.get('https://openapi.daocloud.io/v1/ship/iplist',
  headers={"Authorization": "token {token}"})

print(result.json())  
```

> 获取结果如下:


```json

{
  "iplist": [
    //xxx.xxx.xxx.xxx
  ]
}

```

### HTTP 请求

`GET https://openapi.daocloud.io/v1/ship/iplist`

### 返回结果

字段 | 描述
--------- | -----------
iplist | 构建机器 IP 列表


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
enable\_auto\_redeploy | 是否启用自动发布
created_at | 创建时间 iso8601 utc
last\_operated\_at | 最后操作时间 iso8601 utc


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

获取用户单个 app.

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

## 在自由主机部署应用

```shell
curl -X "POST" "https://openapi.daocloud.io/v1/apps/hyper-runtime" \
     -H "Authorization: token {token}" \
     -d "{\"name\":\"2048\",\"package_id\":\"6f7a340c-b193-4a36-a765-4e660ddebd1c\",\"release_name\":\"latest\",\"instances\":1,\"env_vars\":{\"KEY\":\"VALUE\"},\"metadata\":{\"command\":\"\",\"container_volumes\":[],\"tags\":[{\"name\":\"ubuntu-1\"}],\"container_ports\":[{\"container_port\":22,\"host_port\":null,\"protocol\":\"tcp\",\"published\":true}],\"container_restart\":\"always\",\"container_privileged\":false}}"
```

```python
import requests
import json

result = response = requests.post(
    url="https://openapi.daocloud.io/v1/apps/hyper-runtime",
    headers={
        "Authorization": "token {token}",
    },
    data=json.dumps({
        "instances": 1,
        "metadata": {
            "tags": [
                {
                    "name": "ubuntu-1"
                }
            ],
            "container_ports": [
                {
                    "host_port": None,
                    "protocol": "tcp",
                    "published": True,
                    "container_port": 22
                }
            ],
            "container_privileged": False,
            "container_restart": "always",
            "command": "",
            "container_volumes": []
        },
        "release_name": "latest",
        "name": "2048",
        "package_id": "6f7a340c-b193-4a36-a765-4e660ddebd1c",
        "env_vars": {
        "KEY": "VALUE"
    }
)

print(result.json())  
```

> 获取结果如下:

```json
{
  "app_id": "900fcdbf-e2f4-462e-844a-acea1fac2076",
  "action_id": "35b14fe5-238f-41fd-9dfa-347382154198"
}
```

### HTTP 请求

`POST https://openapi.daocloud.io/v1/apps/hyper-runtime`

### 参数

字段 | 描述
--------- | -----------
instances | 启动的 App 数量
command | 容器启动命令 空为默认
tags | 容器部署的主机名
container_restart | 容器自动重启
expose_ports | 容器开放端口
release_name | 镜像 tag
name | App 名称
package_id | 镜像 ID

### 返回结果

字段 | 描述
--------- | -----------
app_id | 创建的 APP ID
action_id | 创建事件 ID

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
  json={"release_name": "v1.0.0"},
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

# 堆栈编排 Stack

## Stack 列表

```shell
curl "https://openapi.daocloud.io/v1/stacks"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/stacks',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 返回结果如下:

```json
{
  "stacks": [
    {
      "last_operated_at": "2017-06-14T08:06:30+00:00",
      "created_at": "2017-06-14T08:06:30+00:00",
      "stacks": [
        {
          "stack_id": "117ff1ab-d294-406c-9d4b-fa8688ae32e2"
        },
        {
          "stack_id": "dc8e835c-b612-4eae-b977-02c6cb38692e"
        }
      ],
      "id": "fd007fc5-3fdd-4350-9f30-6ea93b6f3b82",
      "name": "test"
    }
  ]
}
```

获取用户的 Stacks 列表.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/stacks`

### 返回结果

字段 | 描述
--------- | -----------
id | Stack id
name | Stack 名称
stack_id | Stack 中 stack 的 id
created_at | 创建时间 iso8601 utc
last\_operated\_at | 最后操作时间 iso8601 utc


## 获取单个 Stack

```shell
curl "https://openapi.daocloud.io/v1/stacks/<stack_id>"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/stacks/{stack_id}',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "last_operated_at": "2017-06-14T16:06:30",
  "created_at": "2017-06-14T16:06:30",
  "stacks": [
    {
      "stack_id": "117ff1ab-d294-406c-9d4b-fa8688ae32e2"
    },
    {
      "stack_id": "dc8e835c-b612-4eae-b977-02c6cb38692e"
    }
  ],
  "id": "fd007fc5-3fdd-4350-9f30-6ea93b6f3b82",
  "name": "asdadsaqwezaaaasd"
}
```

获取用户的单个 Stack.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/stacks/{stack_id}`

### 返回结果

字段 | 描述
--------- | -----------
id | Stack id
name | Stack 名称
stack_id | Stack 中 stack 的 id
created_at | 创建时间 iso8601 utc
last\_operated\_at | 最后操作时间 iso8601 utc

## 在自由主机部署Stack

```shell
curl -X "POST" "https://openapi.daocloud.io/v1/stacks" \
     -H "Authorization: 3yl2gbdiyfoa4wgc46pqiedlreh9enf44x6qbpjt" \
     -H "Content-Type: stacklication/json; charset=utf-8" \
     -d $'{
  "compose_yml": "wordpress: \\n  image: wordpress \\n  links: \\n    - db:mysql \\n  ports: \\n    - \\"80\\" \\n  restart: always \\ndb: \\n  image: mysql \\n  environment: \\n    - MYSQL_ROOT_PASSWORD=example \\n  restart: always",
  "deploy_id": "7d11e027-386e-4d0a-8ea3-7f0d46d110e3",
  "name": "wordpress",
  "deploy_type": "node"
}'
```

```python
import requests
import json

result = requests.post(
    url="https://192.168.1.24:8881/open/v1/stacks",
    headers={
        "Authorization": "token {token}",
    },
    data=json.dumps({
        "name": "testtest3",
        "compose_yml": '''wordpress: 
  image: wordpress 
  links: 
    - db:mysql 
  ports: 
    - "80" 
  restart: always 
db: 
  image: mysql 
  environment: 
    - MYSQL_ROOT_PASSWORD=example 
  restart: always
        ''',
        "deploy_type": "node",
        "deploy_id": "7d11e027-386e-4d0a-8ea3-7f0d46d110e3"
    }
))

print(result.json())  
```

> 获取结果如下:

```json
{
  "stack_id": "900fcdbf-e2f4-462e-844a-acea1fac2076",
  "action_id": "35b14fe5-238f-41fd-9dfa-347382154198"
}
```

### HTTP 请求

`POST https://openapi.daocloud.io/v1/stacks`

### 参数

字段 | 描述
--------- | -----------
name | Stack 名称
deploy_type | 部署类型(node或cluster)
deploy_id   | 部署节点／集群 ID
compose_yml | Stack compose YAML



### 返回结果

字段 | 描述
--------- | -----------
stack_id | 创建的 Stack ID
action_id | 创建事件 ID


## 更改 Stack

```shell
curl -X "PATCH" "https://openapi.daocloud.io/v1/stacks/4ba8609d-f614-439e-8035-8c5e363e3034" \
     -H "Authorization: 3yl2gbdiyfoa4wgc46pqiedlreh9enf44x6qbpjt" \
     -H "Content-Type: stacklication/json; charset=utf-8" \
     -d '{
  "compose_yml": "wordpress: \\n  image: wordpress \\n  links: \\n    - db:mysql \\n  ports: \\n    - \\"80\\" \\n  restart: always \\ndb: \\n  image: mysql \\n  environment: \\n    - MYSQL_ROOT_PASSWORD=example \\n  restart: always"
}'
```

```python
import requests
import json

result = requests.patch(
    url="https://192.168.1.24:8881/open/v1/stacks/4ba8609d-f614-439e-8035-8c5e363e3034",
    headers={
        "Authorization": "token {token}",
    },
    data=json.dumps({
        "compose_yml": '''wordpress: 
  image: wordpress 
  links: 
    - db:mysql 
  ports: 
    - "80" 
  restart: always 
db: 
  image: mysql 
  environment: 
    - MYSQL_ROOT_PASSWORD=example 
  restart: always
        '''
    }
))

print(result.json())  
```

> 获取结果如下:

```json
{
  "action_id": "e8b62595-087f-4a85-a30d-d92c3dabdfa1"
}
```

### HTTP 请求

`PATCH https://openapi.daocloud.io/v1/stacks/4ba8609d-f614-439e-8035-8c5e363e3034`

### 参数

字段 | 描述
--------- | -----------
name | Stack 名称
deploy_type | 部署类型(node或cluster)
deploy_id   | 部署节点／集群 ID
compose_yml | Stack compose YAML



### 返回结果

字段 | 描述
--------- | -----------
action_id | 创建事件 ID


## 启动 stack

```shell
curl -X POST "https://openapi.daocloud.io/v1/stacks/<stack_id>/actions/start"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/start',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

启动 stack.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/start`

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id

## 停止 stack

```shell
curl -X POST "https://openapi.daocloud.io/v1/stacks/<stack_id>/actions/stop"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/stop',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

停止 Stack.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/stop`

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id

## 重启 stack

```shell
curl -X POST "https://openapi.daocloud.io/v1/stacks/<stack_id>/actions/restart"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.post('https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/restart',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "action_id": "80ae7c11-91d6-4edd-a785-e372bd04c4cb"
}
```

重启 Stack.

### HTTP 请求

`POST https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/restart`

### 返回结果

字段 | 描述
--------- | -----------
action_id | 事件 id


## 获取 Stack Action

```shell
curl "https://openapi.daocloud.io/v1/stacks/<stack_id>/actions/<action_id>"
  -H "Authorization: token <my token>"
```

```python
import requests

result = requests.get('https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/{action_id}',
  headers={"Authorization": "token {token}"})

print(result.json())
```

> 获取结果如下:

```json
{
  "time_cost_seconds": 5,
  "end_date": "2017-06-14T01:08:27+00:00",
  "app_id": null,
  "action_name": "create_stack",
  "state": "success",
  "start_date": "2017-06-14T01:08:22+00:00",
  "error_info": {
    "message": null
  },
  "id": "313a3ba1-b776-4e6f-b88d-eb330f5e8b1c"
}
```

获取事件信息.

### HTTP 请求

`GET https://openapi.daocloud.io/v1/stacks/{stack_id}/actions/{action_id}`

### 返回结果

字段 | 描述
--------- | -----------
id | Action id
action_name | Action 名称
state | stack 状态, SUCCESS -> 成功, FAILED -> 失败, IN_PROCESS -> 正在执行
stack_id | stack id
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
 
WebHook 可以用于集成 DaoCloud Services 的项目流水线。当流水线状态变动时，我们会给你发送一个 POST 请求。

Webhook 设置页面：

`https://dashboard.daocloud.io/settings/profile` 

###持续集成
考虑兼容性，返回结果中的`build_type` 是固定值，为 `ci_build`，新用户可以忽略该值。

###状态
当 stages 的每个阶段状态变化时，或整个构建的状态(status)变化时都会发送 webhook 。

##Payloads:

``` json
{
  "repo":"daocloud/api",    
  "image":"daocloud.io/daocloud/api:master-init",    
  "name":"api",  
  "build": {
    "build_flow_id":"8d7622ea-9323-4489-8c8e-fc4bed448961",
    "stages": [
      {
        "name": "test",
        "status": "Success"
      },
      {
        "name": "build",
        "status": "Success"
      },
      {
        "name": "deploy",
        "status": "Success"
      }
    ],
    "status":"Success",    
    "duration_seconds":180,    
    "author":"DaoCloud",  
    "triggered_by":"tag",   
    "sha":"a7c35d9dc7e93788ce81befbadeb0108de495e5e",
    "ref": "v1.0",
    "ref_is_branch": false,    
    "ref_is_tag": true,    
    "tag":"v1.0",    
    "branch":null,   
    "pull_request":"",    
    "message":"init build ",   
    "started_at":"2015-01-01T08:20:00+00:00",   
    "build_type":"ci_build"
  }   
}
``` 

字段 | 描述
--------- | -----------
repo | 用户项目全名， 用户名/项目
image | 构建成功的镜像地址
build_flow_id | 项目 id
name| 项目名
build | 新触发的构建
status | 构建的状态, Success,Failure,Error,Started,Canceled
stages | 构建的各个阶段的状态, Success,Failure,Error,Started,Canceled
duration_seconds | 构建持续的时间
author | 触发构建的用户
triggered_by | 触发条件, 打tag还是手动构建
sha | 代码 sha
tag | 生成镜像的 tag
ref | 代码的 ref, 如 master, v1.0
ref_is_branch | ref 代表 branch
ref_is_tag | ref 代表 tag
branch | 兼容旧版，当 ref 为 branch 时和 ref 相同
pull_request | 代码的 pull request
message | 代码 commit 消息
started_at | 触发时间, iso8601 format
build_type | 值为 ci_build


