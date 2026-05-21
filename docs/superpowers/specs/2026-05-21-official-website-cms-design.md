# 智慧建筑运维科技公司官网 + CMS + 智能聊天体 设计规格

## 1. 项目概述

为智慧建筑运维科技公司构建一个官方网站，包含动态内容管理系统（CMS）和基于 RAG 的智能聊天助手。所有页面内容通过 API 获取，管理后台支持对页面区块、菜单、新闻、主题等进行完整管理。

### 1.1 核心目标

- 访客端：高性能、无加载闪烁的官方网站，支持中英文切换和动态主题切换
- 管理后台：完整 CMS，可视化管理页面内容、菜单、媒体、主题、LLM 配置
- 聊天智能体：基于网站内容和专业知识库的 RAG 问答系统

### 1.2 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12+, FastAPI, SQLAlchemy, Alembic |
| 数据库 | PostgreSQL (业务数据), Qdrant (向量), Redis (缓存/会话) |
| 对象存储 | MinIO (S3 兼容) |
| 访客前端 | Nuxt 3 (Vue3 + TypeScript), SSG/ISR 混合渲染 |
| 管理前端 | Vue3 + TypeScript + Vite, CSR |
| LLM | DeepSeek (默认), 支持 OpenAI/Anthropic/智谱切换 |
| 部署 | Docker Compose |
| 包管理 | uv (Python), pnpm (前端) |

---

## 2. 参考页面结构拆解

参考站 https://jjl-gw.netlify.app/ 分析如下：

```
1. Header/Nav
   ├── Logo + 品牌名
   └── 7 菜单项: 首页、关于我们、解决方案、服务案例、产品与服务、商务合作、联系我们

2. Hero 大图区
   ├── 主标题 + 副标题
   ├── 背景图/视频
   └── 2 个 CTA 按钮: 咨询诊断、了解详情

3. 新闻动态区 (3 条卡片, 含日期/标题/摘要/详情链接)

4. 产品与服务区 (3 卡片: 软件产品/硬件产品/专业服务)

5. 行业解决方案区 (3 卡片 + 探索更多入口)

6. 效果统计数据区 (4 个数字指标)

7. 商务咨询表单区 (公司名称/联系人/电话/留言)

8. Footer
   ├── 公司简介
   ├── 快速导航链接
   ├── 联系方式
   └── 版权/备案号
```

---

## 3. 架构设计

### 3.1 整体架构

```
                       ┌──────────────────────┐
                       │     CDN              │
                       │  静态 HTML + 资源      │
                       └──────┬───────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    ┌─────▼─────┐     ┌──────▼──────┐     ┌──────▼──────┐
    │  Nuxt 3   │     │  Admin      │     │  FastAPI    │
    │ SSG/ISR   │     │  Vue3 CSR   │     │  :8000      │
    │ :3000     │     │  :3001      │     │              │
    └───────────┘     └─────────────┘     └──────┬───────┘
                                                 │
         ┌───────────────────────────────────────┼──────────────────────┐
         │                                       │                      │
   ┌─────▼─────┐   ┌──────────┐     ┌───────────▼────┐     ┌───────────▼────┐
   │ PostgreSQL │   │  Redis   │     │    Qdrant      │     │     MinIO     │
   │ :5432     │   │  :6379   │     │    :6333        │     │     :9000     │
   └───────────┘   └──────────┘     └────────────────┘     └────────────────┘
```

### 3.2 后端模块

```
backend/apps/
├── core/           # JWT认证、权限、全局中间件
├── cms/            # 内容管理核心
│   ├── blocks/     # 页面区块 CRUD
│   ├── menus/      # 导航菜单管理
│   ├── pages/      # 页面定义
│   └── media/      # 图片/视频上传与管理
├── news/           # 新闻文章管理
├── inquiry/        # 商务咨询表单与留言
├── chat/           # 聊天智能体
│   ├── rag/        # 向量检索 + RAG 管线
│   ├── llm/        # LLM 提供商适配
│   └── sessions/   # 对话会话管理
├── theme/          # 主题管理
├── faq/            # FAQ 管理
└── settings/       # 系统配置
```

### 3.3 前端渲染策略

| 页面类型 | 渲染方式 | 说明 |
|---|---|---|
| 首页、关于、产品、解决方案 | SSG 静态生成 | HTML 直出，零白屏 |
| 新闻列表/详情 | ISR 增量再生 | 构建时生成，定时刷新 |
| 聊天助手页面 | CSR 按需 | 仅此页动态加载 |
| 管理后台 | CSR | 无需 SEO |

---

## 4. CMS 区块系统

### 4.1 核心模型

页面由多个区块（Block）按顺序组成。每个区块有固定的类型（type），内容和样式分别存储在 content 和 config 的 JSONB 字段中。

```
Page ─── 1:M ─── Block
  ├── name_zh, name_en, slug, is_published
  └── blocks: [Block]

Block
  ├── type: "hero" | "news_list" | "product_cards" | "solution_cards"
  │         | "stats_counter" | "contact_form" | "richtext" | "video_banner"
  │         | "image_gallery" | "logo_cloud" | "faq" | "cta_banner"
  │         | "digital_twin" | "live_dashboard" | "tech_icon_grid"
  ├── order: int
  ├── config: { background, padding, columns, animation, ... }
  └── content: { title_zh, title_en, ... }  ← 按 type 不同结构不同
```

### 4.2 区块类型

| type | 说明 | content 关键字段 |
|---|---|---|
| hero | 首屏大图/视频区 | title, subtitle, bg_image, bg_video, buttons[] |
| news_list | 新闻列表卡片 | title, count, show_date, show_image, category_filter |
| product_cards | 产品卡片网格 | cards[{icon, title, desc, image, link}] |
| solution_cards | 方案卡片 | cards[{title, desc, link}] |
| stats_counter | 数字统计 | items[{value, unit, label, suffix}] |
| contact_form | 咨询表单 | title, fields[], features[], submit_button |
| richtext | 富文本 | html_content |
| video_banner | 视频背景 | video_id, poster_id, overlay_opacity |
| image_gallery | 图片画廊 | images[{url, caption}] |
| logo_cloud | 合作伙伴logo | logos[{image, link}] |
| faq | FAQ 手风琴 | items[{question, answer}] |
| cta_banner | 行动号召 | title, button_text, button_link, bg_image |
| digital_twin | 3D 数字孪生 | model_url, hotspots[], auto_rotate |
| live_dashboard | 实时数据看板 | widgets[{type, label, data_source}] |
| tech_icon_grid | 科技图标网格 | icons[{icon, label, animation}] |

### 4.3 国际化

每个区块的 content JSONB 内同时存储所有语言版本（zh/en），前端根据当前语言切换显示。菜单、新闻等也支持双语。

### 4.4 主题系统

```
Theme
  ├── name, slug
  ├── variables: {                  ← CSS 自定义属性集合
  │     "--color-primary": "#1E40AF",
  │     "--color-accent": "#F59E0B",
  │     "--font-heading": "Noto Sans SC",
  │     "--font-body": "Inter",
  │     "--border-radius": "8px",
  │     "--card-shadow": "0 4px 20px rgba(0,0,0,0.08)",
  │     ...
  │   }
  ├── tech_effects: {               ← 科技特效配置
  │     hero_particles: "network" | "data_stream" | "grid" | null,
  │     scroll_animation: "reveal" | "parallax" | null,
  │     card_style: "glass" | "neon_edge" | "solid",
  │     cursor: "default" | "glow_ring",
  │     page_transition: "fade" | "none"
  │   }
  └── is_active
```

- 预设 3-5 套主题，管理后台可修改 CSS 变量并实时预览
- CSS 变量通过 `<html style="--color-primary: ...">` 注入
- 图标使用 Iconify，字符串配置，不硬编码

---

## 5. 媒体处理

### 5.1 图片

- 上传到 MinIO，存储原始文件 + 自动生成缩略图
- 访客端通过 Nginx/CDN 直接访问，不经 FastAPI
- 支持 WebP 自动转换（前端 <NuxtImg>）
- 管理后台支持裁剪参数配置

### 5.2 视频

- 存储到 MinIO，支持 HTTP Range 请求（206 Partial Content）
- 前端 <video> 直接播放
- 大文件使用 tus 协议分片上传
- 不做服务端转码，接受 MP4/WebM

### 5.3 3D 模型

- GLB/GLTF 格式
- Three.js GLTFLoader 按需加载
- 存储于 MinIO

---

## 6. 聊天智能体 (RAG)

### 6.1 内容索引管线

```
CMS内容变更 ──► 变更事件 ──► 分块器 ──► Embedding API ──► Qdrant upsert
删除内容   ──► 变更事件 ──► Qdrant delete_by_filter
```

### 6.2 分块策略

| 内容类型 | 策略 |
|---|---|
| news | 标题+日期+摘要→1 chunk, 正文每500字1 chunk, 重叠50字 |
| product/service | 每个产品卡片→1 chunk |
| page_block | 整个区块→1 chunk, 保留 type 作为 metadata |
| solution | 方案名+描述+场景→1 chunk |
| faq | Q&A配对, 一问一答→1 chunk (优先级最高) |
| richtext | 按段落分块, 每500字1 chunk |

### 6.3 Qdrant Collection

```python
{
    "name": "gweb_knowledge",
    "vectors": {"size": 1536, "distance": "Cosine"},
    "payload": {
        "content_id": int,       # 关联 CMS 内容 ID
        "content_type": str,     # news|product|page_block|faq|...
        "title": str,
        "text": str,             # 原文
        "language": "zh"|"en",
        "page_url": str,         # 来源引用
        "updated_at": datetime,
    }
}
```

### 6.4 对话引擎

```
用户提问
  └─► FAQ 精确匹配 (>0.90) ──► 直接返回 FAQ 答案 (不调用 LLM)
      └─► 未命中 ──► 向量检索 top-10
                    └─► 重排序 (LLM Rerank)
                    └─► 上下文窗口裁剪
                    └─► LLM 流式生成 (SSE)
                    └─► 返回: source引用 + token流 + 完整答案
```

### 6.5 LLM 配置

- 默认提供商: DeepSeek
- 支持切换: OpenAI, Anthropic, 智谱
- 配置项: provider, api_key, model, temperature, max_tokens
- Embedding 提供商可独立配置 (OpenAI text-embedding-3-small / 智谱 embedding-2)
- API Key 加密存储 (settings 表 is_encrypted=true)

### 6.6 对话功能

- SSE 流式响应 (token 级别)
- 多轮对话上下文 (最近 6 轮)
- 来源引用标注
- 用户反馈评分 (1-5)
- 管理后台查看对话统计和记录

---

## 7. 数据模型

### 7.1 核心表

```sql
themes (id, name, slug, variables JSONB, tech_effects JSONB, is_active, timestamps)
settings (key TEXT PK, value TEXT, is_encrypted BOOL, timestamps)
users (id, username, password_hash, role ENUM('admin','editor'), timestamps)
media (id, filename, original_name, mime_type, size, type ENUM('image','video','document'), path, thumbnail_path, alt_text_zh, alt_text_en, width, height, duration, timestamps)
pages (id, name_zh, name_en, slug UNIQUE, is_published, timestamps)
blocks (id, page_id FK, type VARCHAR(50), order INT, config JSONB, content JSONB, is_published, timestamps)
menus (id, parent_id FK(self), name_zh, name_en, link, icon VARCHAR(100), order INT, is_visible, location VARCHAR(20), timestamps)
news_articles (id, title_zh, title_en, summary_zh, summary_en, content_zh, content_en, cover_image_id FK, category, published_at, is_published, timestamps)
faqs (id, question_zh, question_en, answer_zh, answer_en, order, is_published, timestamps)
inquiries (id, company_name, contact_name, phone, message, is_read, timestamps)
chat_sessions (id, visitor_id, language VARCHAR(5), timestamps)
chat_messages (id, session_id FK, role ENUM('user','assistant'), content TEXT, sources JSONB, rating INT, timestamps)
```

### 7.2 关系

- Page 1:N Block (按 order 排序)
- Menu N:1 自身 (parent_id, 树形结构)
- NewsArticle N:1 Media (cover_image)
- ChatSession 1:N ChatMessage

---

## 8. API 设计

### 8.1 访客端

```
GET    /api/v1/pages/:slug          # 页面 + 所有区块
GET    /api/v1/news                 # 新闻列表 (?page=&size=&category=)
GET    /api/v1/news/:id             # 新闻详情
POST   /api/v1/inquiries            # 提交咨询
GET    /api/v1/menus?location=      # 获取菜单
GET    /api/v1/settings/public      # 公开设置
GET    /api/v1/themes/active        # 当前主题

POST   /api/v1/chat/sessions        # 创建会话
POST   /api/v1/chat/message         # 发送消息 (SSE 流式)
GET    /api/v1/chat/sessions/:id    # 会话历史
POST   /api/v1/chat/message/:id/rate  # 评价回复
```

### 8.2 管理端 (JWT 认证)

```
POST   /api/v1/admin/auth/login

# Pages & Blocks
GET|POST    /api/v1/admin/pages
GET|PUT|DEL /api/v1/admin/pages/:id
GET|POST    /api/v1/admin/pages/:id/blocks
PUT|DEL     /api/v1/admin/blocks/:id
PUT         /api/v1/admin/blocks/reorder

# Media
POST   /api/v1/admin/media/upload
GET    /api/v1/admin/media
DELETE /api/v1/admin/media/:id

# News / Menus / Themes / FAQs / Inquiries (标准 CRUD)

# Settings
GET|PUT   /api/v1/admin/settings
PUT       /api/v1/admin/settings/llm   # LLM 配置单独接口

# Chat 管理
GET       /api/v1/admin/chat/sessions
GET       /api/v1/admin/chat/sessions/:id/messages
GET       /api/v1/admin/chat/stats
POST      /api/v1/admin/chat/reindex
```

---

## 9. 前端项目结构

```
frontend/                          # Nuxt 3 访客端
├── nuxt.config.ts
├── pages/
│   ├── index.vue                  # 首页 (SSG)
│   ├── about.vue
│   ├── products.vue
│   ├── solutions.vue
│   ├── news/
│   │   ├── index.vue              # 新闻列表 (ISR)
│   │   └── [id].vue               # 新闻详情 (ISR)
│   └── chat.vue                   # 聊天助手 (CSR)
├── components/
│   ├── blocks/                    # 区块渲染组件
│   │   ├── BlockHero.vue
│   │   ├── BlockNewsList.vue
│   │   ├── BlockProductCards.vue
│   │   └── ... (每个 type 一个组件)
│   ├── layout/
│   │   ├── AppHeader.vue
│   │   ├── AppFooter.vue
│   │   └── ThemeProvider.vue
│   └── tech/                      # 科技特效组件
│       ├── ParticleNetwork.vue
│       ├── GlowCursor.vue
│       ├── ScrollReveal.vue
│       └── DigitalTwin.vue
├── composables/
│   ├── usePage.ts                 # 获取页面数据
│   ├── useTheme.ts                # 主题系统
│   └── useI18n.ts
├── assets/styles/
│   └── themes/                    # 预置主题 CSS 变量

admin/                             # Vue3 + Vite 管理后台
├── src/
│   ├── pages/
│   │   ├── dashboard/
│   │   ├── pages/                 # 页面管理 + 区块编辑器
│   │   ├── media/
│   │   ├── news/
│   │   ├── themes/
│   │   ├── settings/
│   │   └── chat/                  # 对话统计与记录
│   ├── components/
│   │   ├── block-editor/          # 区块编辑器
│   │   └── ...
│   └── ...
```

---

## 10. 部署架构 (Docker Compose)

```yaml
services:
  nginx:        # 入口 + 静态资源 + 反向代理
  backend:      # FastAPI
  frontend:     # Nuxt 3 (生产模式)
  admin:        # Vue3 Admin (静态文件)
  postgres:     # PostgreSQL 17
  redis:        # Redis 7
  qdrant:       # Qdrant
  minio:        # MinIO S3
```

---

## 11. 性能与 UX 约束

- SSG/ISR 确保首屏 HTML 直出，零白屏、无骨架屏
- 图片使用 WebP + 模糊占位图，消除布局抖动
- 字体预加载，避免 FOIT (Flash of Invisible Text)
- Three.js / GSAP 动态导入，不阻塞首屏
- 粒子系统仅在视口内运行，滚动出视口自动暂停
- 移动端自动降级特效 (3D→静态、粒子→简化、动画→reduced)
- Chat 页面独立 CSR，不影响其他页面加载
- 视口内链接自动预取

---

## 12. 开发原则

- TDD: 先写测试，再写实现
- 后端每个模块: models → schemas → service → router → tests
- 前端每个组件: props/types → template → logic → test
- 区块类型新增: 后端 content JSON Schema → 前端 BlockXxx.vue → 管理后台编辑器
- YAGNI: 不做过度抽象，3个相似实例出现后再提取公共逻辑
```

