<template>
  <div :class="cardClasses" @click="handleClick">
    <!-- Header -->
    <div v-if="$slots.header || title" class="mb-4 pb-4 border-b border-gray-200">
      <slot name="header">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-bold text-gray-800">{{ title }}</h3>
          <slot name="actions"></slot>
        </div>
      </slot>
    </div>

    <!-- Body -->
    <div class="flex-1">
      <slot></slot>
    </div>

    <!-- Footer -->
    <div v-if="$slots.footer" class="mt-4 pt-4 border-t border-gray-200">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: null
  },
  interactive: {
    type: Boolean,
    default: false
  },
  hover: {
    type: Boolean,
    default: false
  },
  padding: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'none'].includes(value)
  }
})

const emit = defineEmits(['click'])

const cardClasses = computed(() => {
  const baseClasses = 'bg-white rounded-xl shadow-soft border border-gray-200 transition-all duration-200'

  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    none: ''
  }

  const interactiveClasses = props.interactive || props.hover
    ? 'cursor-pointer hover:border-primary-300 hover:shadow-medium'
    : ''

  return [
    baseClasses,
    paddingClasses[props.padding],
    interactiveClasses
  ].join(' ')
})

const handleClick = (event) => {
  if (props.interactive) {
    emit('click', event)
  }
}
</script>
