<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '../stores/quiz.js'

const router = useRouter()
const quiz = useQuizStore()

// Redirect if no results
if (!quiz.finished) {
  router.replace('/')
}

const isExam = computed(() => quiz.mode === 'exam')
const details = computed(() => quiz.scoreDetails)
const LABELS = ['A', 'B', 'C', 'D']

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m.toString().padStart(2, '0')}m ${s.toString().padStart(2, '0')}s`
  return `${m}m ${s.toString().padStart(2, '0')}s`
}

const timeTaken = computed(() => formatTime(quiz.elapsedSeconds))

function goHome() {
  quiz.reset()
  router.push('/')
}

function retry() {
  const qs = [...quiz.questions]
  const mode = quiz.mode
  quiz.startQuiz(shuffleArray(qs), mode)
  // Route to a stable quiz URL — QuizView only checks if questions are loaded
  router.push(mode === 'exam' ? '/study/blocks/exam-active' : '/study/blocks/_retry')
}

function shuffleArray(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

const studyPercent = computed(() => {
  const t = quiz.questions.length
  return t ? Math.round((details.value.correct / t) * 100) : 0
})
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <div class="max-w-2xl mx-auto px-4 py-12">

      <!-- Exam result banner -->
      <template v-if="isExam">
        <div :class="[
          'rounded-2xl p-8 text-center mb-8',
          quiz.isPassed ? 'bg-green-900/60 border border-green-600' : 'bg-red-900/40 border border-red-700'
        ]">
          <div class="text-5xl mb-3">{{ quiz.isPassed ? '🎉' : '😓' }}</div>
          <h1 class="text-3xl font-bold mb-1">{{ quiz.isPassed ? '¡APROBADO!' : 'SUSPENDIDO' }}</h1>
          <p class="text-slate-300 text-lg">
            Puntuación neta:
            <strong :class="quiz.isPassed ? 'text-green-400' : 'text-red-400'">
              {{ details.raw.toFixed(2) }}
            </strong>
            / 130 pts (mínimo 45,5)
          </p>
          <p class="text-slate-400 text-sm mt-2">Tiempo empleado: {{ timeTaken }}</p>
        </div>

        <!-- Score breakdown -->
        <div class="grid grid-cols-3 gap-4 mb-8">
          <div class="bg-slate-800 rounded-xl p-4 text-center">
            <div class="text-3xl font-bold text-green-400">{{ details.correct }}</div>
            <div class="text-sm text-slate-400 mt-1">Correctas</div>
            <div class="text-xs text-slate-500">+{{ details.correct }} pts</div>
          </div>
          <div class="bg-slate-800 rounded-xl p-4 text-center">
            <div class="text-3xl font-bold text-red-400">{{ details.wrong }}</div>
            <div class="text-sm text-slate-400 mt-1">Incorrectas</div>
            <div class="text-xs text-slate-500">-{{ (details.wrong / 3).toFixed(2) }} pts</div>
          </div>
          <div class="bg-slate-800 rounded-xl p-4 text-center">
            <div class="text-3xl font-bold text-slate-400">{{ details.blank }}</div>
            <div class="text-sm text-slate-400 mt-1">En blanco</div>
            <div class="text-xs text-slate-500">0 pts</div>
          </div>
        </div>
      </template>

      <!-- Study result banner -->
      <template v-else>
        <div class="text-center mb-8">
          <div class="text-5xl mb-3">{{ studyPercent >= 70 ? '🌟' : studyPercent >= 50 ? '👍' : '📖' }}</div>
          <h1 class="text-3xl font-bold text-white mb-2">Resultados</h1>
          <p class="text-4xl font-bold mb-1">
            <span class="text-green-400">{{ details.correct }}</span>
            <span class="text-slate-500 text-2xl"> / {{ quiz.questions.length }}</span>
          </p>
          <p class="text-slate-400">{{ studyPercent }}% de acierto</p>
        </div>

        <div class="grid grid-cols-3 gap-4 mb-8">
          <div class="bg-slate-800 rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-green-400">{{ details.correct }}</div>
            <div class="text-xs text-slate-400 mt-1">Correctas</div>
          </div>
          <div class="bg-slate-800 rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-red-400">{{ details.wrong }}</div>
            <div class="text-xs text-slate-400 mt-1">Incorrectas</div>
          </div>
          <div class="bg-slate-800 rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-slate-400">{{ details.blank }}</div>
            <div class="text-xs text-slate-400 mt-1">Sin contestar</div>
          </div>
        </div>
      </template>

      <!-- Wrong answers review (study mode) -->
      <div v-if="!isExam && details.wrong > 0" class="mb-8">
        <h2 class="text-lg font-semibold text-white mb-4">Preguntas falladas</h2>
        <div class="space-y-4">
          <div
            v-for="q in quiz.questions.filter(q => quiz.answers[q.id] !== undefined && quiz.answers[q.id] !== null && quiz.answers[q.id] !== q.correct)"
            :key="q.id"
            class="bg-slate-800 border border-slate-700 rounded-xl p-4 text-sm">
            <p class="text-slate-200 mb-3">{{ q.title }}</p>
            <!-- What you answered -->
            <div class="flex items-start gap-2 mb-1">
              <span class="text-red-400 flex-shrink-0">✗</span>
              <span class="text-red-300/80">
                <strong>{{ LABELS[quiz.answers[q.id]] }}</strong>: {{ q.answers[quiz.answers[q.id]] }}
              </span>
            </div>
            <!-- Correct answer -->
            <div class="flex items-start gap-2">
              <span class="text-green-400 flex-shrink-0">✓</span>
              <span class="text-green-300">
                <strong>{{ LABELS[q.correct] }}</strong>: {{ q.answers[q.correct] }}
              </span>
            </div>
            <div v-if="q.reason" class="mt-2 text-slate-500 italic text-xs">{{ q.reason }}</div>
          </div>
        </div>
      </div>

      <!-- Exam wrong answers review -->
      <div v-if="isExam && details.wrong > 0" class="mb-8">
        <h2 class="text-lg font-semibold text-white mb-4">Preguntas incorrectas</h2>
        <div class="space-y-4">
          <div
            v-for="q in quiz.questions.filter(q => quiz.answers[q.id] !== undefined && quiz.answers[q.id] !== null && quiz.answers[q.id] !== q.correct)"
            :key="q.id"
            class="bg-slate-800 border border-slate-700 rounded-xl p-4 text-sm">
            <div class="flex gap-2 flex-wrap mb-2">
              <span class="text-xs bg-slate-700 text-slate-400 px-2 py-0.5 rounded">{{ q.block }}</span>
              <span class="text-xs bg-slate-700 text-slate-400 px-2 py-0.5 rounded">T{{ q.topic }}</span>
            </div>
            <p class="text-slate-200 mb-3">{{ q.title }}</p>
            <div class="flex items-start gap-2 mb-1">
              <span class="text-red-400 flex-shrink-0">✗</span>
              <span class="text-red-300/80">
                <strong>{{ LABELS[quiz.answers[q.id]] }}</strong>: {{ q.answers[quiz.answers[q.id]] }}
              </span>
            </div>
            <div class="flex items-start gap-2">
              <span class="text-green-400 flex-shrink-0">✓</span>
              <span class="text-green-300">
                <strong>{{ LABELS[q.correct] }}</strong>: {{ q.answers[q.correct] }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button @click="goHome"
          class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors">
          Inicio
        </button>
        <button @click="retry"
          class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition-colors">
          Repetir
        </button>
      </div>
    </div>
  </div>
</template>
