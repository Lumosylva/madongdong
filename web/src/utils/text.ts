export const truncateText = (value: string | null | undefined, maxLength: number) => {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}
