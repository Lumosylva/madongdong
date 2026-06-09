import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptUrl = new URL(import.meta.url)
const scriptDir = path.dirname(fileURLToPath(scriptUrl))
const repoRoot = path.resolve(scriptDir, '..')
const configPath = path.resolve(scriptDir, 'check-hardcoded-urls.config.json')
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'))

const scanRoots = (config.scan?.include ?? []).map((root) => path.resolve(repoRoot, root))
const ignoreDirs = new Set(config.scan?.exclude ?? [])
const extensions = new Set(config.scan?.extensions ?? [])
const allowedPatterns = (config.patterns?.allow ?? []).map((value) => String(value).toLowerCase())
const riskyPatterns = (config.patterns?.deny ?? []).map((item) => ({
  name: item.name,
  pattern: new RegExp(item.pattern, 'i'),
}))
const matches = []

const normalizeSlashes = (value) => value.replace(/\\/g, '/')

const shouldScanFile = (filePath) => {
  const relativePath = path.relative(repoRoot, filePath)
  const normalized = normalizeSlashes(relativePath).toLowerCase()
  if (normalized.includes('/dist/') || normalized.includes('/node_modules/') || normalized.includes('/.git/')) return false
  return [...extensions].some((ext) => normalized.endsWith(ext.toLowerCase()))
}

const isIgnoredLine = (line) => {
  const trimmed = line.trim()
  if (!trimmed) return true
  if (trimmed.startsWith('//') || trimmed.startsWith('#')) return true
  return false
}

const shouldIgnoreMatch = (line) => {
  const normalizedLine = line.toLowerCase()
  return allowedPatterns.some((pattern) => normalizedLine.includes(pattern))
}

const walk = (dir) => {
  if (!fs.existsSync(dir)) return
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) continue
    const fullPath = path.join(dir, entry.name)
    const relativeDir = path.relative(repoRoot, fullPath)
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
      const normalizedLine = line.toLowerCase()
      if (allowedPatterns.some((pattern) => normalizedLine.includes(pattern))) return
      matches.push(`${normalizeSlashes(relativeDir)}:${index + 1}: [${hit.name}] ${line.trim()}`)
    })
  }
}

for (const root of scanRoots) walk(root)

if (matches.length) {
  console.error('Found risky hardcoded network URLs that may break HTTPS migration:')
  for (const item of matches) console.error(`- ${item}`)
  process.exit(1)
}

console.log('No disallowed hardcoded network URLs found.')
