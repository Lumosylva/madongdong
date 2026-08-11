import { ref } from 'vue'
import { webApi } from '../api'

type FooterNavItem = {
  id: number
  title: string
  path: string
  target: string | null
  is_visible: boolean
  sort_order: number
}

const cache = ref<FooterNavItem[] | null>(null)
let inflight: Promise<void> | null = null

export function useFooterNav() {
  const items = ref<FooterNavItem[]>(cache.value ?? [])

  if (cache.value == null && inflight == null) {
    inflight = webApi
      .getFooterNav()
      .then((list) => {
        cache.value = list
        items.value = list
      })
      .catch(() => {
        cache.value = []
        items.value = []
      })
      .finally(() => {
        inflight = null
      })
  } else if (inflight) {
    void inflight.then(() => {
      items.value = cache.value ?? []
    })
  }

  return items
}
