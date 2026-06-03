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
            "金捷利科技（北京）有限公司成立于2018年12月，总部位于北京，"
            '是专精特新中小企业，国高新/村高新技术企业。公司以“让每一栋建筑都拥有智慧大脑”为使命，'
            "聚焦建筑智能运维领域，自主研发AI冷热源优化算法、边缘计算物联网关、"
            "数字孪生可视化平台等核心产品，已为全国超过500栋建筑提供智慧运维服务。"
        ),
        "company_description_en": (
            "GOLDGINNY Technology (Beijing) Co., Ltd., founded in December 2018 and "
            "headquartered in Beijing, is a specialized and sophisticated SME and a national "
            "high-tech enterprise. With the mission of 'giving every building a smart brain,' "
            "we focus on intelligent building operations, developing core products including "
            "AI HVAC optimization algorithms, edge computing IoT gateways, and digital twin "
            "visualization platforms. We have served over 500 buildings nationwide."
        ),
        "hotline": "400-888-0000",
        "contact_email": "aaqiuaa@gmail.com",
        "icp_beian": "沪ICP备XXXXXXXX号",
        "footer_hotline_label": "7x24小时全国智能运维热线",
        "footer_privacy_text": "隐私政策",
        "footer_terms_text": "法律声明",
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
            type="content", sort_order=1, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        # Hero block (3 slides)
        await create_block(pg.id, "hero", config={"full_height": True}, content={
            "slides": [
                {
                    "title_zh": "金捷利AI绿色空间运营商",
                    "title_en": "GOLDGINNY AI Green Space Operator",
                    "subtitle_zh": "智能研发低碳算法与设备集群控制，全面赋能高能效智慧建筑运行",
                    "subtitle_en": "Intelligent R&D of low-carbon algorithms and device cluster control, fully empowering high-efficiency smart building operations",
                    "image": "",
                    "buttons": [
                        {"label_zh": "了解更多", "label_en": "Learn More", "link": "/cooperation", "variant": "primary"},
                        {"label_zh": "免费咨询", "label_en": "Free Consultation", "link": "/contact", "variant": "outline"},
                    ],
                },
                {
                    "title_zh": "机电暖通系统数字化运维服务商",
                    "title_en": "Digital O&M Service Provider for MEP & HVAC Systems",
                    "subtitle_zh": "全周期暖通空调长效运维托管，构建软硬一体化的高能效控制大脑",
                    "subtitle_en": "Full-cycle long-term HVAC O&M managed services, building an integrated hardware-software high-efficiency control brain",
                    "image": "",
                    "buttons": [
                        {"label_zh": "了解更多", "label_en": "Learn More", "link": "/cooperation", "variant": "primary"},
                        {"label_zh": "免费咨询", "label_en": "Free Consultation", "link": "/contact", "variant": "outline"},
                    ],
                },
                {
                    "title_zh": "专业建筑节能技术与解决方案",
                    "title_en": "Professional Building Energy-Saving Technology & Solutions",
                    "subtitle_zh": "提供卓越暖通自适应群控，以低能耗算法助力建筑持久降能降碳",
                    "subtitle_en": "Providing superior HVAC adaptive group control, leveraging low-energy algorithms for lasting building energy and carbon reduction",
                    "image": "",
                    "buttons": [
                        {"label_zh": "了解更多", "label_en": "Learn More", "link": "/cooperation", "variant": "primary"},
                        {"label_zh": "免费咨询", "label_en": "Free Consultation", "link": "/contact", "variant": "outline"},
                    ],
                },
            ],
        })

        # News list
        await create_block(pg.id, "news_list", config={"gradient_top": "#0f172a"}, content={
            "title_zh": "公司新闻",
            "title_en": "News & Updates",
        })

        # Product cards (8 hardware products)
        await create_block(pg.id, "product_cards", config={"gradient_top": "#fafbfc"}, content={
            "title_zh": "产品服务",
            "title_en": "Products & Services",
            "cards": [
                {
                    "title_zh": "Edge-G100 智能边缘网关",
                    "title_en": "Edge-G100 Smart Edge Gateway",
                    "desc_zh": "专为中大型智慧建筑系统集成设计的物理通信中枢，支持Bacnet/Modbus/OPC UA等多协议接入，内置边缘计算引擎实现本地智能决策。",
                    "desc_en": "Physical communication hub for medium-to-large smart building system integration, supporting multi-protocol access and edge computing.",
                    "link": "/products",
                },
                {
                    "title_zh": "IoT无线温湿度传感器组",
                    "title_en": "IoT Wireless Temperature & Humidity Sensor Suite",
                    "desc_zh": "高精度温湿度采集，支持LoRa/WiFi/NB-IoT多种无线通信方式，实现建筑环境的全域分布式感知。",
                    "desc_en": "High-precision temperature and humidity data collection with multi-protocol wireless communication for distributed environmental sensing.",
                    "link": "/products",
                },
                {
                    "title_zh": "智能微机电保护监控模块",
                    "title_en": "Smart MEMS Protection & Monitoring Module",
                    "desc_zh": "集成电流/电压/功率因数实时监测与智能断路保护，实现配电系统精细化安全管控。",
                    "desc_en": "Integrated real-time monitoring of current, voltage, and power factor with smart circuit protection for precise power distribution management.",
                    "link": "/products",
                },
                {
                    "title_zh": "多信道数据采集终端",
                    "title_en": "Multi-Channel Data Acquisition Terminal",
                    "desc_zh": "支持8/16/32信道模拟量与数字量同步采集，适配各类工业传感器，构建建筑机电系统的全息感知网络。",
                    "desc_en": "Supports 8/16/32-channel synchronous analog and digital signal acquisition compatible with various industrial sensors.",
                    "link": "/products",
                },
                {
                    "title_zh": "智能超声波流速热量计",
                    "title_en": "Smart Ultrasonic Flow & Heat Meter",
                    "desc_zh": "非侵入式超声波流量测量与冷热量精确计量，为暖通系统能效分析提供核心数据支撑。",
                    "desc_en": "Non-invasive ultrasonic flow measurement and precise thermal metering for HVAC energy efficiency analysis.",
                    "link": "/products",
                },
                {
                    "title_zh": "六合一多参数环境监视箱",
                    "title_en": "6-in-1 Multi-Parameter Environmental Monitoring Box",
                    "desc_zh": "集成温度/湿度/CO2/PM2.5/TVOC/噪声六项指标，全天候室内外环境质量综合评价。",
                    "desc_en": "Integrates six indicators including temperature, humidity, CO2, PM2.5, TVOC, and noise for comprehensive indoor/outdoor environmental assessment.",
                    "link": "/products",
                },
                {
                    "title_zh": "智能红外温度阵列探针",
                    "title_en": "Smart Infrared Thermal Array Probe",
                    "desc_zh": "高分辨率红外阵列测温，非接触式实时监测设备表面温度分布，助力设备异常预警与预测维护。",
                    "desc_en": "High-resolution infrared array thermometry for contactless real-time equipment surface temperature monitoring and predictive maintenance.",
                    "link": "/products",
                },
                {
                    "title_zh": "电能安全及综合平衡仪",
                    "title_en": "Power Safety & Integrated Balancer",
                    "desc_zh": "三相电能质量监测与负荷平衡调节一体化设备，保障建筑配电系统安全高效运行。",
                    "desc_en": "Integrated three-phase power quality monitoring and load balancing device for safe and efficient building power distribution.",
                    "link": "/products",
                },
            ],
        })

        # Solution cards (6 tabs including hotel and datacenter)
        await create_block(pg.id, "solution_cards", config={"gradient_top": "#f1f5f9"}, content={
            "title_zh": "解决方案",
            "title_en": "Solutions",
            "subtitle_zh": "覆盖楼宇控制、系统深度寻优到工业设施控制的全场景化综合能源效率提升解决方案",
            "subtitle_en": "Full-scenario comprehensive energy efficiency improvement solutions covering building control, deep system optimization, and industrial facility control",
            "tabs": [
                {
                    "key": "commercial",
                    "label_zh": "商业综合体",
                    "label_en": "Commercial",
                    "title_zh": "商业综合体智慧运维方案",
                    "title_en": "Smart Operations for Commercial Complexes",
                    "desc_zh": "中央空调智能调优 + 智能照明 + 室内环境监测 + 综合安防，实现一站式智慧管理，综合节能率达28.5%。",
                    "desc_en": "Central HVAC optimization + smart lighting + indoor environment monitoring + integrated security for one-stop smart management with 28.5% energy savings.",
                    "features": [
                        {"text_zh": "冷热源自适应调控", "text_en": "Adaptive cooling/heating source control"},
                        {"text_zh": "分区分时照明策略", "text_en": "Zone-based scheduled lighting strategy"},
                        {"text_zh": "室内环境实时监测", "text_en": "Real-time indoor environment monitoring"},
                        {"text_zh": "设备预测性维护", "text_en": "Predictive equipment maintenance"},
                    ],
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
                    "features": [
                        {"text_zh": "多楼宇统一监控", "text_en": "Multi-building unified monitoring"},
                        {"text_zh": "能源梯级调度", "text_en": "Cascaded energy dispatch"},
                        {"text_zh": "碳排放实时核算", "text_en": "Real-time carbon emission accounting"},
                        {"text_zh": "园区级安防联动", "text_en": "Park-wide security coordination"},
                    ],
                    "link": "/solutions?tab=park",
                },
                {
                    "key": "office",
                    "label_zh": "5A写字楼",
                    "label_en": "5A Office",
                    "title_zh": "5A写字楼智能化方案",
                    "title_en": "Smart Solutions for 5A Office Buildings",
                    "desc_zh": "暖通空调优化 + 智能照明 + 室内环境品质管理 + 智慧停车，提升租户满意度与资产价值。",
                    "desc_en": "HVAC optimization + smart lighting + indoor environmental quality management + smart parking, enhancing tenant satisfaction and asset value.",
                    "features": [
                        {"text_zh": "新风按需供给", "text_en": "Demand-driven fresh air supply"},
                        {"text_zh": "办公环境舒适度管理", "text_en": "Office comfort management"},
                        {"text_zh": "能源分项计量", "text_en": "Sub-metering by energy category"},
                        {"text_zh": "智慧停车引导", "text_en": "Smart parking guidance"},
                    ],
                    "link": "/solutions?tab=office",
                },
                {
                    "key": "medical",
                    "label_zh": "公共建筑",
                    "label_en": "Public",
                    "title_zh": "公共建筑智慧运维方案",
                    "title_en": "Smart Operations for Public Buildings",
                    "desc_zh": "洁净空调管理 + 医疗级环境监控 + 能效合规管理，满足GB/T 51153等国家标准。",
                    "desc_en": "Clean air management + medical-grade environment monitoring + energy compliance, meeting GB/T 51153 and other national standards.",
                    "features": [
                        {"text_zh": "洁净区域环境管控", "text_en": "Clean-area environment control"},
                        {"text_zh": "医疗设备能耗监测", "text_en": "Medical equipment energy monitoring"},
                        {"text_zh": "环境参数合规记录", "text_en": "Environmental compliance recording"},
                        {"text_zh": "应急联动响应", "text_en": "Emergency coordinated response"},
                    ],
                    "link": "/solutions?tab=medical",
                },
                {
                    "key": "hotel",
                    "label_zh": "中高端酒店",
                    "label_en": "Hotel",
                    "title_zh": "中高端酒店智慧能效方案",
                    "title_en": "Smart Energy Efficiency for Upscale Hotels",
                    "desc_zh": "打通前台PMS与客房RCU系统，配合大楼暖通总控智能预设开房微环境，兼顾品质体验与低碳运营。",
                    "desc_en": "Integrating front-desk PMS with guest-room RCU systems and building HVAC master control for intelligent room micro-environment presets, balancing quality experience with low-carbon operations.",
                    "features": [
                        {"text_zh": "打通前台PMS与客房RCU系统，配合大楼暖通总控智能预设开房微环境", "text_en": "Integrate front-desk PMS with guest-room RCU systems, coordinating building HVAC master control for intelligent room micro-environment presets"},
                        {"text_zh": "依据开房入住状态智能预设空调冷热载荷", "text_en": "Intelligently preset HVAC cooling/heating load based on room occupancy status"},
                        {"text_zh": "兼顾品质体验与低碳运营", "text_en": "Balance quality guest experience with low-carbon operations"},
                    ],
                    "link": "/solutions?tab=hotel",
                },
                {
                    "key": "datacenter",
                    "label_zh": "数据中心",
                    "label_en": "Data Center",
                    "title_zh": "数据中心高能效制冷方案",
                    "title_en": "High-Efficiency Cooling for Data Centers",
                    "desc_zh": "结合气流场热力梯度传感器，对不间断工作的计算物理机网格智慧分配冷量，深度逼近极致能效PUE。",
                    "desc_en": "Leveraging airflow thermal gradient sensors for intelligent cooling distribution across continuously operating computing grids, driving PUE toward ultimate efficiency.",
                    "features": [
                        {"text_zh": "结合气流场热力梯度传感器，对不间断工作的计算物理机网格智慧分配冷量", "text_en": "Leverage airflow thermal gradient sensors for intelligent cooling distribution across continuously operating computing grids"},
                        {"text_zh": "冷热源末端预测调节与冷却塔智能变频联合调度", "text_en": "Joint dispatch of predictive terminal regulation and smart variable-frequency cooling tower control"},
                        {"text_zh": "深度逼近极致能效PUE", "text_en": "Drive PUE toward ultimate efficiency limits"},
                    ],
                    "link": "/solutions?tab=datacenter",
                },
            ],
        })

        # Stats counter block
        await create_block(pg.id, "stats_counter", config={"gradient_top": "#eff6ff"}, content={
            "title_zh": "效果统计",
            "title_en": "Performance Statistics",
            "subtitle_zh": "数字是最有力的证明，金捷利持续为客户创造可量化的业务价值",
            "subtitle_en": "Numbers are the strongest proof — GOLDGINNY consistently delivers quantifiable business value to clients",
            "items": [
                {"value": "15-30%", "label_zh": "综合节能", "label_en": "Energy Saving"},
                {"value": "500+", "label_zh": "交付项目", "label_en": "Projects Delivered"},
                {"value": "100+", "label_zh": "生态伙伴", "label_en": "Ecosystem Partners"},
                {"value": "80+", "label_zh": "服务城市", "label_en": "Cities Served"},
            ],
        })

        # CTA banner
        await create_block(pg.id, "cta_banner", config={"gradient_top": "#0f172a"}, content={
            "title_zh": "携手金捷利，共创智慧建筑未来",
            "title_en": "Partner with GOLDGINNY for a Smarter Building Future",
            "description_zh": "立即联系我们，获取专属智慧建筑解决方案",
            "description_en": "Contact us now for a tailored smart building solution",
            "button_text_zh": "立即咨询",
            "button_text_en": "Get Started",
            "button_link": "/cooperation",
        })

        # 2b. Solutions ---------------------------------------------------
        slug = "solutions"
        pg = await create_page(
            name_zh="解决方案", name_en="Solutions", slug=slug,
            type="content", sort_order=2, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={"full_height": False}, content={
            "slides": [{
                "title_zh": "解决方案",
                "title_en": "Solutions",
                "subtitle_zh": "覆盖楼宇控制、系统深度寻优到工业设施控制的全场景化综合能源效率提升解决方案",
                "subtitle_en": "Full-scenario comprehensive energy efficiency improvement solutions covering building control, deep system optimization, and industrial facility control",
                "image": "",
                "buttons": [],
            }],
        })

        await create_block(pg.id, "solution_cards", config={}, content={
            "title_zh": "解决方案",
            "title_en": "Solutions",
            "subtitle_zh": "覆盖楼宇控制、系统深度寻优到工业设施控制的全场景化综合能源效率提升解决方案",
            "subtitle_en": "Full-scenario comprehensive energy efficiency improvement solutions covering building control, deep system optimization, and industrial facility control",
            "tabs": [
                {
                    "key": "commercial",
                    "label_zh": "商业综合体",
                    "label_en": "Commercial",
                    "title_zh": "商业综合体智慧运维方案",
                    "title_en": "Smart Operations for Commercial Complexes",
                    "desc_zh": "针对商业综合体能耗高、设备多、人流大的特点，提供涵盖暖通空调优化、智能照明、室内环境监测、综合安防的一站式解决方案。通过金捷利自研的冷热源自适应算法，CBD核心区项目实测综合节能率达28.5%。",
                    "desc_en": "A one-stop solution covering HVAC optimization, smart lighting, indoor environment monitoring, and integrated security for commercial complexes. Our self-developed adaptive algorithm achieved 28.5% energy savings in a CBD core-area project.",
                    "features": [
                        {"text_zh": "冷热源自适应调控", "text_en": "Adaptive cooling/heating source control"},
                        {"text_zh": "分区分时照明策略", "text_en": "Zone-based scheduled lighting strategy"},
                        {"text_zh": "室内环境实时监测", "text_en": "Real-time indoor environment monitoring"},
                        {"text_zh": "设备预测性维护", "text_en": "Predictive equipment maintenance"},
                        {"text_zh": "综合安防联动", "text_en": "Integrated security coordination"},
                    ],
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
                    "features": [
                        {"text_zh": "多楼宇统一监控", "text_en": "Multi-building unified monitoring"},
                        {"text_zh": "能源梯级调度", "text_en": "Cascaded energy dispatch"},
                        {"text_zh": "碳排放实时核算", "text_en": "Real-time carbon emission accounting"},
                        {"text_zh": "园区级安防联动", "text_en": "Park-wide security coordination"},
                        {"text_zh": "智能运维工单", "text_en": "Smart O&M work orders"},
                    ],
                    "link": "/cooperation",
                },
                {
                    "key": "office",
                    "label_zh": "5A写字楼",
                    "label_en": "5A Office",
                    "title_zh": "5A写字楼智能化方案",
                    "title_en": "Smart Solutions for 5A Office Buildings",
                    "desc_zh": "为5A级写字楼提供暖通空调优化、智能照明、室内环境品质管理和智慧停车等系统，提升租户满意度与物业资产价值。",
                    "desc_en": "HVAC optimization, smart lighting, indoor environmental quality management, and smart parking for 5A office buildings, enhancing tenant satisfaction and property asset value.",
                    "features": [
                        {"text_zh": "新风按需供给", "text_en": "Demand-driven fresh air supply"},
                        {"text_zh": "办公环境舒适度管理", "text_en": "Office comfort management"},
                        {"text_zh": "能源分项计量", "text_en": "Sub-metering by energy category"},
                        {"text_zh": "智慧停车引导", "text_en": "Smart parking guidance"},
                        {"text_zh": "租户能耗账单", "text_en": "Tenant energy billing"},
                    ],
                    "link": "/cooperation",
                },
                {
                    "key": "medical",
                    "label_zh": "公共建筑",
                    "label_en": "Public",
                    "title_zh": "公共建筑智慧运维方案",
                    "title_en": "Smart Operations for Public Buildings",
                    "desc_zh": "面向医院、政府办公楼等公共建筑，提供洁净空调管理、医疗级环境监控和能效合规管理，满足GB/T 51153等国家标准要求。",
                    "desc_en": "Clean air management, medical-grade environment monitoring, and energy compliance for hospitals and government buildings, meeting GB/T 51153 standards.",
                    "features": [
                        {"text_zh": "洁净区域环境管控", "text_en": "Clean-area environment control"},
                        {"text_zh": "医疗设备能耗监测", "text_en": "Medical equipment energy monitoring"},
                        {"text_zh": "环境参数合规记录", "text_en": "Environmental compliance recording"},
                        {"text_zh": "应急联动响应", "text_en": "Emergency coordinated response"},
                        {"text_zh": "后勤运维管理", "text_en": "Logistics O&M management"},
                    ],
                    "link": "/cooperation",
                },
                {
                    "key": "hotel",
                    "label_zh": "中高端酒店",
                    "label_en": "Hotel",
                    "title_zh": "中高端酒店智慧能效方案",
                    "title_en": "Smart Energy Efficiency for Upscale Hotels",
                    "desc_zh": "针对中高端酒店客房舒适度与能耗平衡的痛点，打通前台PMS预订系统与客房RCU控制系统，结合大楼暖通总控智能预设开房微环境，依据入住状态动态调节空调冷热载荷，兼顾宾客品质体验与酒店低碳运营目标。",
                    "desc_en": "Addressing the balance between guest comfort and energy consumption in upscale hotels by integrating front-desk PMS with room RCU control systems and building HVAC master control for intelligent room environment presets based on occupancy status.",
                    "features": [
                        {"text_zh": "打通前台PMS与客房RCU系统", "text_en": "Integrate front-desk PMS with guest-room RCU systems"},
                        {"text_zh": "依据开房入住状态智能预设空调冷热载荷", "text_en": "Intelligently preset HVAC load based on occupancy status"},
                        {"text_zh": "兼顾品质体验与低碳运营", "text_en": "Balance quality experience with low-carbon operations"},
                        {"text_zh": "公区新风按需调节", "text_en": "Demand-driven fresh air in public areas"},
                        {"text_zh": "热水系统智能调度", "text_en": "Smart hot water system dispatch"},
                    ],
                    "link": "/cooperation",
                },
                {
                    "key": "datacenter",
                    "label_zh": "数据中心",
                    "label_en": "Data Center",
                    "title_zh": "数据中心高能效制冷方案",
                    "title_en": "High-Efficiency Cooling for Data Centers",
                    "desc_zh": "面向高密度数据中心制冷能效挑战，结合气流场热力梯度传感器网络，对不间断工作的计算物理机网格进行冷量智慧分配。通过冷热源末端预测调节与冷却塔智能变频联合调度，深度逼近极致能效PUE目标。",
                    "desc_en": "For high-density data center cooling challenges, leveraging airflow thermal gradient sensor networks for intelligent cooling distribution across computing grids. Combines terminal predictive regulation with smart variable-frequency cooling tower dispatch to approach ultimate PUE targets.",
                    "features": [
                        {"text_zh": "结合气流场热力梯度传感器智慧分配冷量", "text_en": "Leverage thermal gradient sensors for intelligent cooling distribution"},
                        {"text_zh": "冷热源末端预测调节与冷却塔智能变频联合调度", "text_en": "Joint dispatch of predictive terminal regulation and variable-frequency cooling tower"},
                        {"text_zh": "深度逼近极致能效PUE", "text_en": "Drive PUE toward ultimate efficiency"},
                        {"text_zh": "热点自动识别与消除", "text_en": "Automatic hotspot identification and elimination"},
                        {"text_zh": "机柜级精细温控", "text_en": "Rack-level precision temperature control"},
                    ],
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

        await create_block(pg.id, "hero", config={"full_height": False}, content={
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
                    "title_zh": "IoT无线温湿度传感器组",
                    "title_en": "IoT Wireless Temperature & Humidity Sensor Suite",
                    "desc_zh": "高精度温湿度采集，支持LoRa/WiFi/NB-IoT多种无线通信方式，实现建筑环境全域分布式感知与智能联动。",
                    "desc_en": "High-precision temperature and humidity data collection with multi-protocol wireless communication for comprehensive distributed environmental sensing and intelligent linkage.",
                    "link": "/contact",
                },
                {
                    "title_zh": "智能微机电保护监控模块",
                    "title_en": "Smart MEMS Protection & Monitoring Module",
                    "desc_zh": "集成电流、电压、功率因数实时监测与智能断路保护功能，实现对配电系统的精细化安全管控与故障预警。",
                    "desc_en": "Integrated real-time monitoring of current, voltage, and power factor with smart circuit protection for precise power distribution safety management and fault early warning.",
                    "link": "/contact",
                },
                {
                    "title_zh": "多信道数据采集终端",
                    "title_en": "Multi-Channel Data Acquisition Terminal",
                    "desc_zh": "支持8/16/32信道模拟量与数字量同步采集，兼容各类工业传感器协议，构建建筑机电系统的全息感知网络。",
                    "desc_en": "Supports 8/16/32-channel synchronous analog and digital signal acquisition compatible with various industrial sensor protocols, building a holographic perception network for building MEP systems.",
                    "link": "/contact",
                },
                {
                    "title_zh": "智能超声波流速热量计",
                    "title_en": "Smart Ultrasonic Flow & Heat Meter",
                    "desc_zh": "非侵入式超声波流量测量与冷热量精确计量，为暖通空调系统能效分析与优化提供核心数据支撑。",
                    "desc_en": "Non-invasive ultrasonic flow measurement and precise thermal metering for HVAC energy efficiency analysis and optimization with core data support.",
                    "link": "/contact",
                },
                {
                    "title_zh": "六合一多参数环境监视箱",
                    "title_en": "6-in-1 Multi-Parameter Environmental Monitoring Box",
                    "desc_zh": "集成温度、湿度、CO2、PM2.5、TVOC、噪声六项环境指标，支持全天候室内外环境质量综合评估与预警。",
                    "desc_en": "Integrates six environmental indicators for comprehensive indoor/outdoor air quality assessment and early warning.",
                    "link": "/contact",
                },
                {
                    "title_zh": "智能红外温度阵列探针",
                    "title_en": "Smart Infrared Thermal Array Probe",
                    "desc_zh": "高分辨率红外阵列测温技术，非接触式实时监测设备表面温度分布，助力设备异常早期发现与预测性维护。",
                    "desc_en": "High-resolution infrared array thermometry for contactless real-time equipment surface temperature distribution monitoring, supporting early anomaly detection and predictive maintenance.",
                    "link": "/contact",
                },
                {
                    "title_zh": "电能安全及综合平衡仪",
                    "title_en": "Power Safety & Integrated Balancer",
                    "desc_zh": "三相电能质量实时监测与三相负荷不平衡智能调节一体化设备，保障建筑配电系统安全高效稳定运行。",
                    "desc_en": "Integrated three-phase power quality monitoring and three-phase load imbalance intelligent regulation device for safe, efficient, and stable building power distribution.",
                    "link": "/contact",
                },
            ],
        })

        # 2d. About -------------------------------------------------------
        slug = "about"
        pg = await create_page(
            name_zh="关于我们", name_en="About Us", slug=slug,
            type="content", sort_order=5, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={"full_height": False}, content={
            "slides": [{
                "title_zh": "关于金捷利",
                "title_en": "About GOLDGINNY",
                "subtitle_zh": "专注建筑智能运维，以技术赋能建筑全生命周期高效管理",
                "subtitle_en": "Focused on intelligent building operations, empowering full-lifecycle building management with technology",
                "image": "",
                "buttons": [],
            }],
        })

        # Company introduction (rich text)
        await create_block(pg.id, "richtext", config={}, content={
            "html_content_zh": (
                '<h2 class="text-2xl font-bold mb-6">公司介绍</h2>'
                '<p class="text-lg leading-relaxed mb-4">'
                '金捷利科技（北京）有限公司成立于2018年12月，总部位于北京，是专精特新中小企业，'
                '国高新/村高新技术企业，致力于以AI与IoT技术赋能建筑节能与智慧运维。'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                '公司创始团队来自清华大学建筑节能研究中心、阿里巴巴达摩院与华为2012实验室，'
                '在建筑热物理、机器学习、边缘计算与工业控制领域有超过15年的产学研积累。'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                '金捷利以"让每一栋建筑都拥有智慧大脑"为使命，自主研发了AI冷热源自适应算法引擎、'
                'Edge-G系列智能边缘网关、IoT综合环境感知终端、多联机智能群控系统等核心产品，'
                '形成"端-边-云"三位一体的全栈智慧建筑解决方案。'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                '公司自研的冷热源自适应算法经国家第三方检测机构验证，平均节能率达28.5%，'
                '已入选《国家推荐绿色技术名录》。金捷利拥有发明专利12项、软件著作权30余项，'
                '参与编制国家标准2项、行业标准4项。'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                '截至目前，金捷利已累计为全国超过500栋建筑提供智慧运维产品与服务，'
                '覆盖商业综合体、5A写字楼、产业园区、三甲医院、中高端酒店和数据中心等多种业态，'
                '服务面积超过3000万平方米，累计为客户节省能耗成本逾3亿元，'
                '减排二氧化碳超过15万吨。'
                '</p>'
                '<p class="text-lg leading-relaxed">'
                '公司荣获2025年度「智慧建筑优秀服务商」称号，'
                '核心解决方案入选工信部「工业互联网+绿色制造」试点示范项目。'
                '金捷利将持续深耕建筑智能运维赛道，以技术创新推动建筑行业绿色低碳转型，'
                '助力中国"3060双碳"目标实现。'
                '</p>'
            ),
            "html_content_en": (
                '<h2 class="text-2xl font-bold mb-6">Company Overview</h2>'
                '<p class="text-lg leading-relaxed mb-4">'
                'GOLDGINNY Technology (Beijing) Co., Ltd., founded in December 2018 and headquartered '
                'in Beijing, is a specialized and sophisticated SME and a national/regional high-tech '
                'enterprise dedicated to empowering building energy efficiency and smart operations '
                'through AI and IoT technologies.'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                'Our founding team comes from Tsinghua University\'s Building Energy Research Center, '
                'Alibaba DAMO Academy, and Huawei 2012 Labs, with over 15 years of combined expertise '
                'in building thermal physics, machine learning, edge computing, and industrial control.'
                '</p>'
                '<p class="text-lg leading-relaxed mb-4">'
                'With the mission of "giving every building a smart brain," GOLDGINNY has independently '
                'developed core products including the AI HVAC adaptive algorithm engine, Edge-G series '
                'smart edge gateways, IoT environmental sensing terminals, and multi-unit intelligent '
                'group control systems — forming an integrated "edge-to-cloud" smart building solution.'
                '</p>'
            ),
        })

        # Value cards (mission, vision, philosophy)
        await create_block(pg.id, "product_cards", config={}, content={
            "title_zh": "企业文化",
            "title_en": "Corporate Culture",
            "cards": [
                {
                    "title_zh": "核心使命",
                    "title_en": "Core Mission",
                    "desc_zh": "让每一栋建筑都拥有智慧大脑。以AI与IoT技术深度赋能建筑机电系统，实现建筑全生命周期的智能化、精细化管理，为业主降本增效、为使用者营造舒适、为地球减少碳排。",
                    "desc_en": "Giving every building a smart brain. Deeply empowering building MEP systems with AI and IoT technologies to achieve intelligent, refined lifecycle management — reducing costs for owners, creating comfort for users, and cutting carbon for the planet.",
                    "link": "",
                },
                {
                    "title_zh": "愿景目标",
                    "title_en": "Vision & Goals",
                    "desc_zh": '成为中国领先的AI绿色空间运营商。以技术创新为驱动，以客户价值为导向，推动建筑行业从“被动运维”迈向“主动智慧”，引领绿色建筑运维新标准。',
                    "desc_en": "To become China\'s leading AI green space operator. Driven by technological innovation and guided by customer value, we propel the building industry from passive O&M to proactive intelligence, setting new standards for green building operations.",
                    "link": "",
                },
                {
                    "title_zh": "服务理念",
                    "title_en": "Service Philosophy",
                    "desc_zh": "精于技术，忠于客户。我们不仅提供领先的AI产品与算法，更提供贯穿项目全周期的专业服务——从方案设计、系统集成到长效运维托管，成为客户可信赖的长期技术伙伴。",
                    "desc_en": "Masters of technology, devoted to clients. We deliver not only advanced AI products and algorithms but also professional full-cycle services — from solution design and system integration to long-term managed O&M — as our clients\' trusted technology partner.",
                    "link": "",
                },
            ],
        })

        # Stats counter on about page
        await create_block(pg.id, "stats_counter", config={}, content={
            "title_zh": "金捷利 · 实力数据",
            "title_en": "GOLDGINNY by the Numbers",
            "items": [
                {"value": "500+", "label_zh": "服务建筑", "label_en": "Buildings Served"},
                {"value": "80+", "label_zh": "覆盖城市", "label_en": "Cities Covered"},
                {"value": "28.5%", "label_zh": "平均节能率", "label_en": "Avg Energy Savings"},
                {"value": "99.9%", "label_zh": "系统可用率", "label_en": "System Uptime"},
            ],
        })

        # 2e. Cooperation -------------------------------------------------
        slug = "cooperation"
        pg = await create_page(
            name_zh="商务合作", name_en="Cooperation", slug=slug,
            type="content", sort_order=6, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={"full_height": False}, content={
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
            type="contact", sort_order=7, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={"full_height": False}, content={
            "slides": [{
                "title_zh": "联系我们",
                "title_en": "Contact Us",
                "subtitle_zh": "与金捷利建立连接，我们的专家团队竭诚为您服务",
                "subtitle_en": "Connect with GOLDGINNY, our expert team is at your service",
                "image": "",
                "buttons": [],
            }],
        })
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
            type="news", sort_order=8, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        # 2h. Cases -------------------------------------------------------
        slug = "cases"
        pg = await create_page(
            name_zh="服务案例", name_en="Cases", slug=slug,
            type="content", sort_order=4, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "hero", config={"full_height": False}, content={
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

        # 2i. Footer page (global footer content)
        slug = "footer"
        pg = await create_page(
            name_zh="全局底部", name_en="Global Footer", slug=slug,
            type="content", sort_order=99, is_published=True,
        )
        slug_to_id[slug] = pg.id
        print(f"  {slug} (id={pg.id})")

        await create_block(pg.id, "richtext", config={}, content={
            "html_content_zh": (
                '<p>金捷利科技（北京）有限公司成立于2018年12月，是国内领先的智慧运维综合解决方案服务商，'
                '致力于通过AIoT物联硬件+数智化软件+专业服务的一体化综合解决方案，'
                '推动智慧运维行业发展。</p>'
            ),
            "html_content_en": (
                '<p>GOLDGINNY Technology (Beijing) Co., Ltd., founded in December 2018, '
                'is a leading provider of smart O&M solutions, '
                'committed to driving the smart building industry forward.</p>'
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

        # --- Header menus (with 服务案例 inserted) ---
        header_items = [
            ("首页", "Home", "/", 1),
            ("解决方案", "Solutions", "/solutions", 2),
            ("产品服务", "Products", "/products", 3),
            ("服务案例", "Cases", "/cases", 4),
            ("关于我们", "About", "/about", 5),
            ("商务合作", "Cooperation", "/cooperation", 6),
            ("联系我们", "Contact", "/contact", 7),
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
            ("5A写字楼", "5A Office Building", "/solutions?tab=office"),
            ("公共建筑", "Public Building", "/solutions?tab=medical"),
            ("中高端酒店", "Upscale Hotel", "/solutions?tab=hotel"),
            ("数据中心", "Data Center", "/solutions?tab=datacenter"),
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
            # news-01
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
            # news-02
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
            # news-03
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
            # news-04
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
            # news-05
            (
                "金捷利发布新一代边缘计算网关Edge-G200，AI算力提升5倍",
                "GOLDGINNY Launches Next-Gen Edge-G200 Gateway with 5x AI Computing Power",
                "金捷利在2025中国国际智能建筑展上正式发布Edge-G200智能边缘网关，AI推理算力较上一代提升5倍，支持更复杂的本地决策模型。",
                "GOLDGINNY officially launched the Edge-G200 smart edge gateway at the 2025 China International Intelligent Building Expo, delivering 5x AI inference power for more complex local decision models.",
                (
                    "<p>在2025中国国际智能建筑展览会上，金捷利科技正式发布了新一代智能边缘网关产品——Edge-G200。"
                    "该产品搭载全新一代NPU芯片，AI推理算力相较上一代Edge-G100提升5倍，可同时在本地运行多个"
                    "深度学习模型，实现更精准的空调负荷预测与设备故障诊断。</p>"
                    "<p>Edge-G200延续了金捷利“端-边-云”协同架构的设计理念，新增支持TSN时间敏感网络和5G通信模块，"
                    "为智慧建筑的实时控制与大数据量传输提供了更强大的通信保障。产品同时向下兼容Edge-G100的"
                    "全部协议接口，支持存量项目的平滑升级。</p>"
                    "<p>金捷利CTO在产品发布会上表示：“Edge-G200的发布标志着金捷利在建筑边缘智能领域迈上了新台阶，"
                    '我们将持续加大研发投入，以技术创新引领行业发展。"</p>'
                ),
                (
                    "<p>At the 2025 China International Intelligent Building Expo, GOLDGINNY officially "
                    "launched the Edge-G200, its next-generation smart edge gateway. Equipped with a new "
                    "NPU chip, the product delivers 5x the AI inference power of its predecessor, enabling "
                    "multiple deep learning models to run locally for more accurate HVAC load prediction "
                    "and equipment fault diagnosis.</p>"
                    "<p>The Edge-G200 continues GOLDGINNY's edge-to-cloud collaborative architecture, "
                    "adding TSN and 5G support for real-time control and large data transmission in "
                    "smart buildings. It remains fully backward-compatible with all Edge-G100 protocols.</p>"
                ),
                "product",
            ),
            # news-06
            (
                "金捷利中标某新一线城市地铁智慧环控系统项目",
                "GOLDGINNY Wins Bid for Metro Smart Environmental Control System in New First-Tier City",
                "金捷利成功中标某新一线城市地铁线路智慧环控系统项目，将为其地下车站与隧道提供暖通节能优化与空气质量智能管控。",
                "GOLDGINNY won the bid for a metro line smart environmental control system project in a new first-tier city, providing HVAC energy optimization and air quality management for underground stations and tunnels.",
                (
                    "<p>近日，金捷利科技宣布成功中标某新一线城市新建地铁线路的智慧环控系统项目。"
                    "该项目涵盖该线路全部12座地下车站及区间隧道的暖通空调系统节能优化与环境质量控制，"
                    "标志着金捷利在轨道交通智慧运维领域的又一重大突破。</p>"
                    "<p>针对地铁车站客流量波动大、热负荷变化剧烈、空气质量要求高等特点，金捷利将部署"
                    "自研的冷热源自适应算法和多信道数据采集终端，结合车站客流实时数据，实现通风空调系统的"
                    "按需供给与精准调控。预计项目投运后，该线路环控系统综合节能率可达25%以上。</p>"
                    "<p>该项目是金捷利继商业建筑、产业园区、医疗建筑和数据中心之后，在轨道交通这一全新"
                    "业务领域的成功拓展，进一步验证了金捷利AI算法与产品矩阵的跨场景适应能力。</p>"
                ),
                (
                    "<p>GOLDGINNY announced it has won the bid for a smart environmental control system "
                    "project for a new metro line in a new first-tier city. The project covers HVAC energy "
                    "optimization and environmental quality control for all 12 underground stations and "
                    "tunnel sections, marking a significant breakthrough in rail transit smart O&M.</p>"
                    "<p>GOLDGINNY will deploy its self-developed HVAC adaptive algorithm and multi-channel "
                    "data acquisition terminals to achieve demand-driven ventilation and precise control "
                    "based on real-time passenger flow data, with expected 25%+ energy savings.</p>"
                ),
                "project",
            ),
            # news-07
            (
                "金捷利参与编制《建筑设备智能运维系统技术规范》正式发布",
                "GOLDGINNY Co-Authors Technical Specification for Building Equipment Smart O&M Systems",
                "由金捷利参与编制的团体标准《建筑设备智能运维系统技术规范》（T/CECS xxx-2025）正式发布，将于2026年1月1日起实施。",
                "The group standard 'Technical Specification for Building Equipment Smart O&M Systems' (T/CECS xxx-2025), co-authored by GOLDGINNY, has been officially published and will take effect on January 1, 2026.",
                (
                    "<p>近日，由中国建筑科学研究院牵头、金捷利科技作为主要参编单位之一的团体标准"
                    "《建筑设备智能运维系统技术规范》（T/CECS xxx-2025）正式发布。该标准规定了建筑设备"
                    "智能运维系统的架构设计、功能要求、数据接口、性能指标和评估方法。</p>"
                    "<p>金捷利作为标准的主要技术贡献方之一，将其在500余个智慧运维项目中的实践经验提炼为"
                    "标准条款，特别是在冷热源自适应控制、边缘计算网关数据采集、设备预测性维护等核心"
                    "技术环节贡献了关键技术指标和验证方法。</p>"
                    "<p>该标准的发布填补了国内建筑设备智能运维领域技术规范的空白，将为行业规范化发展"
                    "提供重要技术依据。金捷利CEO表示：\"参与行业标准制定是企业技术实力的体现，也是我们"
                    '推动行业高质量发展的责任。"</p>'
                ),
                (
                    "<p>The group standard 'Technical Specification for Building Equipment Smart O&M Systems' "
                    "(T/CECS xxx-2025), led by China Academy of Building Research with GOLDGINNY as a key "
                    "co-author, has been officially published. The standard specifies architecture design, "
                    "functional requirements, data interfaces, performance metrics, and evaluation methods.</p>"
                    "<p>GOLDGINNY contributed practical experience from over 500 smart O&M projects, "
                    "particularly in HVAC adaptive control, edge gateway data acquisition, and predictive "
                    "maintenance domains.</p>"
                ),
                "industry",
            ),
            # news-08
            (
                "金捷利智慧运维平台通过等保二级认证及ISO 27001信息安全管理体系认证",
                "GOLDGINNY Smart O&M Platform Achieves Level 2 Information Security Certification and ISO 27001",
                "金捷利智慧运维平台正式通过国家等保二级认证和ISO 27001信息安全管理体系认证，平台信息安全管理能力获权威认可。",
                "GOLDGINNY's smart O&M platform has officially passed China's Level 2 Information Security Protection certification and ISO 27001 ISMS certification.",
                (
                    "<p>近日，金捷利科技智慧运维管理平台先后通过了国家信息安全等级保护二级认证和"
                    "ISO/IEC 27001:2022信息安全管理体系认证，标志着金捷利在信息安全管理和客户数据保护方面"
                    "达到了国际标准水平。</p>"
                    "<p>在数字化转型加速的背景下，建筑运维数据的安全性和隐私保护日益受到关注。金捷利"
                    "智慧运维平台从架构设计之初即遵循\"安全即设计\"的理念，在数据采集、传输、存储、"
                    "处理和展示的全链路实施了多层次安全防护措施，包括设备身份认证、通信加密、"
                    "访问控制和审计日志等。</p>"
                    "<p>金捷利信息安全负责人表示：\"通过等保二级和ISO 27001双认证是金捷利信息安全建设的"
                    '重要里程碑，我们将在客户数据安全方面持续投入，为客户提供可信赖的服务。"</p>'
                ),
                (
                    "<p>GOLDGINNY's smart O&M platform has passed China's Level 2 Information Security "
                    "Protection certification and ISO/IEC 27001:2022 ISMS certification, marking "
                    "international-standard information security management and customer data protection.</p>"
                    "<p>The platform implements multi-layered security across the full data chain — "
                    "collection, transmission, storage, processing, and presentation — including device "
                    "authentication, communication encryption, access control, and audit logging.</p>"
                ),
                "certification",
            ),
            # news-09
            (
                "金捷利与清华大学联合研究成果发表于顶级期刊《Applied Energy》",
                "GOLDGINNY & Tsinghua University Joint Research Published in Applied Energy",
                "金捷利与清华大学建筑节能研究中心联合研究的成果论文在国际顶级期刊《Applied Energy》上发表，提出基于深度强化学习的建筑冷热源系统多目标优化控制方法。",
                "A joint research paper by GOLDGINNY and Tsinghua University's Building Energy Research Center has been published in Applied Energy, proposing a multi-objective optimization control method for building HVAC systems based on deep reinforcement learning.",
                (
                    "<p>近日，金捷利科技与清华大学建筑节能研究中心联合研究的学术论文"
                    "\"Multi-Objective Deep Reinforcement Learning for Optimal Control of Building "
                    "Heating and Cooling Systems\"在国际顶级学术期刊《Applied Energy》（IF: 11.2）上正式发表。</p>"
                    "<p>该论文提出了一种面向建筑冷热源系统的多目标深度强化学习控制框架，可在同时优化"
                    "系统能耗、室内热舒适度和设备运行寿命三个相互冲突的目标间实现动态平衡。该方法已在"
                    "金捷利智慧运维平台中工程化部署，并在超过100栋实际建筑中验证了其有效性和鲁棒性。</p>"
                    "<p>论文通讯作者、金捷利首席科学家表示：\"产学研深度融合是金捷利的核心创新模式。"
                    '此次与清华大学的合作成果发表于顶刊，是对我们技术路线的学术背书，也为行业提供了可复现的科学方法。"</p>'
                ),
                (
                    "<p>A joint research paper by GOLDGINNY and Tsinghua University titled 'Multi-Objective "
                    "Deep Reinforcement Learning for Optimal Control of Building Heating and Cooling Systems' "
                    "has been published in Applied Energy (IF: 11.2), a top-tier international journal.</p>"
                    "<p>The paper proposes a multi-objective deep reinforcement learning control framework "
                    "that dynamically balances energy consumption, indoor thermal comfort, and equipment "
                    "lifespan. The method has been deployed in GOLDGINNY's platform and validated across "
                    "over 100 real buildings.</p>"
                ),
                "research",
            ),
            # news-10
            (
                "金捷利完成A轮融资，加速智慧建筑全场景布局",
                "GOLDGINNY Completes Series A Funding to Accelerate Full-Scenario Smart Building Deployment",
                "金捷利科技宣布完成数千万元A轮融资，资金将用于AI算法研发升级、产品矩阵完善和全国市场拓展。",
                "GOLDGINNY announced the completion of tens of millions RMB in Series A funding to be used for AI algorithm R&D, product portfolio expansion, and nationwide market development.",
                (
                    "<p>近日，金捷利科技有限公司宣布完成数千万元人民币A轮融资。本轮融资由国内领先的"
                    "绿色科技投资机构领投，老股东跟投。资金将主要用于AI核心算法研发升级、硬件产品矩阵"
                    "完善、全国营销服务网络建设以及行业标准参与。</p>"
                    "<p>金捷利创始人兼CEO表示：\"本轮融资的完成体现了资本市场对建筑智能运维赛道和金捷利"
                    "技术实力的高度认可。我们将在保持技术领先优势的同时，加速全国市场的布局和行业标杆"
                    "项目的打造，致力于让更多的建筑享受到AI驱动的智慧运维服务。\"</p>"
                    "<p>据国家住建部数据，我国既有建筑面积已超过700亿平方米，年新增建筑面积约20亿平方米，"
                    "建筑运行阶段能耗占全社会总能耗的20%以上。金捷利所深耕的建筑智能运维和节能优化领域"
                    "市场空间广阔，是实现\"双碳\"目标的重要技术路径之一。</p>"
                ),
                (
                    "<p>GOLDGINNY Technology Co., Ltd. announced the completion of tens of millions RMB "
                    "in Series A funding, led by a leading domestic green technology investment institution "
                    "with participation from existing investors. The funds will be used for AI algorithm "
                    "R&D, product portfolio expansion, and national marketing network development.</p>"
                    "<p>The CEO stated: \"This funding round reflects the capital market's strong recognition "
                    "of the smart building O&M sector and GOLDGINNY's technical capabilities. We will "
                    "accelerate nationwide deployment and industry benchmark projects.\"</p>"
                ),
                "company_news",
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
                "summary_zh": "专为中大型智慧建筑系统集成设计的物理通信中枢，支持Bacnet/Modbus/OPC UA等多协议接入与边缘计算。",
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
                "name_zh": "IoT无线温湿度传感器组",
                "name_en": "IoT Wireless Temperature & Humidity Sensor Suite",
                "slug": "iot-temp-humidity-sensor",
                "summary_zh": "高精度温湿度采集，支持LoRa/WiFi/NB-IoT多种无线通信方式，实现建筑环境全域分布式感知。",
                "summary_en": "High-precision temperature and humidity data collection with multi-protocol wireless communication for comprehensive distributed environmental sensing.",
                "description_zh": (
                    "金捷利IoT无线温湿度传感器组是专为大型建筑空间设计的分布式环境感知系统，"
                    "由多个无线传感器节点和协调网关组成。单节点支持温度（精度±0.2℃）、湿度"
                    "（精度±2%RH）的高精度采集，可选LoRa、WiFi、NB-IoT等多种无线通信方式，"
                    "覆盖半径可达500米（LoRa模式）。支持电池供电超低功耗运行（续航2年以上），"
                    "适合既有建筑改造项目的免布线快速部署。"
                ),
                "description_en": (
                    "The GOLDGINNY IoT Wireless Temperature & Humidity Sensor Suite is a distributed "
                    "environmental perception system for large building spaces. Each node provides "
                    "high-precision temperature (±0.2°C) and humidity (±2%RH) measurement with "
                    "LoRa, WiFi, or NB-IoT connectivity, covering up to 500m range (LoRa). Ultra-low "
                    "power battery operation enables 2+ year autonomy, ideal for retrofit projects."
                ),
                "sort_order": 2,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "智能微机电保护监控模块",
                "name_en": "Smart MEMS Protection & Monitoring Module",
                "slug": "mems-protection-monitor",
                "summary_zh": "集成电流、电压、功率因数实时监测与智能断路保护，实现配电系统精细化安全管控。",
                "summary_en": "Integrated real-time monitoring of current, voltage, and power factor with smart circuit protection for precise power distribution safety management.",
                "description_zh": (
                    "金捷利智能微机电保护监控模块是针对建筑配电回路精细化管理的创新产品。"
                    "模块集成高精度电流互感器、电压采样单元和MEMS微机电执行器，可对单个配电"
                    "回路进行电流、电压、功率因数、谐波等电气参数的实时监测，并在检测到异常时"
                    "自主执行断路保护。支持Modbus RTU通信，可无缝接入金捷利智慧运维平台或第三方"
                    "楼宇自控系统，实现配电系统的全链路可视化与智能化运维。"
                ),
                "description_en": (
                    "The GOLDGINNY Smart MEMS Protection & Monitoring Module enables fine-grained "
                    "management of building power distribution circuits. It integrates precision CT, "
                    "voltage sampling, and MEMS actuators for real-time monitoring of current, voltage, "
                    "power factor, and harmonics per circuit, with autonomous trip protection. Modbus RTU "
                    "support enables seamless integration with GOLDGINNY or third-party BMS platforms."
                ),
                "sort_order": 3,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "多信道数据采集终端",
                "name_en": "Multi-Channel Data Acquisition Terminal",
                "slug": "multi-channel-daq",
                "summary_zh": "支持8/16/32信道模拟量与数字量同步采集，适配各类工业传感器，构建建筑机电系统全息感知网络。",
                "summary_en": "Supports 8/16/32-channel synchronous analog and digital signal acquisition compatible with various industrial sensors for building MEP system perception.",
                "description_zh": (
                    "金捷利多信道数据采集终端是面向建筑机电系统全面感知需求的高密度数据采集设备。"
                    "支持8/16/32信道可选配置，兼容4-20mA、0-10V、热电偶、热电阻、脉冲、RS485等"
                    "多种工业传感器信号类型。内置信号调理和抗混叠滤波电路，采样率达1kHz/信道，"
                    "支持边缘端数据缓存和批量上传。适用于冷热源机房、变配电站等传感器密集场景的"
                    "集中接入，大幅简化现场接线与系统集成复杂度。"
                ),
                "description_en": (
                    "The GOLDGINNY Multi-Channel Data Acquisition Terminal is a high-density DAQ device "
                    "for comprehensive building MEP system perception. Available in 8/16/32-channel "
                    "configurations, it supports 4-20mA, 0-10V, thermocouple, RTD, pulse, and RS485 "
                    "signal types. With 1kHz/channel sampling, onboard signal conditioning, and edge "
                    "buffering, it is ideal for sensor-dense environments like chiller plants and "
                    "substations, significantly simplifying field wiring and system integration."
                ),
                "sort_order": 4,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "智能超声波流速热量计",
                "name_en": "Smart Ultrasonic Flow & Heat Meter",
                "slug": "ultrasonic-heat-meter",
                "summary_zh": "非侵入式超声波流量测量与冷热量精确计量，为暖通系统能效分析提供核心数据支撑。",
                "summary_en": "Non-invasive ultrasonic flow measurement and precise thermal metering for HVAC energy efficiency analysis with core data support.",
                "description_zh": (
                    "金捷利智能超声波流速热量计采用时差法超声波测量原理，通过管壁外贴式传感器实现"
                    "非侵入式流量测量，无需管道切割或停水安装。产品同步采集供回水温度，实时计算瞬时"
                    "热量/冷量和累计热量/冷量值，精度达2级。支持DN25-DN1200管径范围，适用于空调"
                    "冷冻水、冷却水及采暖热水系统的冷热量独立核算与能效评估。内置Modbus/Bacnet通信接口，"
                    "可直接接入楼宇自控系统或金捷利智慧运维平台。"
                ),
                "description_en": (
                    "The GOLDGINNY Smart Ultrasonic Flow & Heat Meter uses transit-time ultrasonic "
                    "measurement with clamp-on sensors for non-invasive flow measurement — no pipe cutting "
                    "or system shutdown required. It simultaneously measures supply/return temperatures "
                    "for real-time and cumulative thermal energy calculation with Class 2 accuracy. "
                    "Suitable for DN25-DN1200 pipes in chilled water, cooling water, and heating water "
                    "systems. Built-in Modbus/Bacnet interfaces for direct BMS or platform integration."
                ),
                "sort_order": 5,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "六合一多参数环境监视箱",
                "name_en": "6-in-1 Multi-Parameter Environmental Monitoring Box",
                "slug": "6in1-env-monitor",
                "summary_zh": "集成温度、湿度、CO2、PM2.5、TVOC、噪声六项指标，全天候室内外环境质量综合评估。",
                "summary_en": "Integrates six indicators for comprehensive indoor/outdoor environmental quality assessment with 24/7 monitoring capability.",
                "description_zh": (
                    "金捷利六合一多参数环境监视箱将温度、湿度、CO2浓度、PM2.5、TVOC和噪声六项核心"
                    "环境指标集成于一个工业级防护箱体内，支持壁挂或立杆安装，适用于室内大堂、走廊和"
                    "室外公共区域的24小时环境质量监测。采用进口传感器模组和自校准算法，长期漂移小，"
                    "维护周期长。支持4G/WiFi/LoRa多模通信，内置显示屏可本地展示实时数据，也可将数据"
                    "上传至金捷利智慧运维平台或第三方环境监测平台。"
                ),
                "description_en": (
                    "The GOLDGINNY 6-in-1 Multi-Parameter Environmental Monitoring Box integrates "
                    "temperature, humidity, CO2, PM2.5, TVOC, and noise into a single industrial-grade "
                    "enclosure for wall or pole mounting. Suitable for 24/7 monitoring in indoor lobbies, "
                    "corridors, and outdoor public areas. Imported sensor modules with self-calibration "
                    "algorithms ensure low drift and long maintenance intervals. 4G/WiFi/LoRa multi-mode "
                    "communication with local display and cloud data upload capability."
                ),
                "sort_order": 6,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "智能红外温度阵列探针",
                "name_en": "Smart Infrared Thermal Array Probe",
                "slug": "ir-thermal-array",
                "summary_zh": "高分辨率红外阵列测温，非接触式实时监测设备表面温度分布，助力设备异常预警与预测性维护。",
                "summary_en": "High-resolution infrared array thermometry for contactless real-time equipment surface temperature monitoring and predictive maintenance.",
                "description_zh": (
                    "金捷利智能红外温度阵列探针采用32×24像素红外热电堆阵列传感器，可实现768个测温点"
                    "的非接触式温度分布成像。探针视场角为110°×75°，测温范围-20℃至300℃，精度±1.5℃。"
                    "产品专为电气柜、配电箱、电机轴承、管道阀门等关键设备的温度异常监测设计，可自主"
                    "学习设备正常工作温度模式，在温差异常时即时预警。支持RS485/Modbus通信，可成组部署"
                    "构建设备热成像监测网络，是预测性维护体系的核心感知终端之一。"
                ),
                "description_en": (
                    "The GOLDGINNY Smart Infrared Thermal Array Probe uses a 32×24 pixel IR thermopile "
                    "array for contactless temperature distribution imaging with 768 measurement points. "
                    "With a 110°×75° FOV and -20°C to 300°C range (±1.5°C accuracy), it is designed for "
                    "temperature anomaly monitoring of electrical cabinets, distribution boxes, motor "
                    "bearings, and pipe valves. Self-learning normal temperature patterns enable early "
                    "anomaly warning. RS485/Modbus support for networked thermal monitoring deployment."
                ),
                "sort_order": 7,
                "is_published": True,
            },
            {
                "category_id": cat.id,
                "name_zh": "电能安全及综合平衡仪",
                "name_en": "Power Safety & Integrated Balancer",
                "slug": "power-safety-balancer",
                "summary_zh": "三相电能质量监测与三相负荷不平衡智能调节一体化设备，保障建筑配电系统安全高效运行。",
                "summary_en": "Integrated three-phase power quality monitoring and load imbalance intelligent regulation device for safe, efficient building power distribution.",
                "description_zh": (
                    "金捷利电能安全及综合平衡仪是将三相电能质量分析与三相不平衡自动调节功能集于一体的"
                    "创新型配电侧产品。设备实时监测三相电压、电流、有功/无功功率、谐波畸变率等电气参数，"
                    "并在检测到三相负荷不平衡时通过内置IGBT功率模组自动投切补偿，将中性线电流控制在"
                    "安全范围内，有效降低变压器损耗和线路发热。产品适用于大型商业建筑、数据中心和工业厂房"
                    "的低压配电系统，是建筑电气安全和能效提升的重要保障设备。"
                ),
                "description_en": (
                    "The GOLDGINNY Power Safety & Integrated Balancer combines three-phase power quality "
                    "analysis with automatic three-phase imbalance correction in a single innovative device. "
                    "It monitors voltage, current, active/reactive power, and THD in real time, and "
                    "automatically switches compensation via built-in IGBT power modules when phase imbalance "
                    "is detected, keeping neutral current within safe limits and reducing transformer losses "
                    "and line heating. Suitable for LV distribution in large commercial buildings, data "
                    "centers, and industrial plants."
                ),
                "sort_order": 8,
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
            # case-01: 北京某超甲级写字楼智慧运维项目
            {
                "name_zh": "北京某超甲级写字楼智慧运维项目",
                "name_en": "Beijing Premium Grade-A Office Smart O&M Project",
                "slug": "beijing-gradea-office",
                "category": "office",
                "summary_zh": "为北京CBD核心区某超甲级写字楼部署金捷利全栈智慧运维系统，实现综合节能率28.5%，故障响应时间缩短60%，人均管理面积提升2.4倍。",
                "summary_en": "Deployed GOLDGINNY full-stack smart O&M system at a premium Grade-A office in Beijing CBD, achieving 28.5% energy savings, 60% faster fault response, and 2.4x per-capita management area improvement.",
                "content_zh": (
                    "<p>项目位于北京CBD核心区，建筑高度260米，共58层，总建筑面积约18万平方米，"
                    "是区域内标杆性超甲级写字楼。项目面临的挑战包括：暖通空调系统能耗占大楼总能耗"
                    "45%以上，设备种类多、系统耦合复杂，运维依赖人工经验，故障发现和响应效率低。</p>"
                    "<p>金捷利为该项目部署了完整的智慧运维解决方案：在设备层，安装了Edge-G100智能边缘网关、"
                    "多信道数据采集终端和IoT无线温湿度传感器组，实现冷热源、新风、末端空调、供配电、"
                    "给排水等系统的全量数据接入；在平台层，部署了数字孪生可视化平台和AI能耗优化引擎，"
                    "实现对大楼机电系统的实时监控、智能诊断和优化控制。</p>"
                    "<p>核心节能措施包括：冷热源系统采用金捷利自适应群控算法，根据室外气象、室内负荷"
                    "和电价信号动态调节主机出力与水温设定；新风系统基于室内CO2浓度和人员密度实现"
                    "按需供给；末端空调结合分区分时策略精准控温。项目实施周期6个月，上线运行一年后"
                    "实测综合节能率28.5%，年节省电费超过600万元人民币。</p>"
                    "<p>在运维管理方面，系统实现了设备故障的自动诊断和工单自动派发，故障响应时间从"
                    "平均45分钟缩短至18分钟（降幅60%），运维人员人均管理面积从2.5万㎡提升至6万㎡"
                    "（提升2.4倍），预防性维护占比从15%提升至65%。</p>"
                ),
                "content_en": (
                    "<p>Located in Beijing's CBD core area, this landmark premium Grade-A office building "
                    "stands 260 meters tall with 58 floors and approximately 180,000 sqm of total floor area. "
                    "Challenges included HVAC accounting for over 45% of total energy consumption, complex "
                    "multi-system coupling, and experience-dependent O&M with slow fault response.</p>"
                    "<p>GOLDGINNY deployed a comprehensive smart O&M solution: Edge-G100 gateways, "
                    "multi-channel DAQ terminals, and IoT wireless sensor suites for full data integration "
                    "across chiller plants, fresh air, terminal HVAC, power distribution, and water systems; "
                    "a digital twin visualization platform and AI energy optimization engine for real-time "
                    "monitoring, intelligent diagnostics, and optimal control.</p>"
                    "<p>After 6 months of implementation and one year of operation, verified results "
                    "include 28.5% comprehensive energy savings, saving over 6M RMB annually in electricity.</p>"
                ),
                "stats": [
                    {"label_zh": "综合节能率", "label_en": "Energy Savings", "value": "28.5%"},
                    {"label_zh": "故障响应时间", "label_en": "Fault Response", "value": "-60%"},
                    {"label_zh": "人均管理面积提升", "label_en": "Per-Capita Management", "value": "2.4倍"},
                ],
                "sort_order": 1,
                "is_published": True,
            },
            # case-02: 上海某大型商业综合体全生命周期管理
            {
                "name_zh": "上海某大型商业综合体全生命周期管理",
                "name_en": "Shanghai Large Commercial Complex Full-Lifecycle Management",
                "slug": "shanghai-commercial-complex",
                "category": "commercial",
                "summary_zh": "为上海核心商圈某大型商业综合体提供暖通系统全生命周期运维托管服务，碳减排量850吨/年，舒适度投诉率降低45%，维保工作闭环率100%。",
                "summary_en": "Provided full-lifecycle HVAC O&M managed services for a major Shanghai commercial complex, reducing carbon emissions by 850t/year, comfort complaints by 45%, and achieving 100% maintenance work order closure.",
                "content_zh": (
                    "<p>项目位于上海核心商圈，总建筑面积约28万平方米，包含高端购物中心、五星级酒店、"
                    "甲级写字楼和服务式公寓四种业态，日均客流量超过10万人次。项目采用全生命周期运维托管"
                    "模式，金捷利不仅提供智慧运维系统和AI算法，还承担了暖通空调系统的日常运维、"
                    "预防性维护和应急响应等全部管理责任。</p>"
                    "<p>针对综合体多业态、多时段的运行特点，金捷利团队基于自研的冷热源自适应算法和"
                    "多联机群控系统，为购物中心、酒店、写字楼和公寓分别制定了差异化的控制策略。"
                    "商业区域依据人流热力数据和室外气象动态调节；酒店区域结合PMS系统按客房入住状态"
                    "智能切换；写字楼按工作日/节假日及预约加班信息分时管控。</p>"
                    "<p>项目部署了全域IoT无线传感器网络（超过3000个传感节点），通过Edge-G100边缘网关"
                    "实现多系统数据汇聚和本地化决策。数字孪生平台提供了一屏总览的运维驾驶舱，运维团队"
                    "可通过移动端随时随地查看设备状态和处理工单。</p>"
                    "<p>经过一年半的持续优化运营，项目取得了显著成效：年碳减排量850吨，相当于种植"
                    "4.7万棵树木的年碳汇量；基于室内环境监测数据，舒适度投诉率同比下降45%；维保工单"
                    "按时完成率和闭环率均达到100%；设备故障率下降32%，关键设备可用率达到99.8%。</p>"
                ),
                "content_en": (
                    "<p>Located in Shanghai's prime commercial district, this 280,000 sqm complex encompasses "
                    "a luxury shopping mall, five-star hotel, Grade-A office tower, and serviced apartments, "
                    "with over 100,000 daily visitors. GOLDGINNY provides a full-lifecycle managed service "
                    "covering smart O&M systems, AI algorithms, and complete HVAC daily O&M, preventive "
                    "maintenance, and emergency response.</p>"
                    "<p>After 18 months of continuous optimization, results include 850 tons of annual carbon "
                    "reduction, 45% fewer comfort complaints, 100% maintenance work order closure rate, "
                    "32% lower equipment failure rate, and 99.8% critical equipment availability.</p>"
                ),
                "stats": [
                    {"label_zh": "碳减排量", "label_en": "Carbon Reduction", "value": "850t/年"},
                    {"label_zh": "舒适度投诉率", "label_en": "Comfort Complaints", "value": "-45%"},
                    {"label_zh": "维保工作闭环率", "label_en": "Work Order Closure", "value": "100%"},
                ],
                "sort_order": 2,
                "is_published": True,
            },
            # case-03: 广州某半导体产业园区智慧后勤保障
            {
                "name_zh": "广州某半导体产业园区智慧后勤保障",
                "name_en": "Guangzhou Semiconductor Park Smart Facility Support",
                "slug": "guangzhou-semiconductor-park",
                "category": "park",
                "summary_zh": "为广州某半导体产业园区提供关键基础设施智慧运维保障方案，实现关键设备停机率0，巡检效率提升150%，预防性缺陷发现率98%。",
                "summary_en": "Provided smart O&M for critical infrastructure at a Guangzhou semiconductor park, achieving zero critical equipment downtime, 150% inspection efficiency improvement, and 98% preventive defect discovery rate.",
                "content_zh": (
                    "<p>项目位于广州某国家级经济技术开发区，园区一期建筑面积约35万平方米，包括半导体"
                    "晶圆制造厂房、封装测试车间、研发中心和配套动力设施。半导体制造对动力供应、环境"
                    "洁净度和设备可靠性有着极致要求，任何非计划停机都可能造成巨额经济损失。</p>"
                    "<p>金捷利为该园区部署了面向高可靠性场景的智慧后勤保障系统，重点覆盖以下系统："
                    "冷热源及洁净空调系统（含MAU+FFU+DCC全链路监控）、纯水及废水处理系统、"
                    "压缩空气及特殊气体系统、变配电及UPS系统。通过多信道数据采集终端实现数千个"
                    "传感器点位的毫秒级同步采集，结合智能红外温度阵列探针对关键电气设备进行7×24小时"
                    "温度异常监测。</p>"
                    "<p>系统基于设备运行数据构建了数字孪生模型，AI算法可提前72小时预测关键设备的"
                    "潜在故障，自动生成预防性维护工单。智能巡检模块将传统的人工抄表巡检升级为"
                    "移动端+传感器协同的智慧巡检模式，巡检效率提升150%。电能安全及综合平衡仪的部署"
                    "保障了半导体制造设备对电能质量的高标准要求。</p>"
                    "<p>系统上线运行18个月以来，园区关键动力设备实现了零非计划停机，预防性缺陷发现率"
                    "达到98%（较传统模式的65%大幅提升），运维人力成本降低35%，为半导体生产提供了"
                    "坚实可靠的后勤保障。</p>"
                ),
                "content_en": (
                    "<p>Located in a national-level economic and technological development zone in Guangzhou, "
                    "the Phase I campus covers 350,000 sqm including wafer fabrication, packaging/testing, "
                    "R&D center, and supporting utility facilities. Semiconductor manufacturing demands "
                    "extreme reliability for power supply, environmental cleanliness, and equipment — any "
                    "unplanned downtime results in massive economic losses.</p>"
                    "<p>GOLDGINNY deployed a high-reliability smart facility support system covering HVAC and "
                    "cleanroom air (MAU+FFU+DCC full-chain monitoring), pure water and wastewater treatment, "
                    "compressed air and specialty gases, and power distribution/UPS systems. Millisecond-level "
                    "synchronous data acquisition from thousands of sensor points combined with IR thermal "
                    "array probes for 24/7 electrical equipment temperature anomaly monitoring.</p>"
                    "<p>After 18 months of operation: zero unplanned critical equipment downtime, 98% "
                    "preventive defect discovery rate (up from 65%), and 35% reduction in O&M labor costs.</p>"
                ),
                "stats": [
                    {"label_zh": "关键设备停机率", "label_en": "Critical Downtime", "value": "0"},
                    {"label_zh": "巡检效率提升", "label_en": "Inspection Efficiency", "value": "150%"},
                    {"label_zh": "预防性缺陷发现", "label_en": "Preventive Defect Discovery", "value": "98%"},
                ],
                "sort_order": 3,
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
