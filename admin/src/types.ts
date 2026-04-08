export type LoginResponse = {
  success: boolean
  data: {
    access_token: string
    token_type: string
  }
}

export type AdminUser = {
  id: number
  username: string
  nickname: string
  email: string
  avatar: string | null
  is_active: boolean
  roles: Array<{
    id: number
    name: string
    description: string | null
  }>
}

export type ArticlePayload = {
  title: string
  summary: string
  content_markdown: string
  cover_url: string | null
  category_id: number
  tag_ids: number[]
  action: 'draft' | 'submit' | 'publish'
}
