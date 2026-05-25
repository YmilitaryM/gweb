import pytest
from httpx import AsyncClient
from app.apps.products.service import (
    create_category,
    create_product,
    delete_category,
    delete_product,
    get_category_by_id,
    get_category_product_count,
    get_product_by_id,
    get_product_by_slug,
    list_all_products,
    list_categories,
    list_published_products,
    update_category,
    update_product,
)


# --- Service Tests ---

@pytest.mark.asyncio
async def test_create_and_list_categories():
    cat = await create_category(name_zh="软件产品", name_en="Software", slug="software", sort_order=1)
    assert cat.id is not None
    assert cat.name_zh == "软件产品"

    cats = await list_categories()
    assert len(cats) > 0

    found = await get_category_by_id(cat.id)
    assert found is not None
    assert found.slug == "software"

    await delete_category(cat.id)


@pytest.mark.asyncio
async def test_update_category():
    cat = await create_category(name_zh="硬件", name_en="Hardware", slug="hardware", sort_order=2)
    updated = await update_category(cat.id, name_zh="硬件产品")
    assert updated is not None
    assert updated.name_zh == "硬件产品"

    await delete_category(cat.id)
    assert await get_category_by_id(cat.id) is None


@pytest.mark.asyncio
async def test_create_and_get_product():
    cat = await create_category(name_zh="软件", name_en="Software", slug="sw", sort_order=1)
    prod = await create_product(
        category_id=cat.id,
        name_zh="智能楼宇系统",
        name_en="Smart Building System",
        slug="smart-building",
        is_published=True,
    )
    assert prod.id is not None

    found = await get_product_by_id(prod.id)
    assert found is not None
    assert found.name_zh == "智能楼宇系统"

    found_slug = await get_product_by_slug("smart-building")
    assert found_slug is not None

    await delete_product(prod.id)
    await delete_category(cat.id)


@pytest.mark.asyncio
async def test_list_published_products():
    cat = await create_category(name_zh="测试", name_en="Test", slug="test", sort_order=1)
    p1 = await create_product(category_id=cat.id, name_zh="已发布", name_en="Pub", slug="pub", is_published=True)
    p2 = await create_product(category_id=cat.id, name_zh="草稿", name_en="Draft", slug="draft", is_published=False)

    products, total = await list_published_products()
    ids = [p.id for p in products]
    assert p1.id in ids
    assert p2.id not in ids

    await delete_product(p1.id)
    await delete_product(p2.id)
    await delete_category(cat.id)


@pytest.mark.asyncio
async def test_category_product_count():
    cat = await create_category(name_zh="有产品", name_en="Has Products", slug="has", sort_order=1)
    prod = await create_product(category_id=cat.id, name_zh="产品", name_en="P", slug="p1")

    count = await get_category_product_count(cat.id)
    assert count >= 1

    await delete_product(prod.id)
    await delete_category(cat.id)


# --- API Tests ---

@pytest.mark.asyncio
async def test_admin_create_category_api(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "API分类", "name_en": "API Category", "slug": "api-cat", "sort_order": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name_zh"] == "API分类"
    assert data["product_count"] == 0


@pytest.mark.asyncio
async def test_admin_list_categories_api(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/admin/product-categories", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_admin_create_and_list_products_api(client: AsyncClient, auth_headers: dict):
    # First create a category
    cat_resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "测试分类", "name_en": "Test", "slug": "test-api", "sort_order": 1},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    # Create product
    resp = await client.post(
        "/api/v1/admin/products",
        json={
            "category_id": cat_id,
            "name_zh": "API产品",
            "name_en": "API Product",
            "slug": "api-product",
            "summary_zh": "简介",
            "summary_en": "Summary",
            "specs": [{"key": "版本", "value": "1.0"}],
            "is_published": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name_zh"] == "API产品"
    assert data["category"]["id"] == cat_id
    assert len(data["specs"]) == 1

    # List products
    list_resp = await client.get("/api/v1/admin/products", headers=auth_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_admin_update_product_api(client: AsyncClient, auth_headers: dict):
    # Setup
    cat_resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "更新测试", "name_en": "Update", "slug": "update-test", "sort_order": 1},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]
    prod_resp = await client.post(
        "/api/v1/admin/products",
        json={"category_id": cat_id, "name_zh": "旧名称", "name_en": "Old", "slug": "old-slug"},
        headers=auth_headers,
    )
    prod_id = prod_resp.json()["id"]

    # Update
    resp = await client.put(
        f"/api/v1/admin/products/{prod_id}",
        json={"name_zh": "新名称"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name_zh"] == "新名称"


@pytest.mark.asyncio
async def test_admin_delete_product_api(client: AsyncClient, auth_headers: dict):
    # Setup
    cat_resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "删除测试", "name_en": "Delete", "slug": "delete-test", "sort_order": 1},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]
    prod_resp = await client.post(
        "/api/v1/admin/products",
        json={"category_id": cat_id, "name_zh": "待删除", "name_en": "To Delete", "slug": "to-delete"},
        headers=auth_headers,
    )
    prod_id = prod_resp.json()["id"]

    # Delete
    resp = await client.delete(f"/api/v1/admin/products/{prod_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True


@pytest.mark.asyncio
async def test_delete_category_with_products_blocked_api(client: AsyncClient, auth_headers: dict):
    # Setup
    cat_resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "有产品分类", "name_en": "Has Products", "slug": "has-products", "sort_order": 1},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]
    await client.post(
        "/api/v1/admin/products",
        json={"category_id": cat_id, "name_zh": "某产品", "name_en": "Some", "slug": "some-product"},
        headers=auth_headers,
    )

    # Try to delete category with products
    resp = await client.delete(f"/api/v1/admin/product-categories/{cat_id}", headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_public_list_products_api(client: AsyncClient, auth_headers: dict):
    # Setup via admin
    cat_resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "公开分类", "name_en": "Public", "slug": "public-cat", "sort_order": 1},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]
    await client.post(
        "/api/v1/admin/products",
        json={"category_id": cat_id, "name_zh": "公开产品", "name_en": "Public Prod", "slug": "public-prod", "is_published": True},
        headers=auth_headers,
    )

    # Public endpoint
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_public_get_product_by_slug_api(client: AsyncClient, auth_headers: dict):
    # Setup
    cat_resp = await client.post(
        "/api/v1/admin/product-categories",
        json={"name_zh": "详情分类", "name_en": "Detail", "slug": "detail-cat", "sort_order": 1},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]
    await client.post(
        "/api/v1/admin/products",
        json={
            "category_id": cat_id,
            "name_zh": "详情产品",
            "name_en": "Detail Prod",
            "slug": "detail-prod",
            "summary_zh": "摘要",
            "description_zh": "详细描述",
            "specs": [{"key": "型号", "value": "X1"}],
            "is_published": True,
        },
        headers=auth_headers,
    )

    resp = await client.get("/api/v1/products/detail-prod")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name_zh"] == "详情产品"
    assert data["category"]["name_zh"] == "详情分类"


@pytest.mark.asyncio
async def test_product_stats_api(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/admin/product-stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "product_count" in data
    assert "category_count" in data
