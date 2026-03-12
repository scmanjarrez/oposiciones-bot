<script setup>
defineProps({
  status: { type: String, default: 'VIGENTE' },
})

const CONFIG = {
  VIGENTE:   { label: 'Vigente',   cls: 'bg-green-900/50 text-green-400 border-green-700' },
  DESFASADA: { label: 'Desfasada', cls: 'bg-amber-900/50 text-amber-400 border-amber-700' },
  DEROGADA:  { label: 'Derogada',  cls: 'bg-red-900/50 text-red-400 border-red-700' },
  ERRÓNEA:   { label: 'Errónea',   cls: 'bg-purple-900/50 text-purple-400 border-purple-700' },
}
</script>

<template>
  <span :class="['text-xs font-medium border rounded px-1.5 py-0.5', (CONFIG[status] ?? CONFIG.VIGENTE).cls]">
    {{ (CONFIG[status] ?? CONFIG.VIGENTE).label }}
  </span>
</template>
