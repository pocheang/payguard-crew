<template>
  <span :class="badgeClasses">
    <span v-if="dot" class="w-1.5 h-1.5 rounded-full bg-current mr-1.5"></span>
    <span v-if="icon" class="mr-1">{{ icon }}</span>
    <slot></slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info', 'primary'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  dot: {
    type: Boolean,
    default: false
  },
  icon: {
    type: String,
    default: null
  },
  outline: {
    type: Boolean,
    default: false
  }
})

const badgeClasses = computed(() => {
  const baseClasses = 'inline-flex items-center font-semibold rounded-full transition-colors'

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-2xs',
    md: 'px-3 py-1 text-xs',
    lg: 'px-4 py-1.5 text-sm'
  }

  const variantClasses = props.outline ? {
    default: 'bg-transparent border border-gray-300 text-gray-700',
    success: 'bg-transparent border border-success-500 text-success-700',
    warning: 'bg-transparent border border-warning-500 text-warning-700',
    danger: 'bg-transparent border border-danger-500 text-danger-700',
    info: 'bg-transparent border border-blue-500 text-blue-700',
    primary: 'bg-transparent border border-primary-500 text-primary-700'
  } : {
    default: 'bg-gray-100 text-gray-700',
    success: 'bg-success-100 text-success-700',
    warning: 'bg-warning-100 text-warning-700',
    danger: 'bg-danger-100 text-danger-700',
    info: 'bg-blue-100 text-blue-700',
    primary: 'bg-primary-100 text-primary-700'
  }

  return [
    baseClasses,
    sizeClasses[props.size],
    variantClasses[props.variant]
  ].join(' ')
})
</script>
