# PayGuard 前端快速开始指南

## 安装与运行

### 1. 安装依赖

```bash
cd frontend
npm install
```

如果遇到安装问题，可以尝试：

```bash
npm install --legacy-peer-deps
```

### 2. 启动后端服务

在另一个终端窗口中：

```bash
# 返回项目根目录
cd ..

# 激活虚拟环境（如果使用）
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

确保后端运行在 `http://127.0.0.1:8000`

### 3. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

访问 http://localhost:3000

## 测试账号

- **管理员账号**: 
  - 用户名: `admin`
  - 密码: `admin123`
  - 角色: super_admin

- **分析师账号**:
  - 用户名: `demo`
  - 密码: `demo123`
  - 角色: analyst

## 快速演示流程

### 步骤1: 登录系统
1. 访问 http://localhost:3000
2. 自动跳转到登录页
3. 使用 `admin` / `admin123` 登录
4. 成功后跳转到仪表盘

### 步骤2: 查看仪表盘
- 实时统计数据
- 风险分布图表
- 最近审计记录

### 步骤3: 单笔交易审计
1. 点击左侧菜单"单笔审计"
2. 点击"低风险场景"快速填充
3. 点击"🔍 开始审计"
4. 查看右侧审计结果

### 步骤4: 批量审计
1. 点击"批量审计"
2. 点击"添加 5 笔样例"
3. 点击"🚀 批量审计"
4. 查看进度和结果
5. 点击"查看详细结果"

### 步骤5: 审核工作流
1. 点击"待审核"
2. 点击某个交易的"查看详情"
3. 输入审核意见
4. 点击"✅ 批准"或"❌ 拒绝"

### 步骤6: 报告查询
1. 点击"报告查询"
2. 勾选几条记录
3. 点击"📥 导出CSV"

## 功能说明

### 🔐 认证系统
- JWT Token认证
- 自动Token刷新
- 角色权限控制

### 📊 仪表盘
- 交易统计卡片
- Chart.js图表可视化
- 实时数据刷新

### 🔍 单笔审计
- 完整表单验证
- 三种快速测试场景
- 实时风险评估
- 触发规则展示

### 📦 批量审计
- 手动添加/JSON导入
- 并发控制（1-50）
- 进度实时显示
- 结果统计和导出

### ✋ 审核工作流
- 多维度筛选
- 任务分配
- 状态流转
- 评论系统
- 时间线追踪

### 📄 报告查询
- 历史记录查询
- 批量导出
- CSV/Excel格式

## 常见问题

### Q: 页面显示空白？
A: 
1. 检查浏览器控制台是否有错误
2. 确认后端API正常运行
3. 检查浏览器是否支持（需Chrome 90+）

### Q: API调用失败？
A:
1. 确认后端运行在 http://127.0.0.1:8000
2. 检查后端健康接口: http://127.0.0.1:8000/api/health/health
3. 查看浏览器Network标签的请求状态

### Q: 图表不显示？
A:
1. 确认Chart.js已安装: `npm list chart.js`
2. 检查控制台是否有错误
3. 确认有统计数据返回

### Q: 登录后跳转失败？
A:
1. 清除浏览器localStorage
2. 检查后端认证接口返回
3. 确认路由守卫正常工作

## 生产部署

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

### 使用Nginx部署

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用Docker部署

```bash
# 在frontend目录下
docker build -t payguard-frontend .
docker run -p 80:80 payguard-frontend
```

## 技术支持

遇到问题？
1. 查看浏览器控制台
2. 检查后端日志
3. 查阅 frontend/README.md 详细文档
4. 提交Issue到项目仓库

## 下一步

- 集成实际交易数据源
- 添加更多图表类型
- 实现WebSocket实时推送
- 添加更多筛选维度
- 优化移动端体验
