# PayGuard 前端设计系统

## 🎨 设计原则

### 品牌定位
- **企业级**：专业、可信赖的支付风控平台
- **现代化**：简洁、直观的用户界面
- **数据驱动**：清晰的数据可视化和决策支持

### 设计理念
1. **清晰性** - 信息层级分明，关键数据突出
2. **一致性** - 统一的视觉语言和交互模式
3. **高效性** - 减少认知负担，快速完成任务
4. **可访问性** - 符合WCAG 2.1 AA标准

---

## 🎨 颜色系统

### 主色调（Primary）
品牌紫色 - 代表专业、安全、可信
```
50:  #f5f3ff
100: #ede9fe
500: #8b5cf6  ← 主要使用
600: #7c3aed  ← 悬停状态
700: #6d28d9  ← 激活状态
```

### 风险等级色彩

**成功/低风险（Success/Green）**
```css
--success-50:  #f0fdf4  /* 背景 */
--success-100: #dcfce7  /* 浅色 */
--success-500: #22c55e  /* 主色 */
--success-600: #16a34a  /* 深色 */
```

**警告/中风险（Warning/Yellow）**
```css
--warning-50:  #fffbeb
--warning-100: #fef3c7
--warning-500: #f59e0b
--warning-600: #d97706
```

**危险/高风险（Danger/Red）**
```css
--danger-50:  #fef2f2
--danger-100: #fee2e2
--danger-500: #ef4444
--danger-600: #dc2626
```

### 中性色（Gray）
```css
--gray-50:  #f9fafb  /* 背景 */
--gray-100: #f3f4f6  /* 次要背景 */
--gray-200: #e5e7eb  /* 边框 */
--gray-300: #d1d5db  /* 分隔线 */
--gray-500: #6b7280  /* 次要文字 */
--gray-700: #374151  /* 主要文字 */
--gray-900: #111827  /* 标题 */
```

### 语义化颜色

| 用途 | 颜色 | 使用场景 |
|------|------|---------|
| 批准/通过 | Success Green | 低风险交易、审核通过 |
| 待审核 | Warning Yellow | 中风险交易、待人工审核 |
| 拒绝/高危 | Danger Red | 高风险交易、审核拒绝 |
| 信息提示 | Blue | 中性信息、帮助提示 |
| 品牌强调 | Primary Purple | CTA按钮、重要操作 |

---

## 📐 间距系统

基于 4px 网格系统：

```css
xs:  4px   (0.25rem)
sm:  8px   (0.5rem)
md:  16px  (1rem)
lg:  24px  (1.5rem)
xl:  32px  (2rem)
2xl: 48px  (3rem)
```

### 使用指南
- **组件内边距**：使用 md (16px)
- **组件间距**：使用 lg (24px)
- **章节间距**：使用 2xl (48px)
- **卡片内边距**：p-6 (24px)

---

## 🔤 字体系统

### 字体家族
```css
/* 西文字体 */
font-family: 'Inter var', system-ui, -apple-system, sans-serif;

/* 等宽字体（代码、数据） */
font-family: 'JetBrains Mono', Menlo, Monaco, monospace;
```

### 字体大小

| 名称 | 大小 | 行高 | 用途 |
|------|------|------|------|
| 2xs | 10px | 14px | 标签、徽章 |
| xs | 12px | 16px | 辅助文字 |
| sm | 14px | 20px | 正文、输入框 |
| base | 16px | 24px | 主要正文 |
| lg | 18px | 28px | 小标题 |
| xl | 20px | 28px | 卡片标题 |
| 2xl | 24px | 32px | 页面标题 |
| 4xl | 36px | 40px | 大标题 |

### 字重
- **Regular (400)** - 正文
- **Medium (500)** - 强调文本
- **Semibold (600)** - 按钮文字
- **Bold (700)** - 标题

---

## 🔘 组件规范

### 按钮（Button）

#### 尺寸
```vue
<!-- 小按钮 -->
<Button size="sm">Small</Button>
<!-- px-3 py-1.5 text-sm -->

<!-- 中按钮（默认） -->
<Button size="md">Medium</Button>
<!-- px-4 py-2 text-base -->

<!-- 大按钮 -->
<Button size="lg">Large</Button>
<!-- px-6 py-3 text-lg -->
```

#### 变体
- **Primary** - 主要操作（提交、确认）
- **Secondary** - 次要操作（取消、返回）
- **Success** - 成功操作（批准、通过）
- **Danger** - 危险操作（删除、拒绝）
- **Ghost** - 辅助操作（查看、编辑）

#### 状态
- Default - 默认状态
- Hover - 悬停状态（颜色加深）
- Active - 激活状态（颜色更深）
- Disabled - 禁用状态（50%透明度）
- Loading - 加载状态（显示转圈图标）

### 徽章（Badge）

#### 尺寸
- **sm**: px-2 py-0.5 text-2xs
- **md**: px-3 py-1 text-xs
- **lg**: px-4 py-1.5 text-sm

#### 变体
```vue
<Badge variant="success">低风险</Badge>
<Badge variant="warning">中风险</Badge>
<Badge variant="danger">高风险</Badge>
<Badge variant="info">待审核</Badge>
<Badge variant="primary">VIP</Badge>
```

### 输入框（Input）

#### 状态
```vue
<!-- 正常状态 -->
<Input v-model="value" placeholder="输入内容" />

<!-- 错误状态 -->
<Input v-model="value" error="必填项不能为空" />

<!-- 禁用状态 -->
<Input v-model="value" disabled />

<!-- 带图标 -->
<Input v-model="value" prefixIcon="🔍" />
<Input v-model="value" suffixIcon="✓" />
```

### 卡片（Card）

```vue
<!-- 基础卡片 -->
<Card title="卡片标题">
  内容区域
</Card>

<!-- 可交互卡片 -->
<Card interactive @click="handleClick">
  点击卡片
</Card>

<!-- 自定义头部和底部 -->
<Card>
  <template #header>
    <h3>自定义标题</h3>
  </template>
  
  内容区域
  
  <template #footer>
    <Button>操作</Button>
  </template>
</Card>
```

---

## 📊 数据可视化

### 图表配色

#### 风险分布（柱状图）
```javascript
backgroundColor: ['#22c55e', '#f59e0b', '#ef4444']
// 绿色（低）、黄色（中）、红色（高）
```

#### 决策分布（饼图）
```javascript
backgroundColor: ['#22c55e', '#3b82f6', '#ef4444']
// 绿色（批准）、蓝色（审核）、红色（拒绝）
```

### 图表样式
- **字体**：与主字体一致
- **网格线**：#e5e7eb（gray-200）
- **标签颜色**：#6b7280（gray-500）
- **工具提示背景**：白色，带阴影

---

## 🎭 动画效果

### 过渡时间
```css
fast:   150ms  /* 微交互 */
base:   200ms  /* 默认 */
slow:   300ms  /* 页面切换 */
```

### 缓动函数
```css
ease-in:     cubic-bezier(0.4, 0, 1, 1)
ease-out:    cubic-bezier(0, 0, 0.2, 1)
ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
```

### 预定义动画
```vue
<!-- 淡入 -->
<div class="animate-fade-in">内容</div>

<!-- 上滑 -->
<div class="animate-slide-up">内容</div>

<!-- 缩放入场 -->
<div class="animate-scale-in">内容</div>

<!-- 慢速脉冲 -->
<div class="animate-pulse-slow">内容</div>
```

---

## 📱 响应式断点

```css
sm:  640px   /* 手机横屏 */
md:  768px   /* 平板 */
lg:  1024px  /* 小笔记本 */
xl:  1280px  /* 桌面 */
2xl: 1536px  /* 大屏幕 */
```

### 使用示例
```vue
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <!-- 移动端1列，平板2列，桌面4列 -->
</div>
```

---

## 🔄 状态指示

### 在线状态
```vue
<span class="status-online"></span> <!-- 绿点 -->
<span class="status-offline"></span> <!-- 红点 -->
<span class="status-warning"></span> <!-- 黄点 -->
```

### 加载状态
```vue
<!-- 骨架屏 -->
<div class="skeleton h-4 w-32"></div>

<!-- 加载按钮 -->
<Button loading>加载中...</Button>

<!-- 加载指示器 -->
<div class="animate-spin">⟳</div>
```

---

## 📏 阴影系统

```css
.shadow-soft:   0 2px 8px rgba(0,0,0,0.08)   /* 轻微阴影 */
.shadow-medium: 0 4px 16px rgba(0,0,0,0.12)  /* 中等阴影 */
.shadow-strong: 0 8px 32px rgba(0,0,0,0.16)  /* 强阴影 */
.shadow-glow:   0 0 20px rgba(139,92,246,0.3) /* 发光效果 */
```

### 使用场景
- **卡片默认**：shadow-soft
- **卡片悬停**：shadow-medium
- **模态框**：shadow-strong
- **活跃元素**：shadow-glow

---

## 🎨 渐变背景

```css
/* 主品牌渐变 */
.gradient-primary:  linear-gradient(135deg, #667eea 0%, #764ba2 100%)

/* 成功渐变 */
.gradient-success:  linear-gradient(135deg, #10b981 0%, #059669 100%)

/* 警告渐变 */
.gradient-warning:  linear-gradient(135deg, #f59e0b 0%, #d97706 100%)

/* 危险渐变 */
.gradient-danger:   linear-gradient(135deg, #ef4444 0%, #dc2626 100%)
```

---

## ♿ 可访问性

### 对比度要求
- **正文文字**：至少 4.5:1
- **大文字（18px+）**：至少 3:1
- **UI组件**：至少 3:1

### 键盘导航
- 所有交互元素可通过Tab键访问
- 焦点状态清晰可见（ring-2）
- Enter/Space触发按钮

### 屏幕阅读器
- 语义化HTML标签
- 适当的ARIA标签
- 错误信息与输入框关联

---

## 📦 组件清单

### 基础组件
- [x] Button - 按钮
- [x] Input - 输入框
- [x] Badge - 徽章
- [x] Card - 卡片
- [x] Modal - 模态框
- [x] Toast - 提示消息

### 待扩展组件
- [ ] Select - 下拉选择
- [ ] Checkbox - 复选框
- [ ] Radio - 单选框
- [ ] Switch - 开关
- [ ] Table - 表格
- [ ] Pagination - 分页
- [ ] Tabs - 标签页
- [ ] Tooltip - 工具提示
- [ ] Dropdown - 下拉菜单
- [ ] Progress - 进度条

---

## 🚀 使用指南

### 快速开始

```vue
<script setup>
import Button from '@/components/Button.vue'
import Badge from '@/components/Badge.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <Card title="示例卡片">
    <div class="space-y-4">
      <Badge variant="success">低风险</Badge>
      <Button variant="primary">提交审计</Button>
    </div>
  </Card>
</template>
```

### 最佳实践

1. **使用语义化颜色**
   ```vue
   <!-- ✅ 好 -->
   <Badge variant="success">低风险</Badge>
   
   <!-- ❌ 避免 -->
   <Badge class="bg-green-100">低风险</Badge>
   ```

2. **保持间距一致**
   ```vue
   <!-- ✅ 好 - 使用预定义间距 -->
   <div class="space-y-6">
   
   <!-- ❌ 避免 - 随意间距 -->
   <div class="space-y-3.5">
   ```

3. **响应式优先**
   ```vue
   <!-- ✅ 好 -->
   <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
   
   <!-- ❌ 避免 - 固定布局 -->
   <div class="grid grid-cols-3">
   ```

---

## 📚 参考资源

- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Vue 3 文档](https://vuejs.org/)
- [WCAG 2.1 指南](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design](https://m3.material.io/)
- [Figma 设计文件](#) - 待创建

---

**版本**: v1.0.0  
**更新日期**: 2026-07-09  
**维护者**: PayGuard Team
