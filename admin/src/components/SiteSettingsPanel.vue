<template>
  <section class="panel settings-panel">
    <div class="settings-head">
      <div>
        <h3>{{ t('siteSettings.title') }}</h3>
        <p>{{ t('siteSettings.subtitle') }}</p>
      </div>
    </div>

    <div class="settings-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="settings-tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span class="settings-tab-icon" v-html="tab.icon"></span>
        <span class="settings-tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <div class="settings-tab-content">
      <!-- Tab 1: Brand -->
      <div v-show="activeTab === 'brand'" class="settings-card">
        <div class="settings-card-head">
          <div class="settings-card-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          </div>
          <h4>{{ t('siteSettings.brandSection') }}</h4>
        </div>

        <div class="logo-uploader">
          <div
            class="logo-dropzone"
            :class="{ dragging: isDragging }"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
          >
            <div class="logo-preview-wrap">
              <img v-if="previewLogo" :src="previewLogo" alt="site logo" class="logo-preview" />
              <div v-else class="logo-placeholder">64 × 64</div>
            </div>
            <div class="logo-dropzone-info">
              <p v-if="sourceSizeText" class="tips">{{ t('siteSettings.originalSize') }}{{ sourceSizeText }}</p>
              <p v-if="logoUploadMessage" class="tips" :class="logoUploadStatus === 'error' ? 'error-message' : 'success-message'">
                {{ logoUploadMessage }}
              </p>
              <input
                ref="fileInputRef"
                class="logo-file-input"
                type="file"
                accept="image/png,image/jpeg,image/svg+xml"
                :disabled="logoUploading"
                @change="onSelectLogo"
              />
              <button type="button" class="logo-file-button" :disabled="logoUploading" @click="fileInputRef?.click()">
                {{ logoUploading ? t('common.uploading') : t('siteSettings.selectFile') }}
              </button>
            </div>
          </div>
        </div>

        <label class="settings-field">
          <span>{{ t('siteSettings.siteTitleLabel') }}</span>
          <input class="settings-input" :value="siteTitle" :placeholder="t('siteSettings.siteTitlePlaceholder')" @input="$emit('update:siteTitle', ($event.target as HTMLInputElement).value)" />
        </label>
        <label class="settings-field">
          <span>{{ t('siteSettings.subtitleLabel') }}</span>
          <input class="settings-input" :value="siteSubtitle" :placeholder="t('siteSettings.subtitlePlaceholder')" @input="$emit('update:siteSubtitle', ($event.target as HTMLInputElement).value)" />
        </label>

        <div class="save-row">
          <button type="button" class="settings-save-button" :disabled="logoUploading" @click="$emit('save')">
            {{ logoUploading ? t('common.uploading') : t('siteSettings.saveSettings') }}
          </button>
        </div>
      </div>

      <!-- Tab 2: Footer -->
      <div v-show="activeTab === 'footer'" class="settings-card">
        <div class="settings-card-head">
          <div class="settings-card-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="15" x2="21" y2="15"/></svg>
          </div>
          <h4>{{ t('siteSettings.tabFooter') }}</h4>
        </div>

        <label class="settings-field">
          <span>{{ t('siteSettings.copyrightLabel') }}</span>
          <textarea class="settings-input settings-textarea" :value="copyrightText" :placeholder="t('siteSettings.copyrightPlaceholder')" rows="2" @input="$emit('update:copyrightText', ($event.target as HTMLTextAreaElement).value)"></textarea>
          <p class="tips">{{ t('siteSettings.copyrightTip') }}</p>
        </label>
        <label class="settings-field">
          <span>{{ t('siteSettings.icpLabel') }}</span>
          <textarea class="settings-input settings-textarea" :value="icpBeian" :placeholder="t('siteSettings.icpPlaceholder')" rows="2" @input="$emit('update:icpBeian', ($event.target as HTMLTextAreaElement).value)"></textarea>
          <p class="tips">{{ t('siteSettings.icpTip') }}</p>
        </label>
        <label class="settings-field">
          <span>{{ t('siteSettings.policeLabel') }}</span>
          <textarea class="settings-input settings-textarea" :value="policeBeian" :placeholder="t('siteSettings.policePlaceholder')" rows="3" @input="$emit('update:policeBeian', ($event.target as HTMLTextAreaElement).value)"></textarea>
          <p class="tips">{{ t('siteSettings.policeTip') }}</p>
        </label>

        <div class="save-row">
          <button type="button" class="settings-save-button" @click="$emit('save')">
            {{ t('siteSettings.saveSettings') }}
          </button>
        </div>
      </div>

      <!-- Tab: Footer Menu -->
      <div v-show="activeTab === 'footerMenu'" class="settings-card">
        <FooterMenuPanel />
      </div>

      <!-- Tab 3: Server -->
      <div v-show="activeTab === 'server'" class="settings-card">
        <div class="settings-card-head">
          <div class="settings-card-icon-row">
            <div class="settings-card-icon">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
            </div>
            <div>
              <h4>{{ t('siteSettings.serverSection') }}</h4>
              <p class="tips">{{ t('siteSettings.serverTip') }}</p>
            </div>
          </div>
        </div>

        <div class="settings-server-grid">
          <label class="settings-field">
            <span>{{ t('siteSettings.domainLabel') }}</span>
            <div class="settings-field-row">
              <input class="settings-input" :value="serverDomain" :placeholder="t('siteSettings.domainPlaceholder')" @input="$emit('update:serverDomain', ($event.target as HTMLInputElement).value)" />
              <button type="button" class="settings-field-btn" :title="t('siteSettings.autoDetectDomain')" @click="$emit('detect-domain')">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              </button>
            </div>
            <p class="tips">{{ t('siteSettings.domainTip') }}</p>
          </label>

          <label class="settings-field">
            <span>{{ t('siteSettings.jwtLabel') }}</span>
            <div class="settings-field-row">
              <input class="settings-input" :type="showSecretKey ? 'text' : 'password'" :value="serverSecretKey" :placeholder="t('siteSettings.jwtPlaceholder')" @input="$emit('update:serverSecretKey', ($event.target as HTMLInputElement).value)" />
              <button type="button" class="settings-field-btn" :title="showSecretKey ? t('siteSettings.hideKey') : t('siteSettings.showKey')" @click="showSecretKey = !showSecretKey">
                <svg v-if="showSecretKey" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.53 2.47 2.47 3.53l3.06 3.06C3.44 8.3 1.94 10.16 1 12c1.86 3.62 5.75 8 11 8 1.61 0 3.15-.32 4.57-.89l3.9 3.9 1.06-1.06-18-18Zm7.04 9.16 1.8 1.8a2.5 2.5 0 0 1-3.57-3.57l1.77 1.77ZM12 6c4.41 0 8.3 4.38 10 6-1.07 2.09-2.73 4.22-4.78 5.74l-2.05-2.05a4 4 0 0 0-5.61-5.61L7.51 7.51A10.16 10.16 0 0 1 12 6Zm0 12c-4.09 0-7.38-3.1-9.08-6 1.08-1.88 2.6-3.68 4.4-5.01l1.52 1.52a8 8 0 0 0 6.98 6.98l1.52 1.52C15.08 17.52 13.62 18 12 18Z" fill="currentColor"/></svg>
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5c-5.25 0-9.14 4.38-11 7 1.86 2.62 5.75 7 11 7s9.14-4.38 11-7c-1.86-2.62-5.75-7-11-7Zm0 12c-4.09 0-7.38-3.1-9.08-5 1.7-1.9 5-5 9.08-5s7.38 3.1 9.08 5c-1.7 1.9-5 5-9.08 5Zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" fill="currentColor"/></svg>
              </button>
            </div>
            <p class="tips">{{ t('siteSettings.jwtTip') }}</p>
          </label>

          <label class="settings-field">
            <span>{{ t('siteSettings.dbLabel') }}</span>
            <input class="settings-input settings-input-readonly" :value="serverDatabaseUrl" readonly />
            <p class="tips">{{ t('siteSettings.dbTip') }}</p>
          </label>

          <label class="settings-field">
            <span>{{ t('siteSettings.uploadDirLabel') }}</span>
            <input class="settings-input settings-input-readonly" :value="serverUploadDir" readonly />
            <p class="tips">{{ t('siteSettings.uploadDirTip') }}</p>
          </label>
        </div>

        <div class="save-row">
          <button type="button" class="settings-save-button" @click="$emit('save-server-config')">
            {{ t('siteSettings.saveServerConfig') }}
          </button>
        </div>
      </div>

      <!-- Tab 4: Homepage -->
      <div v-show="activeTab === 'homepage'" class="settings-card">
        <div class="settings-card-head">
          <div class="settings-card-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          </div>
          <h4>{{ t('siteSettings.tabHomepage') }}</h4>
        </div>

        <label class="settings-field">
          <span>{{ t('siteSettings.heroLabel') }}</span>
          <div class="hero-input-row">
            <input class="settings-input" :value="homepageHeroImage" :placeholder="t('siteSettings.heroPlaceholder')" @input="$emit('update:homepageHeroImage', ($event.target as HTMLInputElement).value)" />
            <button type="button" class="settings-field-btn" :title="t('siteSettings.heroPickFromMedia')" @click="showHeroPicker = !showHeroPicker">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            </button>
          </div>
          <p class="tips">{{ t('siteSettings.heroTip') }}</p>
          <div v-if="showHeroPicker" class="hero-picker">
            <button
              v-for="item in heroImageMedia"
              :key="item.id"
              type="button"
              class="hero-picker-item"
              :class="{ selected: item.url === homepageHeroImage }"
              @click="selectHeroImage(item.url)"
            >
              <img :src="fullUrl(item.url)" :alt="item.original_name" />
            </button>
            <p v-if="!heroImageMedia.length" class="tips">{{ t('siteSettings.heroNoImages') }}</p>
          </div>
        </label>

        <label class="settings-field">
          <span>{{ t('siteSettings.bgmLabel') }}</span>
          <textarea class="settings-input settings-textarea" :value="homepageBgmUrl" :placeholder="t('siteSettings.bgmPlaceholder')" rows="3" @input="$emit('update:homepageBgmUrl', ($event.target as HTMLTextAreaElement).value)"></textarea>
          <p class="tips">{{ t('siteSettings.bgmTip') }}</p>
        </label>

        <div class="save-row">
          <button type="button" class="settings-save-button" @click="$emit('save')">
            {{ t('siteSettings.saveSettings') }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import FooterMenuPanel from './FooterMenuPanel.vue'

const { t } = useI18n()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const sourceSizeText = ref('')
const showSecretKey = ref(false)
const showHeroPicker = ref(false)
const activeTab = ref('brand')

const tabIcons = {
  brand: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
  footer: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="15" x2="21" y2="15"/></svg>',
  footerMenu: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
  server: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>',
  homepage: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
}

const tabs = computed(() => [
  { key: 'brand', label: t('siteSettings.tabBrand'), icon: tabIcons.brand },
  { key: 'footer', label: t('siteSettings.tabFooter'), icon: tabIcons.footer },
  { key: 'footerMenu', label: t('siteSettings.tabFooterMenu'), icon: tabIcons.footerMenu },
  { key: 'server', label: t('siteSettings.tabServer'), icon: tabIcons.server },
  { key: 'homepage', label: t('siteSettings.tabHomepage'), icon: tabIcons.homepage },
])

const props = defineProps<{
  siteTitle: string
  siteSubtitle: string
  icpBeian: string
  policeBeian: string
  copyrightText: string
  homepageBgmUrl: string
  homepageHeroImage: string
  previewLogo: string
  logoUploading?: boolean
  logoUploadMessage?: string
  logoUploadStatus?: 'success' | 'error' | ''
  logoCropApplied?: boolean
  serverDomain: string
  serverSecretKey: string
  serverDatabaseUrl: string
  serverUploadDir: string
  media?: Array<{ id: number; url: string; original_name: string; media_type?: string; mime_type?: string }>
}>()

const emit = defineEmits<{
  'update:siteTitle': [value: string]
  'update:siteSubtitle': [value: string]
  'update:icpBeian': [value: string]
  'update:policeBeian': [value: string]
  'update:copyrightText': [value: string]
  'update:homepageBgmUrl': [value: string]
  'update:homepageHeroImage': [value: string]
  'update:serverDomain': [value: string]
  'update:serverSecretKey': [value: string]
  'select-logo': [file: File]
  'detect-domain': []
  save: []
  'save-server-config': []
}>()

const inspectImageSize = (file: File) => {
  if (!file.type.startsWith('image/')) {
    sourceSizeText.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    const img = new Image()
    img.onload = () => {
      sourceSizeText.value = `${img.width} × ${img.height}`
    }
    img.src = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}

const emitFile = (file: File) => {
  inspectImageSize(file)
  emit('select-logo', file)
}

const API_ORIGIN = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/api\/v1\/?$/, '') || ''

const fullUrl = (url: string) => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  const origin = API_ORIGIN || window.location.origin
  return `${origin}${value.startsWith('/') ? '' : '/'}${value}`
}

const heroImageMedia = computed(() => {
  if (!props.media) return []
  return props.media.filter(
    (item) => String(item.media_type || '').toUpperCase() === 'IMAGE' || String(item.mime_type || '').toLowerCase() === 'image/svg+xml',
  )
})

const selectHeroImage = (url: string) => {
  emit('update:homepageHeroImage', fullUrl(url))
  showHeroPicker.value = false
}

const onSelectLogo = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  emitFile(file)
  target.value = ''
}

const onDragOver = () => {
  isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event: DragEvent) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  emitFile(file)
}
</script>
