<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>

    <div class="mb-8">
      <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b;">系统设置</h2>
      <p class="text-[13px]" style="color: #94a3b8;">配置 LLM、站点信息等系统参数</p>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <template v-else>
      <!-- LLM Settings -->
      <div class="rounded-xl p-6 mb-6" style="background: #ffffff; border: 1px solid #e8f5e9;">
        <h3 class="text-[14px] font-medium mb-5 flex items-center gap-2" style="color: #1e293b;">
          <span class="w-1.5 h-1.5 rounded-full" style="background: #059669;"></span>
          LLM 配置
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">LLM 提供商</label>
            <select
              v-model="form.llm_provider"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
            >
              <option value="openai">OpenAI</option>
              <option value="deepseek">DeepSeek</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">LLM 模型</label>
            <input
              v-model="form.llm_model"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
              placeholder="gpt-4o / deepseek-chat / claude-sonnet-4-6"
            />
          </div>
          <div class="md:col-span-2">
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">LLM API Key</label>
            <div class="flex gap-3">
              <input
                v-model="form.llm_api_key"
                :type="showLlmKey ? 'text' : 'password'"
                class="flex-1 py-2.5 px-3 text-[14px] outline-none rounded-lg font-mono"
                style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
                :placeholder="origSettings.llm_api_key ? '已设置 (输入新值覆盖)' : 'sk-...'"
              />
              <button
                @click="showLlmKey = !showLlmKey"
                class="text-[12px] border-none cursor-pointer px-3 py-2 rounded-lg transition-colors flex-shrink-0"
                style="color: #64748b; background: #f1f5f9;"
              >
                {{ showLlmKey ? '隐藏' : '显示' }}
              </button>
            </div>
            <p class="text-[11px] mt-1" style="color: #94a3b8;">留空则不修改已有值</p>
          </div>
        </div>
      </div>

      <!-- Embedding Settings -->
      <div class="rounded-xl p-6 mb-6" style="background: #ffffff; border: 1px solid #e8f5e9;">
        <h3 class="text-[14px] font-medium mb-5 flex items-center gap-2" style="color: #1e293b;">
          <span class="w-1.5 h-1.5 rounded-full" style="background: #0284c7;"></span>
          Embedding 配置
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Embedding 提供商</label>
            <select
              v-model="form.embedding_provider"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
            >
              <option value="openai">OpenAI</option>
              <option value="deepseek">DeepSeek</option>
            </select>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Embedding 模型</label>
            <input
              v-model="form.embedding_model"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
              placeholder="text-embedding-3-small"
            />
          </div>
          <div class="md:col-span-2">
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Embedding API Key</label>
            <div class="flex gap-3">
              <input
                v-model="form.embedding_api_key"
                :type="showEmbKey ? 'text' : 'password'"
                class="flex-1 py-2.5 px-3 text-[14px] outline-none rounded-lg font-mono"
                style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
                :placeholder="origSettings.embedding_api_key ? '已设置 (输入新值覆盖)' : 'sk-...'"
              />
              <button
                @click="showEmbKey = !showEmbKey"
                class="text-[12px] border-none cursor-pointer px-3 py-2 rounded-lg transition-colors flex-shrink-0"
                style="color: #64748b; background: #f1f5f9;"
              >
                {{ showEmbKey ? '隐藏' : '显示' }}
              </button>
            </div>
            <p class="text-[11px] mt-1" style="color: #94a3b8;">留空则不修改已有值</p>
          </div>
        </div>
      </div>

      <!-- Site Info Settings -->
      <div class="rounded-xl p-6 mb-6" style="background: #ffffff; border: 1px solid #e8f5e9;">
        <h3 class="text-[14px] font-medium mb-5 flex items-center gap-2" style="color: #1e293b;">
          <span class="w-1.5 h-1.5 rounded-full" style="background: #94a3b8;"></span>
          站点信息
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文站点名</label>
            <input v-model="form.site_name_zh" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文站点名</label>
            <input v-model="form.site_name_en" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">联系邮箱</label>
            <input v-model="form.contact_email" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">联系电话</label>
            <input v-model="form.contact_phone" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <button
          @click="saveAll"
          :disabled="saving"
          class="text-[13px] font-medium text-white border-none cursor-pointer px-6 py-2.5 rounded-lg transition-all disabled:opacity-40 hover:translate-y-[-1px]"
          style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
        >
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
        <span v-if="saveMsg" class="text-[12px]" :style="{ color: saveOk ? '#34d399' : '#f87171' }">{{ saveMsg }}</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const { api, getHeaders } = useAdminApi();

const loading = ref(true);
const saving = ref(false);
const saveMsg = ref('');
const saveOk = ref(false);
const showLlmKey = ref(false);
const showEmbKey = ref(false);

const origSettings = ref<Record<string, string>>({});

const form = ref({
  llm_provider: 'deepseek',
  llm_api_key: '',
  llm_model: 'deepseek-chat',
  embedding_provider: 'openai',
  embedding_api_key: '',
  embedding_model: 'text-embedding-3-small',
  site_name_zh: '',
  site_name_en: '',
  contact_email: '',
  contact_phone: '',
});

const settingToFormKey: Record<string, string> = {
  llm_provider: 'llm_provider',
  llm_model: 'llm_model',
  embedding_provider: 'embedding_provider',
  embedding_model: 'embedding_model',
  site_name_zh: 'site_name_zh',
  site_name_en: 'site_name_en',
  contact_email: 'contact_email',
  contact_phone: 'contact_phone',
};

const loadSettings = async () => {
  loading.value = true;
  try {
    const data = await api<Record<string, string>>('/admin/settings');
    origSettings.value = data;
    for (const [key, val] of Object.entries(data)) {
      const formKey = settingToFormKey[key];
      if (formKey && val) {
        (form.value as any)[formKey] = val;
      }
      // For encrypted keys, only set if value is not masked
      if (key === 'llm_api_key' && val && val !== '••••••••') {
        form.value.llm_api_key = val;
      }
      if (key === 'embedding_api_key' && val && val !== '••••••••') {
        form.value.embedding_api_key = val;
      }
    }
  } catch (e: any) {
    console.error('Failed to load settings:', e);
  } finally {
    loading.value = false;
  }
};

const saveAll = async () => {
  saving.value = true;
  saveMsg.value = '';
  saveOk.value = false;

  const keys = [
    'llm_provider', 'llm_model', 'embedding_provider', 'embedding_model',
    'site_name_zh', 'site_name_en', 'contact_email', 'contact_phone',
  ];

  try {
    for (const key of keys) {
      const val = (form.value as any)[key];
      if (val !== undefined && val !== '') {
        await api(`/admin/settings/${key}`, {
          method: 'PUT', body: { value: val },
        });
      }
    }
    // API keys: only save if user entered a new value
    if (form.value.llm_api_key && form.value.llm_api_key !== '••••••••') {
      await api(`/admin/settings/llm_api_key`, {
        method: 'PUT', body: { value: form.value.llm_api_key },
      });
      form.value.llm_api_key = '';
    }
    if (form.value.embedding_api_key && form.value.embedding_api_key !== '••••••••') {
      await api(`/admin/settings/embedding_api_key`, {
        method: 'PUT', body: { value: form.value.embedding_api_key },
      });
      form.value.embedding_api_key = '';
    }
    saveOk.value = true;
    saveMsg.value = '设置已保存，即刻生效';
    await loadSettings();
  } catch (e: any) {
    saveOk.value = false;
    saveMsg.value = '保存失败: ' + (e?.data?.detail || e?.message || '未知错误');
  } finally {
    saving.value = false;
  }
};

onMounted(loadSettings);
</script>
