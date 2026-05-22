<template>
  <div class="p-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light text-white tracking-tight mb-1">用户管理</h2>
        <p class="text-[13px]" style="color: rgba(255,255,255,0.25);">管理后台管理员和编辑者账号</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 rounded-lg text-[13px] font-medium text-white border-none cursor-pointer transition-all duration-200 hover:opacity-90"
        style="background: linear-gradient(135deg, #059669, #10b981);"
      >
        新建用户
      </button>
    </div>

    <!-- Users table -->
    <div
      class="rounded-xl overflow-hidden"
      style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
    >
      <table class="w-full text-left">
        <thead>
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">用户</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">角色</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">邮箱</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">手机号</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">创建时间</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
            class="transition-colors duration-150"
            style="border-bottom: 1px solid rgba(255,255,255,0.02);"
            :style="hoverId === user.id ? { background: 'rgba(255,255,255,0.02)' } : {}"
            @mouseenter="hoverId = user.id"
            @mouseleave="hoverId = null"
          >
            <td class="py-3 px-5">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center text-[12px] font-medium flex-shrink-0"
                  :style="avatarStyle(user)"
                >
                  {{ avatarText(user) }}
                </div>
                <div>
                  <div class="text-[13px] text-white font-medium">{{ user.display_name || user.username }}</div>
                  <div class="text-[11px]" style="color: rgba(255,255,255,0.2);">{{ user.username }}</div>
                </div>
              </div>
            </td>
            <td class="py-3 px-5">
              <span
                class="inline-block px-2 py-0.5 rounded text-[11px] font-medium"
                :style="roleBadgeStyle(user.role)"
              >{{ user.role === 'admin' ? '管理员' : '编辑者' }}</span>
            </td>
            <td class="py-3 px-5 text-[13px]" style="color: rgba(255,255,255,0.35);">{{ user.email || '—' }}</td>
            <td class="py-3 px-5 text-[13px]" style="color: rgba(255,255,255,0.35);">{{ user.phone || '—' }}</td>
            <td class="py-3 px-5 text-[13px]" style="color: rgba(255,255,255,0.2);">{{ formatDate(user.created_at) }}</td>
            <td class="py-3 px-5">
              <div class="flex items-center gap-3">
                <button
                  @click="openEdit(user)"
                  class="text-[12px] border-none bg-transparent cursor-pointer transition-colors"
                  style="color: rgba(255,255,255,0.3);"
                >编辑</button>
                <button
                  v-if="user.id !== myId"
                  @click="confirmDelete(user)"
                  class="text-[12px] border-none bg-transparent cursor-pointer transition-colors"
                  style="color: rgba(239,68,68,0.5);"
                >删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="users.length === 0" class="py-16 text-center text-[13px]" style="color: rgba(255,255,255,0.15);">
        暂无用户
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="closeModal"
      >
        <div
          class="w-full max-w-[480px] rounded-2xl p-8"
          style="background: #111820; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
        >
          <h3 class="text-lg font-light text-white mb-6">
            {{ editingUser ? '编辑用户' : '新建用户' }}
          </h3>

          <div class="space-y-4">
            <!-- Avatar upload -->
            <div class="flex items-center gap-4 mb-2">
              <div
                class="w-16 h-16 rounded-full flex items-center justify-center text-xl font-medium relative overflow-hidden cursor-pointer"
                :style="formAvatarPreview
                  ? { backgroundImage: `url(${formAvatarPreview})`, backgroundSize: 'cover', backgroundPosition: 'center' }
                  : { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }"
                @click="triggerUpload"
                :title="formAvatarPreview ? '点击更换头像' : '点击上传头像'"
              >
                <span v-if="!formAvatarPreview" style="color: rgba(255,255,255,0.15);">+</span>
                <div
                  v-if="uploadingAvatar"
                  class="absolute inset-0 flex items-center justify-center"
                  style="background: rgba(0,0,0,0.5);"
                >
                  <span class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                </div>
              </div>
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleAvatarUpload"
              />
              <div>
                <div class="text-[13px] text-white mb-1">头像</div>
                <div class="text-[11px]" style="color: rgba(255,255,255,0.2);">点击上传，支持 JPG/PNG</div>
              </div>
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">用户名 *</label>
              <input
                v-model="form.username"
                type="text"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">显示名称</label>
              <input
                v-model="form.display_name"
                type="text"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">
                密码{{ editingUser ? ' (留空则不修改)' : ' *' }}
              </label>
              <input
                v-model="form.password"
                type="password"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">邮箱</label>
              <input
                v-model="form.email"
                type="email"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">手机号</label>
              <input
                v-model="form.phone"
                type="text"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">角色</label>
              <select
                v-model="form.role"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border appearance-none cursor-pointer"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              >
                <option value="editor" style="background: #111820;">编辑者 (Editor)</option>
                <option value="admin" style="background: #111820;">管理员 (Admin)</option>
              </select>
            </div>
          </div>

          <!-- Error message -->
          <div
            v-if="formError"
            class="mt-4 px-4 py-3 rounded-lg text-[13px]"
            style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
          >
            {{ formError }}
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 mt-8">
            <button
              @click="closeModal"
              class="px-4 py-2 rounded-lg text-[13px] border-none cursor-pointer transition-colors"
              style="background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.4);"
            >
              取消
            </button>
            <button
              @click="submitForm"
              :disabled="formLoading"
              class="px-6 py-2 rounded-lg text-[13px] font-medium text-white border-none cursor-pointer transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              style="background: linear-gradient(135deg, #059669, #10b981);"
            >
              <span v-if="!formLoading">{{ editingUser ? '保存' : '创建' }}</span>
              <span v-else class="flex items-center gap-2">
                <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                处理中
              </span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete confirm modal -->
    <Teleport to="body">
      <div
        v-if="deleteTarget"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="deleteTarget = null"
      >
        <div
          class="w-full max-w-[380px] rounded-2xl p-8"
          style="background: #111820; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
        >
          <h3 class="text-lg font-light text-white mb-3">确认删除</h3>
          <p class="text-[14px] mb-1" style="color: rgba(255,255,255,0.4);">
            确定要删除用户 <span class="text-white font-medium">{{ deleteTarget.username }}</span> 吗？
          </p>
          <p class="text-[12px] mb-6" style="color: rgba(239,68,68,0.4);">此操作不可撤销</p>
          <div class="flex justify-end gap-3">
            <button
              @click="deleteTarget = null"
              class="px-4 py-2 rounded-lg text-[13px] border-none cursor-pointer transition-colors"
              style="background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.4);"
            >
              取消
            </button>
            <button
              @click="doDelete"
              :disabled="deleting"
              class="px-6 py-2 rounded-lg text-[13px] font-medium text-white border-none cursor-pointer transition-all disabled:opacity-40"
              style="background: #ef4444;"
            >
              {{ deleting ? '删除中...' : '删除' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['admin-auth'],
});

const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

const getHeaders = () => {
  const token = import.meta.client ? localStorage.getItem('admin_token') : null;
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

interface User {
  id: number;
  username: string;
  role: string;
  display_name: string | null;
  phone: string | null;
  email: string | null;
  avatar: string | null;
  created_at: string;
}

const users = ref<User[]>([]);
const myId = ref<number | null>(null);
const hoverId = ref<number | null>(null);

// --- Table helpers ---

const avatarText = (user: User) => {
  return ((user.display_name || user.username) as string).charAt(0).toUpperCase();
};

const avatarStyle = (user: User) => {
  if (user.avatar) {
    return {
      backgroundImage: `url(${user.avatar})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    };
  }
  return {
    background: user.role === 'admin'
      ? 'linear-gradient(135deg, #059669, #0284c7)'
      : 'linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.12))',
  };
};

const roleBadgeStyle = (role: string) => {
  if (role === 'admin') {
    return {
      background: 'rgba(5,150,105,0.12)',
      color: '#34d399',
      border: '1px solid rgba(5,150,105,0.2)',
    };
  }
  return {
    background: 'rgba(255,255,255,0.04)',
    color: 'rgba(255,255,255,0.5)',
    border: '1px solid rgba(255,255,255,0.06)',
  };
};

const formatDate = (s: string) => {
  if (!s) return '—';
  return new Date(s).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

// --- Data fetching ---

const fetchUsers = async () => {
  try {
    const data = await $fetch<User[]>(`${apiBase}/admin/users`, { headers: getHeaders() });
    users.value = data;
  } catch (e: any) {
    if (e?.response?.status === 403) {
      // editor role, just show empty
      users.value = [];
    }
  }
};

const fetchMe = async () => {
  try {
    const data = await $fetch<User>(`${apiBase}/admin/auth/me`, { headers: getHeaders() });
    myId.value = data.id;
  } catch {}
};

onMounted(() => {
  fetchMe();
  fetchUsers();
});

// --- Modal logic ---

const showModal = ref(false);
const editingUser = ref<User | null>(null);
const form = ref({ username: '', password: '', role: 'editor', display_name: '', phone: '', email: '', avatar: '' });
const formError = ref('');
const formLoading = ref(false);
const formAvatarPreview = ref('');
const uploadingAvatar = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

const resetForm = () => {
  form.value = { username: '', password: '', role: 'editor', display_name: '', phone: '', email: '', avatar: '' };
  formError.value = '';
  formAvatarPreview.value = '';
};

const triggerUpload = () => {
  fileInput.value?.click();
};

const handleAvatarUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  uploadingAvatar.value = true;
  try {
    const body = new FormData();
    body.append('file', file);
    const result = await $fetch<{ url: string }>(`${apiBase}/admin/media/upload`, {
      method: 'POST',
      headers: { ...(getHeaders()) },
      body,
    });
    formAvatarPreview.value = result.url;
    form.value.avatar = result.url;
  } catch {
    formError.value = '头像上传失败';
  } finally {
    uploadingAvatar.value = false;
    target.value = '';
  }
};

const openCreate = () => {
  editingUser.value = null;
  resetForm();
  showModal.value = true;
};

const openEdit = (user: User) => {
  editingUser.value = user;
  form.value = {
    username: user.username,
    password: '',
    role: user.role,
    display_name: user.display_name || '',
    phone: user.phone || '',
    email: user.email || '',
    avatar: user.avatar || '',
  };
  formAvatarPreview.value = user.avatar || '';
  formError.value = '';
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  editingUser.value = null;
};

const submitForm = async () => {
  if (!form.value.username.trim()) {
    formError.value = '用户名不能为空';
    return;
  }
  if (!editingUser.value && !form.value.password) {
    formError.value = '密码不能为空';
    return;
  }

  formLoading.value = true;
  formError.value = '';

  try {
    const body: Record<string, any> = {
      username: form.value.username.trim(),
      role: form.value.role,
    };
    if (form.value.password) body.password = form.value.password;
    if (form.value.display_name) body.display_name = form.value.display_name.trim();
    if (form.value.phone) body.phone = form.value.phone.trim();
    if (form.value.email) body.email = form.value.email.trim();
    if (form.value.avatar) body.avatar = form.value.avatar;

    if (editingUser.value) {
      await $fetch(`${apiBase}/admin/users/${editingUser.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...getHeaders() },
        body: JSON.stringify(body),
      });
    } else {
      await $fetch(`${apiBase}/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getHeaders() },
        body: JSON.stringify(body),
      });
    }
    closeModal();
    await fetchUsers();
  } catch (e: any) {
    formError.value = e?.data?.detail || '操作失败';
  } finally {
    formLoading.value = false;
  }
};

// --- Delete logic ---

const deleteTarget = ref<User | null>(null);
const deleting = ref(false);

const confirmDelete = (user: User) => {
  deleteTarget.value = user;
};

const doDelete = async () => {
  if (!deleteTarget.value) return;
  deleting.value = true;
  try {
    await $fetch(`${apiBase}/admin/users/${deleteTarget.value.id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    deleteTarget.value = null;
    await fetchUsers();
  } catch {}
  deleting.value = false;
};
</script>
