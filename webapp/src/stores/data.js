import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const BASE = import.meta.env.BASE_URL

// Cache loaded data in module scope to survive store resets
const _cache = {}

async function fetchJSON(url) {
  if (_cache[url]) return _cache[url]
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`)
  const data = await res.json()
  _cache[url] = data
  return data
}

export const useDataStore = defineStore('data', () => {
  const meta = ref(null)
  const loadingMeta = ref(false)

  async function loadMeta() {
    if (meta.value) return meta.value
    loadingMeta.value = true
    try {
      meta.value = await fetchJSON(`${BASE}data/meta.json`)
      return meta.value
    } finally {
      loadingMeta.value = false
    }
  }

  async function loadBlock(blockId) {
    const slug = blockId.toLowerCase()
    return fetchJSON(`${BASE}data/blocks/${slug}.json`)
  }

  async function loadYear(year) {
    return fetchJSON(`${BASE}data/years/${year}.json`)
  }

  async function getTopicQuestions(topicId) {
    // Find which block owns this topic
    const m = await loadMeta()
    let ownerBlock = null
    for (const block of m.blocks) {
      if (block.topics.some(t => t.id === String(topicId))) {
        ownerBlock = block.id
        break
      }
    }
    if (!ownerBlock) throw new Error(`Topic ${topicId} not found in any block`)
    const questions = await loadBlock(ownerBlock)
    return questions.filter(q => String(q.topic) === String(topicId))
  }

  const blockById = computed(() => {
    if (!meta.value) return {}
    return Object.fromEntries(meta.value.blocks.map(b => [b.id, b]))
  })

  return { meta, loadingMeta, loadMeta, loadBlock, loadYear, getTopicQuestions, blockById }
})
