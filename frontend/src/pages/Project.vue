<template>
  <LayoutHeader v-if="project.doc">
    <template #left-header>
      <Breadcrumbs
        :items="[
          { label: __('Projects'), route: { name: 'Projects' } },
          { label: project.doc.project_name || project.doc.project_code || projectId },
        ]"
      />
    </template>
    <template #right-header>
      <CustomActions
        v-if="project._actions?.length"
        :actions="project._actions"
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
        :label="__('New Unit')"
        @click="showUnitModal = true"
      />
      <Button
        variant="solid"
        :label="__('Save')"
        :loading="project.save?.loading"
        @click="saveProject"
      />
    </template>
  </LayoutHeader>
  <div
    v-if="project.doc"
    class="flex flex-1 flex-col overflow-y-auto p-6"
  >
    <div class="mx-auto w-full max-w-3xl">
      <FieldLayout
        v-if="tabs.data?.length"
        :tabs="tabs.data"
        :data="project.doc"
        doctype="CRM Project"
      />
      <ErrorMessage v-if="error" class="mt-4" :message="__(error)" />
    </div>
  </div>
  <UnitModal
    v-model="showUnitModal"
    :defaults="{ project: projectId }"
    :redirect="false"
    @created="project.reload()"
  />
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import CustomActions from '@/components/CustomActions.vue'
import UnitModal from '@/components/Modals/UnitModal.vue'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { useDocument } from '@/data/document'
import { Breadcrumbs, createResource, toast } from 'frappe-ui'
import { ref } from 'vue'

const props = defineProps({
  projectId: { type: String, required: true },
})

const { isManager } = usersStore()
const error = ref(null)
const showUnitModal = ref(false)

const { document: project } = useDocument('CRM Project', props.projectId)

function saveProject() {
  error.value = null
  project.save.submit(null, {
    onSuccess: () => {
      toast.success(__('Project saved'))
    },
    onError: (err) => {
      error.value = err.messages?.[0] || __('Error saving project')
      toast.error(error.value)
    },
  })
}

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Project'],
  params: { doctype: 'CRM Project', type: 'Quick Entry' },
  auto: true,
})

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Project' }
}
</script>
