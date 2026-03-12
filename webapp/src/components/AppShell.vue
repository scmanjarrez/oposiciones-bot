<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSettingsStore } from '../stores/settings.js'

const router = useRouter()
const route = useRoute()
const settings = useSettingsStore()

const drawerOpen = ref(false)

const isHome = computed(() => route.path === '/')

const NAV_LINKS = [
  { path: '/', label: 'Inicio', icon: '🏠' },
  { path: '/exam', label: 'Examen Real', icon: '📝' },
  { path: '/study/blocks', label: 'Por Bloque', icon: '🗂️' },
  { path: '/study/topics', label: 'Por Tema', icon: '📚' },
  { path: '/study/years', label: 'Por Año', icon: '📅' },
]

const STATUS_CONFIG = [
  { id: 'VIGENTE', label: 'Vigente', color: 'text-green-400', dot: 'bg-green-500' },
  { id: 'DESFASADA', label: 'Desfasada', color: 'text-amber-400', dot: 'bg-amber-500' },
  { id: 'DEROGADA', label: 'Derogada', color: 'text-red-400', dot: 'bg-red-500' },
  { id: 'ERRÓNEA', label: 'Errónea', color: 'text-purple-400', dot: 'bg-purple-500' },
]

function navigate(path) {
  router.push(path)
  drawerOpen.value = false
}
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 flex flex-col">

    <!-- Sticky header -->
    <header
      class="sticky top-0 z-20 bg-slate-900/95 backdrop-blur border-b border-slate-800 flex items-center gap-2 px-4 h-14 flex-shrink-0"
    >
      <!-- Back button -->
      <button
        v-if="!isHome"
        @click="router.back()"
        class="w-9 h-9 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors flex-shrink-0 text-lg"
      >
        ←
      </button>
      <div
        v-else
        class="w-9 flex-shrink-0"
      ></div>

      <!-- Title -->
      <button
        @click="navigate('/')"
        class="flex-1 text-center font-semibold text-white hover:text-indigo-300 transition-colors truncate text-sm sm:text-base"
      >
        Oposiciones TIC
      </button>

      <!-- Hamburger -->
      <button
        @click="drawerOpen = true"
        class="w-9 h-9 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors flex-shrink-0 text-xl leading-none"
      >
        ☰
      </button>
    </header>

    <!-- Page content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="drawerOpen"
        @click="drawerOpen = false"
        class="fixed inset-0 bg-black/60 z-30"
      >
      </div>
    </Transition>

    <!-- Drawer panel -->
    <Transition name="slide">
      <div
        v-if="drawerOpen"
        class="fixed top-0 right-0 h-full w-72 bg-slate-800 border-l border-slate-700 z-40 flex flex-col overflow-y-auto"
      >

        <!-- Drawer header -->
        <div class="flex items-center justify-between px-4 h-14 border-b border-slate-700 flex-shrink-0">
          <span class="font-semibold text-white">Menú</span>
          <button
            @click="drawerOpen = false"
            class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
          >
            ✕
          </button>
        </div>

        <!-- Navigation links -->
        <div class="px-3 py-4 border-b border-slate-700">
          <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 mb-2">Modos</div>
          <nav class="space-y-1">
            <button
              v-for="link in NAV_LINKS"
              :key="link.path"
              @click="navigate(link.path)"
              :class="[
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors text-left',
                route.path === link.path
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              ]"
            >
              <span>{{ link.icon }}</span>
              <span>{{ link.label }}</span>
            </button>
          </nav>
        </div>

        <!-- Settings: status filter -->
        <div class="px-3 py-4 flex-1">
          <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 mb-1">Filtro de preguntas</div>
          <p class="text-xs text-slate-500 px-2 mb-3">Tipos de preguntas a incluir en los modos de estudio y examen.</p>
          <div class="space-y-1">
            <label
              v-for="s in STATUS_CONFIG"
              :key="s.id"
              class="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-slate-700 cursor-pointer transition-colors select-none"
            >
              <input
                type="checkbox"
                :checked="settings.isAllowed(s.id)"
                @change="settings.toggleStatus(s.id)"
                class="w-4 h-4 rounded accent-indigo-500 flex-shrink-0 cursor-pointer"
              />
              <span
                class="w-2 h-2 rounded-full flex-shrink-0"
                :class="s.dot"
              ></span>
              <span :class="['text-sm font-medium', s.color]">{{ s.label }}</span>
            </label>
          </div>
          <p class="text-xs text-slate-600 px-2 mt-3">Debe haber al menos un tipo seleccionado.</p>

          <div class="border-t border-slate-700 pt-4 mt-4">
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 mb-2">Modo de examen</div>
            <label
              class="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-slate-700 cursor-pointer transition-colors select-none"
            >
              <input
                type="checkbox"
                :checked="settings.blindMode"
                @change="settings.toggleBlind()"
                class="w-4 h-4 rounded accent-indigo-500 flex-shrink-0 cursor-pointer"
              />
              <span class="text-sm font-medium text-slate-300">Examen ciego</span>
            </label>
            <p class="text-xs text-slate-500 px-2 mt-1">Oculta si la respuesta es correcta o incorrecta sobre la marcha.
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
