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


BLOCK_VALIDATORS = {
    "hero": HeroContent,
    "news_list": NewsListContent,
    "product_cards": ProductCardsContent,
    "solution_cards": SolutionCardsContent,
    "stats_counter": StatsCounterContent,
    "contact_form": ContactFormContent,
    "richtext": RichtextContent,
    "video_banner": RichtextContent,
    "image_gallery": RichtextContent,
    "logo_cloud": RichtextContent,
    "faq": RichtextContent,
    "cta_banner": RichtextContent,
    "digital_twin": RichtextContent,
    "live_dashboard": RichtextContent,
    "tech_icon_grid": RichtextContent,
}


def validate_block_content(block_type: str, content: dict):
    validator = BLOCK_VALIDATORS.get(block_type)
    if validator:
        validator(**content)
    return content
