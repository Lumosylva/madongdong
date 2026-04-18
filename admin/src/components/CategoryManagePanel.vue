<template>
  <section class="panel category-panel">
    <div class="article-manage-head category-head">
      <div>
        <h3>文章分类</h3>
        <p class="category-subtitle">统一管理文章分类名称、标识与描述</p>
      </div>
      <span class="article-count category-count">共 {{ categories.length }} 项</span>
    </div>

    <div class="category-create-panel">
      <div class="category-form-head">
        <h4>创建分类</h4>
        <span class="category-form-tip">自动生成 slug，也可以手动修改</span>
      </div>
      <div class="action-row category-action-row">
        <input class="category-input" v-model="newName" placeholder="分类名称" />
        <input class="category-input" v-model="newSlug" placeholder="分类标识（slug）" @input="slugTouched = true" />
        <input class="category-input" v-model="newDescription" placeholder="分类描述（可选）" />
        <button class="category-create-btn" :disabled="duplicatedSlug" @click="create">创建分类</button>
      </div>
      <p v-if="duplicatedSlug" class="error-message category-error">slug 已存在，请修改后再创建</p>
    </div>

    <div class="category-toolbar">
      <div class="category-toolbar-left">
        <span class="category-toolbar-selected">已选择：{{ selectedCategory ? selectedCategory.name : '未选择' }}</span>
        <span v-if="selectedCategory && isDefaultCategory(selectedCategory)" class="category-badge category-badge-locked">默认</span>
      </div>
      <div class="category-toolbar-actions">
        <button :disabled="!selectedCategory || isDefaultCategory(selectedCategory)" @click="openEditSelected">编辑选中</button>
        <button class="danger-btn" :disabled="!selectedCategory || isDefaultCategory(selectedCategory)" @click="deleteSelected">删除选中</button>
      </div>
    </div>

    <div class="category-grid">
      <button
        v-for="item in categories"
        :key="item.id"
        type="button"
        class="category-card"
        :class="{ selected: selectedCategoryId === item.id, 'category-card-default': isDefaultCategory(item) }"
        @click="selectCategory(item)"
      >
        <div class="category-card-head">
          <strong>{{ item.name }}</strong>
          <span v-if="isDefaultCategory(item)" class="category-badge category-badge-locked">锁定</span>
        </div>
        <small class="category-card-meta">slug：{{ item.slug }}</small>
        <p class="category-card-desc">{{ item.description || '无描述' }}</p>
      </button>
    </div>

    <div v-if="editing" class="category-edit-panel">
      <div class="category-edit-head">
        <div>
          <h4>编辑分类</h4>
          <p class="category-form-tip">修改分类名称、标识和描述</p>
        </div>
        <button class="category-edit-close" type="button" @click="editing = false">关闭</button>
      </div>
      <div class="action-row category-edit-row">
        <input class="category-input" v-model="editName" placeholder="分类名称" />
        <input class="category-input" v-model="editSlug" placeholder="分类标识（slug）" />
        <input class="category-input" v-model="editDescription" placeholder="分类描述（可选）" />
        <button class="category-save-btn" @click="saveEdit">保存修改</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

type CategoryItem = {
  id: number
  name: string
  slug: string
  description: string | null
}

const props = defineProps<{
  categories: CategoryItem[]
}>()

const emit = defineEmits<{
  create: [payload: { name: string; slug: string; description: string | null }]
  update: [payload: { id: number; name: string; slug: string; description: string | null }]
  delete: [categoryId: number]
}>()

const newName = ref('')
const newSlug = ref('')
const newDescription = ref('')
const slugTouched = ref(false)

const editing = ref(false)
const editId = ref<number | null>(null)
const editName = ref('')
const editSlug = ref('')
const editDescription = ref('')
const selectedCategoryId = ref<number | null>(null)

const selectedCategory = computed(() => props.categories.find((item) => item.id === selectedCategoryId.value) || null)

const slugify = (value: string) =>
  value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\u4e00-\u9fa5\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'category'

watch(newName, (value) => {
  if (!slugTouched.value) {
    newSlug.value = slugify(value)
  }
})

watch(newSlug, (value) => {
  if (value.trim()) slugTouched.value = true
})

const duplicatedSlug = computed(() => {
  const target = newSlug.value.trim().toLowerCase()
  if (!target) return false
  return props.categories.some((item) => String(item.slug || '').toLowerCase() === target)
})

const create = () => {
  if (!newName.value.trim() || !newSlug.value.trim() || duplicatedSlug.value) return
  emit('create', {
    name: newName.value.trim(),
    slug: newSlug.value.trim(),
    description: newDescription.value.trim() || null,
  })
  newName.value = ''
  newSlug.value = ''
  newDescription.value = ''
  slugTouched.value = false
}

const isDefaultCategory = (item: CategoryItem) => {
  const name = String(item.name || '').trim()
  const slug = String(item.slug || '').trim().toLowerCase()
  return name === '未分类' || slug === 'uncategorized'
}

const selectCategory = (item: CategoryItem) => {
  selectedCategoryId.value = item.id
}

const startEdit = (item: CategoryItem) => {
  if (isDefaultCategory(item)) return
  editing.value = true
  editId.value = item.id
  editName.value = item.name
  editSlug.value = item.slug
  editDescription.value = item.description || ''
}

const openEditSelected = () => {
  if (!selectedCategory.value || isDefaultCategory(selectedCategory.value)) return
  startEdit(selectedCategory.value)
}

const deleteSelected = () => {
  if (!selectedCategory.value || isDefaultCategory(selectedCategory.value)) return
  emit('delete', selectedCategory.value.id)
}

const saveEdit = () => {
  if (!editing.value || editId.value == null || !editName.value.trim() || !editSlug.value.trim()) return
  emit('update', {
    id: editId.value,
    name: editName.value.trim(),
    slug: editSlug.value.trim(),
    description: editDescription.value.trim() || null,
  })
  editing.value = false
  editId.value = null
}
</script>
