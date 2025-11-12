<template>
  <div class="dashboard">
    <!-- Navbar (shared component) -->
    <Navbar :title="title" :tabs="tabsWithoutHome" :current-view="currentView" @change-tab="changeTab"
      @toggle-menu="toggleMenu" @logout="logoutAndClose" />

    <!-- Mobile Menu (shared component) -->
    <MobileMenu :tabs="tabs" :is-open="isMenuOpen" :current-view="currentView" @select-tab="selectTab"
      @close-menu="closeMenu" @logout="logoutAndClose" @go-profile="goProfile" />

    <!-- Main Content -->
    <div class="container mt-4" v-if="currentView">
      <component :is="components[currentView]" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, defineAsyncComponent, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import Navbar from '../Navbar.vue'
import MobileMenu from '../MobileMenu.vue'

const props = defineProps({
  title: String,
  tabs: Array,
  user: Object
})

const router = useRouter()
const route = useRoute()

// components available for the router-view substitute
let components = {}

if (props.user.role === 'admin') {
  components = {
    HomeTab: defineAsyncComponent(() => import('./admin_tabs/HomeTab.vue')),
    DoctorsTab: defineAsyncComponent(() => import('./admin_tabs/DoctorsTab.vue')),
    PatientsTab: defineAsyncComponent(() => import('./admin_tabs/PatientsTab.vue')),
    AppointmentsTab: defineAsyncComponent(() => import('./admin_tabs/AppointmentsTab.vue'))
  }
} else if (props.user.role === 'doctor') {
  components = {
    HomeTab: defineAsyncComponent(() => import('./doctor_tabs/HomeTab.vue')),
    AppointmentsTab: defineAsyncComponent(() => import('./doctor_tabs/AppointmentsTab.vue')),
    PatientsTab: defineAsyncComponent(() => import('./doctor_tabs/PatientsTab.vue')),
    AvailabilityTab: defineAsyncComponent(() => import('./doctor_tabs/AvailabilityTab.vue'))
  }
} else if (props.user.role === 'patient') {
  components = {
    HomeTab: defineAsyncComponent(() => import('./patient_tabs/HomeTab.vue')),
    AppointmentsTab: defineAsyncComponent(() => import('./patient_tabs/AppointmentsTab.vue')),
    DoctorsTab: defineAsyncComponent(() => import('./patient_tabs/DoctorsTab.vue')),
    BookingTab: defineAsyncComponent(() => import('./patient_tabs/BookingTab.vue'))
  }
}

const tabsWithoutHome = computed(() => props.tabs.slice(1))

const currentView = ref(null)
const isMenuOpen = ref(false)

// --- Tab control ---
function updateTabFromQuery() {
  const tabName = route.query.tab
  const match = props.tabs.find(t => t.name === tabName)
  currentView.value = match ? match.component : 'HomeTab'
}

function changeTab(tab) {
  currentView.value = tab.component
  router.replace({ query: { tab: tab.name } })
}

// --- Menu & Navigation ---
function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

function closeMenu() {
  isMenuOpen.value = false
}

function selectTab(tab) {
  changeTab(tab)
  closeMenu()
}

function logoutAndClose() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  closeMenu()
  router.push('/login')
}

function goProfile() {
  closeMenu()
  router.push('/profile')
}

function handleResize() {
  if (window.innerWidth >= 992 && isMenuOpen.value) {
    isMenuOpen.value = false
  }
}

// --- Lifecycle ---
watch(() => route.query.tab, updateTabFromQuery)

onMounted(() => {
  updateTabFromQuery()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>