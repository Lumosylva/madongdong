<template>
  <section class="panel media-panel">
    <div class="article-manage-head media-head">
      <div>
        <h3>{{ t('media.title') }}</h3>
        <p class="media-subtitle">{{ t('media.subtitle') }}</p>
      </div>
      <span class="article-count media-count">{{ t('common.count', { n: media.length }) }}</span>
    </div>

    <p v-if="toastMessage" class="tips media-toast" :class="toastStatus === 'error' ? 'error-message' : 'success-message'">
      {{ toastMessage }}
    </p>
    <p v-if="copyMessage" class="tips success-message">{{ copyMessage }}</p>

    <div class="media-body">
      <!-- 左侧文件夹树侧边栏 -->
      <aside class="media-sidebar">
        <div class="media-sidebar-nodes">
          <button
            type="button"
            class="media-folder-item"
            :class="{ active: activeFolderId === undefined }"
            @click="selectFolder(undefined)"
          >
            <span class="media-folder-icon">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
            </span>
            <span class="media-folder-name">{{ t('media.allMedia') }}</span>
          </button>
          <button
            type="button"
            class="media-folder-item"
            :class="{ active: activeFolderId === null }"
            @click="selectFolder(null)"
          >
            <span class="media-folder-icon">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            </span>
            <span class="media-folder-name">{{ t('media.unorganized') }}</span>
          </button>
          <div v-if="folders.length" class="media-sidebar-divider"></div>
          <template v-for="folder in folders" :key="folder.id">
            <MediaFolderTreeItem
              :folder="folder"
              :active-folder-id="activeFolderId"
              :expanded-ids="expandedFolderIds"
              @select="selectFolder"
              @toggle-expand="toggleFolderExpand"
              @create-child="openCreateChildFolder"
              @rename="openRenameFolder"
              @delete="openDeleteFolder"
            />
          </template>
        </div>
        <button type="button" class="media-sidebar-root-btn" @click="openCreateRootFolder">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          {{ t('media.newRootFolder') }}
        </button>
      </aside>

      <!-- 右侧内容区 -->
      <div class="media-content">
        <div class="media-upload-row">
          <input ref="fileInputRef" class="media-file-input" type="file" accept="image/*,audio/*,video/*" @change="onSelectFile" />
          <button class="media-upload-btn" :disabled="uploading" @click="triggerUpload">{{ uploading ? t('common.uploading') : t('media.uploadButton') }}</button>
        </div>

        <div class="media-bulk-bar" v-if="selectedIds.size">
          <span>{{ t('media.selectedCount', { n: selectedIds.size }) }}</span>
          <button type="button" class="media-bulk-clear-btn" @click="clearSelection">{{ t('media.clearSelection') }}</button>
          <button type="button" class="media-bulk-move-btn" @click="openMoveModal">{{ t('media.moveTo') }}</button>
          <button type="button" class="media-bulk-delete-btn" @click="confirmDelete([...selectedIds])">{{ t('media.batchDelete') }}</button>
        </div>

        <div class="media-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="media-tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <span class="media-tab-icon" v-html="tab.icon"></span>
            <span class="media-tab-label">{{ tab.label }}</span>
            <span class="media-tab-count">{{ tab.count }}</span>
          </button>
          <div class="media-view-toggle">
            <button type="button" class="media-view-btn" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'" :aria-label="t('media.gridView')" :title="t('media.gridView')">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
            </button>
            <button type="button" class="media-view-btn" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'" :aria-label="t('media.listView')" :title="t('media.listView')">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
            </button>
          </div>
        </div>

        <div class="media-tab-content">
          <!-- Images -->
          <div v-show="activeTab === 'image'" class="media-group-panel">
            <div class="media-group-head">
              <h4>{{ t('media.tabImages') }}</h4>
              <div class="media-group-toolbar">
                <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('image')">{{ isGroupFullySelected('image') ? t('media.deselectAll') : t('media.selectAll') }}</button>
              </div>
            </div>
            <!-- Grid View -->
            <div v-if="viewMode === 'grid' && grouped.image.length" class="media-grid">
              <button
                v-for="item in pagedImage"
                :key="item.id"
                type="button"
                class="media-card media-card-image"
                :class="{ selected: selectedIds.has(item.id) }"
                @click="openPreview(item)"
              >
                <input class="media-card-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
                <div class="media-card-thumb-wrap">
                  <img
                    v-if="!imageLoadErrorIds.has(item.id)"
                    class="media-card-thumb"
                    :src="fullUrl(item.url)"
                    :alt="item.original_name"
                    @error="markImageLoadError(item.id)"
                  />
                  <div v-else class="media-card-thumb-fallback">
                    <span>{{ t('media.previewFailed') }}</span>
                  </div>
                </div>
                <div class="media-card-body">
                  <p class="media-card-title">{{ item.original_name }}</p>
                  <small class="media-card-meta">{{ item.mime_type || 'IMAGE' }}</small>
                </div>
              </button>
            </div>
            <!-- List View -->
            <div v-else-if="viewMode === 'list' && grouped.image.length" class="media-list">
              <div class="media-list-header">
                <span class="media-list-col media-list-col-name">{{ t('media.fileName') }}</span>
                <span class="media-list-col media-list-col-type">{{ t('media.fileType') }}</span>
                <span class="media-list-col media-list-col-size">{{ t('media.fileSize') }}</span>
                <span class="media-list-col media-list-col-date">{{ t('time.uploadTime') }}</span>
                <span class="media-list-col media-list-col-actions"></span>
              </div>
              <button
                v-for="item in pagedImage"
                :key="item.id"
                type="button"
                class="media-list-row"
                :class="{ selected: selectedIds.has(item.id) }"
                @click="openPreview(item)"
              >
                <input class="media-list-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
                <span class="media-list-col media-list-col-name">
                  <img v-if="!imageLoadErrorIds.has(item.id)" class="media-list-thumb" :src="fullUrl(item.thumbnail_url || item.url)" :alt="item.original_name" @error="markImageLoadError(item.id)" />
                  {{ item.original_name }}
                </span>
                <span class="media-list-col media-list-col-type">{{ item.mime_type || 'IMAGE' }}</span>
                <span class="media-list-col media-list-col-size">{{ formatFileSize(item.file_size || item.size) }}</span>
                <span class="media-list-col media-list-col-date">{{ formatDate(item.uploaded_at || item.created_at) }}</span>
                <span class="media-list-col media-list-col-actions">
                  <button type="button" class="media-copy-btn" @click.stop="copyUrl(item.url, item.original_name)">{{ t('common.copyLink') }}</button>
                </span>
              </button>
            </div>
            <div class="media-pagination" v-if="imageTotalPages > 1 || grouped.image.length > pageSizeOptions[0]">
              <div class="media-page-size">
                <span>{{ t('common.perPage') }}</span>
                <select :value="pageSize" @change="onPageSizeChange(+($event.target as HTMLSelectElement).value)">
                  <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
                <span>{{ t('common.items') }}</span>
              </div>
              <div class="media-page-nav">
                <button type="button" :disabled="imageCurrentPage <= 1" @click="goToPage('image', imageCurrentPage - 1)">{{ t('common.previous') }}</button>
                <span>{{ t('articleManage.pageInfo', { current: imageCurrentPage, total: imageTotalPages }) }}</span>
                <button type="button" :disabled="imageCurrentPage >= imageTotalPages" @click="goToPage('image', imageCurrentPage + 1)">{{ t('common.next') }}</button>
              </div>
            </div>
            <p v-else class="tips media-empty">{{ t('media.noImages') }}</p>
          </div>

          <!-- Audio -->
          <div v-show="activeTab === 'audio'" class="media-group-panel">
            <div class="media-group-head">
              <h4>{{ t('media.tabAudio') }}</h4>
              <div class="media-group-toolbar">
                <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('audio')">{{ isGroupFullySelected('audio') ? t('media.deselectAll') : t('media.selectAll') }}</button>
              </div>
            </div>
            <div v-if="grouped.audio.length" class="media-grid">
              <article v-for="item in pagedAudio" :key="item.id" class="media-card media-card-file" :class="{ selected: selectedIds.has(item.id) }">
                <input class="media-card-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
                <div class="media-card-body">
                  <p class="media-card-title">{{ item.original_name }}</p>
                  <small class="media-card-meta">{{ item.mime_type || 'AUDIO' }}</small>
                  <div class="media-card-link-row">
                    <span class="media-card-link-text">{{ fullUrl(item.url) }}</span>
                    <button type="button" class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">{{ t('common.copyLink') }}</button>
                  </div>
                </div>
              </article>
            </div>
            <div class="media-pagination" v-if="audioTotalPages > 1 || grouped.audio.length > pageSizeOptions[0]">
              <div class="media-page-size">
                <span>{{ t('common.perPage') }}</span>
                <select :value="pageSize" @change="onPageSizeChange(+($event.target as HTMLSelectElement).value)">
                  <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
                <span>{{ t('common.items') }}</span>
              </div>
              <div class="media-page-nav">
                <button type="button" :disabled="audioCurrentPage <= 1" @click="goToPage('audio', audioCurrentPage - 1)">{{ t('common.previous') }}</button>
                <span>{{ t('articleManage.pageInfo', { current: audioCurrentPage, total: audioTotalPages }) }}</span>
                <button type="button" :disabled="audioCurrentPage >= audioTotalPages" @click="goToPage('audio', audioCurrentPage + 1)">{{ t('common.next') }}</button>
              </div>
            </div>
            <p v-else class="tips media-empty">{{ t('media.noAudio') }}</p>
          </div>

          <!-- Video -->
          <div v-show="activeTab === 'video'" class="media-group-panel">
            <div class="media-group-head">
              <h4>{{ t('media.tabVideo') }}</h4>
              <div class="media-group-toolbar">
                <button type="button" class="media-select-all-btn" @click="toggleGroupSelection('video')">{{ isGroupFullySelected('video') ? t('media.deselectAll') : t('media.selectAll') }}</button>
              </div>
            </div>
            <div v-if="grouped.video.length" class="media-grid">
              <article v-for="item in pagedVideo" :key="item.id" class="media-card media-card-file" :class="{ selected: selectedIds.has(item.id) }">
                <input class="media-card-checkbox" type="checkbox" :checked="selectedIds.has(item.id)" @click.stop="toggleSelected(item.id)" />
                <div class="media-card-body">
                  <p class="media-card-title">{{ item.original_name }}</p>
                  <small class="media-card-meta">{{ item.mime_type || 'VIDEO' }}</small>
                  <div class="media-card-link-row">
                    <span class="media-card-link-text">{{ fullUrl(item.url) }}</span>
                    <button type="button" class="media-copy-btn" @click="copyUrl(item.url, item.original_name)">{{ t('common.copyLink') }}</button>
                  </div>
                </div>
              </article>
            </div>
            <div class="media-pagination" v-if="videoTotalPages > 1 || grouped.video.length > pageSizeOptions[0]">
              <div class="media-page-size">
                <span>{{ t('common.perPage') }}</span>
                <select :value="pageSize" @change="onPageSizeChange(+($event.target as HTMLSelectElement).value)">
                  <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
                <span>{{ t('common.items') }}</span>
              </div>
              <div class="media-page-nav">
                <button type="button" :disabled="videoCurrentPage <= 1" @click="goToPage('video', videoCurrentPage - 1)">{{ t('common.previous') }}</button>
                <span>{{ t('articleManage.pageInfo', { current: videoCurrentPage, total: videoTotalPages }) }}</span>
                <button type="button" :disabled="videoCurrentPage >= videoTotalPages" @click="goToPage('video', videoCurrentPage + 1)">{{ t('common.next') }}</button>
              </div>
            </div>
            <p v-else class="tips media-empty">{{ t('media.noVideo') }}</p>
          </div>
        </div>
      </div>
    </div>

    <teleport to="body">
      <transition name="media-delete-fade">
        <div v-if="deleteConfirmOpen" class="media-delete-overlay" @click.self="closeDeleteConfirm">
          <div class="media-delete-modal" role="dialog" aria-modal="true" aria-labelledby="media-delete-title">
            <div class="media-delete-head">
              <span class="media-delete-icon">!</span>
              <div>
                <h4 id="media-delete-title">{{ t('media.deleteTitle') }}</h4>
                <p class="media-delete-subtitle">{{ t('media.deleteSubtitle') }}</p>
              </div>
            </div>
            <div class="media-delete-body">
              <p class="media-delete-text">{{ t('media.deleteConfirm', { n: deleteTargetIds.length }) }}</p>
              <div class="media-delete-preview-list">
                <span v-for="item in deleteTargetNames" :key="item" class="media-delete-preview-item">{{ item }}</span>
              </div>
            </div>
            <div class="media-delete-actions">
              <button type="button" class="media-delete-cancel" @click="closeDeleteConfirm">{{ t('common.cancel') }}</button>
              <button type="button" class="media-delete-confirm" @click="submitDeleteConfirm">{{ t('common.delete') }}</button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

    <teleport to="body">
      <transition name="media-preview-fade">
        <div v-if="previewItem" class="media-preview-overlay" @click.self="closePreview">
          <div class="media-preview-modal" role="dialog" aria-modal="true" aria-labelledby="media-preview-title">
            <div class="media-preview-image-wrap">
              <img v-if="!imagePreviewError" class="media-preview-image" :src="fullUrl(previewItem.url)" :alt="previewItem.original_name" @error="markPreviewLoadError" />
              <div v-else class="media-preview-image-fallback">
                <span>{{ t('media.imageLoadFailed') }}</span>
              </div>
            </div>
            <div class="media-preview-info">
              <div class="media-preview-head">
                <h4 id="media-preview-title">{{ t('media.detailTitle') }}</h4>
                <button type="button" class="media-preview-close" @click="closePreview">{{ t('common.close') }}</button>
              </div>
              <div class="media-preview-meta-list">
                <div class="media-preview-meta-item"><span>{{ t('time.uploadTime') }}</span><strong>{{ formatDate(previewItem.uploaded_at || previewItem.created_at) }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.uploader') }}</span><strong>{{ previewItem.uploader?.nickname || previewItem.user?.nickname || previewItem.author?.nickname || 'admin' }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.fileName') }}</span><strong>{{ previewItem.original_name }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.fileType') }}</span><strong>{{ previewItem.mime_type || t('common.unknown') }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.fileSize') }}</span><strong>{{ formatFileSize(previewItem.file_size || previewItem.size) }}</strong></div>
                <div class="media-preview-meta-item"><span>{{ t('media.resolution') }}</span><strong>{{ formatResolution(previewItem.width, previewItem.height) }}</strong></div>
                <div class="media-preview-meta-item media-preview-url"><span>{{ t('media.fileUrl') }}</span><strong>{{ fullUrl(previewItem.url) }}</strong></div>
              </div>
              <div class="media-preview-actions">
                <button type="button" class="media-copy-btn" @click="copyUrl(previewItem.url, previewItem.original_name)">{{ t('common.copyLink') }}</button>
                <button type="button" class="danger-btn media-preview-delete" @click="$emit('delete-media', previewItem.id)">{{ t('common.delete') }}</button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

    <!-- 文件夹创建/重命名弹窗 -->
    <Teleport to="body">
      <Transition name="media-delete-fade">
        <div v-if="folderModalOpen" class="media-delete-overlay" @click.self="folderModalOpen = false">
          <div class="media-delete-modal media-folder-modal" role="dialog" aria-modal="true">
            <div class="media-delete-head">
              <div>
                <h4>{{ folderModalMode === 'rename' ? t('media.renameFolder') : t('media.newFolder') }}</h4>
              </div>
            </div>
            <div class="media-delete-body">
              <input
                v-model="folderModalName"
                class="media-folder-name-input"
                type="text"
                :placeholder="t('media.folderNamePlaceholder')"
                @keyup.enter="submitFolderModal"
                @keyup.esc="folderModalOpen = false"
              />
            </div>
            <div class="media-delete-actions">
              <button type="button" class="media-delete-cancel" @click="folderModalOpen = false">{{ t('common.cancel') }}</button>
              <button type="button" class="media-delete-confirm media-folder-confirm-btn" :disabled="!folderModalName.trim()" @click="submitFolderModal">{{ t('common.confirm') }}</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 文件夹删除确认弹窗 -->
    <Teleport to="body">
      <Transition name="media-delete-fade">
        <div v-if="deleteFolderConfirmOpen" class="media-delete-overlay" @click.self="deleteFolderConfirmOpen = false">
          <div class="media-delete-modal" role="dialog" aria-modal="true">
            <div class="media-delete-head">
              <span class="media-delete-icon">!</span>
              <div>
                <h4>{{ t('media.deleteFolderTitle') }}</h4>
                <p class="media-delete-subtitle">{{ t('media.deleteFolderSubtitle') }}</p>
              </div>
            </div>
            <div class="media-delete-body">
              <p class="media-delete-text">{{ t('media.deleteFolderConfirm', { name: deleteFolderTargetName }) }}</p>
            </div>
            <div class="media-delete-actions">
              <button type="button" class="media-delete-cancel" @click="deleteFolderConfirmOpen = false">{{ t('common.cancel') }}</button>
              <button type="button" class="media-delete-confirm" @click="submitDeleteFolder">{{ t('common.delete') }}</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 移动到文件夹弹窗 -->
    <Teleport to="body">
      <Transition name="media-delete-fade">
        <div v-if="moveModalOpen" class="media-delete-overlay" @click.self="moveModalOpen = false">
          <div class="media-delete-modal media-move-modal" role="dialog" aria-modal="true">
            <div class="media-delete-head">
              <div>
                <h4>{{ t('media.moveToFolder') }}</h4>
              </div>
            </div>
            <div class="media-delete-body media-move-folder-list">
              <button
                type="button"
                class="media-move-folder-item"
                :class="{ active: moveTargetFolderId === null }"
                @click="moveTargetFolderId = null"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                {{ t('media.unorganized') }}
              </button>
              <template v-for="folder in folders" :key="folder.id">
                <MediaMoveFolderItem
                  :folder="folder"
                  :active-id="moveTargetFolderId"
                  :depth="0"
                  @select="moveTargetFolderId = $event"
                />
              </template>
            </div>
            <div class="media-delete-actions">
              <button type="button" class="media-delete-cancel" @click="moveModalOpen = false">{{ t('common.cancel') }}</button>
              <button type="button" class="media-folder-confirm-btn" @click="submitMove">{{ t('common.confirm') }}</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref, watch, type VNode } from 'vue'
import { useI18n } from 'vue-i18n'
import { toAbsoluteAssetUrl } from '../api'

const { t, locale } = useI18n()

interface FolderNode {
  id: number
  name: string
  parent_id: number | null
  sort_order: number
  children: FolderNode[]
}

const props = defineProps<{
  media: any[]
  uploading: boolean
  folders: FolderNode[]
  toastMessage?: string
  toastStatus?: 'success' | 'error' | ''
}>()

const emit = defineEmits<{
  upload: [file: File, folderId: number | null | undefined]
  'delete-media': [mediaId: number]
  'delete-media-batch': [mediaIds: number[]]
  'select-folder': [folderId: number | null | undefined]
  'create-folder': [name: string, parentId: number | null]
  'rename-folder': [id: number, name: string]
  'delete-folder': [id: number]
  'move-media': [mediaIds: number[], targetFolderId: number | null]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const copyMessage = ref('')
const previewItem = ref<any | null>(null)
const imageLoadErrorIds = ref<Set<number>>(new Set())
const imagePreviewError = ref(false)
const selectedIds = ref<Set<number>>(new Set())
const deleteConfirmOpen = ref(false)
const deleteTargetIds = ref<number[]>([])
const deleteTargetNames = ref<string[]>([])
const activeTab = ref('image')
const viewMode = ref<'grid' | 'list'>('grid')

// 分页状态
const pageSizeOptions = [20, 40, 80]
const pageSize = ref(20)
const imageCurrentPage = ref(1)
const audioCurrentPage = ref(1)
const videoCurrentPage = ref(1)

// 文件夹侧边栏状态
const activeFolderId = ref<number | null | undefined>(undefined)
const expandedFolderIds = ref<Set<number>>(new Set())
// 文件夹 CRUD 弹窗状态
const folderModalOpen = ref(false)
const folderModalMode = ref<'create-root' | 'create-child' | 'rename'>('create-root')
const folderModalParentId = ref<number | null>(null)
const folderModalTargetId = ref<number | null>(null)
const folderModalName = ref('')
// 文件夹删除确认弹窗状态
const deleteFolderConfirmOpen = ref(false)
const deleteFolderTargetId = ref<number | null>(null)
const deleteFolderTargetName = ref('')
// 移动到文件夹弹窗状态
const moveModalOpen = ref(false)
const moveTargetFolderId = ref<number | null | undefined>(undefined)

const tabIcons = {
  image: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
  audio: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  video: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>',
}

const grouped = computed(() => {
  const image = props.media.filter((item) => {
    const mediaType = String(item.media_type || '').toUpperCase()
    const mime = String(item.mime_type || '').toLowerCase()
    return mediaType === 'IMAGE' || mime === 'image/svg+xml'
  })
  const audio = props.media.filter((item) => String(item.media_type || '').toUpperCase() === 'AUDIO')
  const video = props.media.filter((item) => String(item.media_type || '').toUpperCase() === 'VIDEO')
  return { image, audio, video }
})

watch(
  () => props.media,
  () => {
    imageCurrentPage.value = 1
    audioCurrentPage.value = 1
    videoCurrentPage.value = 1
  }
)

const pagedImage = computed(() => {
  const start = (imageCurrentPage.value - 1) * pageSize.value
  return grouped.value.image.slice(start, start + pageSize.value)
})
const pagedAudio = computed(() => {
  const start = (audioCurrentPage.value - 1) * pageSize.value
  return grouped.value.audio.slice(start, start + pageSize.value)
})
const pagedVideo = computed(() => {
  const start = (videoCurrentPage.value - 1) * pageSize.value
  return grouped.value.video.slice(start, start + pageSize.value)
})

const imageTotalPages = computed(() => Math.max(1, Math.ceil(grouped.value.image.length / pageSize.value)))
const audioTotalPages = computed(() => Math.max(1, Math.ceil(grouped.value.audio.length / pageSize.value)))
const videoTotalPages = computed(() => Math.max(1, Math.ceil(grouped.value.video.length / pageSize.value)))

const goToPage = (tab: 'image' | 'audio' | 'video', page: number) => {
  const total = tab === 'image' ? imageTotalPages.value
              : tab === 'audio' ? audioTotalPages.value
              : videoTotalPages.value
  const clamped = Math.min(Math.max(1, page), total)
  if (tab === 'image') imageCurrentPage.value = clamped
  else if (tab === 'audio') audioCurrentPage.value = clamped
  else videoCurrentPage.value = clamped
}

const onPageSizeChange = (newSize: number) => {
  pageSize.value = newSize
  imageCurrentPage.value = 1
  audioCurrentPage.value = 1
  videoCurrentPage.value = 1
}

const tabs = computed(() => [
  { key: 'image', label: t('media.tabImages'), icon: tabIcons.image, count: grouped.value.image.length },
  { key: 'audio', label: t('media.tabAudio'), icon: tabIcons.audio, count: grouped.value.audio.length },
  { key: 'video', label: t('media.tabVideo'), icon: tabIcons.video, count: grouped.value.video.length },
])

const triggerUpload = () => {
  fileInputRef.value?.click()
}

const onSelectFile = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  emit('upload', file, activeFolderId.value)
  target.value = ''
}

const fullUrl = (url: string) => toAbsoluteAssetUrl(url)

const copyUrl = async (url: string, fileName: string) => {
  await navigator.clipboard.writeText(fullUrl(url))
  copyMessage.value = t('media.copySuccess', { name: fileName })
  setTimeout(() => {
    copyMessage.value = ''
  }, 1800)
}

const openPreview = (item: any) => {
  previewItem.value = item
  imagePreviewError.value = false
}

const markImageLoadError = (id: number) => {
  const next = new Set(imageLoadErrorIds.value)
  next.add(id)
  imageLoadErrorIds.value = next
}

const markPreviewLoadError = () => {
  imagePreviewError.value = true
}

const closePreview = () => {
  previewItem.value = null
}

const toggleSelected = (id: number) => {
  const next = new Set(selectedIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedIds.value = next
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

const toggleGroupSelection = (group: 'image' | 'audio' | 'video') => {
  const groupIds = grouped.value[group].map((item) => item.id)
  const next = new Set(selectedIds.value)
  const allSelected = groupIds.length > 0 && groupIds.every((id) => next.has(id))
  if (allSelected) {
    groupIds.forEach((id) => next.delete(id))
  } else {
    groupIds.forEach((id) => next.add(id))
  }
  selectedIds.value = next
}

const isGroupFullySelected = (group: 'image' | 'audio' | 'video') => {
  const groupIds = grouped.value[group].map((item) => item.id)
  return groupIds.length > 0 && groupIds.every((id) => selectedIds.value.has(id))
}

const confirmDelete = (ids: number[]) => {
  const items = props.media.filter((item) => ids.includes(item.id))
  deleteTargetIds.value = ids
  deleteTargetNames.value = items.map((item) => item.original_name)
  deleteConfirmOpen.value = true
}

const closeDeleteConfirm = () => {
  deleteConfirmOpen.value = false
  deleteTargetIds.value = []
  deleteTargetNames.value = []
}

const submitDeleteConfirm = () => {
  if (!deleteTargetIds.value.length) return
  const ids = [...deleteTargetIds.value]
  if (ids.length === 1) emit('delete-media', ids[0])
  else emit('delete-media-batch', ids)
  if (selectedIds.value.size) {
    const next = new Set(selectedIds.value)
    deleteTargetIds.value.forEach((id) => next.delete(id))
    selectedIds.value = next
  }
  closeDeleteConfirm()
}

const formatDate = (value?: string) => {
  const text = String(value || '').trim()
  if (!text) return t('common.unknown')
  const date = new Date(text)
  if (Number.isNaN(date.getTime())) return text
  return date.toLocaleString(locale.value)
}

const formatFileSize = (value?: number) => {
  const size = Number(value || 0)
  if (!size) return t('common.unknown')
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  return `${(size / 1024 / 1024 / 1024).toFixed(1)} GB`
}

const formatResolution = (width?: number, height?: number) => {
  const w = Number(width || 0)
  const h = Number(height || 0)
  if (!w || !h) return t('common.unknown')
  return `${w} × ${h} px`
}

// ── 文件夹侧边栏逻辑 ──

const selectFolder = (id: number | null | undefined) => {
  activeFolderId.value = id
  clearSelection()
  emit('select-folder', id)
}

const toggleFolderExpand = (id: number) => {
  const next = new Set(expandedFolderIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expandedFolderIds.value = next
}

const openCreateRootFolder = () => {
  folderModalMode.value = 'create-root'
  folderModalParentId.value = null
  folderModalTargetId.value = null
  folderModalName.value = ''
  folderModalOpen.value = true
}

const openCreateChildFolder = (parentId: number) => {
  folderModalMode.value = 'create-child'
  folderModalParentId.value = parentId
  folderModalTargetId.value = null
  folderModalName.value = ''
  folderModalOpen.value = true
}

const openRenameFolder = (id: number, currentName: string) => {
  folderModalMode.value = 'rename'
  folderModalTargetId.value = id
  folderModalParentId.value = null
  folderModalName.value = currentName
  folderModalOpen.value = true
}

const openDeleteFolder = (id: number, name: string) => {
  deleteFolderTargetId.value = id
  deleteFolderTargetName.value = name
  deleteFolderConfirmOpen.value = true
}

const submitFolderModal = () => {
  const name = folderModalName.value.trim()
  if (!name) return
  if (folderModalMode.value === 'rename' && folderModalTargetId.value !== null) {
    emit('rename-folder', folderModalTargetId.value, name)
  } else {
    emit('create-folder', name, folderModalParentId.value)
  }
  folderModalOpen.value = false
}

const submitDeleteFolder = () => {
  if (deleteFolderTargetId.value === null) return
  emit('delete-folder', deleteFolderTargetId.value)
  if (activeFolderId.value === deleteFolderTargetId.value) {
    selectFolder(undefined)
  }
  deleteFolderConfirmOpen.value = false
  deleteFolderTargetId.value = null
  deleteFolderTargetName.value = ''
}

const openMoveModal = () => {
  moveTargetFolderId.value = undefined
  moveModalOpen.value = true
}

const submitMove = () => {
  if (moveTargetFolderId.value === undefined) return
  emit('move-media', [...selectedIds.value], moveTargetFolderId.value)
  moveModalOpen.value = false
  clearSelection()
}

// ── 内联子组件：文件夹树节点 ──

interface FolderTreeItemProps {
  folder: FolderNode
  activeFolderId: number | null | undefined
  expandedIds: Set<number>
}

const MediaFolderTreeItem = defineComponent({
  name: 'MediaFolderTreeItem',
  props: ['folder', 'activeFolderId', 'expandedIds'],
  emits: ['select', 'toggle-expand', 'create-child', 'rename', 'delete'],
  setup(props: FolderTreeItemProps, { emit: emitItem }): () => VNode {
    const isExpanded = computed(() => props.expandedIds.has(props.folder.id))
    const hasChildren = computed(() => props.folder.children && props.folder.children.length > 0)
    return (): VNode => {
      const children = props.folder.children || []
      return h('div', { class: 'media-folder-tree-node' }, [
        h('div',
          {
            class: ['media-folder-item', { active: props.activeFolderId === props.folder.id }],
            onClick: () => emitItem('select', props.folder.id),
          },
          [
            hasChildren.value
              ? h('button', {
                  type: 'button',
                  class: ['media-folder-expand-btn', { expanded: isExpanded.value }],
                  onClick: (e: MouseEvent) => { e.stopPropagation(); emitItem('toggle-expand', props.folder.id) },
                }, [
                  h('svg', { viewBox: '0 0 24 24', width: '10', height: '10', fill: 'none', stroke: 'currentColor', 'stroke-width': '2.5' }, [
                    h('polyline', { points: '9 18 15 12 9 6' }),
                  ]),
                ])
              : h('span', { class: 'media-folder-expand-placeholder' }),
            h('svg', { viewBox: '0 0 24 24', width: '14', height: '14', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', class: 'media-folder-svg' }, [
              h('path', { d: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z' }),
            ]),
            h('span', { class: 'media-folder-name' }, props.folder.name),
            h('span', { class: 'media-folder-actions' }, [
              h('button', {
                type: 'button',
                class: 'media-folder-action-btn',
                title: '新建子文件夹',
                onClick: (e: MouseEvent) => { e.stopPropagation(); emitItem('create-child', props.folder.id) },
              }, [h('svg', { viewBox: '0 0 24 24', width: '11', height: '11', fill: 'none', stroke: 'currentColor', 'stroke-width': '2.5' }, [h('line', { x1: '12', y1: '5', x2: '12', y2: '19' }), h('line', { x1: '5', y1: '12', x2: '19', y2: '12' })])]),
              h('button', {
                type: 'button',
                class: 'media-folder-action-btn',
                title: '重命名',
                onClick: (e: MouseEvent) => { e.stopPropagation(); emitItem('rename', props.folder.id, props.folder.name) },
              }, [h('svg', { viewBox: '0 0 24 24', width: '11', height: '11', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' }), h('path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' })])]),
              h('button', {
                type: 'button',
                class: 'media-folder-action-btn media-folder-delete-btn',
                title: '删除',
                onClick: (e: MouseEvent) => { e.stopPropagation(); emitItem('delete', props.folder.id, props.folder.name) },
              }, [h('svg', { viewBox: '0 0 24 24', width: '11', height: '11', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '3 6 5 6 21 6' }), h('path', { d: 'M19 6l-1 14H6L5 6' }), h('path', { d: 'M10 11v6' }), h('path', { d: 'M14 11v6' }), h('path', { d: 'M9 6V4h6v2' })])]),
            ]),
          ]
        ),
        isExpanded.value && children.length
          ? h('div', { class: 'media-folder-children' },
              children.map((child: FolderNode) =>
                h(MediaFolderTreeItem, {
                  key: child.id,
                  folder: child,
                  activeFolderId: props.activeFolderId,
                  expandedIds: props.expandedIds,
                  onSelect: (id: number) => emitItem('select', id),
                  onToggleExpand: (id: number) => emitItem('toggle-expand', id),
                  onCreateChild: (id: number) => emitItem('create-child', id),
                  onRename: (id: number, name: string) => emitItem('rename', id, name),
                  onDelete: (id: number, name: string) => emitItem('delete', id, name),
                })
              )
            )
          : null,
      ])
    }
  },
})

// ── 内联子组件：移动弹窗文件夹列表项 ──

const MediaMoveFolderItem = defineComponent({
  name: 'MediaMoveFolderItem',
  props: ['folder', 'activeId', 'depth'],
  emits: ['select'],
  setup(props: { folder: FolderNode; activeId: number | null | undefined; depth: number }, { emit: emitItem }): () => VNode {
    return (): VNode => {
      const children = props.folder.children || []
      const indent = (props.depth || 0) * 14
      return h('div', {}, [
        h('button', {
          type: 'button',
          class: ['media-move-folder-item', { active: props.activeId === props.folder.id }],
          style: { paddingLeft: `${10 + indent}px` },
          onClick: () => emitItem('select', props.folder.id),
        }, [
          h('svg', { viewBox: '0 0 24 24', width: '14', height: '14', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
            h('path', { d: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z' }),
          ]),
          props.folder.name,
        ]),
        ...children.map((child: FolderNode) =>
          h(MediaMoveFolderItem, {
            key: child.id,
            folder: child,
            activeId: props.activeId,
            depth: (props.depth || 0) + 1,
            onSelect: (id: number) => emitItem('select', id),
          })
        ),
      ])
    }
  },
})
</script>

<style scoped>
.media-card-thumb-wrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-soft);
}

.media-card-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.media-card-thumb-fallback {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--text-soft);
  font-size: 12px;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(14, 165, 164, 0.08));
}

.media-preview-image,
.media-preview-image-fallback {
  max-width: 100%;
  max-height: 62vh;
  border-radius: 16px;
}

.media-preview-image {
  object-fit: contain;
}

.media-preview-image-fallback {
  width: 100%;
  min-height: 240px;
  display: grid;
  place-items: center;
  color: var(--text-soft);
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(14, 165, 164, 0.08));
}

.media-view-toggle {
  display: flex;
  gap: 2px;
  margin-left: 12px;
  padding: 2px;
  background: var(--bg-soft);
  border-radius: 8px;
  border: 1px solid var(--line);
}

.media-view-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-soft);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.media-view-btn:hover {
  color: var(--text);
  background: rgba(14, 165, 164, 0.1);
}

.media-view-btn.active {
  background: var(--accent);
  color: white;
  box-shadow: 0 2px 8px rgba(14, 165, 164, 0.3);
}

.media-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-panel);
}

.media-list-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 100px;
  gap: 12px;
  padding: 10px 16px;
  background: linear-gradient(135deg, var(--bg-soft), rgba(14, 165, 164, 0.03));
  border-bottom: 1px solid var(--line);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-soft);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.media-list-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 100px;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(14, 165, 164, 0.08);
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.media-list-row:last-child {
  border-bottom: none;
}

.media-list-row:hover {
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.04), rgba(14, 165, 164, 0.02));
}

.media-list-row.selected {
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.1), rgba(14, 165, 164, 0.05));
  border-color: rgba(14, 165, 164, 0.2);
}

.media-list-checkbox {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.media-list-col {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.media-list-col-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  padding-left: 20px;
}

.media-list-thumb {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid var(--line);
}

.media-list-col-type {
  color: var(--text-soft);
  font-size: 12px;
}

.media-list-col-size {
  color: var(--text-soft);
  font-size: 12px;
}

.media-list-col-date {
  color: var(--text-soft);
  font-size: 12px;
}

.media-list-col-actions {
  display: flex;
  justify-content: flex-end;
}

.media-copy-btn {
  padding: 4px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--bg-soft);
  color: var(--text-soft);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.media-copy-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(14, 165, 164, 0.08);
}

.media-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 4px 4px;
  gap: 12px;
  flex-wrap: wrap;
}

.media-page-size {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-soft);
}

.media-page-size select {
  padding: 3px 6px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--bg-soft);
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
}

.media-page-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-soft);
}

.media-page-nav button {
  padding: 4px 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--bg-soft);
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.media-page-nav button:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(14, 165, 164, 0.08);
}

.media-page-nav button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
