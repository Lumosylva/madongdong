<template>
  <footer class="footer">
    <div class="footer-inner">
      <RouterLink to="/friend-links" class="footer-friend-links-link">友情链接</RouterLink>

      <div class="footer-copy-section">
        <span v-html="icpBeian || '页脚信息待配置'"></span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
defineProps<{
  icpBeian?: string | null
}>()
</script>

<style scoped>
.footer {
  margin-top: 28px;
  padding: 24px 0 30px;
}

.footer-inner {
  display: grid;
  gap: 12px;
}

.footer-friend-links-link {
  justify-self: center;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent);
  padding: 8px 2px;
  position: relative;
}

.footer-friend-links-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 2px;
  width: 100%;
  height: 1px;
  background: color-mix(in srgb, var(--accent) 55%, transparent);
  transform: scaleX(0.7);
  transform-origin: center;
  transition: transform 0.18s ease, opacity 0.18s ease;
  opacity: 0.8;
}

.footer-friend-links-link:hover::after {
  transform: scaleX(1);
  opacity: 1;
}

.footer-copy-section {
  text-align: center;
  color: var(--text-soft);
  font-size: 13px;
}

@media (max-width: 640px) {
  .footer {
    padding: 18px 0 24px;
  }
}
</style>
