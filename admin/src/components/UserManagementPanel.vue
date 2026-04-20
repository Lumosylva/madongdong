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

<style scoped>
.userPanelRoot {
  display: grid;
  gap: 24px;
  min-width: 0;
  padding: 8px 0 10px;
}

.user-hero {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 4px 2px 2px;
}

.user-hero h3 {
  margin: 0;
  font-size: 22px;
  letter-spacing: 0.01em;
  line-height: 1.2;
}

.user-hero p {
  margin: 8px 0 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.6;
}

.user-heroCount {
  flex: 0 0 auto;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid rgba(14, 165, 164, 0.14);
  background: rgba(14, 165, 164, 0.06);
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1;
  white-space: nowrap;
}

.toolbarRow {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px auto;
  gap: 14px;
  align-items: center;
}

.fieldInput {
  width: 100%;
  min-height: 42px;
  border-radius: 13px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(255, 255, 255, 0.74);
  color: var(--text);
  padding: 0 14px;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.58) inset, 0 6px 16px rgba(16, 35, 63, 0.04);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.fieldInput:hover {
  border-color: rgba(14, 165, 164, 0.3);
  background: rgba(255, 255, 255, 0.88);
}

.fieldInput:focus {
  outline: none;
  border-color: rgba(14, 165, 164, 0.6);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.16);
  transform: translateY(-1px);
}

.bulkBar {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.64);
}

.selectAll {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-soft);
  font-size: 13px;
}

.bulkActions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.userList {
  display: grid;
  gap: 14px;
}

.userCard {
  display: grid;
  grid-template-columns: 28px 54px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  padding: 16px 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
  box-shadow: 0 6px 16px rgba(16, 35, 63, 0.04);
}

.checkWrap {
  display: grid;
  place-items: center;
}

.avatarWrap {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.16), rgba(56, 189, 248, 0.12));
  display: grid;
  place-items: center;
}

.avatarImg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatarFallback {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.userMain {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.cardHead {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.roleList {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.roleList em {
  font-style: normal;
  font-size: 12px;
  color: var(--accent);
  background: rgba(14, 165, 164, 0.08);
  border: 1px solid rgba(14, 165, 164, 0.12);
  padding: 4px 8px;
  border-radius: 999px;
}

.metaRow {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.45;
}

.actionRow {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.button {
  min-height: 40px;
  border-radius: 12px;
  padding: 0 14px;
  border: 1px solid rgba(14, 165, 164, 0.2);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(56, 189, 248, 0.08));
  color: var(--text);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.button:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: rgba(14, 165, 164, 0.34);
  box-shadow: 0 10px 22px rgba(16, 35, 63, 0.09);
}

.buttonSecondary {
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.12), rgba(56, 189, 248, 0.06));
}

.buttonPrimary {
  min-width: 120px;
}

.buttonDanger {
  border-color: rgba(227, 91, 119, 0.2);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.14), rgba(255, 255, 255, 0.08));
}

.button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.emptyState {
  margin: 0;
  padding: 20px 16px;
  text-align: center;
  color: var(--text-soft);
  border: 1px dashed var(--line);
  border-radius: 14px;
}

.modalBackdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.48);
  backdrop-filter: blur(8px);
  display: grid;
  place-items: center;
  z-index: 600;
  padding: 24px;
}

.modalCard {
  width: min(760px, 100%);
  border: 1px solid var(--line);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22);
  padding: 22px;
  display: grid;
  gap: 18px;
}

.modalHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.eyebrow {
  margin: 0 0 4px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.modalHead h4 {
  margin: 0;
  font-size: 18px;
}

.modalClose {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(148, 163, 184, 0.08);
  color: var(--text-soft);
}

.modalGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}

.fieldBlock {
  display: grid;
  gap: 8px;
}

.fieldBlock > span {
  color: var(--text-soft);
  font-size: 13px;
}

.modalActions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 900px) {
  .toolbarRow,
  .modalGrid {
    grid-template-columns: 1fr;
  }

  .bulkBar,
  .userCard {
    grid-template-columns: 1fr;
  }

  .actionRow {
    justify-content: flex-start;
  }

  .bulkBar {
    align-items: flex-start;
  }
}
</style>
