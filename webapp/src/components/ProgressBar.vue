<script setup>
defineProps({
  current: { type: Number, required: true },
  total:   { type: Number, required: true },
  percent: { type: Number, required: true },
})
</script>

<template>
  <div class="bg-slate-800 px-4 py-2 flex items-center gap-3">
    <span class="text-xs text-slate-400 flex-shrink-0">{{ current }} / {{ total }}</span>
    <div class="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
      <div
        :style="{ width: percent + '%' }"
        class="h-full bg-indigo-500 rounded-full transition-all duration-300">
      </div>
    </div>
    <span class="text-xs text-slate-500 flex-shrink-0">{{ percent }}%</span>
  </div>
</template>
