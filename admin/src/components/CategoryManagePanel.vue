<template>
  <section class="panel">
    <h3>文章分类</h3>

    <div class="action-row">
      <input v-model="newName" placeholder="分类名称" />
      <input v-model="newSlug" placeholder="分类标识（slug）" @input="slugTouched = true" />
      <input v-model="newDescription" placeholder="分类描述（可选）" />
      <button :disabled="duplicatedSlug" @click="create">创建分类</button>
    </div>
    <p v-if="duplicatedSlug" class="error-message">slug 已存在，请修改后再创建</p>

    <ul>
      <li v-for="item in categories" :key="item.id" class="article-row">
        <div>
          <strong>{{ item.name }}</strong>
          <small>slug: {{ item.slug }} ｜ {{ item.description || '无描述' }}</small>
        </div>
        <div class="row-actions">
          <button @click="startEdit(item)">编辑</button>
          <button class="danger-btn" @click="$emit('delete', item.id)">删除</button>
        </div>
      </li>
    </ul>

    <div v-if="editing" class="panel" style="margin-top: 12px;">
      <h4>编辑分类</h4>
      <div class="action-row">
        <input v-model="editName" placeholder="分类名称" />
        <input v-model="editSlug" placeholder="分类标识（slug）" />
        <input v-model="editDescription" placeholder="分类描述（可选）" />
        <button @click="saveEdit">保存修改</button>
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

const startEdit = (item: CategoryItem) => {
  editing.value = true
  editId.value = item.id
  editName.value = item.name
  editSlug.value = item.slug
  editDescription.value = item.description || ''
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
