<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '../stores/quiz.js'
import { useSettingsStore } from '../stores/settings.js'
import TimerBar from '../components/TimerBar.vue'
import ProgressBar from '../components/ProgressBar.vue'
import StatusBadge from '../components/StatusBadge.vue'

const router = useRouter()
const quiz = useQuizStore()
const settings = useSettingsStore()

// Redirect to home if no active quiz
onMounted(() => {
  if (!quiz.questions.length) {
    router.replace('/')
  }
})

// Navigate to results when quiz is finished
watch(() => quiz.finished, (done) => {
  if (done) router.push('/results')
})

const isExam = computed(() => quiz.mode === 'exam')
const q = computed(() => quiz.currentQuestion)

const LABELS = ['A', 'B', 'C', 'D']

// Tracks whether this question's answer has been revealed (non-blind pick).
// Stored separately so switching to blind mode afterwards doesn't re-unlock it.
const revealed = ref(false)

// Reset revealed state whenever the question index changes
watch(() => quiz.currentIndex, () => { revealed.value = false })

// Seal revealed if blind mode is turned OFF while an answer is already selected
watch(() => settings.blindMode, (blind) => {
  if (!blind && quiz.currentAnswer !== null) {
    revealed.value = true
  }
})

function selectAnswer(idx) {
  if (revealed.value) return

  if (settings.blindMode) {
    if (isExam.value) {
      // Blind exam: toggle freely
      quiz.answer(quiz.currentAnswer === idx ? null : idx)
    } else {
      // Blind study: change freely
      quiz.answer(idx)
    }
  } else {
    // Non-blind: first pick is final, mark as revealed
    if (quiz.currentAnswer === null) {
      quiz.answer(idx)
      revealed.value = true
    }
  }
}

function handleNext() {
  quiz.nextQuestion()
}

const studyAnswered = computed(() => quiz.mode === 'study' && quiz.currentAnswer !== null)

// isLocked: either revealed non-blind, or in non-blind mode with an answer already set
// (the second condition handles the case blind→non-blind transition with existing answer)
const isLocked = computed(() => revealed.value || (!settings.blindMode && quiz.currentAnswer !== null))

// Unified answer class: shows correct/wrong when not in blind mode and an answer is selected
function answerClass(idx) {
  const answered = quiz.currentAnswer !== null
  const isSelected = idx === quiz.currentAnswer

  if (!settings.blindMode && answered) {
    if (idx === q.value.correct) return 'bg-green-900/60 border-green-500 text-green-200'
    if (isSelected) return 'bg-red-900/60 border-red-500 text-red-200'
    return 'bg-slate-800/50 border-slate-700 text-slate-400'
  }

  if (isSelected) return 'bg-indigo-700 border-indigo-400 text-white'
  return 'bg-slate-800 border-slate-700 hover:border-slate-500 text-slate-200'
}

const progressPercent = computed(() =>
  quiz.questions.length ? Math.round((quiz.currentIndex / quiz.questions.length) * 100) : 0
)
</script>

<template>
  <div class="bg-slate-900 text-slate-100 flex flex-col">

    <!-- Timer (exam only) -->
    <TimerBar
      v-if="isExam"
      :time-left="quiz.timeLeft"
    />

    <!-- Progress bar -->
    <ProgressBar
      :current="quiz.currentIndex + 1"
      :total="quiz.questions.length"
      :percent="progressPercent"
    />

    <!-- Main content -->
    <div class="flex-1 max-w-2xl mx-auto w-full px-4 py-6">

      <!-- Question header -->
      <div
        v-if="q"
        class="mb-5"
      >
        <div class="flex flex-wrap items-center gap-2 mb-3">
          <!-- Status badge -->
          <StatusBadge :status="q.status" />
          <!-- Metadata chips -->
          <span
            v-if="q.block"
            class="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded"
          >{{ q.block }}</span>
          <span
            v-if="q.topic"
            class="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded"
          >T{{ q.topic }}</span>
          <span
            v-if="q.year"
            class="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded"
          >{{ q.year }}</span>
          <span
            v-if="q.id"
            class="text-xs bg-slate-800/60 text-slate-500 px-2 py-0.5 rounded font-mono"
          >#{{ q.id }}</span>
        </div>

        <!-- Question number -->
        <div class="text-xs text-slate-500 mb-2">
          Pregunta {{ quiz.currentIndex + 1 }} de {{ quiz.questions.length }}
        </div>

        <!-- Question text -->
        <p class="text-white text-base leading-relaxed">{{ q.title }}</p>

        <p
          v-if="q.comments"
          class="text-xs text-slate-500 mt-2 italic"
        >{{ q.comments }}</p>
      </div>

      <!-- Answer options -->
      <div
        v-if="q"
        class="space-y-3 mb-6"
      >
        <button
          v-for="(answer, idx) in q.answers"
          :key="idx"
          @click="selectAnswer(idx)"
          :disabled="isLocked"
          :class="[
            'w-full text-left border rounded-xl px-4 py-3 transition-all duration-150 text-sm flex items-start gap-3',
            answerClass(idx)
          ]"
        >
          <span class="font-bold flex-shrink-0 w-5 text-center">{{ LABELS[idx] }}</span>
          <span>{{ answer }}</span>
        </button>

        <!-- Blank option: exam only, hidden once locked in non-blind mode -->
        <button
          v-if="isExam && !isLocked"
          @click="quiz.answer(null)"
          :class="[
            'w-full text-left border rounded-xl px-4 py-3 transition-all duration-150 text-sm flex items-center gap-3',
            quiz.currentAnswer === null
              ? 'bg-slate-700 border-slate-500 text-slate-300'
              : 'bg-slate-800/50 border-slate-700/50 text-slate-500 hover:border-slate-600'
          ]"
        >
          <span class="font-bold flex-shrink-0 w-5 text-center">—</span>
          <span>Sin contestar</span>
        </button>
      </div>

      <!-- Study mode: show explanation after answering (only when not blind) -->
      <div
        v-if="studyAnswered && !settings.blindMode && q.reason"
        class="bg-slate-800 border border-amber-600/50 rounded-xl p-4 mb-6 text-sm"
      >
        <div class="text-amber-400 font-semibold mb-1">⚠️ Nota sobre esta pregunta</div>
        <p class="text-slate-300">{{ q.reason }}</p>
      </div>
      <div
        v-if="studyAnswered && !settings.blindMode && q.correct_original !== null && q.correct_original !== undefined && q.correct_original !== q.correct"
        class="bg-indigo-950 border border-indigo-700 rounded-xl p-4 mb-6 text-sm"
      >
        <div class="text-indigo-300 font-semibold mb-1">🤖 Respuesta corregida por IA</div>
        <p class="text-slate-300">La respuesta original era <strong>{{ LABELS[q.correct_original] }}</strong>.</p>
      </div>

      <!-- Navigation -->
      <div class="flex gap-3">
        <button
          v-if="!isExam && quiz.currentIndex > 0"
          @click="quiz.prevQuestion()"
          class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors"
        >
          ← Anterior
        </button>

        <button
          v-if="!isExam"
          @click="handleNext"
          :disabled="!studyAnswered"
          :class="[
            'flex-1 font-semibold py-3 rounded-xl transition-colors text-white',
            studyAnswered
              ? 'bg-emerald-600 hover:bg-emerald-500'
              : 'bg-slate-700 cursor-not-allowed text-slate-400'
          ]"
        >
          {{ quiz.isLastQuestion ? 'Ver resultados' : 'Siguiente →' }}
        </button>

        <!-- Exam: navigate freely -->
        <template v-if="isExam">
          <button
            v-if="quiz.currentIndex > 0"
            @click="quiz.prevQuestion()"
            class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-medium py-3 px-5 rounded-xl transition-colors"
          >
            ←
          </button>
          <button
            v-if="!quiz.isLastQuestion"
            @click="handleNext"
            class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Siguiente →
          </button>
          <button
            v-else
            @click="quiz.finishQuiz()"
            class="flex-1 bg-green-600 hover:bg-green-500 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Finalizar examen ✓
          </button>
        </template>
      </div>

      <!-- Exam: bottom finish button (always visible) -->
      <div
        v-if="isExam"
        class="mt-4 text-center"
      >
        <button
          @click="quiz.finishQuiz()"
          class="text-sm text-slate-500 hover:text-red-400 transition-colors underline"
        >
          Terminar examen ahora
        </button>
      </div>
    </div>
  </div>
</template>
