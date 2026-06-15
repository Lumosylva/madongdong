<template>
  <teleport to="body">
    <transition name="trash-confirm-fade">
      <div v-if="open" class="trash-confirm-overlay" @click.self="emit('cancel')">
        <div class="trash-confirm-card" role="dialog" aria-modal="true" aria-labelledby="trash-confirm-title">
          <div class="trash-confirm-header">
            <span class="trash-confirm-icon">!</span>
            <div>
              <h4 id="trash-confirm-title">{{ t('articleTrashConfirm.title') }}</h4>
              <p class="trash-confirm-subtitle">{{ t('articleTrashConfirm.subtitle') }}</p>
            </div>
          </div>

          <div class="trash-confirm-body">
            <p class="trash-confirm-text">{{ message }}</p>
            <div class="trash-confirm-preview">
              <span class="trash-confirm-preview-label">{{ t('articleTrashConfirm.titleLabel') }}</span>
              <strong>{{ title }}</strong>
            </div>
          </div>

          <div class="trash-confirm-actions">
            <button type="button" class="trash-confirm-cancel" @click="emit('cancel')">{{ t('common.cancel') }}</button>
            <button type="button" class="trash-confirm-submit" @click="emit('confirm')">{{ t('articleTrashConfirm.confirm') }}</button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import '../styles/article-trash-confirm.css'

const { t } = useI18n()

defineProps<{
  open: boolean
  title: string
  message?: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>
