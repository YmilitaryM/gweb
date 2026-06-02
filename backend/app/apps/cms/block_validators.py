from pydantic import BaseModel


class HeroSlide(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    subtitle_zh: str = ""
    subtitle_en: str = ""
    image: str = ""
    buttons: list[dict] = []


class HeroContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    subtitle_zh: str = ""
    subtitle_en: str = ""
    bg_image: int | None = None
    bg_video: int | None = None
    buttons: list[dict] = []
    slides: list[dict] = []


class NewsListContent(BaseModel):
    title_zh: str
    title_en: str
    count: int = 3
    show_date: bool = True
    show_image: bool = True
    category_filter: list[str] = []


class ProductCardsContent(BaseModel):
    title_zh: str
    title_en: str
    cards: list[dict] = []


class SolutionCardsContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    cards: list[dict] = []
    tabs: list[dict] = []


class StatsCounterContent(BaseModel):
    title_zh: str
    title_en: str
    items: list[dict] = []


class ContactFormContent(BaseModel):
    title_zh: str
    title_en: str
    fields: list[str] = ["company_name", "contact_name", "phone", "message"]
    features: list[dict] = []
    submit_button_zh: str = "提交"
    submit_button_en: str = "Submit"


class RichtextContent(BaseModel):
    html_content_zh: str = ""
    html_content_en: str = ""


class CtaBannerContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    button_link: str = ""
    button_text_zh: str = ""
    button_text_en: str = ""


class VideoBannerContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    subtitle_zh: str = ""
    subtitle_en: str = ""
    video_url: str = ""
    poster_image: int | None = None


class ImageGalleryContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    images: list[dict] = []


class LogoCloudContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    logos: list[dict] = []


class FaqContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""


class DigitalTwinContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    stats: list[dict] = []


class LiveDashboardContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    metrics: list[dict] = []


class TechIconGridContent(BaseModel):
    title_zh: str = ""
    title_en: str = ""
    items: list[dict] = []


BLOCK_VALIDATORS = {
    "hero": HeroContent,
    "news_list": NewsListContent,
    "product_cards": ProductCardsContent,
    "solution_cards": SolutionCardsContent,
    "stats_counter": StatsCounterContent,
    "contact_form": ContactFormContent,
    "richtext": RichtextContent,
    "video_banner": VideoBannerContent,
    "image_gallery": ImageGalleryContent,
    "logo_cloud": LogoCloudContent,
    "faq": FaqContent,
    "cta_banner": CtaBannerContent,
    "digital_twin": DigitalTwinContent,
    "live_dashboard": LiveDashboardContent,
    "tech_icon_grid": TechIconGridContent,
}


def validate_block_content(block_type: str, content: dict):
    validator = BLOCK_VALIDATORS.get(block_type)
    if validator:
        return validator(**content).model_dump()
    return content
