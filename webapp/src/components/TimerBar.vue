<script setup>
import { computed } from 'vue'

const props = defineProps({
  timeLeft: { type: Number, required: true },
})

function pad(n) {
  return n.toString().padStart(2, '0')
}

const hours = computed(() => Math.floor(props.timeLeft / 3600))
const minutes = computed(() => Math.floor((props.timeLeft % 3600) / 60))
const seconds = computed(() => props.timeLeft % 60)
const display = computed(() => `${pad(hours.value)}:${pad(minutes.value)}:${pad(seconds.value)}`)

const isWarning = computed(() => props.timeLeft <= 1800 && props.timeLeft > 300)   // <30 min
const isDanger = computed(() => props.timeLeft <= 300)                              // <5 min

const barPercent = computed(() => Math.max(0, (props.timeLeft / 7200) * 100))
</script>

<template>
  <div :class="[
    'sticky top-0 z-10 px-4 py-2 flex items-center justify-between text-sm font-mono transition-colors',
    isDanger ? 'bg-red-900 text-red-200' : isWarning ? 'bg-amber-900 text-amber-200' : 'bg-slate-800 text-slate-300'
  ]">
    <span class="text-xs text-slate-400 font-sans">Tiempo restante</span>
    <span
      :class="['text-xl font-bold tabular-nums', isDanger ? 'text-red-400 animate-pulse' : isWarning ? 'text-amber-400' : 'text-white']"
    >
      {{ display }}
    </span>
    <!-- Progress bar -->
    <div class="hidden sm:block w-32 h-1.5 bg-slate-700 rounded-full overflow-hidden">
      <div
        :style="{ width: barPercent + '%' }"
        :class="['h-full rounded-full transition-all duration-1000', isDanger ? 'bg-red-500' : isWarning ? 'bg-amber-500' : 'bg-indigo-500']"
      >
      </div>
    </div>
  </div>
</template>
