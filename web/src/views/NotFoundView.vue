<template>
  <div class="not-found-page">
    <div class="not-found-card">
      <div class="not-found-code">404</div>
      <h1>{{ t('notFound.title') }}</h1>
      <p>{{ t('notFound.description') }}</p>
      <RouterLink to="/" class="not-found-btn">{{ t('common.backToHome') }}</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

onMounted(() => {
  document.title = '404 - MaDongDong'
})
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 20px;
}

.not-found-card {
  text-align: center;
  display: grid;
  gap: 12px;
  justify-items: center;
}

.not-found-code {
  font-size: clamp(80px, 15vw, 120px);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  color: var(--accent);
  opacity: 0.25;
}

.not-found-card h1 {
  margin: 0;
  font-size: clamp(22px, 4vw, 28px);
}

.not-found-card p {
  margin: 0;
  color: var(--text-soft);
  font-size: 15px;
  max-width: 40ch;
}

.not-found-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 24px;
  margin-top: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent), #38bdf8);
  color: #02131f;
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.not-found-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(14, 165, 164, 0.25);
}
</style>
