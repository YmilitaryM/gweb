"""Seed CMS data: admin user, pages with blocks, menus, news, FAQs, settings."""
import asyncio, os

os.environ["GWEB_DATABASE_URL"] = "postgresql+asyncpg://gweb:gweb@127.0.0.1:5432/gweb"

from app.core.database import async_session, engine
from app.shared.models import Base
from app.apps.auth.service import create_user, authenticate
from app.apps.cms.service_page import create_page, list_pages, update_page
from app.apps.cms.service_block import create_block
from app.apps.cms.service_menu import create_menu_item
from app.apps.cms.models import Menu
from app.apps.news.service import create_article
from app.apps.faq.service import create_faq
from app.apps.settings.service import set_setting
from sqlalchemy import select

API = "http://localhost:8000/api/v1"

LINK_TO_SLUG = {
    "/": "home",
    "/products": "products",
    "/solutions": "solutions",
    "/about": "about",
    "/news": "news",
    "/contact": "contact",
    "/faq": "faq",
}


async def cleanup():
    """Drop and recreate all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables recreated.")


async def seed():
    await cleanup()
    # 1. Admin user
    print("Creating admin user...")
    try:
        user = await create_user("admin", "admin123", "admin")
        print(f"  User: admin (id={user.id})")
    except Exception:
        print("  User admin already exists")

    token = await authenticate("admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Settings
    print("Creating settings...")
    await set_setting("site_name_zh", "智慧建筑运维平台")
    await set_setting("site_name_en", "Smart Building Ops")
    await set_setting("site_description_zh", "领先的智慧建筑运维解决方案提供商")
    await set_setting("site_description_en", "Leading smart building operations solutions")
    await set_setting("contact_email", "info@gweb.example.com")
    await set_setting("contact_phone", "+86 400-888-8888")
    print("  Done")

    # 3. Pages
    slug_to_id = {}

    pages = [
        ("home", "首页", "Home"),
        ("about", "关于我们", "About Us"),
        ("products", "产品中心", "Products"),
        ("solutions", "解决方案", "Solutions"),
        ("contact", "联系我们", "Contact Us"),
    ]

    for slug, zh, en in pages:
        # Determine page type
        page_type = "content"
        if slug == "products":
            page_type = "products"
        elif slug == "contact":
            page_type = "contact"

        print(f"Creating page: {slug} (type={page_type})...")
        pg = await create_page(name_zh=zh, name_en=en, slug=slug, type=page_type, is_published=True)
        page_id = pg.id
        slug_to_id[slug] = page_id

        if slug == "home":
            # Hero block
            await create_block(page_id, "hero", config={}, content={
                "title_zh": "智慧建筑 · 智领未来",
                "title_en": "Smart Buildings, Smarter Future",
                "subtitle_zh": "以数字孪生与AI技术为核心，打造高效、节能、安全的建筑运维新范式",
                "subtitle_en": "Powered by digital twin and AI, creating a new paradigm for building operations",
                "buttons": [
                    {"label_zh": "了解产品", "label_en": "Products", "link": "/products", "variant": "solid"},
                    {"label_zh": "联系我们", "label_en": "Contact", "link": "/contact", "variant": "outline"},
                ],
            })
            # Stats counter
            await create_block(page_id, "stats_counter", config={}, content={
                "title_zh": "平台数据",
                "title_en": "Platform Stats",
                "items": [
                    {"value": "500+", "label_zh": "服务建筑", "label_en": "Buildings"},
                    {"value": "50+", "label_zh": "覆盖城市", "label_en": "Cities"},
                    {"value": "99.9%", "label_zh": "系统可用率", "label_en": "Uptime"},
                    {"value": "30%", "label_zh": "平均节能", "label_en": "Energy Saved"},
                ],
            })
            # Product cards
            await create_block(page_id, "product_cards", config={}, content={
                "title_zh": "核心产品",
                "title_en": "Core Products",
                "cards": [
                    {"title_zh": "数字孪生平台", "title_en": "Digital Twin Platform", "desc_zh": "1:1 精准还原建筑数字模型，实时映射运行状态", "desc_en": "1:1 accurate building digital model with real-time status mapping", "link": "/products"},
                    {"title_zh": "能耗管理系统", "title_en": "Energy Management", "desc_zh": "AI驱动的能耗分析与优化，降低运营成本", "desc_en": "AI-driven energy analysis and optimization to reduce costs", "link": "/products"},
                    {"title_zh": "智能巡检系统", "title_en": "Smart Inspection", "desc_zh": "自动化巡检任务，AI缺陷识别，提升运维效率", "desc_en": "Automated inspection tasks with AI defect detection", "link": "/products"},
                ],
            })

        elif slug == "about":
            await create_block(page_id, "hero", config={}, content={
                "title_zh": "关于我们",
                "title_en": "About Us",
                "subtitle_zh": "致力于成为全球领先的智慧建筑运维服务商",
                "subtitle_en": "Committed to becoming a global leader in smart building operations",
                "buttons": [],
            })
            await create_block(page_id, "richtext", config={}, content={
                "html_content_zh": '<p class="text-lg leading-relaxed">我们是一家专注于智慧建筑运维领域的科技公司，核心团队来自清华大学、阿里巴巴、华为等顶尖机构。通过自主研发的数字孪生、AI能耗优化、智能巡检等技术，已为全国500+栋建筑提供智慧运维解决方案。</p>',
                "html_content_en": '<p class="text-lg leading-relaxed">We are a technology company focused on smart building operations. Our core team comes from top institutions. With self-developed digital twin, AI energy optimization, and smart inspection technologies, we have provided solutions for 500+ buildings nationwide.</p>',
            })
            await create_block(page_id, "logo_cloud", config={}, content={
                "title_zh": "合作伙伴",
                "title_en": "Partners",
                "logos": [
                    {"url": "https://placehold.co/200x60/eee/999?text=Partner+A", "name": "Partner A"},
                    {"url": "https://placehold.co/200x60/eee/999?text=Partner+B", "name": "Partner B"},
                    {"url": "https://placehold.co/200x60/eee/999?text=Partner+C", "name": "Partner C"},
                    {"url": "https://placehold.co/200x60/eee/999?text=Partner+D", "name": "Partner D"},
                ],
            })

        elif slug == "products":
            await create_block(page_id, "hero", config={}, content={
                "title_zh": "产品中心",
                "title_en": "Products",
                "subtitle_zh": "全栈智慧建筑运维产品矩阵",
                "subtitle_en": "Full-stack smart building operations product matrix",
                "buttons": [],
            })
            await create_block(page_id, "product_cards", config={}, content={
                "title_zh": "全部产品",
                "title_en": "All Products",
                "cards": [
                    {"title_zh": "BIM数字孪生", "title_en": "BIM Digital Twin", "desc_zh": "基于BIM模型构建建筑数字孪生体，实时展示设备运行状态、环境参数和能耗数据", "desc_en": "Build digital twins from BIM models with real-time equipment status", "link": "/contact"},
                    {"title_zh": "AI能耗优化", "title_en": "AI Energy Optimization", "desc_zh": "基于深度学习的冷热负荷预测与策略优化，实现空调节能20-40%", "desc_en": "Deep learning based HVAC load prediction for 20-40% energy savings", "link": "/contact"},
                    {"title_zh": "智能运维平台", "title_en": "Smart Ops Platform", "desc_zh": "设备全生命周期管理、故障预测、自动化工单派发", "desc_en": "Full lifecycle management, fault prediction, automated work orders", "link": "/contact"},
                    {"title_zh": "AI巡检助手", "title_en": "AI Inspection Assistant", "desc_zh": "视觉AI自动识别设备缺陷、管道泄漏、仪表读数", "desc_en": "Visual AI for defect detection, leak detection, meter reading", "link": "/contact"},
                    {"title_zh": "室内环境监测", "title_en": "Indoor Environment Monitor", "desc_zh": "实时监测温湿度、CO2、PM2.5等环境指标，联动暖通系统自动调节", "desc_en": "Real-time monitoring of temp, humidity, CO2, PM2.5 with HVAC integration", "link": "/contact"},
                    {"title_zh": "能源管理驾驶舱", "title_en": "Energy Dashboard", "desc_zh": "多维度能耗数据可视化，碳排核算，对标分析", "desc_en": "Multi-dimensional energy visualization, carbon accounting, benchmarking", "link": "/contact"},
                ],
            })

        elif slug == "solutions":
            await create_block(page_id, "hero", config={}, content={
                "title_zh": "解决方案",
                "title_en": "Solutions",
                "subtitle_zh": "针对不同场景的智慧建筑解决方案",
                "subtitle_en": "Smart building solutions for different scenarios",
                "buttons": [],
            })
            await create_block(page_id, "solution_cards", config={}, content={
                "title_zh": "行业解决方案",
                "title_en": "Industry Solutions",
                "description_zh": "覆盖商业办公、数据中心、医院、园区等多种场景",
                "description_en": "Covering commercial offices, data centers, hospitals, and industrial parks",
                "cards": [
                    {"title_zh": "商业办公楼宇", "title_en": "Commercial Office", "desc_zh": "中央空调优化 + 智能照明 + 室内环境监测，综合节能30%以上", "desc_en": "HVAC optimization + smart lighting + environment monitoring, 30%+ energy savings", "link": "/contact"},
                    {"title_zh": "数据中心", "title_en": "Data Center", "desc_zh": "精密空调群控 + PUE优化 + 热点识别，PUE从1.6降至1.2以下", "desc_en": "Precision AC group control + PUE optimization, reducing PUE from 1.6 to under 1.2", "link": "/contact"},
                    {"title_zh": "医院建筑", "title_en": "Hospital", "desc_zh": "洁净空调管理 + 医疗环境监控 + 能效合规，满足GB/T 51153标准", "desc_en": "Clean AC management + medical environment monitoring + energy compliance", "link": "/contact"},
                    {"title_zh": "产业园区", "title_en": "Industrial Park", "desc_zh": "多楼宇集中管控 + 能源调度 + 碳排管理，降低园区整体运营成本", "desc_en": "Multi-building centralized control + energy dispatch + carbon management", "link": "/contact"},
                ],
            })

        elif slug == "contact":
            await create_block(page_id, "contact_form", config={}, content={
                "title_zh": "联系我们",
                "title_en": "Contact Us",
                "fields": ["company_name", "contact_name", "phone", "message"],
                "submit_button_zh": "提交咨询",
                "submit_button_en": "Submit Inquiry",
            })

        print(f"  {slug} done (id={page_id})")

    # Create news and faq pages
    print("Creating news page...")
    news_pg = await create_page(name_zh="新闻中心", name_en="News", slug="news", type="news", is_published=True)
    slug_to_id["news"] = news_pg.id
    print(f"  news done (id={news_pg.id})")

    print("Creating faq page...")
    faq_pg = await create_page(name_zh="常见问题", name_en="FAQ", slug="faq", type="faq", is_published=True)
    slug_to_id["faq"] = faq_pg.id
    print(f"  faq done (id={faq_pg.id})")

    # 4. Menu (with page_id resolved from slug)
    print("Creating menus...")
    header_items = [
        (None, "首页", "Home", "/", "header"),
        (None, "产品中心", "Products", "/products", "header"),
        (None, "解决方案", "Solutions", "/solutions", "header"),
        (None, "关于我们", "About Us", "/about", "header"),
        (None, "新闻中心", "News", "/news", "header"),
        (None, "联系我们", "Contact", "/contact", "header"),
    ]
    for parent_id, zh, en, link, loc in header_items:
        slug = LINK_TO_SLUG.get(link)
        if slug is None:
            raise ValueError(f"No slug mapping for menu link '{link}' — add it to LINK_TO_SLUG")
        pid = slug_to_id[slug]
        m = await create_menu_item(location=loc, name_zh=zh, name_en=en, link=link, page_id=pid, parent_id=parent_id, order=0)
        print(f"  {zh} -> id={m.id} page_id={pid}")

    footer_items = [
        (None, "关于我们", "About", "/about", "footer"),
        (None, "产品中心", "Products", "/products", "footer"),
        (None, "新闻中心", "News", "/news", "footer"),
        (None, "常见问题", "FAQ", "/faq", "footer"),
    ]
    for parent_id, zh, en, link, loc in footer_items:
        slug = LINK_TO_SLUG.get(link)
        if slug is None:
            raise ValueError(f"No slug mapping for menu link '{link}' — add it to LINK_TO_SLUG")
        pid = slug_to_id[slug]
        m = await create_menu_item(location=loc, name_zh=zh, name_en=en, link=link, page_id=pid, parent_id=parent_id, order=0)
        print(f"  {zh} -> id={m.id} page_id={pid}")

    # 5. News
    print("Creating news articles...")
    articles = [
        ("公司发布数字孪生平台v3.0版本", "Digital Twin Platform v3.0 Released",
         "新一代数字孪生平台正式发布，支持BIM模型自动轻量化与实时数据映射",
         "New generation digital twin platform officially released with auto BIM lightweight and real-time data mapping",
         "<p>2026年5月18日，公司正式发布数字孪生平台v3.0版本...</p>",
         "<p>May 18, 2026 - Digital Twin Platform v3.0 officially released...</p>",
         "product_release"),
        ("公司与某省建筑设计院签署战略合作", "Strategic Partnership with Provincial Design Institute",
         "双方将在智慧建筑设计与运维领域开展深度合作",
         "Both parties will cooperate deeply in smart building design and operations",
         "<p>近日，公司与某省建筑设计院签署战略合作协议...</p>",
         "<p>Recently signed a strategic cooperation agreement...</p>",
         "company_news"),
        ("AI能耗优化系统通过国家节能认证", "AI Energy System Passes National Certification",
         "我司AI能耗优化系统通过CQC节能认证，实测节能率达34.7%",
         "Our AI energy optimization system passed CQC certification with 34.7% measured savings",
         "<p>经中国质量认证中心检测，我司AI能耗优化系统...</p>",
         "<p>Certified by China Quality Certification Centre...</p>",
         "company_news"),
        ("2026智慧建筑行业峰会即将举办", "2026 Smart Building Summit Coming Soon",
         "公司受邀作为主论坛嘉宾分享数字孪生技术最新实践",
         "Company invited as keynote speaker to share latest digital twin practices",
         "<p>2026智慧建筑行业峰会将于6月15日在上海举办...</p>",
         "<p>The 2026 Smart Building Summit will be held on June 15 in Shanghai...</p>",
         "industry_news"),
    ]
    for t_zh, t_en, s_zh, s_en, c_zh, c_en, cat in articles:
        a = await create_article(
            title_zh=t_zh, title_en=t_en,
            summary_zh=s_zh, summary_en=s_en,
            content_zh=c_zh, content_en=c_en,
            category=cat, is_published=True,
        )
        print(f"  {t_zh[:30]}... -> id={a.id}")

    # 6. FAQs
    print("Creating FAQs...")
    faqs = [
        ("平台支持哪些建筑管理系统（BMS）对接？", "Which BMS systems are supported?",
         "我们支持主流BMS系统的标准协议对接，包括BACnet、Modbus、OPC UA等，同时提供REST API和数据网关用于私有协议适配。",
         "We support standard protocols including BACnet, Modbus, OPC UA. REST API and data gateway available for proprietary protocols."),
        ("数字孪生模型的数据更新频率是多少？", "What is the data update frequency?",
         "默认刷新频率为5秒，支持按需配置为1秒至60秒。关键告警数据采用推送模式，延迟小于1秒。",
         "Default refresh is 5 seconds, configurable from 1 to 60 seconds. Critical alerts use push mode with <1s latency."),
        ("AI能耗优化系统需要多久才能看到节能效果？", "How long to see energy savings?",
         "系统部署后约1-2周完成冷热负荷模型训练，之后自动进入优化模式。通常在1个月内可看到明显节能效果。",
         "HVAC load model training takes 1-2 weeks after deployment, then auto optimization begins. Visible savings typically within 1 month."),
        ("平台部署方式有哪些？", "What deployment options are available?",
         "支持私有化部署（本地服务器）、混合云部署和SaaS订阅三种模式，可根据企业IT策略灵活选择。",
         "We offer on-premise, hybrid cloud, and SaaS subscription deployment models."),
        ("如何确保建筑数据安全？", "How is building data security ensured?",
         "我们已通过ISO 27001信息安全管理体系认证，支持数据脱敏、传输加密、RBAC权限控制和操作审计。",
         "ISO 27001 certified. Supports data anonymization, transport encryption, RBAC access control, and audit logging."),
    ]
    for q_zh, q_en, a_zh, a_en in faqs:
        f = await create_faq(question_zh=q_zh, question_en=q_en, answer_zh=a_zh, answer_en=a_en, is_published=True)
        print(f"  {q_zh[:30]}... -> id={f.id}")

    print("\nSeed complete!")
    print(f"Login: admin / admin123")
    print(f"API Base: {API}")
    print(f"Admin token: {token[:20]}...")


async def migrate_pages_and_menus():
    """Migrate existing (non-empty) database:
    1. Set type="contact" on contact page and type="products" on products page.
    2. Create news and faq pages if they don't exist.
    3. Resolve all menu link values to page_id (for menus with link but no page_id).
    """
    print("Starting migration (pages + menus)...")

    # 1. Get all existing pages and build slug->id map
    pages = await list_pages()
    slug_to_id = {p.slug: p.id for p in pages}
    print(f"  Found {len(pages)} existing pages")

    # 2. Update types for known pages
    for slug, expected_type in [("contact", "contact"), ("products", "products")]:
        page = next((p for p in pages if p.slug == slug), None)
        if page and page.type != expected_type:
            await update_page(page.id, type=expected_type)
            print(f"  Updated '{slug}' page (id={page.id}) type to '{expected_type}'")
        elif page:
            print(f"  Page '{slug}' already has type='{expected_type}'")
        else:
            print(f"  Page '{slug}' not found, skipping type update")

    # 3. Create news and faq pages if they don't exist
    for slug, zh, en, ptype in [
        ("news", "新闻中心", "News", "news"),
        ("faq", "常见问题", "FAQ", "faq"),
    ]:
        if slug not in slug_to_id:
            pg = await create_page(name_zh=zh, name_en=en, slug=slug, type=ptype, is_published=True)
            slug_to_id[slug] = pg.id
            print(f"  Created '{slug}' page (id={pg.id})")
        else:
            print(f"  Page '{slug}' already exists (id={slug_to_id[slug]})")

    # 4. Resolve menu link -> page_id
    async with async_session() as db:
        result = await db.execute(
            select(Menu).where(Menu.link != "", Menu.page_id == None)
        )
        menus_to_update = result.scalars().all()

        updated = 0
        for menu in menus_to_update:
            slug = LINK_TO_SLUG.get(menu.link)
            if slug and slug in slug_to_id:
                menu.page_id = slug_to_id[slug]
                updated += 1

        if updated > 0:
            await db.commit()
            print(f"  Linked {updated} menu items to pages")
            for menu in menus_to_update:
                slug = LINK_TO_SLUG.get(menu.link)
                if slug and slug in slug_to_id:
                    print(f"    Menu '{menu.name_zh}' ({menu.link}) -> page_id={slug_to_id[slug]}")
        else:
            print("  No unlinked menus found (all already have page_id)")

    print("Migration complete!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        asyncio.run(migrate_pages_and_menus())
    else:
        asyncio.run(seed())
