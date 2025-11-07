<template>
  <div>
    <!-- Mobile Menu Drawer -->
    <div class="mobile-menu d-lg-none" :class="{ show: isOpen }">
      <ul class="navbar-nav px-3 mt-4">
        <li class="nav-item my-2">
          <button class="btn w-100 text-start text-white fw-semibold mobile-link" @click="$emit('go-profile')">
            <i class="bi bi-person-circle me-2"></i> Profile
          </button>
        </li>

        <li v-for="tab in tabs" :key="tab.name" class="nav-item my-2">
          <button
            class="btn w-100 text-start text-white fw-semibold mobile-link"
            :class="{ active: currentView === tab.component }"
            @click="$emit('select-tab', tab)"
          >
            <i :class="tab.icon + ' me-2'"></i>{{ tab.label }}
          </button>
        </li>

        <hr class="bg-light my-2" />

        <li class="nav-item my-2">
          <button class="btn btn-danger w-100 fw-semibold" @click="$emit('logout')">
            <i class="bi bi-box-arrow-right me-1"></i> Logout
          </button>
        </li>
      </ul>
    </div>

    <!-- Backdrop -->
    <div v-if="isOpen" class="menu-backdrop" @click="$emit('close-menu')"></div>
  </div>
</template>

<script setup>
defineProps({
  tabs: Array,
  isOpen: Boolean,
  currentView: String
})
</script>

<style scoped>
.mobile-menu {
  position: fixed;
  top: 0;
  right: -260px;
  width: 260px;
  height: 100vh;
  background-color: #0d6efd;
  box-shadow: -3px 0 8px rgba(0, 0, 0, 0.3);
  transition: right 0.3s ease;
  z-index: 1050;
  overflow-y: auto;
  padding-bottom: 2rem;
}
.mobile-menu.show {
  right: 0;
}
.menu-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
}

.mobile-link {
  border: none;
  outline: none;
  background: transparent;
  font-size: 1rem;
  padding: 12px;
  text-align: left;
  transition: background-color 0.2s ease-in-out;
}
.mobile-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.mobile-link.active {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>
