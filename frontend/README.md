# PayGuard Frontend

PayGuard 前端应用 - 企业级支付风控审计系统的现代化Web界面

## 功能特性

### 🔐 认证授权
- JWT Token认证
- 基于角色的访问控制（RBAC）
- 安全的登录/登出流程
- Token自动刷新

### 📊 仪表盘
- 实时风控数据概览
- 风险等级分布图表
- 决策分布统计
- TOP 10触发规则
- 最近审计记录

### 🔍 单笔交易审计
- 可视化交易信息表单
- 实时风险评估
- 快速测试场景（低/中/高风险）
- 详细的审计结果展示
- 触发规则列表
- 一键创建人工审核

### 📦 批量交易审计
- 手动添加交易
- JSON批量导入
- 样例数据生成
- 并发控制配置
- 批量审计进度显示
- 风险分布统计
- 详细结果查看
- CSV导出功能

### ✋ 审核工作流
- 待审核交易列表
- 多维度筛选（优先级、分配人）
- 审核统计概览
- 审核详情页面
- 状态流转（批准/拒绝/上报）
- 评论系统
- 审核人分配
- 时间线追踪

### 📄 报告查询与导出
- 历史审计记录查询
- 多条件筛选
- 批量选择
- CSV导出
- Excel导出（带格式）
- 分页浏览

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **UI框架**: Tailwind CSS
- **图表**: Chart.js + vue-chartjs

## 快速开始

### 前置要求

- Node.js >= 16
- npm 或 pnpm

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── index.html              # HTML入口
├── package.json            # 依赖配置
├── vite.config.js          # Vite配置
├── tailwind.config.js      # Tailwind配置
├── postcss.config.js       # PostCSS配置
└── src/
    ├── main.js             # 应用入口
    ├── App.vue             # 根组件
    ├── style.css           # 全局样式
    ├── router/             # 路由配置
    │   └── index.js
    ├── stores/             # Pinia状态管理
    │   ├── auth.js         # 认证状态
    │   ├── audit.js        # 审计状态
    │   └── review.js       # 审核状态
    ├── services/           # API服务
    │   └── api.js          # API封装
    ├── layouts/            # 布局组件
    │   └── MainLayout.vue  # 主布局
    └── views/              # 页面组件
        ├── Login.vue           # 登录页
        ├── Dashboard.vue       # 仪表盘
        ├── SingleAudit.vue     # 单笔审计
        ├── BatchAudit.vue      # 批量审计
        ├── PendingReviews.vue  # 待审核列表
        ├── ReviewDetail.vue    # 审核详情
        └── Reports.vue         # 报告查询
```

## API配置

API代理配置在 `vite.config.js`：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true
    }
  }
}
```

## 测试账号

- **管理员**: `admin` / `admin123` (super_admin 角色)
- **分析师**: `demo` / `demo123` (analyst 角色)

## 环境变量

如需自定义API地址，可以在 `src/services/api.js` 中修改 `baseURL`：

```javascript
const api = axios.create({
  baseURL: '/api',  // 或自定义URL
  timeout: 30000
})
```

## 主要功能演示

### 1. 登录系统
- 访问根路径自动跳转到登录页
- 使用测试账号登录
- JWT Token自动存储到 localStorage
- 登录后跳转到仪表盘

### 2. 单笔审计
1. 点击左侧菜单"单笔审计"
2. 填写交易信息或使用快速测试按钮
3. 点击"开始审计"
4. 查看右侧风险评估结果
5. 可创建人工审核或查看详细报告

### 3. 批量审计
1. 点击"批量审计"
2. 手动添加交易或使用样例数据
3. 配置并发数
4. 点击"批量审计"
5. 查看进度和结果
6. 导出CSV报告

### 4. 审核工作流
1. 点击"待审核"查看需要人工审核的交易
2. 使用筛选器过滤
3. 点击"分配给我"或"查看详情"
4. 在详情页添加评论、批准/拒绝
5. 状态自动更新

### 5. 报告查询
1. 点击"报告查询"
2. 设置筛选条件
3. 勾选需要导出的记录
4. 点击"导出CSV"或"导出Excel"

## 样式定制

全局样式定义在 `src/style.css`，使用 Tailwind CSS 的 `@layer` 指令：

```css
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-primary-600 text-white rounded-lg ...;
  }
}
```

主题色配置在 `tailwind.config.js`：

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#8b5cf6',
        600: '#7c3aed',
        ...
      }
    }
  }
}
```

## 部署

### Docker部署（推荐）

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 静态服务器部署

```bash
npm run build
# 将 dist/ 目录部署到任何静态服务器
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 常见问题

### 1. API调用失败
- 确认后端服务已启动（http://127.0.0.1:8000）
- 检查 API Key 是否正确（默认: `demo-test-key-12345`）
- 查看浏览器控制台网络请求

### 2. 图表不显示
- 确认已安装 Chart.js 依赖
- 检查数据格式是否正确
- 查看浏览器控制台错误

### 3. 路由404
- 开发模式使用 Vite 的 SPA fallback
- 生产部署需配置 nginx 的 `try_files`

## 开发建议

### 代码规范
- 使用 Composition API
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case
- 提交前确保无 ESLint 错误

### 性能优化
- 路由懒加载已启用
- 图片使用适当的格式和大小
- API 请求添加适当的缓存
- 大列表使用虚拟滚动（如需要）

## License

MIT License

## 联系方式

- GitHub: [payguard_crew_starter](https://github.com/your-repo)
- 文档: 查看 `docs/` 目录
