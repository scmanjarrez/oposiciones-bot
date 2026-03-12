<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '../stores/data.js'
import { useQuizStore } from '../stores/quiz.js'
import { useSettingsStore } from '../stores/settings.js'

const router = useRouter()
const dataStore = useDataStore()
const quizStore = useQuizStore()
const settings = useSettingsStore()

function filteredCount(item) {
  if (!item.countByStatus) return item.count
  return settings.allowedStatuses.reduce((sum, s) => sum + (item.countByStatus[s] ?? 0), 0)
}
const loading = ref(true)
const error = ref(null)
const meta = ref(null)
const filterBlock = ref('ALL')

onMounted(async () => {
  try {
    meta.value = await dataStore.loadMeta()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

const allTopics = computed(() => {
  if (!meta.value) return []
  return meta.value.blocks.flatMap(block =>
    block.topics.map(t => ({ ...t, blockId: block.id }))
  )
})

const filteredTopics = computed(() =>
  filterBlock.value === 'ALL'
    ? allTopics.value
    : allTopics.value.filter(t => t.blockId === filterBlock.value)
)

async function startTopic(topic) {
  try {
    loading.value = true
    const qs = await dataStore.getTopicQuestions(topic.id)
    const filtered = qs.filter(q => settings.isAllowed(q.status))
    const shuffled = shuffleArray(filtered)
    quizStore.startQuiz(shuffled, 'study')
    router.push(`/study/topics/${topic.id}`)
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
}

function shuffleArray(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}
</script>

<template>
  <div class="bg-slate-900 text-slate-100">
    <div class="max-w-3xl mx-auto px-4 pt-6 pb-12">
      <h1 class="text-3xl font-bold text-white mb-2">📚 Estudiar por Tema</h1>
      <p class="text-slate-400 mb-6">Selecciona un tema concreto para practicar.</p>

      <div
        v-if="loading"
        class="text-center py-16 text-slate-400"
      >Cargando…</div>
      <div
        v-else-if="error"
        class="bg-red-900/50 border border-red-700 rounded-xl p-4 text-red-300"
      >{{ error }}</div>

      <template v-else>
        <!-- Block filter -->
        <div class="flex flex-wrap gap-2 mb-6">
          <button
            @click="filterBlock = 'ALL'"
            :class="['text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors',
              filterBlock === 'ALL'
                ? 'bg-sky-600 border-sky-500 text-white'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-500']"
          >
            Todos
          </button>
          <button
            v-for="block in meta.blocks"
            :key="block.id"
            @click="filterBlock = block.id"
            :class="['text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors',
              filterBlock === block.id
                ? 'bg-sky-600 border-sky-500 text-white'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-500']"
          >
            {{ block.id }}
          </button>
        </div>

        <!-- Topics grid -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <button
            v-for="topic in filteredTopics"
            :key="topic.id"
            @click="startTopic(topic)"
            class="group bg-slate-800 hover:bg-sky-700 border border-slate-700 hover:border-sky-500 rounded-xl p-3 text-left transition-all duration-200"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-lg font-bold text-sky-400 group-hover:text-white">T{{ topic.id }}</span>
              <span :class="['text-xs px-1.5 py-0.5 rounded font-medium',
                topic.isGeneral ? 'bg-indigo-900 text-indigo-300' : 'bg-slate-700 text-slate-400']">
                {{ topic.blockId }}
              </span>
            </div>
            <div class="text-xs text-slate-400 group-hover:text-sky-200">
              {{ filteredCount(topic) }} pregs.
              <span
                v-if="topic.isGeneral"
                class="text-indigo-400 ml-1"
              >· General</span>
            </div>
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
