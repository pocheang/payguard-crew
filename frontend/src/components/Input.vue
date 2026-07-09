<template>
  <div class="relative">
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :class="inputClasses"
      @input="handleInput"
      @blur="$emit('blur', $event)"
      @focus="$emit('focus', $event)"
    />

    <!-- Prefix icon -->
    <div v-if="prefixIcon" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
      {{ prefixIcon }}
    </div>

    <!-- Suffix icon -->
    <div v-if="suffixIcon" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
      {{ suffixIcon }}
    </div>

    <!-- Error message -->
    <p v-if="error" class="mt-1 text-sm text-danger-600 animate-slide-down">
      {{ error }}
    </p>

    <!-- Helper text -->
    <p v-else-if="helperText" class="mt-1 text-sm text-gray-500">
      {{ helperText }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: String,
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text'
  },
  placeholder: String,
  disabled: Boolean,
  readonly: Boolean,
  error: String,
  helperText: String,
  prefixIcon: String,
  suffixIcon: String,
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputClasses = computed(() => {
  const baseClasses = 'w-full border rounded-lg outline-none transition-all duration-200 placeholder:text-gray-400'

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-3 text-lg'
  }

  const stateClasses = props.error
    ? 'border-danger-500 focus:ring-2 focus:ring-danger-500 focus:border-transparent'
    : 'border-gray-300 hover:border-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent'

  const disabledClasses = props.disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'

  const iconPadding = props.prefixIcon ? 'pl-10' : props.suffixIcon ? 'pr-10' : ''

  return [
    baseClasses,
    sizeClasses[props.size],
    stateClasses,
    disabledClasses,
    iconPadding
  ].join(' ')
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}
</script>
