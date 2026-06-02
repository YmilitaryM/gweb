# 金捷利官网前端重设计 — 设计规格书

**日期:** 2026-06-02
**目标:** 将 GWeb 前端 100% 还原为 https://jinjieliyanshi.netlify.app/ 的设计风格，所有动态数据来源于后端 API，并对齐管理端缺失项。

---

## 1. 参考网站分析摘要

参考网站为 React + Tailwind CSS v4 构建的「金捷利科技」官网。通过解析其 JS Bundle 和 CSS 文件，提取了完整的设计系统和页面结构。

### 1.1 设计 Token

| Token | 值 |
|---|---|
| 字体 (Sans) | `"Inter", ui-sans-serif, system-ui, sans-serif` |
| 字体 (Mono) | `"JetBrains Mono", ui-monospace, SFMono-Regular, monospace` |
| 品牌主色 500 | `#2563eb` (blue-600) |
| 品牌主色 600 | `#1d4ed8` (blue-700) |
| 品牌主色 900 | `#1e3a8a` (blue-900) |
| 品牌浅色 50 | `#eff6ff` |
| 品牌浅色 100 | `#dbeafe` |
| 背景色 | `#f8fafc` (slate-50) + `radial-gradient(circle at 50% -20%, #eff6ff, #f1f5f9)` |
| 正文色 | `#0f172a` (slate-900) |
| Glass 效果 | `bg-white/80` + `backdrop-blur-md` (12px) |
| Glass 强效 | `bg-white/95` + `backdrop-blur-2xl` (40px) |
| 圆角-大 | `rounded-2xl` (1rem) / `rounded-3xl` (1.5rem) |
| 阴影-品牌 | `shadow-xl + shadow-brand-600/30` |

### 1.2 页面结构 (从 JS Bundle 解析)

参考网站路由和页面区块:

```
/           首页: [Header] [Hero(轮播)] [服务卡片] [方案Tab] [产品] [新闻] [CTA] [Footer] [AI浮动]
/products   产品服务: 分类筛选 + 产品卡片网格
/solutions  解决方案: Tab切换(产业园区|医疗建筑|写字楼|商业综合体)
/about      关于我们: 公司介绍 + 新闻 + 历程
/cooperation 商务合作: 合作模式 + 表单
/cases      服务案例: 案例卡片网格
/contact    联系我们: 表单 + 联系信息
/news/:id   新闻详情
/privacy    隐私政策
/terms      法律声明
```

---

## 2. 架构概览

```
┌──────────────────────────────────────────────┐
│                   Frontend (Nuxt 3)           │
│                                               │
│  layouts/default.vue ── 全局设计系统          │
│  ├── AppHeader.vue      (重写)               │
│  ├── <NuxtPage />                              │
│  │   ├── index.vue      (CMS Page 'home')     │
│  │   ├── [...slug].vue  (CMS Page 通用路由)    │
│  │   ├── pages/products/ (产品列表+详情)       │
│  │   ├── pages/news/     (新闻列表+详情)       │
│  │   ├── pages/cases/    (案例列表+详情)  +    │
│  │   └── pages/contact/  (联系页)             │
│  ├── AppFooter.vue      (重写)               │
│  └── ChatFloatingButton  (重写)  +            │
│                                               │
│  组件库:                                       │
│  ├── BlockRenderer → 15+ Block 类型           │
│  ├── BlockHero (升级为轮播)                    │
│  ├── BlockSolutionCards (新增Tab组件)  +       │
│  └── 其他Blocks (改造样式)                     │
└──────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────┐
│                Backend API (FastAPI)           │
│                                               │
│  现有模块:                                     │
│  ├── CMS:    pages, blocks, menus, media      │
│  ├── News:   articles CRUD + public list      │
│  ├── Products: categories + products CRUD     │
│  ├── Settings: key-value store                │
│  ├── Theme:   theme management                │
│  ├── Inquiry: contact forms                   │
│  ├── FAQ, Chat, Users, Auth, Audit            │
│                                               │
│  新增模块:                                     │
│  ├── Cases:  案例 CRUD + public list  +        │
│  └── Settings: 扩展 public keys  +             │
└──────────────────────────────────────────────┘
```

---

## 3. 全局设计系统改造

### 3.1 CSS/Tailwind 覆写

**文件: `frontend/assets/css/main.css`**

新增 Tailwind v4 `@theme` 块:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-500: #2563eb;
  --color-brand-600: #1d4ed8;
  --color-brand-900: #1e3a8a;
  --color-dark-bg: #f8fafc;
  --color-glass: #ffffffbf;
}

body {
  color: #0f172a;
  font-family: var(--font-sans);
  background-color: #f8fafc;
  background-image: radial-gradient(circle at 50% -20%, #eff6ff, #f1f5f9);
}
```

所有现有 emerald 品牌色 (`#059669`, `#10b981`) 替换为 blue 品牌色 (`#2563eb`, `#1d4ed8`)。

### 3.2 不引入 @nuxt/ui

当前项目使用了 `@nuxt/ui`，但参考网站使用纯 Tailwind v4 工具类。保留 `@nuxt/ui` 仅用于必要的基础组件，页面组件全部使用 Tailwind 工具类编写以精确匹配设计。

---

## 4. 全局组件重设计

### 4.1 AppHeader.vue (重写)

**当前状态:** 简单 sticky header，emerald 主题色，基础 dropdown。

**目标设计:**
- 品牌色 blue (`bg-white/80`, `backdrop-blur-md`)
- Scroll 显隐动画: 向下滚隐藏 (`-translate-y-full`)，向上滚显示 (`translate-y-0`)
- 导航项: 蓝色下划线 hover 动画 (`scale-x-0 → scale-x-100`)
- 移动端: 汉堡图标 → 全屏滑出面板 (`absolute top-full`)
- 语言切换: Toggle 按钮（中/EN），参考网站无此功能但保留现有能力

**API 数据映射:**
```
GET /api/v1/menus?location=header
→ [
    { id, name_zh, name_en, link, page_slug, children: [...] },
    ...
  ]
```
Logo 来源: `GET /api/v1/settings/public` → `logo_id`，通过 `/media/id/{id}` 渲染。

### 4.2 AppFooter.vue (重写)

**当前状态:** 单行 flex 菜单 + Copyright。

**目标设计:** 4 列网格 + 底部 bar

```
[Logo + 简介 + 热线] [产品服务] [解决方案] [公司]
                     楼宇自控系统    商业综合体    关于我们
                     能源管理平台    产业园区      服务案例
                     综合安防系统    写字楼        新闻动态
                     智慧运维平台    公共建筑      商务合作
                     暖通优化系统                  联系我们

─────────────────────────────────────────────────
© 2026 金捷利科技有限公司 | All Rights Reserved.
隐私政策 · 法律声明 · 沪ICP备XXXXXXXX号
```

**API 数据映射:**
- 公司信息: `GET /api/v1/settings/public` → `company_name_zh`, `company_description_zh`, `hotline`, `icp_beian`
- 产品/方案/公司链接: `GET /api/v1/menus?location=footer`（菜单按分组组织）
- Logo: 同上通过 logo_id

### 4.3 AI Chat 浮动按钮 (重写 ChatFloatingButton.vue)

**当前状态:** 简单聊天面板，通过 `/chat` 路由访问。

**目标设计:**
- 固定右下角 "AI" 浮动按钮 (`bg-brand-600`, `rounded-full`, `shadow-xl shadow-brand-600/30`)
- 点击展开对话窗口 (glass card, `rounded-3xl`, 580px 高)
- 窗口 header: "金捷利 AI 智能管家" + "24/7 Energy & IoT Advisor"
- 预设快捷分类按钮（可选）
- 返回顶部按钮（上滑 300px 后出现）
- 保留现有 Chat API 对接

### 4.4 语言切换

保留现有的中/英 toggle（参考网站无此功能但项目需要）。放置在 Header 右侧。

---

## 5. Block 组件改造清单

### 5.1 BlockHero.vue (升级为轮播)

**当前:** 单一背景图 + glass 文字卡片。

**目标:** 多图轮播

```yaml
# Block content 扩展:
slides:
  - image_id: 123          # media id
    title_zh: "智慧运维..."
    title_en: "Smart Ops..."
    subtitle_zh: "智能研发..."
    subtitle_en: "..."
    buttons:
      - label_zh: "了解更多"
        label_en: "Learn More"
        link: "/products"
        type: "primary"    # primary | outline
  - image_id: 456
    ...
auto_play: true             # 自动播放间隔(ms)
auto_play_interval: 5000
```

功能:
- 左右箭头按钮 (半透明 glass, hover 显示)
- 渐变叠加层 (`bg-black/12` 到 `bg-gradient-to-t from-slate-950/20`)
- 文字内容居中 (title, subtitle, buttons)
- 全屏高度: `min-h-[660px] lg:h-[86vh] lg:max-h-[800px]`
- 过渡动画

### 5.2 BlockSolutionCards.vue (新增 Tab 组件)

**新增:** 参考网站方案页的核心组件。

```yaml
# Block content:
tabs:
  - key: "park"
    title_zh: "智慧产业园区"
    title_en: "Smart Industrial Park"
    image_id: 789
    features:
      - text_zh: "变配电系统集团化运维"
        text_en: "..."
      - text_zh: "照明集控与水冷动力"
      - ...
  - key: "medical"
    title_zh: "智慧医疗建筑"
    ...
  - key: "office"
    title_zh: "智慧写字楼"
    ...
  - key: "commercial"
    title_zh: "商业综合体"
    ...
```

功能:
- Tab 按钮栏 (active 蓝色下划线)
- 左侧文字 + 右侧图片布局
- 特性列表 (icon + text)
- Tab 切换动画 (fade/slide)
- 响应式: 移动端竖向堆叠

### 5.3 其他 Block 组件（样式对齐）

以下组件功能不变，仅更新 Tailwind 样式类以匹配 blue 主题:

| Block | 改动点 |
|---|---|
| BlockRichtext | prose 主题色 emerald → blue |
| BlockProductCards | 卡片阴影、品牌色、hover 效果 |
| BlockNewsList | 卡片布局、蓝色分类标签 |
| BlockFaq | 展开图标颜色、border |
| BlockContactForm | 输入框 focus ring blue、按钮样式 |
| BlockStatsCounter | 数字颜色、蓝色渐变 |
| BlockCtaBanner | 蓝色渐变背景、按钮 |
| BlockVideoBanner | 叠加层颜色 |
| BlockImageGallery | 圆角、阴影 |
| BlockLogoCloud | 灰度 → 颜色 hover |
| BlockDigitalTwin | 保持，品牌色调整 |
| BlockLiveDashboard | 保持，品牌色调整 |
| BlockTechIconGrid | 图标颜色、hover 效果 |

---

## 6. 新增页面

### 6.1 /cases (案例列表) — 新建

**路由:** `frontend/pages/cases/index.vue` + `frontend/pages/cases/[slug].vue`

**列表页:** 卡片网格，按分类筛选（商业/园区/办公/医疗）

**详情页:** 
- 封面图
- 标题 + 分类标签
- 关键数据 stats（数字高亮卡片）
- 正文（富文本）

**API:**
```
GET /api/v1/cases?page=1&size=12&category=park
GET /api/v1/cases/{slug}
```

### 6.2 /solutions (方案页) — 通过 Page API

通过 CMS 创建 `solutions` 页面，使用 `solution_cards` Block 渲染。

### 6.3 /cooperation (商务合作) — 通过 Page API

通过 CMS 创建 `cooperation` 页面，使用 richtext + contact_form Blocks。

### 6.4 /privacy, /terms — 通过 Page API

CMS 创建 content 类型页面即可。

---

## 7. 后端新增

### 7.1 Case 模型

**文件:** `backend/app/apps/cases/models.py`

```python
class Case(Base, TimestampMixin):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(300), nullable=False)
    name_en: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    cover_image_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    summary_zh: Mapped[str] = mapped_column(Text, default="")
    summary_en: Mapped[str] = mapped_column(Text, default="")
    content_zh: Mapped[str] = mapped_column(Text, default="")
    content_en: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="park")  # park|medical|office|commercial
    stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # [{label, value}]
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    cover_image: Mapped["Media | None"] = relationship("Media")
```

配套: schemas.py, service.py, router.py (public + admin CRUD)

### 7.2 Settings 扩展

在 seed.py 和 admin settings 中新增以下 public keys:

| Key | 默认值 | 用途 |
|---|---|---|
| `company_name_zh` | 金捷利科技有限公司 | 全局公司名 |
| `company_name_en` | GOLDGINNY Technology | 英文公司名 |
| `company_description_zh` | 专注建筑智能运维领域... | Footer 简介 |
| `hotline` | 400-888-0000 | 服务热线 |
| `contact_email` | aaqiuaa@gmail.com | 联系邮箱 |
| `icp_beian` | 沪ICP备XXXXXXXX号 | 备案号 |
| `logo_id` | (media id) | Logo 图片 |
| `og_image_id` | (media id) | 社交分享图 |

Settings 模型已支持 key-value，无需改表。Seed 时写入默认值。Admin settings 页面已有管理功能。

### 7.3 Alembic Migration

```bash
alembic revision --autogenerate -m "add_cases_table"
alembic upgrade head
```

---

## 8. Seed 数据更新

**文件:** `backend/seed.py`

更新预置数据以匹配金捷利品牌:

1. **Settings:** 写入公司名、热线、邮箱、ICP备案等
2. **Menu (header):** 首页、解决方案、产品服务、关于我们、商务合作、联系我们
3. **Menu (footer):** 产品服务组、解决方案组、公司组
4. **Pages:**
   - `home`: hero(轮播) + product_cards + solution_cards + news_list + cta_banner
   - `solutions`: solution_cards (4 tabs)
   - `about`: hero + richtext + stats_counter
   - `cooperation`: hero + richtext + contact_form
   - `privacy`: richtext
   - `terms`: richtext
5. **News:** 4 条示例新闻（获奖、项目、入选名录、战略合作）
6. **Products:** Edge-G100 智能边缘网关、环境传感器等
7. **Cases:** 3-4 条示例案例

---

## 9. 管理端新增页面

### 9.1 cases.vue (案例管理)

参考 `products.vue` 的 CRUD 模式:

- 列表: 表格 (名称、分类、发布时间、状态)
- 新建/编辑表单: 名称(中/英)、slug、分类、封面图、摘要、内容(富文本)、Stats JSON编辑、排序、发布状态

### 9.2 settings.vue (扩展)

在现有 settings 页面中新增金捷利相关 key 的编辑区域，或通过 seed 预置后由管理员自行修改。

---

## 10. 实施顺序

| 阶段 | 内容 | 依赖 |
|---|---|---|
| **Phase 1** | 后端 Case 模型 + Migration + API | 无 |
| **Phase 2** | Seed 数据更新 (Settings, Menus, Pages, News, Products, Cases) | Phase 1 |
| **Phase 3** | 全局 CSS/Tailwind 主题覆写 | 无 |
| **Phase 4** | AppHeader + AppFooter 重写 | Phase 2, 3 |
| **Phase 5** | BlockHero 升级为轮播 | Phase 3 |
| **Phase 6** | BlockSolutionCards 新增 + 其他 Block 样式对齐 | Phase 3 |
| **Phase 7** | /cases 前端页面 | Phase 1, 3 |
| **Phase 8** | AI Chat 浮动按钮改造 | Phase 3 |
| **Phase 9** | 管理端 cases.vue | Phase 1 |
| **Phase 10** | 整体验证 + 设计走查 | All |

---

## 11. 不做的事项

- ❌ 不改变后端 API 已有接口的返回格式（向前兼容）
- ❌ 不删除现有的 theme 管理功能（保留但不强制使用）
- ❌ 不引入新的前端依赖（纯 Tailwind 工具类实现）
- ❌ 不改变 nuxt.config.ts 中的路由规则（仅扩展现有结构）
- ❌ 不改变认证/授权逻辑
- ❌ 不改变现有的国际化策略 (zh/en, prefix_except_default)
