<template>
  <section class="user-panelRoot">
    <div class="user-hero">
      <div>
        <h3>{{ t('userManage.title') }}</h3>
        <p>{{ t('userManage.subtitle') }}</p>
      </div>
      <span class="user-heroCount">{{ t('common.count', { n: filteredUsers.length }) }}</span>
    </div>

    <div class="toolbarRow">
      <input v-model="keyword" class="fieldInput" :placeholder="t('userManage.searchPlaceholder')" />
      <select v-model="roleFilter" class="fieldInput">
        <option value="all">{{ t('userManage.allRoles') }}</option>
        <option value="admin">{{ t('role.admin') }}</option>
        <option value="author">{{ t('role.author') }}</option>
        <option value="reader">{{ t('role.reader') }}</option>
      </select>
      <button type="button" class="button buttonSecondary" @click="openAddUser">{{ t('userManage.addUser') }}</button>
      <button type="button" class="button buttonSecondary" :disabled="props.refreshing" @click="emit('refresh')">{{ props.refreshing ? t('common.refreshing') : t('common.refresh') }}</button>
    </div>

    <div class="bulkBar">
      <label class="selectAll">
        <input type="checkbox" :checked="allSelected" :indeterminate.prop="indeterminateSelected" @change="toggleSelectAll" />
        <span>{{ t('common.selectAll') }}</span>
      </label>
      <div class="bulkActions">
        <button type="button" class="button buttonSecondary" :disabled="!selectedIds.length" @click="bulkChangeRole('author')">{{ t('userManage.batchToAuthor') }}</button>
        <button type="button" class="button buttonSecondary" :disabled="!selectedIds.length" @click="bulkChangeRole('reader')">{{ t('userManage.batchToReader') }}</button>
        <button type="button" class="button buttonDanger" :disabled="!selectedIds.length" @click="bulkDelete">{{ t('userManage.batchDelete') }}</button>
      </div>
    </div>

    <div class="userList">
      <article v-for="item in pagedUsers" :key="item.id" class="userCard">
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
            <span>{{ t('userManage.usernamePrefix') }}{{ item.username }}</span>
            <span>{{ t('userManage.emailPrefix') }}{{ item.email }}</span>
          </div>
        </div>

        <div class="actionRow">
          <button type="button" class="button buttonSecondary" @click="editUser(item)">{{ t('common.edit') }}</button>
          <button type="button" class="button buttonDanger" @click="deleteOne(item.id)">{{ t('common.delete') }}</button>
        </div>
      </article>

      <p v-if="!pagedUsers.length" class="emptyState">{{ t('userManage.empty') }}</p>
    </div>

    <div class="paginationBar">
      <div class="pageSizeControl">
        <span>{{ t('common.perPage') }}</span>
        <select v-model="pageSize" class="fieldInput pageSizeSelect" @change="changePageSize">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>{{ t('common.items') }}</span>
      </div>
      <span class="pageIndicator">{{ t('userManage.pageInfo', { current: currentPage, total: totalPages }) }}</span>
      <div class="pageControls">
        <button type="button" class="button buttonSecondary" :disabled="!canGoPrev" @click="goPrevPage">{{ t('common.previous') }}</button>
        <button type="button" class="button buttonSecondary" :disabled="!canGoNext" @click="goNextPage">{{ t('common.next') }}</button>
      </div>
    </div>

    <div v-if="editorOpen" class="editorBackdrop" @click.self="closeEditor">
      <div class="editorPage">
        <div class="editorHero">
          <div>
            <p class="eyebrow">{{ editingUser?.id ? t('userManage.editUser') : t('userManage.newUser') }}</p>
            <h4>{{ editingUser?.id ? t('userManage.editHeading') : t('userManage.newHeading') }}</h4>
            <p>{{ t('userManage.avatarHint') }}</p>
          </div>
          <button type="button" class="modalClose" @click="closeEditor">×</button>
        </div>

        <div class="editorGrid">
          <section class="avatarPanel">
            <div class="avatarFrame">
              <img v-if="avatarPreview" :src="avatarPreview" :alt="t('userManage.avatarPreview')" class="avatarPreviewImg" />
              <div v-else class="avatarPreviewFallback">{{ avatarLetter(form.nickname || form.username) }}</div>
            </div>
            <div class="avatarPanelActions">
              <input ref="avatarFileInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" class="avatarFileInput" @change="onAvatarSelect" />
              <button type="button" class="button buttonSecondary" @click="avatarFileInputRef?.click()">{{ t('userManage.changeAvatar') }}</button>
              <button type="button" class="button buttonSecondary" @click="clearAvatar">{{ t('userManage.clearAvatar') }}</button>
            </div>
            <p class="avatarHint">{{ t('userManage.avatarTip') }}</p>
          </section>

          <section class="formPanel">
            <label class="fieldBlock">
              <span>{{ t('userManage.usernameLabel') }}</span>
              <input v-model="form.username" :disabled="!!editingUser?.id" class="fieldInput" />
            </label>
            <label class="fieldBlock">
              <span>{{ t('userManage.nicknameLabel') }}</span>
              <input v-model="form.nickname" class="fieldInput" />
            </label>
            <label class="fieldBlock">
              <span>{{ t('userManage.emailLabel') }}</span>
              <input v-model="form.email" class="fieldInput" />
            </label>
            <label class="fieldBlock">
              <span>{{ t('userManage.roleLabel') }}</span>
              <select v-model="form.role_name" class="fieldInput">
                <option value="reader">{{ t('role.reader') }}</option>
                <option value="author">{{ t('role.author') }}</option>
                <option value="admin">{{ t('role.admin') }}</option>
              </select>
            </label>
            <label class="fieldBlock">
              <span>{{ t('userManage.passwordLabel') }} {{ editingUser?.id ? t('userManage.passwordHint') : '' }}</span>
              <input v-model="form.password" type="password" class="fieldInput" />
            </label>
          </section>
        </div>

        <div class="editorActions">
          <button type="button" class="button buttonSecondary" @click="closeEditor">{{ t('common.cancel') }}</button>
          <button type="button" class="button buttonPrimary" @click="submitEditor">{{ t('common.save') }}</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

type UserRow = {
  id: number
  username: string
  nickname: string
  email: string
  avatar: string | null
  role_names: string[]
}

const props = defineProps<{ users: UserRow[]; refreshing?: boolean }>()
const emit = defineEmits<{
  create: [payload: Record<string, unknown>]
  update: [payload: Record<string, unknown>]
  delete: [ids: number[]]
  batchChangeRole: [ids: number[], role: string]
  refresh: []
}>()

const keyword = ref('')
const roleFilter = ref<'all' | 'admin' | 'author' | 'reader'>('all')
const pageSizeOptions = [10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)
const selectedIds = ref<number[]>([])
const editorOpen = ref(false)
const editingUser = ref<UserRow | null>(null)
const avatarFileInputRef = ref<HTMLInputElement | null>(null)
const avatarPreview = ref('')
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

const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize.value)))
const pagedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredUsers.value.slice(start, start + pageSize.value)
})
const canGoPrev = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)
const allSelected = computed(() => pagedUsers.value.length > 0 && pagedUsers.value.every((item) => selectedIds.value.includes(item.id)))
const indeterminateSelected = computed(() => selectedIds.value.length > 0 && !allSelected.value)

const avatarLetter = (value: string) => (value || 'U').slice(0, 1).toUpperCase()
const roleLabel = (value: string) => ({ admin: t('role.admin'), author: t('role.author'), reader: t('role.reader') }[value] || value)

const readFileAsDataUrl = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error(t('profile.readFailed')))
    reader.onload = () => resolve(String(reader.result || ''))
    reader.readAsDataURL(file)
  })

const cropToSquare = async (dataUrl: string) => {
  return await new Promise<string>((resolve, reject) => {
    const image = new Image()
    image.onload = () => {
      try {
        const size = Math.min(image.width, image.height)
        const offsetX = Math.floor((image.width - size) / 2)
        const offsetY = Math.floor((image.height - size) / 2)
        const canvas = document.createElement('canvas')
        const outputSize = Math.min(320, size || 320)
        canvas.width = outputSize
        canvas.height = outputSize
        const context = canvas.getContext('2d')
        if (!context) throw new Error(t('profile.compressFailed'))
        context.drawImage(image, offsetX, offsetY, size, size, 0, 0, outputSize, outputSize)
        resolve(canvas.toDataURL('image/jpeg', 0.92))
      } catch (error) {
        reject(error)
      }
    }
    image.onerror = () => reject(new Error(t('profile.loadFailed')))
    image.src = dataUrl
  })
}

const onAvatarSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  try {
    const result = await readFileAsDataUrl(file)
    const cropped = file.type === 'image/svg+xml' ? result : await cropToSquare(result)
    avatarPreview.value = cropped
    form.avatar = cropped
  } catch {
    avatarPreview.value = ''
  } finally {
    target.value = ''
  }
}

const clearAvatar = () => {
  avatarPreview.value = ''
  form.avatar = ''
  if (avatarFileInputRef.value) avatarFileInputRef.value.value = ''
}

const toggleSelect = (id: number) => {
  selectedIds.value = selectedIds.value.includes(id) ? selectedIds.value.filter((item) => item !== id) : [...selectedIds.value, id]
}

const toggleSelectAll = () => {
  const currentPageIds = pagedUsers.value.map((item) => item.id)
  if (allSelected.value) {
    selectedIds.value = selectedIds.value.filter((id) => !currentPageIds.includes(id))
    return
  }
  const merged = new Set([...selectedIds.value, ...currentPageIds])
  selectedIds.value = Array.from(merged)
}

const changePageSize = () => {
  currentPage.value = 1
}

const goPrevPage = () => {
  if (canGoPrev.value) currentPage.value -= 1
}

const goNextPage = () => {
  if (canGoNext.value) currentPage.value += 1
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
  avatarPreview.value = ''
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
  avatarPreview.value = item.avatar || ''
  editorOpen.value = true
}

const closeEditor = () => {
  editorOpen.value = false
  if (avatarFileInputRef.value) avatarFileInputRef.value.value = ''
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