import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// modes: 'exam' | 'study'
export const useQuizStore = defineStore('quiz', () => {
  const questions = ref([])
  const mode = ref(null)         // 'exam' | 'study'
  const currentIndex = ref(0)
  const answers = ref({})        // questionId → answerIdx (null = no contestada)
  const startTime = ref(null)
  const timeLeft = ref(0)
  const finished = ref(false)
  const timerId = ref(null)

  const endTime = ref(null)

  // --- Actions ---

  function startQuiz(qs, quizMode) {
    stopTimer()
    questions.value = qs
    mode.value = quizMode
    currentIndex.value = 0
    answers.value = {}
    finished.value = false
    startTime.value = Date.now()

    if (quizMode === 'exam') {
      timeLeft.value = 7200  // 2 hours in seconds
      timerId.value = setInterval(() => {
        timeLeft.value--
        if (timeLeft.value <= 0) {
          finishQuiz()
        }
      }, 1000)
    } else {
      timeLeft.value = 0
    }
  }

  function answer(answerIdx) {
    const q = questions.value[currentIndex.value]
    if (!q) return
    answers.value[q.id] = answerIdx
  }

  function nextQuestion() {
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
    } else {
      finishQuiz()
    }
  }

  function prevQuestion() {
    if (currentIndex.value > 0) currentIndex.value--
  }

  function finishQuiz() {
    stopTimer()
    endTime.value = Date.now()
    finished.value = true
  }

  function stopTimer() {
    if (timerId.value) {
      clearInterval(timerId.value)
      timerId.value = null
    }
  }

  function reset() {
    stopTimer()
    questions.value = []
    mode.value = null
    currentIndex.value = 0
    answers.value = {}
    startTime.value = null
    endTime.value = null
    timeLeft.value = 0
    finished.value = false
  }

  // --- Getters ---

  const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)

  const currentAnswer = computed(() => {
    const q = currentQuestion.value
    return q ? answers.value[q.id] ?? null : null
  })

  const isLastQuestion = computed(() => currentIndex.value === questions.value.length - 1)

  // Raw score: correct +1, wrong -1/3, blank 0
  const scoreDetails = computed(() => {
    let correct = 0
    let wrong = 0
    let blank = 0

    for (const q of questions.value) {
      const ans = answers.value[q.id]
      if (ans === null || ans === undefined) {
        blank++
      } else if (ans === q.correct) {
        correct++
      } else {
        wrong++
      }
    }

    const raw = correct - wrong / 3
    return { correct, wrong, blank, raw: parseFloat(raw.toFixed(3)) }
  })

  const isPassed = computed(() => {
    if (mode.value !== 'exam') return null
    return scoreDetails.value.raw >= 45.5
  })

  const elapsedSeconds = computed(() => {
    if (!startTime.value) return 0
    const end = endTime.value ?? Date.now()
    return Math.floor((end - startTime.value) / 1000)
  })

  return {
    questions, mode, currentIndex, answers, startTime, endTime,
    timeLeft, finished,
    startQuiz, answer, nextQuestion, prevQuestion, finishQuiz, reset,
    currentQuestion, currentAnswer, isLastQuestion,
    scoreDetails, isPassed, elapsedSeconds,
  }
})
