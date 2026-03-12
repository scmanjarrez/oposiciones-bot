<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <div class="max-w-3xl mx-auto px-4 py-12">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-white mb-2">Oposiciones TIC</h1>
        <p class="text-slate-400 text-lg">Cuerpo Superior de Sistemas y Tecnologías de la Información</p>
      </div>

      <!-- Mode cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Examen real -->
        <button @click="$router.push('/exam')"
          class="group bg-slate-800 hover:bg-indigo-600 border border-slate-700 hover:border-indigo-500 rounded-2xl p-6 text-left transition-all duration-200">
          <div class="text-3xl mb-3">📝</div>
          <h2 class="text-xl font-semibold text-white mb-1">Examen Real</h2>
          <p class="text-slate-400 group-hover:text-indigo-200 text-sm">
            130 preguntas · 2 horas · Puntuación oficial
          </p>
          <div class="mt-4 text-xs text-slate-500 group-hover:text-indigo-300">
            30 temas generales + 100 temas específicos
          </div>
        </button>

        <!-- Por bloque -->
        <button @click="$router.push('/study/blocks')"
          class="group bg-slate-800 hover:bg-emerald-600 border border-slate-700 hover:border-emerald-500 rounded-2xl p-6 text-left transition-all duration-200">
          <div class="text-3xl mb-3">🗂️</div>
          <h2 class="text-xl font-semibold text-white mb-1">Por Bloque</h2>
          <p class="text-slate-400 group-hover:text-emerald-200 text-sm">
            Estudia preguntas de un bloque concreto
          </p>
          <div class="mt-4 text-xs text-slate-500 group-hover:text-emerald-300">
            A1 · A2 · A3 · A4 · B1 · B2 · B3 · B4
          </div>
        </button>

        <!-- Por tema -->
        <button @click="$router.push('/study/topics')"
          class="group bg-slate-800 hover:bg-sky-600 border border-slate-700 hover:border-sky-500 rounded-2xl p-6 text-left transition-all duration-200">
          <div class="text-3xl mb-3">📚</div>
          <h2 class="text-xl font-semibold text-white mb-1">Por Tema</h2>
          <p class="text-slate-400 group-hover:text-sky-200 text-sm">
            Estudia las preguntas de un tema específico
          </p>
          <div class="mt-4 text-xs text-slate-500 group-hover:text-sky-300">
            133 temas disponibles
          </div>
        </button>

        <!-- Por año -->
        <button @click="$router.push('/study/years')"
          class="group bg-slate-800 hover:bg-amber-600 border border-slate-700 hover:border-amber-500 rounded-2xl p-6 text-left transition-all duration-200">
          <div class="text-3xl mb-3">📅</div>
          <h2 class="text-xl font-semibold text-white mb-1">Por Año</h2>
          <p class="text-slate-400 group-hover:text-amber-200 text-sm">
            Repasa los exámenes de convocatorias anteriores
          </p>
          <div class="mt-4 text-xs text-slate-500 group-hover:text-amber-300">
            2001 – 2024
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
