<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '../stores/data.js'
import { useQuizStore } from '../stores/quiz.js'

const router = useRouter()
const dataStore = useDataStore()
const quizStore = useQuizStore()
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

async function startBlock(block) {
  try {
    loading.value = true
    const qs = await dataStore.loadBlock(block.id)
    const shuffled = shuffleArray(qs)
    quizStore.startQuiz(shuffled, 'study')
    router.push(`/study/blocks/${block.id.toLowerCase()}`)
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

const BLOCK_ICONS = { A1: '🏛️', A2: '🏢', A3: '🇪🇺', A4: '⚖️', B1: '💻', B2: '🛠️', B3: '🌐', B4: '🔒' }
const BLOCK_SHORT = {
  A1: 'Organización del Estado',
  A2: 'Adm. General del Estado',
  A3: 'Unión Europea',
  A4: 'Régimen Jurídico',
  B1: 'Tecnologías de la Información',
  B2: 'Desarrollo de Sistemas',
  B3: 'Sistemas y Comunicaciones',
  B4: 'Seguridad y Auditoría',
}
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <div class="max-w-3xl mx-auto px-4 py-12">
      <button @click="$router.push('/')" class="flex items-center gap-2 text-slate-400 hover:text-white mb-8 transition-colors">
        ← Volver
      </button>

      <h1 class="text-3xl font-bold text-white mb-2">🗂️ Estudiar por Bloque</h1>
      <p class="text-slate-400 mb-8">Elige un bloque para practicar sus preguntas en orden aleatorio.</p>

      <div v-if="loading" class="text-center py-16 text-slate-400">Cargando…</div>
      <div v-else-if="error" class="bg-red-900/50 border border-red-700 rounded-xl p-4 text-red-300">{{ error }}</div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          v-for="block in meta.blocks"
          :key="block.id"
          @click="startBlock(block)"
          class="group bg-slate-800 hover:bg-emerald-700 border border-slate-700 hover:border-emerald-500 rounded-2xl p-5 text-left transition-all duration-200">
          <div class="flex items-start justify-between mb-3">
            <span class="text-2xl">{{ BLOCK_ICONS[block.id] ?? '📦' }}</span>
            <span class="text-xs font-bold bg-slate-700 group-hover:bg-emerald-600 text-slate-300 group-hover:text-white px-2 py-1 rounded-lg transition-colors">
              {{ block.id }}
            </span>
          </div>
          <h2 class="font-semibold text-white text-sm mb-1">{{ BLOCK_SHORT[block.id] ?? block.name }}</h2>
          <p class="text-slate-400 group-hover:text-emerald-200 text-xs">{{ block.count }} preguntas · {{ block.topics.length }} temas</p>
        </button>
      </div>
    </div>
  </div>
</template>
