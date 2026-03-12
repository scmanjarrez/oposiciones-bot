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

onMounted(async () => {
  try {
    meta.value = await dataStore.loadMeta()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function startYear(year) {
  try {
    loading.value = true
    const qs = await dataStore.loadYear(year.id)
    const filtered = qs.filter(q => settings.isAllowed(q.status))
    const shuffled = shuffleArray(filtered)
    quizStore.startQuiz(shuffled, 'study')
    router.push(`/study/years/${year.id}`)
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
      <h1 class="text-3xl font-bold text-white mb-2">📅 Estudiar por Año</h1>
      <p class="text-slate-400 mb-8">Repasa las preguntas de convocatorias anteriores.</p>

      <div
        v-if="loading"
        class="text-center py-16 text-slate-400"
      >Cargando…</div>
      <div
        v-else-if="error"
        class="bg-red-900/50 border border-red-700 rounded-xl p-4 text-red-300"
      >{{ error }}</div>

      <div
        v-else
        class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3"
      >
        <button
          v-for="year in [...meta.years].reverse()"
          :key="year.id"
          @click="startYear(year)"
          class="group bg-slate-800 hover:bg-amber-700 border border-slate-700 hover:border-amber-500 rounded-xl p-4 text-center transition-all duration-200"
        >
          <div class="text-xl font-bold text-amber-400 group-hover:text-white">{{ year.id }}</div>
          <div class="text-xs text-slate-500 group-hover:text-amber-200 mt-1">{{ filteredCount(year) }} pregs.</div>
        </button>
      </div>
    </div>
  </div>
</template>
