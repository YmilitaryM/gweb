<template>
  <div class="min-h-screen" style="background: #f8fafc;">
    <div v-if="loading" class="text-[14px] py-20 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="text-[14px] py-20 text-center" style="color: #f87171;">{{ error }}</div>

    <template v-else-if="product">
      <!-- Breadcrumb -->
      <div class="max-w-5xl mx-auto px-4 py-6">
        <div class="flex items-center gap-2 text-[12px]" style="color: #94a3b8;">
          <NuxtLink to="/" class="no-underline hover:opacity-70" style="color: #94a3b8;">首页</NuxtLink>
          <span>/</span>
          <NuxtLink to="/products" class="no-underline hover:opacity-70" style="color: #94a3b8;">产品中心</NuxtLink>
          <span v-if="product.category">/</span>
          <span v-if="product.category" style="color: #34d399;">{{ product.category.name_zh }}</span>
          <span>/</span>
          <span style="color: #64748b;">{{ product.name_zh }}</span>
        </div>
      </div>

      <!-- Hero -->
      <div class="max-w-5xl mx-auto px-4 pb-8">
        <div class="rounded-2xl overflow-hidden" style="background: #ffffff; border: 1px solid #e2e8f0;">
          <div class="grid grid-cols-1 md:grid-cols-2">
            <div class="h-72 md:h-auto overflow-hidden" style="background: #f1f5f9;">
              <img
                v-if="product.cover_image_id"
                :src="`${apiBase}/../../media/id/${product.cover_image_id}`"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-[14px]" style="color: #94a3b8;">暂无图片</div>
            </div>
            <div class="p-8 flex flex-col justify-center">
              <span v-if="product.category" class="text-[11px] px-2 py-1 rounded-full mb-3 self-start" style="background: rgba(5,150,105,0.08); color: #34d399;">{{ product.category.name_zh }}</span>
              <h1 class="text-2xl font-light tracking-tight mb-3" style="color: #1e293b">{{ product.name_zh }}</h1>
              <p class="text-[14px] leading-relaxed" style="color: #64748b;">{{ product.summary_zh }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Specs -->
      <div v-if="product.specs && product.specs.length > 0" class="max-w-5xl mx-auto px-4 pb-8">
        <h2 class="text-[16px] font-medium mb-4" style="color: #1e293b">规格参数</h2>
        <div class="rounded-xl overflow-hidden" style="background: #ffffff; border: 1px solid #e2e8f0;">
          <table class="w-full text-[14px]">
            <tbody>
              <tr v-for="(spec, i) in product.specs" :key="i" :style="i % 2 === 0 ? 'background: #ffffff;' : 'background: #f8fafc;'">
                <td class="px-5 py-3 w-48" style="color: #94a3b8;">{{ spec.key }}</td>
                <td class="px-5 py-3" style="color: #1e293b;">{{ spec.value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Description -->
      <div v-if="product.description_zh" class="max-w-5xl mx-auto px-4 pb-12">
        <h2 class="text-[16px] font-medium mb-4" style="color: #1e293b">产品详情</h2>
        <div class="rounded-xl p-6 text-[14px] leading-relaxed" style="background: #ffffff; border: 1px solid #e2e8f0; color: #334155;" v-html="product.description_zh.replace(/\n/g, '<br/>')">
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;
const route = useRoute();

interface Category {
  id: number;
  name_zh: string;
}

interface ProductDetail {
  id: number;
  name_zh: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  description_zh: string;
  specs: { key: string; value: string }[] | null;
  category: Category | null;
}

const product = ref<ProductDetail | null>(null);
const loading = ref(true);
const error = ref('');

const fetchProduct = async () => {
  loading.value = true;
  error.value = '';
  try {
    product.value = await $fetch<ProductDetail>(`${apiBase}/products/${route.params.slug}`);
  } catch (e: any) {
    error.value = e?.data?.detail || '产品不存在';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchProduct);
</script>
