<template>
  <section class="user-panelRoot">
    <div class="user-hero">
      <div>
        <h3>用户管理</h3>
        <p>搜索、筛选、编辑与批量管理系统用户</p>
      </div>
      <span class="user-heroCount">共 {{ filteredUsers.length }} 人</span>
    </div>

    <div class="toolbarRow">
      <input v-model="keyword" class="fieldInput" placeholder="搜索用户名、昵称或邮箱" />
      <select v-model="roleFilter" class="fieldInput">
        <option value="all">全部角色</option>
        <option value="admin">系统管理员</option>
        <option value="author">内容作者</option>
        <option value="reader">普通读者</option>
      </select>
      <button type="button" class="button buttonSecondary" @click="openAddUser">添加用户</button>
    </div>

    <div class="bulkBar">
      <label class="selectAll">
        <input type="checkbox" :checked="allSelected" :indeterminate.prop="indeterminateSelected" @change="toggleSelectAll" />
        <span>全选当前页</span>
      </label>
      <div class="bulkActions">
        <button type="button" class="button buttonSecondary" :disabled="!selectedIds.length" @click="bulkChangeRole('author')">批量改为作者</button>
        <button type="button" class="button buttonSecondary" :disabled="!selectedIds.length" @click="bulkChangeRole('reader')">批量改为读者</button>
        <button type="button" class="button buttonDanger" :disabled="!selectedIds.length" @click="bulkDelete">批量删除</button>
      </div>
    </div>

    <div class="userList">
      <article v-for="item in filteredUsers" :key="item.id" class="userCard">
        <label class="checkWrap">
          <input type="checkbox" :checked="selectedIds.includes(item.id)" @change="toggleSelect(item.id)" />
        </label>

        <div class="avatarWrap">
          <img v-if="item.avatar" :src="item.avatar" :alt="item.username" class="avatarImg" />
          <div v-else class="avatarFallback">{{ avatarLetter(item.nickname || item.username) }}</div>
        </div>

        <div class="userMain">
          <div class="cardHead">
            <strong>{{ item.nickname || '-' }}</strong>
            <span class="roleList">
              <em v-for="role in item.role_names" :key="role">{{ roleLabel(role) }}</em>
            </span>
          </div>
          <div class="metaRow">
            <span>用户名：{{ item.username }}</span>
            <span>邮箱：{{ item.email }}</span>
          </div>
        </div>

        <div class="actionRow">
          <button type="button" class="button buttonSecondary" @click="editUser(item)">编辑</button>
          <button type="button" class="button buttonDanger" @click="deleteOne(item.id)">删除</button>
        </div>
      </article>

      <p v-if="!filteredUsers.length" class="emptyState">暂无符合条件的用户</p>
    </div>

    <div v-if="editorOpen" class="modalBackdrop" @click.self="closeEditor">
      <div class="modalCard">
        <div class="modalHead">
          <div>
            <p class="eyebrow">{{ editingUser?.id ? '编辑用户' : '添加用户' }}</p>
            <h4>{{ editingUser?.id ? '修改用户信息' : '新建用户' }}</h4>
          </div>
          <button type="button" class="modalClose" @click="closeEditor">×</button>
        </div>

        <div class="modalGrid">
          <label class="fieldBlock">
            <span>用户名</span>
            <input v-model="form.username" :disabled="!!editingUser?.id" class="fieldInput" />
          </label>
          <label class="fieldBlock">
            <span>昵称</span>
            <input v-model="form.nickname" class="fieldInput" />
          </label>
          <label class="fieldBlock">
            <span>邮箱</span>
            <input v-model="form.email" class="fieldInput" />
          </label>
          <label class="fieldBlock">
            <span>头像</span>
            <input v-model="form.avatar" class="fieldInput" placeholder="头像 URL 或 base64" />
          </label>
          <label class="fieldBlock">
            <span>角色</span>
            <select v-model="form.role_name" class="fieldInput">
              <option value="reader">普通读者</option>
              <option value="author">内容作者</option>
              <option value="admin">系统管理员</option>
            </select>
          </label>
          <label class="fieldBlock">
            <span>密码 {{ editingUser?.id ? '(留空则不修改)' : '' }}</span>
            <input v-model="form.password" type="password" class="fieldInput" />
          </label>
        </div>

        <div class="modalActions">
          <button type="button" class="button buttonSecondary" @click="closeEditor">取消</button>
          <button type="button" class="button buttonPrimary" @click="submitEditor">保存</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

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

<style src="../styles/user-management.css" scoped></style>