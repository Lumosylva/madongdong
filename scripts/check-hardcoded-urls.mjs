import fs from 'node:fs'
import path from 'node:path'

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname)
const scanRoots = ['app', 'web/src', 'admin/src']
const allowedPatterns = [
  /http:\/\/127\.0\.0\.1:8000/i,
  /http:\/\/localhost:5173/i,
  /http:\/\/localhost:5174/i,
  /http:\/\/127\.0\.0\.1:5173/i,
  /http:\/\/127\.0\.0\.1:5174/i,
]
const riskyPatterns = [
  { name: 'http://', pattern: /http:\/\//i },
  { name: 'ws://', pattern: /ws:\/\//i },
  { name: 'localhost:', pattern: /localhost:\d+/i },
  { name: '127.0.0.1:', pattern: /127\.0\.0\.1:\d+/i },
  { name: 'absolute domain', pattern: /(?:https?:\/\/)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?(?:\/[^\s"'`)]*)?/i },
]
const extensions = new Set(['.ts', '.tsx', '.js', '.jsx', '.vue', '.py', '.json', '.md', '.yml', '.yaml', '.env', '.example', '.ini', '.conf', '.txt'])
const ignoreDirs = new Set(['node_modules', 'dist', '.git', '.venv', '__pycache__'])
const matches = []

const shouldScanFile = (filePath) => {
  const lower = filePath.toLowerCase()
  if (lower.includes(`${path.sep}dist${path.sep}`) || lower.includes(`${path.sep}node_modules${path.sep}`) || lower.includes(`${path.sep}.git${path.sep}`)) return false
  return [...extensions].some((ext) => lower.endsWith(ext))
}

const isIgnoredLine = (line) => {
  const trimmed = line.trim()
  if (!trimmed) return true
  if (trimmed.startsWith('//') || trimmed.startsWith('#')) return true
  if (/^import\s+.*from\s+['"].*['"]$/.test(trimmed)) return false
  return false
}

const shouldIgnoreMatch = (line) => allowedPatterns.some((pattern) => pattern.test(line))

const walk = (dir) => {
  if (!fs.existsSync(dir)) return
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) continue
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walk(fullPath)
      continue
    }
    if (!shouldScanFile(fullPath)) continue
    const content = fs.readFileSync(fullPath, 'utf8')
    const lines = content.split(/\r?\n/)
    lines.forEach((line, index) => {
      if (isIgnoredLine(line)) return
      if (shouldIgnoreMatch(line)) return
      const hit = riskyPatterns.find((item) => item.pattern.test(line))
      if (!hit) return
      matches.push(`${path.relative(repoRoot, fullPath)}:${index + 1}: [${hit.name}] ${line.trim()}`)
    })
  }
}

for (const root of scanRoots) walk(path.join(repoRoot, root))

if (matches.length) {
  console.error('Found risky hardcoded network URLs that may break HTTPS migration:')
  for (const item of matches) console.error(`- ${item}`)
  process.exit(1)
}

console.log('No disallowed hardcoded network URLs found.')
