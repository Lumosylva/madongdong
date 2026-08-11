<template>
  <section class="panel fm-panel">
    <div class="fm-head">
      <div>
        <h3>{{ t('siteSettings.tabFooterMenu') }}</h3>
        <p class="fm-subtitle">{{ t('siteSettings.footerMenuSubtitle') }}</p>
      </div>
      <button type="button" class="fm-add-btn" @click="addItem">{{ t('siteSettings.addFooterMenuItem') }}</button>
    </div>

    <p v-if="toastMessage" class="fm-toast" :class="`toast-${toastStatus}`">{{ toastMessage }}</p>

    <ul v-if="items.length" class="fm-list">
      <li v-for="(item, idx) in items" :key="item.id ?? `new-${idx}`" class="fm-card">
        <label class="fm-field">
          <span>{{ t('siteSettings.fmTitle') }}</span>
          <input class="fm-input" v-model="item.title" :placeholder="t('siteSettings.fmTitlePlaceholder')" />
        </label>
        <label class="fm-field">
          <span>{{ t('siteSettings.fmPath') }}</span>
          <input class="fm-input" v-model="item.path" :placeholder="t('siteSettings.fmPathPlaceholder')" />
          <p class="fm-tips">{{ t('siteSettings.fmPathTip') }}</p>
        </label>
        <div class="fm-row-inline">
          <label class="fm-checkbox">
            <input type="checkbox" :checked="item.target === '_blank'" @change="onToggleBlank(item, $event)" />
            <span>{{ t('siteSettings.fmOpenInNewTab') }}</span>
          </label>
          <label class="fm-checkbox">
            <input type="checkbox" v-model="item.is_visible" />
            <span>{{ t('siteSettings.fmEnabled') }}</span>
          </label>
          <label class="fm-field fm-sort-field">
            <span>{{ t('siteSettings.fmSortOrder') }}</span>
            <input class="fm-input fm-sort-input" type="number" v-model.number="item.sort_order" />
          </label>
        </div>
        <div class="fm-actions">
          <button type="button" class="fm-btn fm-btn-save" :disabled="savingId === item.id" @click="save(item)">
            {{ t('common.save') }}
          </button>
          <button type="button" class="fm-btn fm-btn-delete" @click="remove(item, idx)">
            {{ t('common.delete') }}
          </button>
        </div>
      </li>
    </ul>
    <p v-else class="fm-empty">{{ t('siteSettings.fmEmpty') }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { adminApi } from '../api'

type Draft = {
  id?: number
  title: string
  path: string
  sort_order: number
  is_visible: boolean
  target: string | null
  description: string | null
  location: 'footer'
}

const { t } = useI18n()
const items = ref<Draft[]>([])
const savingId = ref<number | null>(null)
const toastMessage = ref('')
const toastStatus = ref<'success' | 'error' | ''>('')
let toastTimer: number | null = null

const showToast = (message: string, status: 'success' | 'error') => {
  toastMessage.value = message
  toastStatus.value = status
  if (toastTimer !== null) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toastMessage.value = ''
    toastStatus.value = ''
    toastTimer = null
  }, 2400)
}

const refetch = async () => {
  const res = await adminApi.getNavItems('footer')
  items.value = (res.data || []).map((raw: any) => ({
    id: raw.id,
    title: String(raw.title || ''),
    path: String(raw.path || ''),
    sort_order: Number(raw.sort_order || 0),
    is_visible: Boolean(raw.is_visible),
    target: raw.target ?? null,
    description: raw.description ?? null,
    location: 'footer',
  }))
}

const addItem = () => {
  const maxSort = items.value.reduce((max, it) => Math.max(max, it.sort_order), 0)
  items.value.unshift({
    title: '',
    path: '',
    sort_order: maxSort + 10,
    is_visible: true,
    target: null,
    description: null,
    location: 'footer',
  })
}

const onToggleBlank = (item: Draft, event: Event) => {
  item.target = (event.target as HTMLInputElement).checked ? '_blank' : null
}

const validate = (item: Draft): string | null => {
  if (!String(item.title || '').trim()) return t('siteSettings.fmTitleRequired')
  if (!String(item.path || '').trim()) return t('siteSettings.fmPathRequired')
  return null
}

const save = async (item: Draft) => {
  const err = validate(item)
  if (err) {
    showToast(err, 'error')
    return
  }
  savingId.value = item.id ?? -1
  try {
    const payload = {
      title: item.title.trim(),
      path: item.path.trim(),
      sort_order: Number(item.sort_order) || 0,
      is_visible: !!item.is_visible,
      target: item.target,
      description: item.description,
      location: 'footer' as const,
    }
    if (item.id) {
      await adminApi.updateNavItem(item.id, payload)
    } else {
      await adminApi.createNavItem(payload)
    }
    await refetch()
    showToast(t('siteSettings.fmSaved'), 'success')
  } catch (error) {
    showToast(error instanceof Error ? error.message : 'error', 'error')
  } finally {
    savingId.value = null
  }
}

const remove = async (item: Draft, idx: number) => {
  if (!item.id) {
    items.value.splice(idx, 1)
    return
  }
  try {
    await adminApi.deleteNavItem(item.id)
    await refetch()
    showToast(t('siteSettings.fmDeleted'), 'success')
  } catch (error) {
    showToast(error instanceof Error ? error.message : 'error', 'error')
  }
}

onMounted(() => {
  void refetch()
})
</script>

<style scoped>
.fm-panel {
  display: grid;
  gap: 14px;
}
.fm-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.fm-head h3 {
  margin: 0;
  font-size: 20px;
}
.fm-subtitle {
  margin: 4px 0 0;
  color: var(--text-soft);
  font-size: 13px;
}
.fm-add-btn {
  min-height: 40px;
  border-radius: 12px;
  padding: 0 16px;
  font-weight: 600;
  border: 1px solid rgba(14, 165, 164, 0.2);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(56, 189, 248, 0.08));
  color: var(--text);
  cursor: pointer;
}
.fm-add-btn:hover {
  border-color: rgba(14, 165, 164, 0.36);
}
.fm-toast {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
}
.fm-toast.toast-success {
  background: rgba(16, 185, 129, 0.1);
  color: #0f766e;
  border: 1px solid rgba(16, 185, 129, 0.24);
}
.fm-toast.toast-error {
  background: rgba(227, 91, 119, 0.1);
  color: #be123c;
  border: 1px solid rgba(227, 91, 119, 0.24);
}
.fm-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.fm-card {
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.7);
  display: grid;
  gap: 10px;
}
.fm-field {
  display: grid;
  gap: 4px;
}
.fm-field > span {
  font-size: 13px;
  color: var(--text-soft);
}
.fm-input {
  min-height: 40px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(255, 255, 255, 0.85);
  padding: 0 12px;
  font-size: 14px;
  color: var(--text);
}
.fm-input:focus {
  outline: none;
  border-color: rgba(14, 165, 164, 0.6);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.15);
}
.fm-tips {
  margin: 0;
  color: var(--text-soft);
  font-size: 12px;
}
.fm-row-inline {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  align-items: center;
}
.fm-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text);
}
.fm-sort-field {
  min-width: 120px;
}
.fm-sort-input {
  max-width: 100px;
}
.fm-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.fm-btn {
  min-height: 36px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(148, 163, 184, 0.08);
  color: var(--text-soft);
  cursor: pointer;
}
.fm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.fm-btn-save {
  border-color: rgba(14, 165, 164, 0.24);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(56, 189, 248, 0.08));
  color: var(--text);
}
.fm-btn-delete {
  border-color: rgba(227, 91, 119, 0.24);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.12), rgba(227, 91, 119, 0.06));
  color: #be123c;
}
.fm-empty {
  margin: 0;
  padding: 24px;
  text-align: center;
  color: var(--text-soft);
  border: 1px dashed var(--line);
  border-radius: 14px;
}
</style>
