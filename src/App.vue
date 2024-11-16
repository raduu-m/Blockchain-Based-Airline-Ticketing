<template>
  <div class="max-w-2xl mx-auto p-6 space-y-8">
    <!-- Account Toggle -->
    <div class="flex justify-center gap-4 items-center p-4 bg-white rounded-lg shadow">
      <button
        @click="switchAccount('personal')"
        :class="[
          'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
          accountType === 'personal' ? 'bg-blue-500 text-white' : 'bg-gray-100'
        ]"
      >
        <i class="fas fa-user"></i>
        Personal
      </button>
      <button
        @click="switchAccount('business')"
        :class="[
          'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
          accountType === 'business' ? 'bg-blue-500 text-white' : 'bg-gray-100'
        ]"
      >
        <i class="fas fa-briefcase"></i>
        Business
      </button>
    </div>

    <!-- Document Carousel -->
    <div class="relative flex items-center justify-center gap-4">
      <button
        @click="prevDoc"
        class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
      >
        <i class="fas fa-chevron-left text-xl"></i>
      </button>

      <div class="flex-1 max-w-md">
        <div
          :class="[
            'aspect-[3/2] rounded-xl shadow-lg p-6',
            getDocumentColor(currentDocs[currentIndex].type)
          ]"
        >
          <div class="h-full flex flex-col justify-between">
            <div>
              <h3 class="text-xl font-semibold mb-2">{{ currentDocs[currentIndex].title }}</h3>
              <p class="text-gray-600 capitalize">Type: {{ currentDocs[currentIndex].type }}</p>
            </div>
            <div class="text-sm text-gray-600">
              <p v-if="currentDocs[currentIndex].expiry">
                Expires: {{ currentDocs[currentIndex].expiry }}
              </p>
              <p v-if="currentDocs[currentIndex].date">
                Date: {{ currentDocs[currentIndex].date }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <button
        @click="nextDoc"
        class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
      >
        <i class="fas fa-chevron-right text-xl"></i>
      </button>
    </div>

    <!-- Document Indicators -->
    <div class="flex justify-center gap-2">
      <div
        v-for="(_, index) in currentDocs"
        :key="index"
        :class="[
          'w-2 h-2 rounded-full transition-colors',
          index === currentIndex ? 'bg-blue-500' : 'bg-gray-300'
        ]"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Sample data structure
const sampleData = {
  personal: [
    { id: 1, type: 'passport', title: 'Personal Passport', expiry: '2025-12-31' },
    { id: 2, type: 'id', title: 'National ID', expiry: '2026-08-15' },
    { id: 3, type: 'ticket', title: 'Flight to Paris', date: '2024-12-20' }
  ],
  business: [
    { id: 4, type: 'passport', title: 'Business Passport', expiry: '2026-01-31' },
    { id: 5, type: 'id', title: 'Corporate ID', expiry: '2025-06-30' },
    { id: 6, type: 'ticket', title: 'Flight to NYC', date: '2024-11-25' }
  ]
}

// Reactive state
const accountType = ref('personal')
const currentIndex = ref(0)

// Computed property for current documents
const currentDocs = computed(() => sampleData[accountType.value])

// Methods
const switchAccount = (type) => {
  accountType.value = type
  currentIndex.value = 0
}

const nextDoc = () => {
  currentIndex.value = (currentIndex.value + 1) % currentDocs.value.length
}

const prevDoc = () => {
  currentIndex.value = (currentIndex.value - 1 + currentDocs.value.length) % currentDocs.value.length
}

const getDocumentColor = (type) => {
  switch (type) {
    case 'passport': return 'bg-blue-100'
    case 'id': return 'bg-green-100'
    case 'ticket': return 'bg-yellow-100'
    default: return 'bg-gray-100'
  }
}
</script>