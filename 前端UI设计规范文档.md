# ETF资产配置策略系统 - 前端UI设计规范

## 🎨 设计理念

### 核心设计原则
- **现代科技感**: 体现金融科技的专业性和前瞻性
- **简洁大气**: 去除冗余元素，突出核心功能
- **用户友好**: 符合用户认知习惯，操作简单直观
- **品质感**: 精致的视觉细节，提升产品品质感知

### 设计目标
- 打造专业、现代、易用的金融科技产品界面
- 通过视觉设计增强用户对产品的信任感
- 提供一致性的用户体验和交互反馈
- 确保界面在不同设备上的良好展示效果

## 🎯 整体风格定位

### 风格关键词
- **科技感** - 现代、前沿、智能
- **专业感** - 可信、严谨、权威
- **简洁感** - 清晰、高效、直观
- **品质感** - 精致、优雅、高端

### 视觉风格特征
- 简洁的几何形状和线条
- 科技蓝为主的现代色彩搭配
- 适度的阴影和渐变效果
- 流畅的动画和过渡效果

## 🌈 色彩系统

### 主色调定义
```css
/* 主要颜色 */
:root {
  /* 品牌主色 - 科技蓝 */
  --primary-color: #1890FF;
  --primary-hover: #40A9FF;
  --primary-active: #096DD9;
  --primary-disabled: #91D5FF;
  
  /* 辅助色 - 成功/警告/错误 */
  --success-color: #52C41A;
  --success-hover: #73D13D;
  --success-active: #389E0D;
  
  --warning-color: #FAAD14;
  --warning-hover: #FFC53D;
  --warning-active: #D48806;
  
  --error-color: #FF4D4F;
  --error-hover: #FF7875;
  --error-active: #D9363E;
  
  /* 中性色 - 背景和文字 */
  --background-primary: #FFFFFF;
  --background-secondary: #F0F2F5;
  --background-tertiary: #FAFAFA;
  --background-quaternary: #F5F5F5;
  
  --text-primary: #262626;
  --text-secondary: #595959;
  --text-tertiary: #8C8C8C;
  --text-disabled: #BFBFBF;
  --text-inverse: #FFFFFF;
  
  /* 边框和分割线 */
  --border-color: #D9D9D9;
  --border-light: #F0F0F0;
  --border-dark: #BFBFBF;
}
```

### 色彩应用规范

#### 主色调应用
- **按钮**: 主要操作按钮使用科技蓝
- **链接**: 文字链接和可点击元素
- **进度条**: 加载进度和状态指示
- **选中状态**: 菜单选中、选项卡激活等

#### 功能色应用
- **成功色**: 成功提示、正收益显示、完成状态
- **警告色**: 警告提示、风险提示、注意事项
- **错误色**: 错误提示、负收益显示、失败状态

#### 中性色应用
- **背景色**: 页面背景、卡片背景、输入框背景
- **文字色**: 标题、正文、辅助文字、禁用文字
- **边框色**: 分割线、边框、表格线条

## 📝 字体系统

### 字体族定义
```css
:root {
  /* 中文字体 */
  --font-family-chinese: 'PingFang SC', '苹方', 'Microsoft YaHei', '微软雅黑', 
                        'Source Han Sans CN', '思源黑体', sans-serif;
  
  /* 英文字体 */
  --font-family-english: 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
  
  /* 等宽字体 - 用于代码和数字 */
  --font-family-monospace: 'SF Mono', 'Monaco', 'Consolas', 'Liberation Mono', 
                          'Courier New', monospace;
}
```

### 字体尺寸规范
```css
:root {
  /* 字体大小 */
  --font-size-xs: 10px;      /* 极小文字 */
  --font-size-sm: 12px;      /* 小号文字 */
  --font-size-base: 14px;    /* 基础文字 */
  --font-size-lg: 16px;      /* 大号文字 */
  --font-size-xl: 18px;      /* 特大文字 */
  --font-size-xxl: 20px;     /* 标题文字 */
  --font-size-xxxl: 24px;    /* 大标题 */
  --font-size-display: 32px; /* 展示数字 */
  
  /* 行高 */
  --line-height-tight: 1.2;
  --line-height-base: 1.5;
  --line-height-loose: 1.8;
  
  /* 字重 */
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

### 字体应用场景

#### 标题层级
- **H1 (32px/700)**: 页面主标题
- **H2 (24px/600)**: 区块标题
- **H3 (20px/600)**: 小节标题
- **H4 (18px/500)**: 子标题
- **H5 (16px/500)**: 卡片标题
- **H6 (14px/500)**: 列表标题

#### 正文文字
- **大号正文 (16px/400)**: 重要内容描述
- **标准正文 (14px/400)**: 常规文字内容
- **小号正文 (12px/400)**: 辅助说明文字
- **极小文字 (10px/400)**: 版权信息、时间戳

#### 数字显示
- **展示数字 (32px/600)**: 重要指标展示
- **数据数字 (16px/500)**: 表格中的数值
- **等宽数字**: 金额、百分比等对齐显示

## 📏 间距系统

### 间距规范
```css
:root {
  /* 基础间距单位 */
  --spacing-unit: 4px;
  
  /* 间距尺寸 */
  --spacing-xs: 4px;    /* 极小间距 */
  --spacing-sm: 8px;    /* 小间距 */
  --spacing-md: 16px;   /* 中等间距 */
  --spacing-lg: 24px;   /* 大间距 */
  --spacing-xl: 32px;   /* 特大间距 */
  --spacing-xxl: 48px;  /* 超大间距 */
  --spacing-xxxl: 64px; /* 巨大间距 */
}
```

### 间距应用规范

#### 组件内间距
- **按钮内边距**: 8px 16px（小按钮）、12px 24px（标准按钮）
- **输入框内边距**: 8px 12px
- **卡片内边距**: 16px 或 24px
- **表格单元格**: 8px 16px

#### 组件间间距
- **相关元素间距**: 8px（紧密关联）
- **一般元素间距**: 16px（常规间距）
- **区块间距**: 24px（不同区块）
- **页面边距**: 24px 或 32px

#### 布局间距
- **栅格间隙**: 16px 或 24px
- **页面边距**: 24px（移动端）、32px（桌面端）
- **内容区域**: 最大宽度1200px，居中对齐

## 🔘 圆角系统

### 圆角规范
```css
:root {
  /* 圆角尺寸 */
  --border-radius-none: 0;
  --border-radius-sm: 2px;    /* 小圆角 */
  --border-radius-base: 4px;  /* 基础圆角 */
  --border-radius-md: 6px;    /* 中等圆角 */
  --border-radius-lg: 8px;    /* 大圆角 */
  --border-radius-xl: 12px;   /* 特大圆角 */
  --border-radius-full: 50%;  /* 圆形 */
}
```

### 圆角应用场景
- **按钮**: 6px（中等圆角）
- **输入框**: 4px（基础圆角）
- **卡片**: 8px（大圆角）
- **标签**: 12px（特大圆角）
- **头像**: 50%（圆形）
- **图片**: 4px 或 8px

## 🌟 阴影系统

### 阴影层级
```css
:root {
  /* 阴影效果 */
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-base: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 12px 24px rgba(0, 0, 0, 0.12);
  --shadow-xxl: 0 16px 32px rgba(0, 0, 0, 0.15);
  
  /* 特殊阴影 */
  --shadow-inner: inset 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-focus: 0 0 0 3px rgba(24, 144, 255, 0.2);
  --shadow-glow: 0 0 20px rgba(24, 144, 255, 0.3);
}
```

### 阴影应用规范
- **卡片静态**: shadow-sm（轻微阴影）
- **卡片悬停**: shadow-md（中等阴影）
- **按钮**: shadow-sm（静态）、shadow-base（悬停）
- **模态框**: shadow-xl（重阴影）
- **下拉菜单**: shadow-lg（较重阴影）
- **聚焦状态**: shadow-focus（蓝色外发光）

## 🎭 动画系统

### 动画时间
```css
:root {
  /* 动画持续时间 */
  --duration-fast: 150ms;     /* 快速动画 */
  --duration-base: 200ms;     /* 基础动画 */
  --duration-slow: 300ms;     /* 慢速动画 */
  --duration-slower: 500ms;   /* 更慢动画 */
  
  /* 动画缓动函数 */
  --ease-linear: linear;
  --ease-in: ease-in;
  --ease-out: ease-out;
  --ease-in-out: ease-in-out;
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 动画应用场景

#### 微交互动画
- **按钮悬停**: 背景颜色变化 + 轻微上浮
- **链接悬停**: 颜色变化 + 下划线动画
- **输入框聚焦**: 边框颜色 + 外发光效果
- **卡片悬停**: 阴影加深 + 轻微上浮

#### 状态变化动画
- **加载状态**: 旋转、脉冲、波浪等动画
- **成功状态**: 对勾动画、颜色变化
- **错误状态**: 摇晃动画、颜色变化
- **切换状态**: 滑动、淡入淡出

#### 页面转场动画
- **路由切换**: 滑动、淡入淡出
- **模态框**: 缩放 + 透明度变化
- **抽屉**: 滑动进出
- **提示框**: 从上方滑入

## 🖼️ 图标系统

### 图标风格
- **线性图标**: 2px 线宽，圆角端点
- **填充图标**: 用于激活状态和重要操作
- **双色图标**: 主色调 + 中性色组合
- **动态图标**: 支持悬停和点击动画

### 图标尺寸
```css
:root {
  /* 图标尺寸 */
  --icon-xs: 12px;    /* 极小图标 */
  --icon-sm: 14px;    /* 小图标 */
  --icon-base: 16px;  /* 基础图标 */
  --icon-lg: 20px;    /* 大图标 */
  --icon-xl: 24px;    /* 特大图标 */
  --icon-xxl: 32px;   /* 超大图标 */
}
```

### 图标应用规范
- **导航图标**: 20px，线性风格
- **操作图标**: 16px，与文字对齐
- **状态图标**: 14px，用于表示状态
- **装饰图标**: 根据上下文调整尺寸

## 📱 响应式设计

### 断点系统
```css
:root {
  /* 响应式断点 */
  --breakpoint-xs: 480px;   /* 小屏手机 */
  --breakpoint-sm: 768px;   /* 大屏手机/小平板 */
  --breakpoint-md: 1024px;  /* 平板 */
  --breakpoint-lg: 1280px;  /* 小屏笔记本 */
  --breakpoint-xl: 1440px;  /* 大屏显示器 */
  --breakpoint-xxl: 1920px; /* 超大屏显示器 */
}
```

### 响应式规则

#### 布局适配
- **移动端**: 单列布局，全宽卡片
- **平板端**: 两列布局，适中卡片
- **桌面端**: 多列布局，固定宽度

#### 字体适配
- **移动端**: 基础字号14px
- **平板端**: 基础字号15px
- **桌面端**: 基础字号16px

#### 间距适配
- **移动端**: 较小间距，紧凑布局
- **平板端**: 中等间距，平衡布局
- **桌面端**: 较大间距，宽松布局

## 🎨 组件设计规范

### 按钮设计

#### 主要按钮 (Primary Button)
```css
.btn-primary {
  background: linear-gradient(135deg, #1890FF, #40A9FF);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(24, 144, 255, 0.2);
  transition: all 200ms ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #40A9FF, #1890FF);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transform: translateY(-1px);
}
```

#### 次要按钮 (Secondary Button)
```css
.btn-secondary {
  background: transparent;
  color: #1890FF;
  border: 1px solid #1890FF;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  transition: all 200ms ease;
}

.btn-secondary:hover {
  background: #1890FF;
  color: white;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
}
```

### 输入框设计

#### 标准输入框
```css
.input-base {
  background: white;
  border: 1px solid #D9D9D9;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  color: #262626;
  transition: all 200ms ease;
  outline: none;
}

.input-base:focus {
  border-color: #1890FF;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.input-base::placeholder {
  color: #BFBFBF;
}
```

### 卡片设计

#### 标准卡片
```css
.card-base {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 24px;
  transition: all 300ms ease;
  border: 1px solid #F0F0F0;
}

.card-base:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
```

#### 科技感卡片
```css
.card-tech {
  background: linear-gradient(145deg, #FFFFFF, #F8FAFF);
  border-radius: 12px;
  box-shadow: 
    0 4px 12px rgba(24, 144, 255, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.card-tech::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #1890FF, #40A9FF);
}
```

## 📊 数据展示规范

### 数字显示
- **金额**: 千分位分隔符，保留2位小数
- **百分比**: 保留2位小数，带%符号
- **收益率**: 正数绿色，负数红色，零值灰色
- **数量**: 根据大小自动使用K、M、B单位

### 图表配色
- **主色调**: 科技蓝系列渐变
- **多色调**: 蓝、绿、橙、紫、红的搭配
- **状态色**: 绿色（上涨）、红色（下跌）、灰色（平盘）

### 表格设计
- **表头**: 深色背景，白色文字
- **斑马纹**: 交替行浅色背景
- **悬停**: 行悬停时背景高亮
- **排序**: 可点击的排序图标

## 🔄 状态设计

### 加载状态
- **按钮加载**: 旋转图标 + 文字变化
- **页面加载**: 骨架屏占位
- **数据加载**: 波浪动画或脉冲效果
- **图表加载**: 渐进式绘制动画

### 空状态
- **无数据**: 友好的插图 + 提示文字
- **网络错误**: 错误图标 + 重试按钮
- **权限不足**: 锁定图标 + 说明文字
- **搜索无结果**: 搜索图标 + 建议操作

### 反馈状态
- **成功**: 绿色对勾 + 成功提示
- **警告**: 黄色感叹号 + 警告说明
- **错误**: 红色叉号 + 错误信息
- **信息**: 蓝色信息图标 + 提示内容

## 🎯 设计实施指南

### 设计工具
- **设计软件**: Figma、Sketch
- **原型工具**: Figma、Principle
- **图标库**: Feather Icons、Heroicons
- **字体**: Google Fonts、Adobe Fonts

### 设计交付
- **设计稿**: 包含各种状态和尺寸
- **标注文档**: 详细的尺寸和样式说明
- **切图资源**: 各种分辨率的图片资源
- **交互说明**: 动画和交互行为描述

### 质量控制
- **设计评审**: 多轮设计评审和优化
- **用户测试**: 可用性测试和反馈收集
- **技术评审**: 与开发团队确认实现可行性
- **上线验收**: 确保实现效果与设计一致

## 📋 设计检查清单

### 视觉检查
- [ ] 色彩搭配符合品牌规范
- [ ] 字体大小和层级清晰
- [ ] 间距使用统一的规范
- [ ] 圆角和阴影保持一致
- [ ] 图标风格统一

### 交互检查
- [ ] 所有可点击元素有明确的视觉反馈
- [ ] 悬停状态设计合理
- [ ] 加载和等待状态有适当提示
- [ ] 错误状态有清晰的错误信息
- [ ] 动画时长和缓动函数合适

### 响应式检查
- [ ] 在不同屏幕尺寸下显示正常
- [ ] 移动端触摸目标大小合适
- [ ] 文字在小屏幕上仍然可读
- [ ] 布局在各种设备上都合理
- [ ] 图片和媒体内容自适应

### 可访问性检查
- [ ] 颜色对比度符合WCAG标准
- [ ] 重要信息不仅依赖颜色传达
- [ ] 表单元素有适当的标签
- [ ] 键盘导航功能正常
- [ ] 屏幕阅读器兼容性良好

这套设计规范将确保ETF资产配置策略系统具有现代、专业、科技感十足的用户界面，提供优秀的用户体验。
