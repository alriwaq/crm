<template>
  <LayoutHeader v-if="unit.doc">
    <template #left-header>
      <Breadcrumbs
        :items="[
          { label: __('Units'), route: { name: 'Units' } },
          { label: unit.doc.title || unit.doc.name || unitId },
        ]"
      />
    </template>
    <template #right-header>
      <CustomActions
        v-if="unit._actions?.length"
        :actions="unit._actions"
      />
      <Button
        v-if="isManager() && !isMobileView"
        variant="ghost"
        class="w-7"
        :tooltip="__('Edit Fields Layout')"
        :icon="EditIcon"
        @click="openQuickEntryModal"
      />
      <Button
        variant="solid"
        :label="__('Save')"
        :loading="unit.save?.loading"
        @click="saveUnit"
      />
    </template>
  </LayoutHeader>
  <div
    v-if="unit.doc"
    class="flex flex-1 flex-col overflow-y-auto p-6"
  >
    <div class="mx-auto w-full max-w-3xl">
      <FieldLayout
        v-if="tabs.data?.length"
        :tabs="tabs.data"
        :data="unit.doc"
        doctype="Units"
      />
      <ErrorMessage v-if="error" class="mt-4" :message="__(error)" />
    </div>
  </div>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import CustomActions from '@/components/CustomActions.vue'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { useDocument } from '@/data/document'
import { Breadcrumbs, createResource, toast } from 'frappe-ui'
import { ref } from 'vue'

const props = defineProps({
  unitId: { type: String, required: true },
})

const { isManager } = usersStore()
const error = ref(null)

const { document: unit } = useDocument('Units', props.unitId)

function saveUnit() {
  error.value = null
  unit.save.submit(null, {
    onSuccess: () => {
      toast.success(__('Unit saved'))
    },
    onError: (err) => {
      error.value = err.messages?.[0] || __('Error saving unit')
      toast.error(error.value)
    },
  })
}

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'Units'],
  params: { doctype: 'Units', type: 'Quick Entry' },
  auto: true,
})

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'Units' }
}
</script>