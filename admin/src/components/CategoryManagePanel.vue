<template>
  <section class="panel category-panel">
    <div class="article-manage-head category-head">
      <div>
        <h3>{{ t('category.title') }}</h3>
        <p class="category-subtitle">{{ t('category.subtitle') }}</p>
      </div>
      <span class="article-count category-count">{{ t('common.count', { n: categories.length }) }}</span>
    </div>

    <div class="category-create-panel">
      <div class="category-form-head">
        <h4>{{ t('category.createHeading') }}</h4>
        <span class="category-form-tip">{{ t('category.createTip') }}</span>
      </div>
      <div class="category-form-stack">
        <label class="category-field">
          <span>{{ t('category.parentLabel') }}</span>
          <select class="category-input" v-model="newParentId">
            <option :value="null">{{ t('category.noParent') }}</option>
            <option v-for="item in rootCategories" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </label>
        <label class="category-field">
          <span>{{ t('category.nameLabel') }}</span>
          <input class="category-input" v-model="newName" :placeholder="t('category.namePlaceholder')" />
        </label>
        <label class="category-field">
          <span>{{ t('category.slugLabel') }}</span>
          <input class="category-input" v-model="newSlug" :placeholder="t('category.slugPlaceholder')" @input="slugTouched = true" />
        </label>
        <label class="category-field">
          <span>{{ t('category.descLabel') }}</span>
          <input class="category-input" v-model="newDescription" :placeholder="t('category.descPlaceholder')" />
        </label>
        <button class="category-create-btn" :disabled="duplicatedSlug" @click="create">{{ t('category.createButton') }}</button>
      </div>
      <p v-if="duplicatedSlug" class="error-message category-error">{{ t('category.slugExists') }}</p>
    </div>

    <div class="category-toolbar">
      <div class="category-toolbar-left">
        <span class="category-toolbar-selected">{{ t('category.selected') }}{{ selectedCategory ? selectedCategory.name : t('category.noneSelected') }}</span>
        <span v-if="selectedCategory && isDefaultCategory(selectedCategory)" class="category-badge category-badge-locked">{{ t('category.defaultBadge') }}</span>
      </div>
      <div class="category-toolbar-actions">
        <button :disabled="!selectedCategory || isDefaultCategory(selectedCategory)" @click="openEditSelected">{{ t('category.editSelected') }}</button>
        <button class="danger-btn" :disabled="!selectedCategory || isDefaultCategory(selectedCategory)" @click="deleteSelected">{{ t('category.deleteSelected') }}</button>
      </div>
    </div>

    <div class="category-tree">
      <template v-for="item in rootCategories" :key="item.id">
        <div
          type="button"
          class="category-card category-card-root"
          :class="{ selected: selectedCategoryId === item.id, 'category-card-default': isDefaultCategory(item) }"
          @click="selectCategory(item)"
        >
          <div class="category-card-head">
            <strong>{{ item.name }}</strong>
            <span v-if="isDefaultCategory(item)" class="category-badge category-badge-locked">{{ t('category.locked') }}</span>
          </div>
          <small class="category-card-meta">{{ t('category.slugPrefix') }}{{ item.slug }}</small>
          <p class="category-card-desc">{{ item.description || t('category.noDescription') }}</p>
        </div>
        <div v-if="getChildCategories(item.id).length" class="category-children">
          <div
            v-for="child in getChildCategories(item.id)"
            :key="child.id"
            type="button"
            class="category-card category-card-child"
            :class="{ selected: selectedCategoryId === child.id }"
            @click="selectCategory(child)"
          >
            <div class="category-card-head">
              <strong>{{ child.name }}</strong>
            </div>
            <small class="category-card-meta">{{ t('category.slugPrefix') }}{{ child.slug }}</small>
            <p class="category-card-desc">{{ child.description || t('category.noDescription') }}</p>
          </div>
        </div>
      </template>
    </div>

    <div v-if="editing" class="category-edit-panel">
      <div class="category-edit-head">
        <div>
          <h4>{{ t('category.editHeading') }}</h4>
          <p class="category-form-tip">{{ t('category.editTip') }}</p>
        </div>
        <button class="category-edit-close" type="button" @click="editing = false">{{ t('common.close') }}</button>
      </div>
      <div class="category-form-stack">
        <label class="category-field">
          <span>{{ t('category.parentLabel') }}</span>
          <select class="category-input" v-model="editParentId" :disabled="isDefaultCategory(selectedCategory!)">
            <option :value="null">{{ t('category.noParent') }}</option>
            <option v-for="item in editableParentOptions" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </label>
        <label class="category-field">
          <span>{{ t('category.editNameLabel') }}</span>
          <input class="category-input" v-model="editName" :placeholder="t('category.editNamePlaceholder')" />
        </label>
        <label class="category-field">
          <span>{{ t('category.editSlugLabel') }}</span>
          <input class="category-input" v-model="editSlug" :placeholder="t('category.editSlugPlaceholder')" />
        </label>
        <label class="category-field">
          <span>{{ t('category.editDescLabel') }}</span>
          <input class="category-input" v-model="editDescription" :placeholder="t('category.editDescPlaceholder')" />
        </label>
        <button class="category-save-btn" @click="saveEdit">{{ t('category.saveChanges') }}</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { pinyin } from 'pinyin-pro'

const { t } = useI18n()

type CategoryItem = {
  id: number
  name: string
  slug: string
  description: string | null
  parent_id: number | null
}

const props = defineProps<{
  categories: CategoryItem[]
}>()

const emit = defineEmits<{
  create: [payload: { name: string; slug: string; description: string | null; parent_id: number | null }]
  update: [payload: { id: number; name: string; slug: string; description: string | null; parent_id: number | null }]
  delete: [categoryId: number]
}>()

const newName = ref('')
const newSlug = ref('')
const newDescription = ref('')
const newParentId = ref<number | null>(null)
const slugTouched = ref(false)

const editing = ref(false)
const editId = ref<number | null>(null)
const editName = ref('')
const editSlug = ref('')
const editDescription = ref('')
const editParentId = ref<number | null>(null)
const selectedCategoryId = ref<number | null>(null)

const rootCategories = computed(() => props.categories.filter((item) => !item.parent_id))
const getChildCategories = (parentId: number) => props.categories.filter((item) => item.parent_id === parentId)

const selectedCategory = computed(() => props.categories.find((item) => item.id === selectedCategoryId.value) || null)

const editableParentOptions = computed(() => {
  if (!editing.value || editId.value == null) return rootCategories.value
  return rootCategories.value.filter((item) => item.id !== editId.value)
})

const slugify = (value: string) => {
  const converted = pinyin(value, { toneType: 'none', type: 'array' }).join('')
  return converted
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'category'
}

watch(newName, (value) => {
  if (!value.trim()) {
    slugTouched.value = false
    return
  }
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
    parent_id: newParentId.value,
  })
  newName.value = ''
  newSlug.value = ''
  newDescription.value = ''
  newParentId.value = null
  slugTouched.value = false
}

const isDefaultCategory = (item: CategoryItem) => {
  const name = String(item.name || '').trim()
  const slug = String(item.slug || '').trim().toLowerCase()
  return name === t('category.uncategorized') || slug === 'uncategorized'
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
  editParentId.value = item.parent_id
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
    parent_id: editParentId.value,
  })
  editing.value = false
  editId.value = null
}
</script>
