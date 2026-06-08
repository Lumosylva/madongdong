import fs from 'node:fs'
import path from 'node:path'

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname)
const configPath = path.join(repoRoot, 'scripts', 'check-hardcoded-urls.config.json')
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'))

const scanRoots = config.scan?.include ?? []
const ignoreDirs = new Set(config.scan?.exclude ?? [])
const extensions = new Set(config.scan?.extensions ?? [])
const allowedPatterns = (config.patterns?.allow ?? []).map((value) => new RegExp(value, 'i'))
const riskyPatterns = (config.patterns?.deny ?? []).map((item) => ({
  name: item.name,
  pattern: new RegExp(item.pattern, 'i'),
}))
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
