from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.apps.audit.service import create_audit_log
from app.apps.auth.router import get_current_user
from app.apps.products.schemas import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCategoryUpdate,
    ProductCreate,
    ProductDetailResponse,
    ProductResponse,
    ProductUpdate,
)
from app.apps.products.service import (
    count_categories,
    count_products,
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

public_router = APIRouter(prefix="/api/v1", tags=["products"])

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-products"],
    dependencies=[Depends(get_current_user)],
)


# --- Helper ---

async def _category_to_response(cat) -> ProductCategoryResponse:
    count = await get_category_product_count(cat.id)
    return ProductCategoryResponse(
        id=cat.id,
        name_zh=cat.name_zh,
        name_en=cat.name_en,
        slug=cat.slug,
        sort_order=cat.sort_order,
        is_published=cat.is_published,
        created_at=cat.created_at,
        updated_at=cat.updated_at,
        product_count=count,
    )


# --- Public routes ---

@public_router.get("/product-categories")
async def public_list_categories():
    cats = await list_categories()
    return [await _category_to_response(c) for c in cats if c.is_published]


@public_router.get("/products", response_model=dict)
async def public_list_products(
    page: int = 1,
    size: int = 20,
    category: str | None = None,
):
    products, total = await list_published_products(page, size, category)
    return {
        "items": [ProductDetailResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "size": size,
    }


@public_router.get("/products/{slug}", response_model=ProductDetailResponse)
async def public_get_product(slug: str):
    product = await get_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# --- Admin: Category routes ---

@admin_router.get("/product-categories")
async def admin_list_categories():
    cats = await list_categories()
    return [await _category_to_response(c) for c in cats]


@admin_router.post(
    "/product-categories", response_model=ProductCategoryResponse, status_code=201
)
async def admin_create_category(
    data: ProductCategoryCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    cat = await create_category(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="product_category",
        resource_id=cat.id,
        resource_name=cat.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await _category_to_response(cat)


@admin_router.put(
    "/product-categories/{cat_id}", response_model=ProductCategoryResponse
)
async def admin_update_category(
    cat_id: int,
    data: ProductCategoryUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    cat = await update_category(cat_id, **data.model_dump(exclude_none=True))
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="product_category",
        resource_id=cat.id,
        resource_name=cat.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await _category_to_response(cat)


@admin_router.delete("/product-categories/{cat_id}")
async def admin_delete_category(
    cat_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    product_count = await get_category_product_count(cat_id)
    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {product_count} existing products",
        )
    cat = await get_category_by_id(cat_id)
    name = cat.name_zh if cat else None
    deleted = await delete_category(cat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="product_category",
        resource_id=cat_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


# --- Admin: Product routes ---

@admin_router.get("/products")
async def admin_list_products(
    page: int = 1,
    size: int = 20,
    category_id: int | None = None,
):
    products, total = await list_all_products(page, size, category_id)
    return {
        "items": [ProductDetailResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "size": size,
    }


@admin_router.post("/products", response_model=ProductDetailResponse, status_code=201)
async def admin_create_product(
    data: ProductCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    prod = await create_product(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="product",
        resource_id=prod.id,
        resource_name=prod.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await get_product_by_id(prod.id)


@admin_router.get("/products/{prod_id}", response_model=ProductDetailResponse)
async def admin_get_product(prod_id: int):
    prod = await get_product_by_id(prod_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@admin_router.put("/products/{prod_id}", response_model=ProductDetailResponse)
async def admin_update_product(
    prod_id: int,
    data: ProductUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    prod = await update_product(prod_id, **data.model_dump(exclude_none=True))
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="product",
        resource_id=prod.id,
        resource_name=prod.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await get_product_by_id(prod_id)


@admin_router.delete("/products/{prod_id}")
async def admin_delete_product(
    prod_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    prod = await get_product_by_id(prod_id)
    name = prod.name_zh if prod else None
    deleted = await delete_product(prod_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="product",
        resource_id=prod_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


# --- Admin: Stats ---

@admin_router.get("/product-stats")
async def admin_product_stats():
    return {
        "product_count": await count_products(),
        "category_count": await count_categories(),
    }
