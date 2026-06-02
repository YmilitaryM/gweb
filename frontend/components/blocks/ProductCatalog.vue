<template>
  <div class="min-h-screen" style="background: #f8fafc;">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <h1 class="text-3xl font-light tracking-tight mb-2" style="color: #1e293b">
        {{ locale === 'zh' ? '产品中心' : 'Products' }}
      </h1>
      <p class="text-[14px] mb-8" style="color: #94a3b8;">
        {{ locale === 'zh' ? '探索我们的产品与解决方案' : 'Explore our products and solutions' }}
      </p>

      <!-- Category tabs -->
      <div class="flex flex-wrap gap-3 mb-8">
        <button
          v-for="tab in tabs"
          :key="tab.slug"
          @click="activeCategory = tab.slug; page = 1; fetchProducts()"
          class="text-[13px] border-none cursor-pointer px-5 py-2 rounded-full transition-colors"
          :style="activeCategory === tab.slug
            ? 'background: rgba(37,99,235,0.12); color: #60a5fa;'
            : 'background: #ffffff; color: #94a3b8; border: 1px solid #e2e8f0;'"
        >
          {{ locale === 'zh' ? tab.name_zh : tab.name_en }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-[14px] py-20 text-center" style="color: #94a3b8;">
        {{ locale === 'zh' ? '加载中...' : 'Loading...' }}
      </div>

      <!-- Empty -->
      <div v-else-if="products.length === 0" class="text-[14px] py-20 text-center" style="color: #94a3b8;">
        {{ locale === 'zh' ? '暂无产品' : 'No products found' }}
      </div>

      <!-- Product grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="prod in products"
          :key="prod.id"
          :to="`/products/${prod.slug}`"
          class="rounded-xl overflow-hidden no-underline transition-all duration-200 hover:translate-y-[-2px] block"
          style="background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);"
        >
          <div class="h-48 overflow-hidden" style="background: #f1f5f9;">
            <img
              v-if="prod.cover_image_id"
              :src="`${apiBase}/../../media/id/${prod.cover_image_id}`"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-[12px]" style="color: #94a3b8;">
              {{ locale === 'zh' ? '暂无图片' : 'No image' }}
            </div>
          </div>
          <div class="p-5">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-[11px] px-2 py-0.5 rounded-full" style="background: rgba(37,99,235,0.08); color: #60a5fa;">
                {{ locale === 'zh' ? prod.category?.name_zh : prod.category?.name_en }}
              </span>
            </div>
            <h3 class="text-[16px] font-medium mb-2" style="color: #1e293b">
              {{ locale === 'zh' ? prod.name_zh : prod.name_en }}
            </h3>
            <p class="text-[13px] leading-relaxed line-clamp-2" style="color: #94a3b8;">
              {{ locale === 'zh' ? prod.summary_zh : prod.summary_en }}
            </p>
          </div>
        </NuxtLink>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-10">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchProducts()"
          class="text-[13px] border-none cursor-pointer w-9 h-9 rounded-lg transition-colors"
          :style="p === page
            ? 'background: rgba(37,99,235,0.15); color: #60a5fa;'
            : 'background: #ffffff; color: #94a3b8; border: 1px solid #e2e8f0;'"
        >{{ p }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any> }>();

const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;
const { locale } = useI18n();

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
}

interface ProductItem {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  summary_en: string;
  category: Category | null;
}

const tabs = ref<(Category & { slug: string })[]>([
  { id: 0, name_zh: '全部', name_en: 'All', slug: '' },
]);
const activeCategory = ref('');
const products = ref<ProductItem[]>([]);
const loading = ref(true);
const page = ref(1);
const totalPages = ref(1);

const fetchCategories = async () => {
  try {
    const cats = await $fetch<Category[]>(`${apiBase}/product-categories`);
    tabs.value = [{ id: 0, name_zh: '全部', name_en: 'All', slug: '' }, ...cats];
  } catch {}
};

const fetchProducts = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({ page: String(page.value), size: '12' });
    if (activeCategory.value) params.set('category', activeCategory.value);
    const data = await $fetch<{ items: ProductItem[]; total: number; size: number }>(
      `${apiBase}/products?${params}`
    );
    products.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await fetchCategories();
  await fetchProducts();
});
</script>
