# 错误处理

DaoCloud API 可能返回以下错误:


Error Code | Meaning
---------- | -------
400 | Bad Request -- 请求格式错误，请查阅对应的文档条目
401 | bad credentials -- access token 过期，或请求的API超过授权
404 | Not Found -- 调用的 API 不存在，请查看本文档
405 | Method Not Allowed -- 请求 method 错误， 请查阅对应的文档条目
406 | Not Acceptable -- 请求不是 json 格式
500 | Internal Server Error -- 服务器错误，请联系 DaoCloud 客服
503 | Service Unavailable -- 服务器暂时下线，请稍候重试
