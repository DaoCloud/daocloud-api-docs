# dao-openapi

This repository contains OpenAPI documentation, which is a sub-project that will be integrated into [DaoCloud/Daocloud-docs](https://github.com/DaoCloud/Daocloud-docs) for the purpose of building our website: [docs.daocloud.io](https://docs.daocloud.io/)

## 维护原则

每发布一个新版本（在 `docs/openapi/<模块>/` 下新增一对 `vX.Y.Z.md` + `vX.Y.Z.json`）后，
需要同步更新下面三个文件，让它们与各模块目录里的实际文件保持一致。

| 涉及文件 | 规则 | 说明 |
| :--- | :--- | :--- |
| `index.md` / `midware.md` | 每个模块最多 4 行 × 4 版本 | 每个模块最多 16 条链接；**老的版本不用放**，卡片只保留最新的 4×4 条 |
| `index.md` / `midware.md` | 同系列补丁合并成一条 | 同一个 `vX.Y` 系列有 2 个及以上补丁版本时，合并成**一条** `vX.Y.x`（链接指向该系列最早的补丁），不要每个补丁都铺开，否则很快会占满 4 行 |
| `index.md` / `midware.md` | 旧版本不会丢失 | 页面上列不全的旧版本，在 `openapi-nav.yml` 的「早期版本」里仍然可以访问 |
| `openapi-nav.yml` | 每个产品露出 3 个最新版本 | **通常只露出 3 个最新版本**，其他旧版本全部放到「早期版本」内 |
| `openapi-nav.yml` | 同系列补丁折叠成分组 | 同一个 `vX.Y` 系列有 2 个及以上补丁版本时，折叠成 `vX.Y.x` 分组，组内按从新到旧排列 |
| `openapi-nav.yml` | 版本不足 3 个全部露出 | 版本数不足 3 个的产品（如运营管理）全部露出，不生成「早期版本」 |
| `openapi-nav.yml` | 导航是**全量**的 | `docs/openapi/` 下的每个版本页面都应该能在 nav 里找到；截断只发生在 `index.md` / `midware.md` 这两个索引页上 |
| `scripts/` | 巡检工具（改完跑一遍） | `python3 scripts/scan-openapi-nav.py` —— 检查 nav 与 `docs/openapi/` 的引用/遗漏/重复；`python3 scripts/midware-tools.py scan` —— 预览各中间件组件按上述规则会选出的版本 |
