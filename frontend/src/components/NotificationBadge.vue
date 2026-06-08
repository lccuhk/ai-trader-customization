<template>
  <div class="notification-badge" v-if="count > 0">
    <span class="badge-content">{{ displayCount }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  count: number
  max?: number
}>(), {
  max: 99
})

const displayCount = computed(() => {
  if (props.count > props.max) {
    return `${props.max}+`
  }
  return props.count.toString()
})
</script>

<style scoped>
.notification-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: var(--danger-color);
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: 9px;
  line-height: 1;
}

.badge-content {
  display: inline-block;
  min-width: 8px;
  text-align: center;
}
</style>
