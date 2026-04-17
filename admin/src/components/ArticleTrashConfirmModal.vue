<template>
  <teleport to="body">
    <transition name="trash-confirm-fade">
      <div v-if="open" class="trash-confirm-overlay" @click.self="emit('cancel')">
        <div class="trash-confirm-card" role="dialog" aria-modal="true" aria-labelledby="trash-confirm-title">
          <div class="trash-confirm-header">
            <span class="trash-confirm-icon">!</span>
            <div>
              <h4 id="trash-confirm-title">移入垃圾箱</h4>
              <p class="trash-confirm-subtitle">确认后文章将进入垃圾箱，可随时恢复。</p>
            </div>
          </div>

          <div class="trash-confirm-body">
            <p class="trash-confirm-text">{{ message }}</p>
            <div class="trash-confirm-preview">
              <span class="trash-confirm-preview-label">文章标题</span>
              <strong>{{ title }}</strong>
            </div>
          </div>

          <div class="trash-confirm-actions">
            <button type="button" class="trash-confirm-cancel" @click="emit('cancel')">取消</button>
            <button type="button" class="trash-confirm-submit" @click="emit('confirm')">移入垃圾箱</button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import '../styles/article-trash-confirm.css'

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
