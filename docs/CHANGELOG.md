本阶段默认初始化的管理员账号为：

- 用户名：admin

- 密码：admin123456

当前执行清单进度：

- [x] 1. 重构 app/main.py 为 FastAPI 应用入口，并建立基础应用结构。

- [x] 2. 新增 app/core、app/models、app/schemas、app/api、app/services、app/utils 目录结构。

- [x] 3. 建立数据库配置、SQLite 连接与基础模型基类。

- [x] 4. 建立用户、角色、权限及其关联表模型。

- [x] 5. 建立 JWT 登录认证与权限校验基础能力。

- [x] 6. 实现后台认证接口与当前用户信息接口。

任务进度更新：

[2026-04-08]

\- 已修改：app/main.py app/core/config.py app/core/database.py app/core/security.py app/core/init_db.py app/models/base.py app/models/auth.py app/schemas/auth.py app/services/auth.py app/api/health.py app/api/admin/auth.py pyproject.toml 以及多个 __init__.py

\- 更改：完成第一阶段后端骨架、数据库基础、RBAC 模型、JWT 认证、后台登录与当前用户接口

\- 原因：落实已批准计划的第 1-6 项，为后续文章审核流和后台管理功能提供基础设施

\- 阻碍因素：导入校验时缺少新增依赖，已通过同步依赖解决

\- 状态：成功