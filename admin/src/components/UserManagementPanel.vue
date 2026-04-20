<template>
  <section class="panel user-panel">
    <div class="article-manage-head user-head">
      <div>
        <h3>用户管理</h3>
        <p class="user-subtitle">搜索、筛选、编辑与批量管理系统用户</p>
      </div>
      <span class="article-count user-count">共 {{ filteredUsers.length }} 人</span>
    </div>

    <div class="user-toolbar">
      <input v-model="keyword" class="user-search-input" placeholder="搜索用户名、昵称或邮箱" />
      <select v-model="roleFilter" class="user-filter-select">
        <option value="all">全部角色</option>
        <option value="admin">系统管理员</option>
        <option value="author">内容作者</option>
        <option value="reader">普通读者</option>
      </select>
      <button type="button" class="user-button secondary" @click="openAddUser">添加用户</button>
    </div>

    <div class="user-bulk-bar">
      <label class="user-select-all">
        <input type="checkbox" :checked="allSelected" :indeterminate.prop="indeterminateSelected" @change="toggleSelectAll" />
        <span>全选当前页</span>
      </label>
      <div class="user-bulk-actions">
        <button type="button" class="user-button secondary" :disabled="!selectedIds.length" @click="bulkChangeRole('author')">批量改为作者</button>
        <button type="button" class="user-button secondary" :disabled="!selectedIds.length" @click="bulkChangeRole('reader')">批量改为读者</button>
        <button type="button" class="user-button danger" :disabled="!selectedIds.length" @click="bulkDelete">批量删除</button>
      </div>
    </div>

    <div class="user-list">
      <article v-for="item in filteredUsers" :key="item.id" class="user-card">
        <label class="user-checkbox-wrap">
          <input type="checkbox" :checked="selectedIds.includes(item.id)" @change="toggleSelect(item.id)" />
        </label>

        <div class="user-avatar-wrap">
          <img v-if="item.avatar" :src="item.avatar" :alt="item.username" class="user-avatar" />
          <div v-else class="user-avatar-placeholder">{{ avatarLetter(item.nickname || item.username) }}</div>
        </div>

        <div class="user-main">
          <div class="user-card-head">
            <strong>{{ item.nickname || '-' }}</strong>
            <span class="user-role-list">
              <em v-for="role in item.role_names" :key="role">{{ roleLabel(role) }}</em>
            </span>
          </div>
          <div class="user-meta">
            <span>用户名：{{ item.username }}</span>
            <span>邮箱：{{ item.email }}</span>
          </div>
        </div>

        <div class="user-actions">
          <button type="button" class="user-button secondary" @click="editUser(item)">编辑</button>
          <button type="button" class="user-button danger" @click="deleteOne(item.id)">删除</button>
        </div>
      </article>
    </div>

    <div v-if="editorOpen" class="user-modal-backdrop" @click.self="closeEditor">
      <div class="user-modal">
        <div class="user-modal-head">
          <div>
            <p class="user-modal-eyebrow">{{ editingUser?.id ? '编辑用户' : '添加用户' }}</p>
            <h4>{{ editingUser?.id ? '修改用户信息' : '新建用户' }}</h4>
          </div>
          <button type="button" class="user-modal-close" @click="closeEditor">×</button>
        </div>

        <div class="user-modal-grid">
          <label class="user-field">
            <span>用户名</span>
            <input v-model="form.username" :disabled="!!editingUser?.id" class="user-input" />
          </label>
          <label class="user-field">
            <span>昵称</span>
            <input v-model="form.nickname" class="user-input" />
          </label>
          <label class="user-field">
            <span>邮箱</span>
            <input v-model="form.email" class="user-input" />
          </label>
          <label class="user-field">
            <span>头像</span>
            <input v-model="form.avatar" class="user-input" placeholder="头像 URL 或 base64" />
          </label>
          <label class="user-field">
            <span>角色</span>
            <select v-model="form.role_name" class="user-input">
              <option value="reader">普通读者</option>
              <option value="author">内容作者</option>
              <option value="admin">系统管理员</option>
            </select>
          </label>
          <label class="user-field">
            <span>密码 {{ editingUser?.id ? '(留空则不修改)' : '' }}</span>
            <input v-model="form.password" type="password" class="user-input" />
          </label>
        </div>

        <div class="user-modal-actions">
          <button type="button" class="user-button secondary" @click="closeEditor">取消</button>
          <button type="button" class="user-button primary" @click="submitEditor">保存</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

type UserRow = {
  id: number
  username: string
  nickname: string
  email: string
  avatar: string | null
  role_names: string[]
}

const props = defineProps<{ users: UserRow[] }>()
const emit = defineEmits<{
  search: [keyword: string]
  filterRole: [role: string]
  create: [payload: Record<string, unknown>]
  update: [payload: Record<string, unknown>]
  delete: [ids: number[]]
  batchChangeRole: [ids: number[], role: string]
}>()

const keyword = ref('')
const roleFilter = ref<'all' | 'admin' | 'author' | 'reader'>('all')
const selectedIds = ref<number[]>([])
const editorOpen = ref(false)
const editingUser = ref<UserRow | null>(null)
const form = reactive({
  username: '',
  nickname: '',
  email: '',
  avatar: '',
  role_name: 'reader',
  password: '',
})

const filteredUsers = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  return props.users.filter((item) => {
    const matchedKeyword = !key || [item.username, item.nickname, item.email].some((value) => String(value || '').toLowerCase().includes(key))
    const matchedRole = roleFilter.value === 'all' || item.role_names.includes(roleFilter.value)
    return matchedKeyword && matchedRole
  })
})

const allSelected = computed(() => filteredUsers.value.length > 0 && filteredUsers.value.every((item) => selectedIds.value.includes(item.id)))
const indeterminateSelected = computed(() => selectedIds.value.length > 0 && !allSelected.value)

watch(keyword, (value) => emit('search', value))
watch(roleFilter, (value) => emit('filterRole', value))

const avatarLetter = (value: string) => (value || 'U').slice(0, 1).toUpperCase()
const roleLabel = (value: string) => ({ admin: '系统管理员', author: '内容作者', reader: '普通读者' }[value] || value)

const toggleSelect = (id: number) => {
  selectedIds.value = selectedIds.value.includes(id) ? selectedIds.value.filter((item) => item !== id) : [...selectedIds.value, id]
}

const toggleSelectAll = () => {
  selectedIds.value = allSelected.value ? [] : filteredUsers.value.map((item) => item.id)
}

const bulkDelete = () => emit('delete', selectedIds.value)
const bulkChangeRole = (role: string) => emit('batchChangeRole', selectedIds.value, role)

const openAddUser = () => {
  editingUser.value = null
  form.username = ''
  form.nickname = ''
  form.email = ''
  form.avatar = ''
  form.role_name = 'reader'
  form.password = ''
  editorOpen.value = true
}

const editUser = (item: UserRow) => {
  editingUser.value = item
  form.username = item.username
  form.nickname = item.nickname
  form.email = item.email
  form.avatar = item.avatar || ''
  form.role_name = item.role_names[0] || 'reader'
  form.password = ''
  editorOpen.value = true
}

const closeEditor = () => {
  editorOpen.value = false
}

const submitEditor = () => {
  const payload = {
    id: editingUser.value?.id,
    username: form.username.trim(),
    nickname: form.nickname.trim(),
    email: form.email.trim(),
    avatar: form.avatar.trim() || null,
    role_name: form.role_name,
    password: form.password || null,
  }
  if (editingUser.value?.id) emit('update', payload)
  else emit('create', payload)
  editorOpen.value = false
}

const deleteOne = (id: number) => emit('delete', [id])
</script>
