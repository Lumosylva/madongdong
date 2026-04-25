export type NavItem = {
  id: number
  title: string
  path: string
  sort_order: number
  is_visible: boolean
  target: string | null
  description: string | null
}

export type SiteSetting = {
  id: number
  site_title: string
  site_logo: string | null
  site_subtitle: string | null
  icp_beian: string | null
  copyright_text: string | null
  homepage_page_size: number
  comment_requires_review: boolean
}

export type Category = {
  id: number
  name: string
  slug: string
  description: string | null
}

export type Tag = {
  id: number
  name: string
  slug: string
}

export type Author = {
  id: number
  username: string
  nickname: string
  email: string
  avatar: string | null
  is_active: boolean
}

export type Article = {
  id: number
  title: string
  summary: string
  content_markdown?: string
  content_html?: string
  cover_url: string | null
  status: string
  review_comment: string | null
  published_at: string | null
  view_count: number
  comment_count: number
  created_at: string
  updated_at: string
  category: Category
  author: Author
  tags: Tag[]
}

export type Comment = {
  id: number
  article_id: number
  user_id: number | null
  guest_nickname: string | null
  guest_email: string | null
  content: string
  status: string
  parent_id: number | null
  created_at: string
  updated_at: string
  user: Author | null
}

export type Paginated<T> = {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export type HomeResponse = {
  site: SiteSetting
  nav_items: NavItem[]
  hot_articles: Article[]
  latest_articles: Paginated<Article>
}

export type ArticlePageResponse = {
  site: SiteSetting
  nav_items: NavItem[]
  article: Article
  previous_article: Article | null
  next_article: Article | null
  comments: Comment[]
}

export type SearchResponse = {
  keyword: string
  site: SiteSetting
  nav_items: NavItem[]
  categories: Category[]
  tags: Tag[]
  articles: Paginated<Article>
}

export type CategoryArticlesResponse = {
  category: Category
  site: SiteSetting
  nav_items: NavItem[]
  articles: Paginated<Article>
}

export type TagArticlesResponse = {
  tag: Tag
  site: SiteSetting
  nav_items: NavItem[]
  articles: Paginated<Article>
}
