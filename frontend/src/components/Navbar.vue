<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
    <div class="container-fluid">
      <!-- Brand -->
      <a
        class="navbar-brand fw-bold fs-4 d-flex align-items-center me-4"
        href="#"
        @click.prevent="$emit('change-tab', { component: 'HomeTab', name: 'home' })"
      >
        <i class="bi bi-speedometer2 me-2"></i> {{ title }} Dashboard
      </a>

      <!-- Hamburger (mobile only) -->
      <button
        class="d-lg-none btn text-white fw-semibold position-relative mx-1"
        type="button"
        aria-label="Toggle navigation"
        @click="$emit('toggle-menu')"
      >
        <i class="bi bi-list hambueger h3 "></i>
      </button>

      <!-- Desktop Menu -->
      <div class="collapse navbar-collapse d-none d-lg-flex justify-content-between">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 d-flex align-items-center">
          <li v-for="tab in tabs.filter(t => !t.hidden)" :key="tab.name" class="nav-item mx-2">
            <button
              class="btn nav-link-custom text-white fw-semibold position-relative px-1 mx-1"
              :class="{ active: currentView === tab.component }"
              @click="$emit('change-tab', tab)"
            >
              <i :class="tab.icon + ' me-1'"></i> {{ tab.label }}
            </button>
          </li>
        </ul>

        <div class="d-flex align-items-center ms-auto">
          <button class="btn btn-danger fw-semibold px-3 me-3" @click="$emit('logout')">
            <i class="bi bi-box-arrow-right me-1"></i> Logout
          </button>
          <button class="btn btn-link text-white" title="Profile" @click="$router.push('/profile')">
            <i class="bi bi-person-circle h3"></i>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  title: String,
  tabs: Array,
  currentView: String
})
</script>

<style scoped>
.nav-link-custom {
  background: transparent;
  border: none;
  outline: none;
  padding: 8px 0;
  font-size: 0.95rem;
  position: relative;
  transition: color 0.2s ease-in-out;
}
.nav-link-custom:hover {
  color: #f8f9fa;
}
.nav-link-custom::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 2px;
  background-color: white;
  transition: width 0.25s ease-in-out;
}
.nav-link-custom:hover::after {
  width: 100%;
}
.nav-link-custom.active::after {
  width: 100%;
  background-color: #ffc107;
}
</style>
