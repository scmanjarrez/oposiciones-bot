<script setup>
import { useRouter } from 'vue-router'
import { useDataStore } from '../stores/data.js'
import { useQuizStore } from '../stores/quiz.js'
import { useSettingsStore } from '../stores/settings.js'
import { onMounted, ref, computed } from 'vue'

const router = useRouter()
const dataStore = useDataStore()
const quizStore = useQuizStore()
const settings = useSettingsStore()
const loading = ref(false)
const error = ref(null)

const STATUS_LABELS = { VIGENTE: 'Vigente', DESFASADA: 'Desfasada', DEROGADA: 'Derogada', 'ERRÓNEA': 'Errónea' }
const activeLabels = computed(() => settings.allowedStatuses.map(s => STATUS_LABELS[s] ?? s).join(', '))

async function startExam() {
  loading.value = true
  error.value = null
  try {
    const meta = await dataStore.loadMeta()

    // Collect VIGENTE questions from ALL blocks
    let generals = []
    let specifics = []

    for (const block of meta.blocks) {
      const qs = await dataStore.loadBlock(block.id)
      const vigente = qs.filter(q => settings.isAllowed(q.status))
      for (const q of vigente) {
        const topicNum = parseInt(q.topic)
        if (topicNum >= 1 && topicNum <= 28) {
          generals.push(q)
        } else {
          specifics.push(q)
        }
      }
    }

    // Shuffle and pick 30 generals + 100 specifics
    generals = shuffleArray(generals).slice(0, 30)
    specifics = shuffleArray(specifics).slice(0, 100)

    // Interleave: first generals, then specifics (mirrors real exam order)
    const selected = [...generals, ...specifics]

    quizStore.startQuiz(selected, 'exam')
    router.push('/study/blocks/exam-active')
  } catch (e) {
    error.value = e.message
  } finally {
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
    <div class="max-w-2xl mx-auto px-4 pt-6 pb-12">
      <h1 class="text-3xl font-bold text-white mb-8">📝 Simulacro de Examen</h1>

      <!-- Info cards -->
      <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-slate-800 rounded-xl p-4">
          <div class="text-2xl font-bold text-indigo-400">130</div>
          <div class="text-sm text-slate-400 mt-1">Preguntas totales</div>
          <div class="text-xs text-slate-500 mt-1">30 generales + 100 específicas</div>
        </div>
        <div class="bg-slate-800 rounded-xl p-4">
          <div class="text-2xl font-bold text-indigo-400">2 h</div>
          <div class="text-sm text-slate-400 mt-1">Tiempo máximo</div>
          <div class="text-xs text-slate-500 mt-1">120 minutos</div>
        </div>
        <div class="bg-slate-800 rounded-xl p-4">
          <div class="text-2xl font-bold text-green-400">45,5 pts</div>
          <div class="text-sm text-slate-400 mt-1">Puntuación mínima</div>
          <div class="text-xs text-slate-500 mt-1">Para aprobar</div>
        </div>
        <div class="bg-slate-800 rounded-xl p-4">
          <div class="text-2xl font-bold text-amber-400">-⅓</div>
          <div class="text-sm text-slate-400 mt-1">Penalización</div>
          <div class="text-xs text-slate-500 mt-1">Por respuesta incorrecta</div>
        </div>
      </div>

      <!-- Scoring explanation -->
      <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 mb-8 space-y-2">
        <h2 class="font-semibold text-white mb-3">Sistema de puntuación</h2>
        <div class="flex items-center gap-3 text-sm">
          <span class="w-3 h-3 rounded-full bg-green-500 flex-shrink-0"></span>
          <span class="text-slate-300"><strong class="text-green-400">+1 punto</strong> por pregunta correcta</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="w-3 h-3 rounded-full bg-red-500 flex-shrink-0"></span>
          <span class="text-slate-300"><strong class="text-red-400">-⅓ puntos</strong> por respuesta incorrecta</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="w-3 h-3 rounded-full bg-slate-500 flex-shrink-0"></span>
          <span class="text-slate-300"><strong class="text-slate-400">0 puntos</strong> por pregunta en blanco</span>
        </div>
      </div>

      <!-- Important notes -->
      <div class="bg-indigo-950 border border-indigo-800 rounded-xl p-4 mb-8 text-sm text-indigo-200">
        <strong class="text-indigo-300">Nota:</strong> Se incluirán preguntas con estado
        <span class="font-medium text-indigo-300">{{ activeLabels }}</span>,
        seleccionadas aleatoriamente del banco completo. Puedes cambiar los filtros desde el menú ☰.
      </div>

      <div
        v-if="error"
        class="bg-red-900/50 border border-red-700 rounded-xl p-4 mb-6 text-red-300 text-sm"
      >
        Error al cargar las preguntas: {{ error }}
      </div>

      <button
        @click="startExam"
        :disabled="loading"
        class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl text-lg transition-colors"
      >
        {{ loading ? 'Cargando preguntas…' : '🚀 Empezar examen' }}
      </button>
    </div>
  </div>
</template>
