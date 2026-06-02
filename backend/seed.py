"""Seed CMS data: Jinjieli (金捷利) brand data.

Usage:
    python seed.py           # idempotent seed (checks existence before insert)
    python seed.py clean     # drop all tables, recreate, then seed
    python seed.py migrate   # migrate existing pages/menus (legacy)
"""
import asyncio, os

os.environ["GWEB_DATABASE_URL"] = "postgresql+asyncpg://gweb:gweb@127.0.0.1:5432/gweb"

from app.core.database import async_session, engine
from app.shared.models import Base
from app.apps.auth.service import create_user, authenticate
from app.apps.cms.service_page import create_page, list_pages, update_page
from app.apps.cms.service_block import create_block
from app.apps.cms.service_menu import create_menu_item
from app.apps.cms.models import Menu, Page, Block
from app.apps.news.models import NewsArticle
from app.apps.news.service import create_article
from app.apps.settings.service import set_setting
from app.apps.products.service import create_category as create_product_category, create_product
from app.apps.products.models import ProductCategory, Product
from app.apps.cases.service import create_case
from app.apps.cases.models import Case
from sqlalchemy import select, func

API = "http://localhost:8000/api/v1"

LINK_TO_SLUG = {
    "/": "home",
    "/products": "products",
    "/solutions": "solutions",
    "/about": "about",
    "/cooperation": "cooperation",
    "/contact": "contact",
    "/news": "news",
    "/cases": "cases",
    "/privacy": "privacy",
    "/terms": "terms",
}


async def cleanup():
    """Drop and recreate all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tables recreated.")


async def seed():
    """Idempotent seed: populate Settings, Pages, Menus, News, Products, Cases.

    Checks existence before inserting each section, so it is safe to run
    multiple times against an existing database.
    """

    # ---- 0. Admin user --------------------------------------------------
    print("Creating admin user...")
    try:
        user = await create_user("admin", "admin123", "admin")
        print(f"  User: admin (id={user.id})")
    except Exception:
        print("  User admin already exists")

    # ---- 1. Settings (upsert via set_setting) ---------------------------
    print("Creating settings...")
    jinjieli_settings = {
        "company_name_zh": "金捷利科技有限公司",
        "company_name_en": "GOLDGINNY Technology Co., Ltd.",
        "company_description_zh": (
            "专注建筑智能运维领域，以技术赋能建筑全生命周期高效管理，"
            "致力于成为中国领先的智慧建筑服务商。"
        ),
        "company_description_en": (
            "Focused on intelligent building operations, empowering full-lifecycle "
            "building management with technology, committed to becoming China's "
            "leading smart building service provider."
        ),
        "hotline": "400-888-0000",
        "contact_email": "aaqiuaa@gmail.com",
        "icp_beian": "沪ICP备XXXXXXXX号",
    }
    for k, v in jinjieli_settings.items():
        await set_setting(k, v)
    print("  Done")

    # ---- 2. Pages + Blocks ----------------------------------------------
    async with async_session() as db:
        result = await db.execute(
            select(func.count(Page.id)).where(Page.slug == "home")
        )
        home_exists = (result.scalar() or 0) > 0

    if home_exists:
        print("Pages already exist, loading for menu linking...")
        existing_pages = await list_pages()
        slug_to_id = {p.slug: p.id for p in existing_pages}
    else:
        print("Creating pages...")
        slug_to_id = {}

        # 2a. Home --------------------------------------------------------
        slug = "home"
        pg = await create_page(
            name_zh="首页", name_en="Home", slug=slug,
            type="page", sort_order=1, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        # Hero block (3 slides)
        await create_block(pg.id, "hero", config={}, content={
            "slides": [
                {
                    "title_zh": "智慧建筑 · 智领未来",
                    "title_en": "Smart Buildings, Smarter Future",
                    "subtitle_zh": "以AI与物联网技术为核心，打造高效、节能、安全的建筑运维新范式",
                    "subtitle_en": "Powered by AI and IoT, creating a new paradigm for efficient, energy-saving, and safe building operations",
                    "image": "",
                    "buttons": [
                        {"label_zh": "了解产品", "label_en": "Products", "link": "/products", "variant": "primary"},
                        {"label_zh": "联系我们", "label_en": "Contact", "link": "/contact", "variant": "outline"},
                    ],
                },
                {
                    "title_zh": "全生命周期智慧运维",
                    "title_en": "Full-Lifecycle Smart Operations",
                    "subtitle_zh": "从设计、建造到运营，覆盖建筑全生命周期的数字化管理方案",
                    "subtitle_en": "From design and construction to operations, digital management across the full building lifecycle",
                    "image": "",
                    "buttons": [
                        {"label_zh": "查看方案", "label_en": "Solutions", "link": "/solutions", "variant": "primary"},
                    ],
                },
                {
                    "title_zh": "数据驱动 · 节能降碳",
                    "title_en": "Data-Driven Energy Efficiency",
                    "subtitle_zh": "AI冷热源自适应算法，平均节能率超28%，助力双碳目标",
                    "subtitle_en": "AI-powered HVAC adaptive algorithms deliver 28%+ energy savings for carbon goals",
                    "image": "",
                    "buttons": [
                        {"label_zh": "了解更多", "label_en": "Learn More", "link": "/about", "variant": "primary"},
                        {"label_zh": "商务合作", "label_en": "Cooperation", "link": "/cooperation", "variant": "outline"},
                    ],
                },
            ],
        })

        # Product cards
        await create_block(pg.id, "product_cards", config={}, content={
            "title_zh": "核心产品",
            "title_en": "Core Products",
            "cards": [
                {
                    "title_zh": "Edge-G100 智能边缘网关",
                    "title_en": "Edge-G100 Smart Edge Gateway",
                    "desc_zh": "专为中大型智慧建筑系统集成设计的物理通信中枢，支持多协议接入与边缘计算",
                    "desc_en": "Physical communication hub designed for medium-to-large smart building system integration, supporting multi-protocol access and edge computing",
                    "link": "/products",
                },
                {
                    "title_zh": "IoT 综合环境传感器",
                    "title_en": "IoT Environmental Sensor",
                    "desc_zh": "高精度温湿度、CO2、PM2.5多合一传感器，实时监测室内环境质量",
                    "desc_en": "High-precision all-in-one sensor for temperature, humidity, CO2, and PM2.5 monitoring",
                    "link": "/products",
                },
                {
                    "title_zh": "多联机集控器",
                    "title_en": "Multi-Unit Central Controller",
                    "desc_zh": "支持Bacnet/Modbus标准协议，集成本地微推理算法，实现空调系统智能调控",
                    "desc_en": "Supports Bacnet/Modbus protocols with local micro-inference algorithms for intelligent HVAC control",
                    "link": "/products",
                },
            ],
        })

        # Solution cards (4 tabs)
        await create_block(pg.id, "solution_cards", config={}, content={
            "title_zh": "行业解决方案",
            "title_en": "Industry Solutions",
            "description_zh": "覆盖商业综合体、产业园区、写字楼、公共建筑等多种场景",
            "description_en": "Covering commercial complexes, industrial parks, office buildings, and public facilities",
            "tabs": [
                {
                    "key": "commercial",
                    "label_zh": "商业综合体",
                    "label_en": "Commercial",
                    "title_zh": "商业综合体智慧运维方案",
                    "title_en": "Smart Operations for Commercial Complexes",
                    "desc_zh": "中央空调智能调优 + 智能照明 + 室内环境监测 + 综合安防，实现一站式智慧管理，综合节能率达28.5%。",
                    "desc_en": "Central HVAC optimization + smart lighting + indoor environment monitoring + integrated security for one-stop smart management with 28.5% energy savings.",
                    "features": ["冷热源自适应调控", "分区分时照明策略", "室内环境实时监测", "设备预测性维护"],
                    "link": "/solutions?tab=commercial",
                },
                {
                    "key": "park",
                    "label_zh": "产业园区",
                    "label_en": "Industrial Park",
                    "title_zh": "产业园区集中管控方案",
                    "title_en": "Centralized Management for Industrial Parks",
                    "desc_zh": "多楼宇集中管控 + 能源调度 + 碳排管理 + 智慧安防，降低园区整体运营成本30%以上。",
                    "desc_en": "Multi-building centralized control + energy dispatch + carbon management + smart security, reducing overall park operation costs by 30%+.",
                    "features": ["多楼宇统一监控", "能源梯级调度", "碳排放实时核算", "园区级安防联动"],
                    "link": "/solutions?tab=park",
                },
                {
                    "key": "office",
                    "label_zh": "写字楼",
                    "label_en": "Office",
                    "title_zh": "5A写字楼智能化方案",
                    "title_en": "Smart Solutions for 5A Office Buildings",
                    "desc_zh": "暖通空调优化 + 智能照明 + 室内环境品质管理 + 智慧停车，提升租户满意度与资产价值。",
                    "desc_en": "HVAC optimization + smart lighting + indoor environmental quality management + smart parking, enhancing tenant satisfaction and asset value.",
                    "features": ["新风按需供给", "办公环境舒适度管理", "能源分项计量", "智慧停车引导"],
                    "link": "/solutions?tab=office",
                },
                {
                    "key": "hospital",
                    "label_zh": "公共建筑",
                    "label_en": "Public",
                    "title_zh": "公共建筑智慧运维方案",
                    "title_en": "Smart Operations for Public Buildings",
                    "desc_zh": "洁净空调管理 + 医疗级环境监控 + 能效合规管理，满足GB/T 51153等国家标准。",
                    "desc_en": "Clean air management + medical-grade environment monitoring + energy compliance, meeting GB/T 51153 and other national standards.",
                    "features": ["洁净区域环境管控", "医疗设备能耗监测", "环境参数合规记录", "应急联动响应"],
                    "link": "/solutions?tab=hospital",
                },
            ],
        })

        # News list
        await create_block(pg.id, "news_list", config={}, content={
            "title_zh": "新闻动态",
            "title_en": "News & Updates",
        })

        # CTA banner
        await create_block(pg.id, "cta_banner", config={}, content={
            "title_zh": "携手金捷利，共创智慧建筑未来",
            "title_en": "Partner with GOLDGINNY for a Smarter Building Future",
            "subtitle_zh": "立即联系我们，获取专属智慧建筑解决方案",
            "subtitle_en": "Contact us now for a tailored smart building solution",
            "button_zh": "立即咨询",
            "button_en": "Get Started",
            "link": "/cooperation",
        })

        # 2b. Solutions ---------------------------------------------------
        slug = "solutions"
        pg = await create_page(
            name_zh="解决方案", name_en="Solutions", slug=slug,
            type="page", sort_order=2, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={}, content={
            "slides": [{
                "title_zh": "解决方案",
                "title_en": "Solutions",
                "subtitle_zh": "针对不同建筑场景的智慧化解决方案，助力建筑运营提质增效",
                "subtitle_en": "Smart solutions tailored for different building scenarios to improve operational efficiency",
                "image": "",
                "buttons": [],
            }],
        })

        await create_block(pg.id, "solution_cards", config={}, content={
            "title_zh": "行业解决方案",
            "title_en": "Industry Solutions",
            "description_zh": "覆盖商业综合体、产业园区、写字楼、公共建筑等多种场景",
            "description_en": "Covering commercial complexes, industrial parks, office buildings, and public facilities",
            "tabs": [
                {
                    "key": "commercial",
                    "label_zh": "商业综合体",
                    "label_en": "Commercial",
                    "title_zh": "商业综合体智慧运维方案",
                    "title_en": "Smart Operations for Commercial Complexes",
                    "desc_zh": "针对商业综合体能耗高、设备多、人流大的特点，提供涵盖暖通空调优化、智能照明、室内环境监测、综合安防的一站式解决方案。通过金捷利自研的冷热源自适应算法，CBD核心区项目实测综合节能率达28.5%。",
                    "desc_en": "A one-stop solution covering HVAC optimization, smart lighting, indoor environment monitoring, and integrated security for commercial complexes. Our self-developed adaptive algorithm achieved 28.5% energy savings in a CBD core-area project.",
                    "features": ["冷热源自适应调控", "分区分时照明策略", "室内环境实时监测", "设备预测性维护", "综合安防联动"],
                    "link": "/cooperation",
                },
                {
                    "key": "park",
                    "label_zh": "产业园区",
                    "label_en": "Industrial Park",
                    "title_zh": "产业园区集中管控方案",
                    "title_en": "Centralized Management for Industrial Parks",
                    "desc_zh": "面向大型产业园区多楼宇、多业态的管理需求，通过统一管控平台实现能源调度、碳排管理和智慧安防，降低园区整体运营成本30%以上。",
                    "desc_en": "For large industrial parks with multiple buildings and business types, our unified platform enables energy dispatch, carbon management, and smart security, reducing overall operational costs by 30%+.",
                    "features": ["多楼宇统一监控", "能源梯级调度", "碳排放实时核算", "园区级安防联动", "智能运维工单"],
                    "link": "/cooperation",
                },
                {
                    "key": "office",
                    "label_zh": "写字楼",
                    "label_en": "Office",
                    "title_zh": "5A写字楼智能化方案",
                    "title_en": "Smart Solutions for 5A Office Buildings",
                    "desc_zh": "为5A级写字楼提供暖通空调优化、智能照明、室内环境品质管理和智慧停车等系统，提升租户满意度与物业资产价值。",
                    "desc_en": "HVAC optimization, smart lighting, indoor environmental quality management, and smart parking for 5A office buildings, enhancing tenant satisfaction and property asset value.",
                    "features": ["新风按需供给", "办公环境舒适度管理", "能源分项计量", "智慧停车引导", "租户能耗账单"],
                    "link": "/cooperation",
                },
                {
                    "key": "hospital",
                    "label_zh": "公共建筑",
                    "label_en": "Public",
                    "title_zh": "公共建筑智慧运维方案",
                    "title_en": "Smart Operations for Public Buildings",
                    "desc_zh": "面向医院、政府办公楼等公共建筑，提供洁净空调管理、医疗级环境监控和能效合规管理，满足GB/T 51153等国家标准要求。",
                    "desc_en": "Clean air management, medical-grade environment monitoring, and energy compliance for hospitals and government buildings, meeting GB/T 51153 standards.",
                    "features": ["洁净区域环境管控", "医疗设备能耗监测", "环境参数合规记录", "应急联动响应", "后勤运维管理"],
                    "link": "/cooperation",
                },
            ],
        })

        # 2c. Products ----------------------------------------------------
        slug = "products"
        pg = await create_page(
            name_zh="产品服务", name_en="Products", slug=slug,
            type="products", sort_order=3, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={}, content={
            "slides": [{
                "title_zh": "产品服务",
                "title_en": "Products & Services",
                "subtitle_zh": "全栈智慧建筑硬件与软件产品矩阵",
                "subtitle_en": "Full-stack smart building hardware and software product portfolio",
                "image": "",
                "buttons": [],
            }],
        })

        await create_block(pg.id, "product_cards", config={}, content={
            "title_zh": "智能硬件产品",
            "title_en": "Smart Hardware Products",
            "cards": [
                {
                    "title_zh": "Edge-G100 智能边缘网关",
                    "title_en": "Edge-G100 Smart Edge Gateway",
                    "desc_zh": "专为中大型智慧建筑系统集成设计的物理通信中枢，支持Bacnet/Modbus/OPC UA等多协议接入，内置边缘计算引擎实现本地智能决策。",
                    "desc_en": "A physical communication hub for medium-to-large smart building system integration, supporting Bacnet/Modbus/OPC UA protocols with built-in edge computing for local intelligent decision-making.",
                    "link": "/contact",
                },
                {
                    "title_zh": "IoT 综合环境传感器",
                    "title_en": "IoT Environmental Sensor",
                    "desc_zh": "高精度温湿度、CO2、PM2.5多合一传感器，支持LoRa/WiFi/NB-IoT多种通信方式，实现室内环境质量的全面监测。",
                    "desc_en": "High-precision all-in-one sensor for temperature, humidity, CO2, and PM2.5, supporting LoRa/WiFi/NB-IoT communication for comprehensive indoor environment monitoring.",
                    "link": "/contact",
                },
                {
                    "title_zh": "多联机集控器",
                    "title_en": "Multi-Unit Central Controller",
                    "desc_zh": "支持Bacnet/Modbus标准协议，集成本地微推理算法，实现对多联机空调系统的智能群控与能效优化。",
                    "desc_en": "Supports Bacnet/Modbus standard protocols with integrated local micro-inference algorithms for intelligent group control and energy optimization of multi-unit HVAC systems.",
                    "link": "/contact",
                },
            ],
        })

        # 2d. About -------------------------------------------------------
        slug = "about"
        pg = await create_page(
            name_zh="关于我们", name_en="About Us", slug=slug,
            type="page", sort_order=4, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={}, content={
            "slides": [{
                "title_zh": "关于金捷利",
                "title_en": "About GOLDGINNY",
                "subtitle_zh": "专注建筑智能运维，以技术赋能建筑全生命周期高效管理",
                "subtitle_en": "Focused on intelligent building operations, empowering full-lifecycle building management with technology",
                "image": "",
                "buttons": [],
            }],
        })

        await create_block(pg.id, "richtext", config={}, content={
            "html_content_zh": (
                '<p class="text-lg leading-relaxed mb-4">'
                '金捷利科技有限公司（GOLDGINNY Technology Co., Ltd.）成立于2018年，'
                '是一家专注于建筑智能运维领域的科技公司。公司核心团队来自清华大学、'
                '阿里巴巴、华为等顶尖机构，拥有深厚的自动控制、人工智能与物联网技术积累。'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                '公司以"让每一栋建筑都拥有智慧大脑"为使命，自主研发了包括智能边缘网关、'
                '综合环境传感器、多联机集控器在内的硬件产品线，以及建筑数字孪生平台、'
                'AI能耗优化引擎、智慧运维管理平台等软件系统，形成了"端-边-云"协同的'
                '全栈智慧建筑解决方案。'
                '</p>'
                '<p class="text-lg leading-relaxed">'
                '截至2026年，金捷利已为全国200+栋建筑提供智慧运维服务，覆盖商业综合体、'
                '产业园区、5A写字楼、医院、数据中心等多种业态，累计为客户节省能耗成本超2亿元。'
                '公司自主研发的冷热源自适应算法入选《国家推荐绿色技术名录》，'
                '并荣获2025年度「智慧建筑优秀服务商」称号。'
                '</p>'
            ),
            "html_content_en": (
                '<p class="text-lg leading-relaxed mb-4">'
                'GOLDGINNY Technology Co., Ltd., founded in 2018, is a technology company '
                'focused on intelligent building operations. Our core team comes from top '
                'institutions including Tsinghua University, Alibaba, and Huawei, with deep '
                'expertise in automatic control, artificial intelligence, and IoT technologies.'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                'With the mission of "giving every building a smart brain," we have developed '
                'a hardware product line including smart edge gateways, integrated environmental '
                'sensors, and multi-unit central controllers, as well as software systems including '
                'digital twin platforms, AI energy optimization engines, and smart operations '
                'management platforms — forming a complete "edge-to-cloud" smart building solution.'
                '</p>'
                '<p class="text-lg leading-relaxed">'
                'By 2026, GOLDGINNY has provided smart operations services to 200+ buildings '
                'nationwide, covering commercial complexes, industrial parks, 5A office buildings, '
                'hospitals, and data centers, saving clients over 200 million RMB in energy costs. '
                'Our self-developed HVAC adaptive algorithm has been included in the National '
                'Recommended Green Technology Catalogue, and we were honored with the 2025 '
                '"Outstanding Smart Building Service Provider" award.'
                '</p>'
            ),
        })

        await create_block(pg.id, "stats_counter", config={}, content={
            "title_zh": "金捷利 · 实力数据",
            "title_en": "GOLDGINNY by the Numbers",
            "items": [
                {"value": "200+", "label_zh": "服务建筑", "label_en": "Buildings Served"},
                {"value": "50+", "label_zh": "覆盖城市", "label_en": "Cities Covered"},
                {"value": "28.5%", "label_zh": "平均节能率", "label_en": "Avg Energy Savings"},
                {"value": "99.9%", "label_zh": "系统可用率", "label_en": "System Uptime"},
            ],
        })

        # 2e. Cooperation -------------------------------------------------
        slug = "cooperation"
        pg = await create_page(
            name_zh="商务合作", name_en="Cooperation", slug=slug,
            type="page", sort_order=5, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={}, content={
            "slides": [{
                "title_zh": "商务合作",
                "title_en": "Business Cooperation",
                "subtitle_zh": "携手金捷利，共同开拓智慧建筑蓝海市场",
                "subtitle_en": "Partner with GOLDGINNY to explore the blue ocean of smart buildings",
                "image": "",
                "buttons": [],
            }],
        })

        await create_block(pg.id, "richtext", config={}, content={
            "html_content_zh": (
                '<p class="text-lg leading-relaxed mb-4">'
                '金捷利始终秉持开放共赢的合作理念，诚邀各界合作伙伴携手共进。'
                '我们提供灵活多样的合作模式，包括项目合作、渠道代理、技术授权、'
                '联合研发等多种形式，期待与您在智慧建筑领域共创价值。'
                '</p>'
                '<p class="text-lg leading-relaxed">'
                '无论您是建筑业主、物业管理方、系统集成商还是行业ISV，'
                '金捷利都能为您提供量身定制的合作方案。请填写下方表单，'
                '我们的商务团队将在24小时内与您联系。'
                '</p>'
            ),
            "html_content_en": (
                '<p class="text-lg leading-relaxed mb-4">'
                'GOLDGINNY embraces an open and win-win cooperation philosophy, welcoming '
                'partners from all sectors. We offer flexible cooperation models including '
                'project collaboration, channel distribution, technology licensing, and joint '
                'R&D — creating value together in the smart building domain.'
                '</p>'
                '<p class="text-lg leading-relaxed">'
                'Whether you are a building owner, property manager, system integrator, or '
                'industry ISV, GOLDGINNY can provide a tailored cooperation plan. Please fill '
                'out the form below and our business team will contact you within 24 hours.'
                '</p>'
            ),
        })

        await create_block(pg.id, "contact_form", config={}, content={
            "title_zh": "合作咨询",
            "title_en": "Cooperation Inquiry",
            "fields": ["company_name", "contact_name", "phone", "message"],
            "submit_button_zh": "提交咨询",
            "submit_button_en": "Submit Inquiry",
        })

        # 2f. Contact -----------------------------------------------------
        slug = "contact"
        pg = await create_page(
            name_zh="联系我们", name_en="Contact Us", slug=slug,
            type="contact", sort_order=6, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "contact_form", config={}, content={
            "title_zh": "联系我们",
            "title_en": "Contact Us",
            "fields": ["company_name", "contact_name", "phone", "message"],
            "submit_button_zh": "提交",
            "submit_button_en": "Submit",
        })

        # 2g. News --------------------------------------------------------
        slug = "news"
        pg = await create_page(
            name_zh="新闻动态", name_en="News", slug=slug,
            type="news", sort_order=7, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        # 2h. Cases -------------------------------------------------------
        slug = "cases"
        pg = await create_page(
            name_zh="服务案例", name_en="Cases", slug=slug,
            type="content", sort_order=8, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={}, content={
            "slides": [{
                "title_zh": "服务案例",
                "title_en": "Case Studies",
                "subtitle_zh": "以技术实力赢得信赖，用实际效果说话",
                "subtitle_en": "Earning trust through technical excellence and proven results",
                "image": "",
                "buttons": [],
            }],
        })

        # 2i. Privacy -----------------------------------------------------
        slug = "privacy"
        pg = await create_page(
            name_zh="隐私政策", name_en="Privacy Policy", slug=slug,
            type="content", sort_order=9, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "richtext", config={}, content={
            "html_content_zh": (
                '<h2 class="text-2xl font-bold mb-4">隐私政策</h2>'
                '<p class="mb-4">金捷利科技有限公司（以下简称"本公司"）深知个人信息对您的重要性，'
                '并会尽全力保护您的个人信息安全。本隐私政策阐述了本公司如何收集、使用和保护您的个人信息。</p>'
                '<h3 class="text-xl font-semibold mb-2">一、信息收集</h3>'
                '<p class="mb-4">在您使用本公司网站及服务时，本公司可能会收集您的公司名称、'
                '联系人姓名、联系电话、电子邮箱等信息，仅用于向您提供产品咨询和商务合作服务。</p>'
                '<h3 class="text-xl font-semibold mb-2">二、信息使用</h3>'
                '<p class="mb-4">本公司收集的信息将用于：回复您的咨询请求、提供产品和服务信息、'
                '发送相关行业资讯（在您同意的前提下）、改进本公司的产品和服务。</p>'
                '<h3 class="text-xl font-semibold mb-2">三、信息保护</h3>'
                '<p class="mb-4">本公司采用行业标准的安全措施保护您的个人信息，'
                '防止未经授权的访问、使用或泄露。本公司不会将您的个人信息出售或出租给第三方。</p>'
            ),
            "html_content_en": (
                '<h2 class="text-2xl font-bold mb-4">Privacy Policy</h2>'
                '<p class="mb-4">GOLDGINNY Technology Co., Ltd. ("the Company") understands '
                'the importance of personal information and is committed to protecting your '
                'personal information security.</p>'
                '<h3 class="text-xl font-semibold mb-2">1. Information Collection</h3>'
                '<p class="mb-4">When using our website and services, we may collect your '
                'company name, contact name, phone number, and email address, solely for '
                'providing product consultation and business cooperation services.</p>'
                '<h3 class="text-xl font-semibold mb-2">2. Information Usage</h3>'
                '<p class="mb-4">Collected information will be used to: respond to your '
                'inquiries, provide product and service information, send relevant industry '
                'updates (with your consent), and improve our products and services.</p>'
                '<h3 class="text-xl font-semibold mb-2">3. Information Protection</h3>'
                '<p class="mb-4">We use industry-standard security measures to protect your '
                'personal information from unauthorized access, use, or disclosure. We will '
                'not sell or rent your personal information to third parties.</p>'
            ),
        })

        # 2j. Terms -------------------------------------------------------
        slug = "terms"
        pg = await create_page(
            name_zh="使用条款", name_en="Terms of Use", slug=slug,
            type="content", sort_order=10, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "richtext", config={}, content={
            "html_content_zh": (
                '<h2 class="text-2xl font-bold mb-4">使用条款</h2>'
                '<p class="mb-4">欢迎访问金捷利科技有限公司网站。使用本网站即表示您同意遵守以下条款和条件。</p>'
                '<h3 class="text-xl font-semibold mb-2">一、知识产权</h3>'
                '<p class="mb-4">本网站所有内容，包括但不限于文字、图片、图表、标识、'
                '按钮图标、图像、音频剪辑和软件，均为金捷利科技有限公司或其内容供应商的财产，'
                '受中国和国际知识产权法保护。</p>'
                '<h3 class="text-xl font-semibold mb-2">二、免责声明</h3>'
                '<p class="mb-4">本网站所提供的信息仅供参考，不构成任何形式的保证。'
                '本公司在法律允许的最大范围内，不对因使用本网站信息而产生的任何直接或间接损失承担责任。</p>'
                '<h3 class="text-xl font-semibold mb-2">三、适用法律</h3>'
                '<p class="mb-4">本使用条款受中华人民共和国法律管辖，因本条款产生的争议应提交本公司所在地有管辖权的人民法院解决。</p>'
            ),
            "html_content_en": (
                '<h2 class="text-2xl font-bold mb-4">Terms of Use</h2>'
                '<p class="mb-4">Welcome to the GOLDGINNY Technology Co., Ltd. website. '
                'By using this website, you agree to comply with the following terms and conditions.</p>'
                '<h3 class="text-xl font-semibold mb-2">1. Intellectual Property</h3>'
                '<p class="mb-4">All content on this website, including but not limited to text, '
                'images, graphics, logos, button icons, audio clips, and software, is the property '
                'of GOLDGINNY or its content suppliers, protected by Chinese and international '
                'intellectual property laws.</p>'
                '<h3 class="text-xl font-semibold mb-2">2. Disclaimer</h3>'
                '<p class="mb-4">The information provided on this website is for reference only '
                'and does not constitute any form of warranty. To the fullest extent permitted by law, '
                'the Company shall not be liable for any direct or indirect damages arising from '
                'the use of information on this website.</p>'
                '<h3 class="text-xl font-semibold mb-2">3. Governing Law</h3>'
                '<p class="mb-4">These Terms of Use are governed by the laws of the People\'s '
                'Republic of China. Any disputes arising from these terms shall be submitted to '
                'the competent court at the Company\'s location.</p>'
            ),
        })

    # ---- 3. Menus -------------------------------------------------------
    async with async_session() as db:
        result = await db.execute(select(func.count(Menu.id)))
        menu_count = result.scalar() or 0

    if menu_count > 0:
        print(f"  {menu_count} menus already exist, skipping menu creation")
    else:
        print("Creating menus...")

        # --- Header menus ---
        header_items = [
            ("首页", "Home", "/", 1),
            ("解决方案", "Solutions", "/solutions", 2),
            ("产品服务", "Products", "/products", 3),
            ("关于我们", "About", "/about", 4),
            ("商务合作", "Cooperation", "/cooperation", 5),
            ("联系我们", "Contact", "/contact", 6),
        ]
        for zh, en, link, order in header_items:
            slug = LINK_TO_SLUG.get(link)
            pid = slug_to_id.get(slug) if slug else None
            m = await create_menu_item(
                location="header", name_zh=zh, name_en=en,
                link=link, page_id=pid, order=order,
            )
            print(f"  [header] {zh} -> id={m.id} page_id={pid}")

        # --- Footer menus (parent with children) ---
        # Footer group: 产品服务
        parent_prod = await create_menu_item(
            location="footer", name_zh="产品服务", name_en="Products",
            link="", page_id=None, order=1,
        )
        print(f"  [footer] parent: 产品服务 -> id={parent_prod.id}")
        prod_children = [
            ("楼宇自控系统", "Building Automation System"),
            ("能源管理平台", "Energy Management Platform"),
            ("综合安防系统", "Integrated Security System"),
            ("智慧运维平台", "Smart Operations Platform"),
            ("暖通优化系统", "HVAC Optimization System"),
        ]
        for zh, en in prod_children:
            child = await create_menu_item(
                location="footer", name_zh=zh, name_en=en,
                link="/products", page_id=slug_to_id.get("products"),
                parent_id=parent_prod.id, order=0,
            )
            print(f"    -> {zh} (id={child.id})")

        # Footer group: 解决方案
        parent_sol = await create_menu_item(
            location="footer", name_zh="解决方案", name_en="Solutions",
            link="", page_id=None, order=2,
        )
        print(f"  [footer] parent: 解决方案 -> id={parent_sol.id}")
        sol_children = [
            ("商业综合体", "Commercial Complex", "/solutions?tab=commercial"),
            ("产业园区", "Industrial Park", "/solutions?tab=park"),
            ("写字楼", "Office Building", "/solutions?tab=office"),
            ("公共建筑", "Public Building", "/solutions?tab=hospital"),
        ]
        for zh, en, link in sol_children:
            child = await create_menu_item(
                location="footer", name_zh=zh, name_en=en,
                link=link, page_id=slug_to_id.get("solutions"),
                parent_id=parent_sol.id, order=0,
            )
            print(f"    -> {zh} (id={child.id})")

        # Footer group: 公司
        parent_comp = await create_menu_item(
            location="footer", name_zh="公司", name_en="Company",
            link="", page_id=None, order=3,
        )
        print(f"  [footer] parent: 公司 -> id={parent_comp.id}")
        comp_children = [
            ("关于我们", "About Us", "/about"),
            ("服务案例", "Cases", "/cases"),
            ("新闻动态", "News", "/news"),
            ("商务合作", "Cooperation", "/cooperation"),
            ("联系我们", "Contact", "/contact"),
        ]
        for zh, en, link in comp_children:
            slug = LINK_TO_SLUG.get(link)
            pid = slug_to_id.get(slug) if slug else None
            child = await create_menu_item(
                location="footer", name_zh=zh, name_en=en,
                link=link, page_id=pid,
                parent_id=parent_comp.id, order=0,
            )
            print(f"    -> {zh} (id={child.id})")

    # ---- 4. News Articles -----------------------------------------------
    async with async_session() as db:
        result = await db.execute(select(func.count(NewsArticle.id)))
        news_count = result.scalar() or 0

    if news_count > 0:
        print(f"  {news_count} news articles already exist, skipping")
    else:
        print("Creating news articles...")
        articles = [
            (
                "金捷利荣获2025年度「智慧建筑优秀服务商」称号",
                "GOLDGINNY Wins 2025 'Outstanding Smart Building Service Provider' Award",
                "凭借在智慧建筑运维领域的技术创新和优质服务，金捷利荣获行业权威评选的2025年度「智慧建筑优秀服务商」称号。",
                "GOLDGINNY has been honored with the 2025 'Outstanding Smart Building Service Provider' award for its technological innovation and quality service in smart building operations.",
                (
                    "<p>近日，在2025中国智慧建筑产业峰会上，金捷利科技有限公司凭借在建筑智能运维领域的"
                    "持续技术创新和卓越服务能力，从数百家参评企业中脱颖而出，荣获2025年度「智慧建筑优秀"
                    "服务商」称号。</p>"
                    "<p>本次评选由行业权威机构联合组织，从技术创新、项目落地、客户评价等多个维度进行"
                    "综合评定。金捷利自研的冷热源自适应算法和端边云协同架构获得了评审专家的高度认可。</p>"
                    "<p>金捷利CEO表示：\"这一荣誉是对团队多年努力的肯定，我们将继续深耕建筑智能运维领域，"
                    '为更多客户提供优质的智慧建筑解决方案。"</p>'
                ),
                (
                    "<p>At the 2025 China Smart Building Industry Summit, GOLDGINNY Technology Co., Ltd. "
                    "stood out from hundreds of participating enterprises and won the 2025 'Outstanding "
                    "Smart Building Service Provider' award for its continuous technological innovation "
                    "and excellent service capabilities in intelligent building operations.</p>"
                    "<p>The award was jointly organized by industry authorities, with comprehensive "
                    "evaluation across technology innovation, project implementation, and customer "
                    "satisfaction. GOLDGINNY's self-developed HVAC adaptive algorithm and edge-cloud "
                    "collaborative architecture received high recognition from the expert panel.</p>"
                ),
                "company_news",
            ),
            (
                "某CBD核心区项目通过金捷利智慧调控实现能耗降幅28.5%",
                "CBD Core-Area Project Achieves 28.5% Energy Reduction with GOLDGINNY Smart Control",
                "金捷利为某一线城市CBD核心区商业综合体部署智慧运维系统，实测年能耗降幅达28.5%，年节省电费超600万元。",
                "GOLDGINNY deployed its smart operations system in a CBD core-area commercial complex, achieving a verified 28.5% annual energy reduction and saving over 6 million RMB in electricity costs.",
                (
                    "<p>近日，金捷利科技公布了某一线城市CBD核心区商业综合体的智慧运维项目阶段性成果。"
                    "通过部署金捷利自研的冷热源自适应算法和多联机集控器，该项目在2025年度实现了"
                    "综合能耗降幅28.5%，年节省电费超600万元。</p>"
                    "<p>该项目建筑面积约15万平方米，涵盖商业、办公、酒店等多种业态。金捷利团队针对"
                    "项目特点，制定了分区分时的空调优化策略，并部署了Edge-G100智能边缘网关和IoT综合"
                    "环境传感器，实现了对建筑环境的精准感知和智能调控。</p>"
                    "<p>项目物业方表示：\"金捷利的方案不仅大幅降低了能耗成本，还提升了室内环境舒适度，"
                    '租户满意度明显提高。"</p>'
                ),
                (
                    "<p>GOLDGINNY recently announced the phased results of a smart operations project "
                    "for a CBD core-area commercial complex in a first-tier city. By deploying GOLDGINNY's "
                    "self-developed HVAC adaptive algorithm and multi-unit central controllers, the project "
                    "achieved a 28.5% reduction in overall energy consumption and saved over 6 million RMB "
                    "in electricity costs in 2025.</p>"
                    "<p>The project covers approximately 150,000 square meters, encompassing commercial, "
                    "office, and hotel spaces. The GOLDGINNY team developed zone-specific and time-specific "
                    "HVAC optimization strategies and deployed Edge-G100 smart edge gateways and IoT sensors "
                    "for precise environmental sensing and intelligent control.</p>"
                ),
                "project",
            ),
            (
                "金捷利冷热源自适应算法入选《国家推荐绿色技术名录》",
                "GOLDGINNY's HVAC Adaptive Algorithm Included in National Recommended Green Technology Catalogue",
                "金捷利自主研发的冷热源自适应算法经严格评审，正式入选《国家推荐绿色技术名录》，标志着该技术获得国家级认可。",
                "GOLDGINNY's self-developed HVAC adaptive algorithm has been officially included in the National Recommended Green Technology Catalogue after rigorous review, marking national-level recognition.",
                (
                    "<p>近日，国家发展和改革委员会公布最新一批《国家推荐绿色技术名录》，金捷利科技"
                    "自主研发的冷热源自适应算法成功入选。这是该名录中少数来自民营科技企业的建筑节能技术。</p>"
                    "<p>金捷利冷热源自适应算法基于深度强化学习技术，能够根据建筑实时负荷、室外气象、"
                    "电价信号等多维数据，动态优化冷热源系统的运行策略，在保证室内舒适度的前提下最大化节能效果。"
                    "经第三方检测机构验证，该算法的平均节能率达到28.5%。</p>"
                    "<p>入选《国家推荐绿色技术名录》意味着金捷利的技术方案将在政府采购、绿色建筑评价、"
                    "节能改造补贴等方面获得政策支持，为公司未来发展带来新的机遇。</p>"
                ),
                (
                    "<p>The National Development and Reform Commission recently announced the latest batch "
                    "of the National Recommended Green Technology Catalogue, and GOLDGINNY's self-developed "
                    "HVAC adaptive algorithm was successfully included — one of the few building energy-saving "
                    "technologies from private tech companies on the list.</p>"
                    "<p>Based on deep reinforcement learning, the algorithm dynamically optimizes HVAC system "
                    "operation strategies according to real-time building load, outdoor weather, and electricity "
                    "pricing signals, maximizing energy savings while ensuring indoor comfort. Third-party testing "
                    "verified an average energy saving rate of 28.5%.</p>"
                ),
                "certification",
            ),
            (
                "金捷利与某世界500强集团达成智慧科技园区战略合作",
                "GOLDGINNY Forms Strategic Partnership with Fortune 500 Group for Smart Technology Park",
                "金捷利科技与某世界500强企业集团签署战略合作协议，将为其旗下多个科技园区提供智慧运维整体解决方案。",
                "GOLDGINNY has signed a strategic cooperation agreement with a Fortune 500 group to provide smart operations solutions for multiple technology parks under its management.",
                (
                    "<p>近日，金捷利科技有限公司与某世界500强企业集团正式签署战略合作协议，双方将在"
                    "智慧科技园区建设与运维领域开展全面合作。根据协议，金捷利将为该集团旗下的多个科技园区"
                    "提供涵盖能耗管理、环境监测、安防联动和智能运维在内的整体解决方案。</p>"
                    "<p>该集团在全国运营管理超过20个科技产业园区，总面积超过500万平方米。此次合作将首先在"
                    "长三角地区的3个旗舰园区部署金捷利的智慧运维系统，后续逐步推广至全国其他园区。</p>"
                    "<p>金捷利CEO表示：\"与世界500强企业的合作是对金捷利技术实力和服务能力的充分认可。"
                    '我们将全力以赴，打造智慧科技园区运维的行业标杆。"</p>'
                ),
                (
                    "<p>GOLDGINNY Technology Co., Ltd. has officially signed a strategic cooperation "
                    "agreement with a Fortune 500 group for comprehensive collaboration in smart technology "
                    "park construction and operations. Under the agreement, GOLDGINNY will provide integrated "
                    "solutions covering energy management, environmental monitoring, security coordination, "
                    "and smart operations for multiple technology parks.</p>"
                    "<p>The group operates over 20 technology parks nationwide, totaling more than 5 million "
                    "square meters. The cooperation will first deploy GOLDGINNY's smart operations system in "
                    "3 flagship parks in the Yangtze River Delta region, with gradual expansion nationwide.</p>"
                ),
                "cooperation",
            ),
        ]
        for t_zh, t_en, s_zh, s_en, c_zh, c_en, cat in articles:
            a = await create_article(
                title_zh=t_zh, title_en=t_en,
                summary_zh=s_zh, summary_en=s_en,
                content_zh=c_zh, content_en=c_en,
                category=cat, is_published=True,
            )
            print(f"  {t_zh[:35]}... -> id={a.id}")

    # ---- 5. Products (Categories + Products) ---------------------------
    async with async_session() as db:
        result = await db.execute(select(func.count(ProductCategory.id)))
        cat_count = result.scalar() or 0

    if cat_count > 0:
        print(f"  {cat_count} product categories already exist, skipping")
    else:
        print("Creating products...")

        cat = await create_product_category(
            name_zh="智能硬件", name_en="Smart Hardware",
            slug="smart-hardware", sort_order=1, is_published=True,
        )
        print(f"  Category: {cat.name_zh} (id={cat.id})")

        products = [
            {
                "category_id": cat.id,
                "name_zh": "Edge-G100 智能边缘网关",
                "name_en": "Edge-G100 Smart Edge Gateway",
                "slug": "edge-g100",
                "summary_zh": "专为中大型智慧建筑系统集成设计的物理通信中枢，支持多协议接入与边缘计算。",
                "summary_en": "A physical communication hub designed for medium-to-large smart building system integration, supporting multi-protocol access and edge computing.",
                "description_zh": (
                    "Edge-G100 是金捷利自主研发的智能边缘网关，专为中大型智慧建筑系统集成设计。"
                    "产品支持Bacnet、Modbus、OPC UA等主流建筑自动化协议，内置高性能边缘计算引擎，"
                    "可在本地完成数据预处理、协议转换和智能决策，有效降低云端通信负载和响应延迟。"
                    "产品采用工业级设计，支持-20℃至70℃宽温工作，适合各类建筑现场部署。"
                ),
                "description_en": (
                    "The Edge-G100 is GOLDGINNY's self-developed smart edge gateway, designed for "
                    "medium-to-large smart building system integration. It supports mainstream building "
                    "automation protocols including Bacnet, Modbus, and OPC UA, with a built-in "
                    "high-performance edge computing engine for local data preprocessing, protocol "
                    "conversion, and intelligent decision-making."
                ),
                "sort_order": 1,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "IoT 综合环境传感器",
                "name_en": "IoT Environmental Sensor",
                "slug": "iot-env-sensor",
                "summary_zh": "高精度温湿度、CO2、PM2.5多合一传感器，支持多种通信方式。",
                "summary_en": "High-precision all-in-one sensor for temperature, humidity, CO2, and PM2.5, supporting multiple communication methods.",
                "description_zh": (
                    "金捷利IoT综合环境传感器是一款集温湿度、CO2浓度、PM2.5、TVOC等多项环境指标"
                    "于一体的高精度传感设备。产品采用进口传感器模组，测量精度达到工业级标准，"
                    "支持LoRa、WiFi、NB-IoT等多种通信方式，可灵活适配不同建筑场景的部署需求。"
                    "配合金捷利智慧运维平台，实现环境数据的实时采集、可视化和智能预警。"
                ),
                "description_en": (
                    "The GOLDGINNY IoT Environmental Sensor integrates temperature, humidity, CO2, "
                    "PM2.5, TVOC, and other environmental indicators into a single high-precision device. "
                    "It uses imported sensor modules with industrial-grade accuracy and supports LoRa, "
                    "WiFi, and NB-IoT communication for flexible deployment in various building scenarios."
                ),
                "sort_order": 2,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "多联机集控器",
                "name_en": "Multi-Unit Central Controller",
                "slug": "multi-unit-controller",
                "summary_zh": "支持Bacnet/Modbus标准协议，集成本地微推理算法，实现空调系统智能群控。",
                "summary_en": "Supports Bacnet/Modbus standard protocols with integrated local micro-inference algorithms for intelligent HVAC group control.",
                "description_zh": (
                    "金捷利多联机集控器是专为多联机空调系统设计的智能控制设备，支持Bacnet和Modbus"
                    "标准协议，可与主流品牌的多联机系统无缝对接。产品集成了金捷利自研的本地微推理算法，"
                    "能够在不依赖云端的条件下，根据室内外环境数据和历史运行模式，自主优化空调运行策略，"
                    "实现单栋建筑10-20%的空调节能效果。"
                ),
                "description_en": (
                    "The GOLDGINNY Multi-Unit Central Controller is an intelligent control device designed "
                    "for multi-unit HVAC systems. It supports Bacnet and Modbus standard protocols for "
                    "seamless integration with major multi-unit system brands. With integrated local "
                    "micro-inference algorithms, it can autonomously optimize HVAC operation strategies "
                    "based on environmental data and historical patterns, achieving 10-20% energy savings "
                    "per building without relying on cloud connectivity."
                ),
                "sort_order": 3,
                "is_published": True,
            },
        ]
        for pdata in products:
            prod = await create_product(**pdata)
            print(f"    {prod.name_zh} -> id={prod.id}")

    # ---- 6. Cases ------------------------------------------------------
    async with async_session() as db:
        result = await db.execute(select(func.count(Case.id)))
        case_count = result.scalar() or 0

    if case_count > 0:
        print(f"  {case_count} cases already exist, skipping")
    else:
        print("Creating cases...")
        cases = [
            {
                "name_zh": "CBD智慧改造项目",
                "name_en": "CBD Smart Retrofit Project",
                "slug": "cbd-smart-retrofit",
                "category": "commercial",
                "summary_zh": "为某一线城市CBD核心区15万平米商业综合体提供智慧运维整体方案，实现年能耗降幅28.5%。",
                "summary_en": "Provided smart operations solution for a 150,000 sqm commercial complex in a first-tier city CBD core area, achieving 28.5% annual energy reduction.",
                "content_zh": (
                    "<p>某一线城市CBD核心区商业综合体，建筑面积约15万平方米，涵盖商业、办公、酒店等"
                    "多种业态。项目面临能耗成本高、设备管理复杂、租户舒适度要求高等挑战。</p>"
                    "<p>金捷利为其部署了包括Edge-G100智能边缘网关、IoT综合环境传感器和多联机集控器"
                    "在内的硬件系统，配合冷热源自适应算法，实现了对暖通空调系统的精细化智能调控。</p>"
                    "<p>项目实施后，年综合能耗降低28.5%，年节省电费超600万元，室内环境满意度提升至95%以上。</p>"
                ),
                "content_en": (
                    "<p>A commercial complex in the CBD core area of a first-tier city, approximately "
                    "150,000 square meters, covering retail, office, and hotel spaces. The project faced "
                    "challenges including high energy costs, complex equipment management, and demanding "
                    "tenant comfort requirements.</p>"
                    "<p>GOLDGINNY deployed hardware including Edge-G100 smart edge gateways, IoT sensors, "
                    "and multi-unit central controllers, combined with the HVAC adaptive algorithm, to "
                    "achieve precise intelligent control of HVAC systems.</p>"
                    "<p>After implementation, annual energy consumption decreased by 28.5%, saving over "
                    "6 million RMB in electricity costs, with indoor environment satisfaction exceeding 95%.</p>"
                ),
                "stats": [
                    {"label": "节能率", "value": "28.5%"},
                    {"label": "建筑面积", "value": "15万㎡"},
                ],
                "sort_order": 1,
                "is_published": True,
            },
            {
                "name_zh": "智慧产业园区项目",
                "name_en": "Smart Industrial Park Project",
                "slug": "smart-industrial-park",
                "category": "park",
                "summary_zh": "为某国家级高新区提供多楼宇集中管控方案，覆盖50栋建筑，降低园区整体运营成本30%以上。",
                "summary_en": "Provided centralized multi-building management for a national-level high-tech zone covering 50 buildings, reducing overall park operation costs by 30%+.",
                "content_zh": (
                    "<p>某国家级高新技术产业开发区，园区总面积超过200万平方米，涵盖50余栋各类建筑，"
                    "包括研发办公楼、标准化厂房、数据中心和配套服务设施。</p>"
                    "<p>金捷利为园区部署了统一智慧运维平台，实现多楼宇设备集中监控、能源梯级调度、"
                    "碳排放实时核算和园区级安防联动。通过Edge-G100网关实现各建筑子系统的互联互通，"
                    "建立园区级数字孪生驾驶舱。</p>"
                    "<p>项目全面上线后，园区整体运营成本降低30%以上，运维人员效率提升50%，年度碳排放减少约8000吨。</p>"
                ),
                "content_en": (
                    "<p>A national-level high-tech industrial development zone covering over 2 million "
                    "square meters with 50+ buildings including R&D offices, standardized factories, "
                    "data centers, and supporting facilities.</p>"
                    "<p>GOLDGINNY deployed a unified smart operations platform enabling centralized "
                    "multi-building equipment monitoring, cascaded energy dispatch, real-time carbon "
                    "accounting, and park-wide security coordination.</p>"
                    "<p>After full deployment, overall park operation costs decreased by 30%+, "
                    "maintenance staff efficiency improved by 50%, and annual carbon emissions "
                    "reduced by approximately 8,000 tons.</p>"
                ),
                "stats": [
                    {"label": "运营成本降幅", "value": "30%"},
                    {"label": "覆盖建筑", "value": "50栋"},
                ],
                "sort_order": 2,
                "is_published": True,
            },
            {
                "name_zh": "三甲医院智慧运维项目",
                "name_en": "Grade-A Hospital Smart Operations Project",
                "slug": "hospital-smart-ops",
                "category": "medical",
                "summary_zh": "为某三甲医院提供洁净空调管理和医疗环境监控方案，满足国家医疗建筑环境标准。",
                "summary_en": "Provided clean air management and medical environment monitoring for a Grade-A hospital, meeting national medical building environment standards.",
                "content_zh": (
                    "<p>某三甲医院总建筑面积约12万平方米，日门诊量超过8000人次。医院对环境温湿度、"
                    "洁净度、压差梯度等参数有严格要求，同时面临能耗成本高、设备运维压力大的挑战。</p>"
                    "<p>金捷利针对医疗建筑的特殊需求，部署了洁净空调智能管理系统和医疗环境实时监控"
                    "方案。IoT综合环境传感器覆盖手术室、ICU、检验科等重点区域，实现对温度、湿度、"
                    "压差、颗粒物等关键指标的7x24小时监测与自动调控。</p>"
                    "<p>项目实施后，医院重点区域环境合规率达到100%，空调系统节能率达22%，运维工单"
                    "响应时间从平均4小时缩短至30分钟。</p>"
                ),
                "content_en": (
                    "<p>A Grade-A hospital covering approximately 120,000 square meters with over 8,000 "
                    "daily outpatient visits. The hospital has strict requirements for temperature, humidity, "
                    "cleanliness, and pressure gradients, along with high energy costs and equipment "
                    "maintenance pressure.</p>"
                    "<p>GOLDGINNY deployed intelligent clean air management and real-time medical environment "
                    "monitoring tailored to healthcare facilities. IoT sensors cover critical areas including "
                    "operating rooms, ICU, and laboratories for 24/7 monitoring of key indicators.</p>"
                    "<p>After implementation, environmental compliance reached 100% in critical areas, "
                    "HVAC energy savings reached 22%, and maintenance response time decreased from "
                    "4 hours to 30 minutes.</p>"
                ),
                "stats": [
                    {"label": "环境合规率", "value": "100%"},
                    {"label": "响应提速", "value": "8倍"},
                ],
                "sort_order": 3,
                "is_published": True,
            },
            {
                "name_zh": "5A写字楼智能化项目",
                "name_en": "5A Office Building Smart Project",
                "slug": "5a-office-smart",
                "category": "office",
                "summary_zh": "为某5A级写字楼提供暖通优化和室内环境品质管理方案，提升租户满意度与物业资产价值。",
                "summary_en": "Provided HVAC optimization and indoor environmental quality management for a 5A office building, enhancing tenant satisfaction and property value.",
                "content_zh": (
                    "<p>某5A级写字楼位于城市核心商务区，建筑高度180米，共42层，入驻企业超过100家。"
                    "物业管理方面临能耗成本高、租户舒适度投诉多、设备维护效率低等问题。</p>"
                    "<p>金捷利为该写字楼部署了暖通空调智能优化系统、室内环境品质监测系统和智慧停车"
                    "管理系统。通过多联机集控器和IoT环境传感器，实现分楼层、分区域的精准环境调控，"
                    "同时为租户提供可视化的室内环境数据和能耗报告。</p>"
                    "<p>项目上线后，写字楼整体能耗降低25%，租户舒适度投诉减少70%，物业满意度评分"
                    "从3.2提升至4.6（满分5分），有效提升了物业资产价值和市场竞争力。</p>"
                ),
                "content_en": (
                    "<p>A 5A office building in a city's core business district, 180 meters tall with 42 "
                    "floors and over 100 tenant companies. Property management faced challenges including "
                    "high energy costs, tenant comfort complaints, and low maintenance efficiency.</p>"
                    "<p>GOLDGINNY deployed intelligent HVAC optimization, indoor environmental quality "
                    "monitoring, and smart parking management. Multi-unit controllers and IoT sensors "
                    "enable floor-by-floor and zone-specific precise environmental control, with "
                    "visualized environmental data and energy reports for tenants.</p>"
                    "<p>After deployment, overall energy consumption decreased by 25%, tenant comfort "
                    "complaints reduced by 70%, and property satisfaction scores improved from 3.2 to "
                    "4.6 out of 5.</p>"
                ),
                "stats": [
                    {"label": "整体节能率", "value": "25%"},
                    {"label": "满意度提升", "value": "4.6/5"},
                ],
                "sort_order": 4,
                "is_published": True,
            },
        ]
        for cdata in cases:
            c = await create_case(**cdata)
            print(f"    {c.name_zh} -> id={c.id}")

    # ---- Done -----------------------------------------------------------
    print("\nSeed complete!")
    print(f"Login: admin / admin123")
    print(f"API Base: {API}")


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
            sort_order = {"news": 6, "faq": 7}.get(slug, 0)
            pg = await create_page(name_zh=zh, name_en=en, slug=slug, type=ptype, sort_order=sort_order, is_published=True)
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
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        asyncio.run(cleanup())
        asyncio.run(seed())
    elif len(sys.argv) > 1 and sys.argv[1] == "migrate":
        asyncio.run(migrate_pages_and_menus())
    else:
        asyncio.run(seed())
