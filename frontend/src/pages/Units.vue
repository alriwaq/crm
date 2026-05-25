<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Units" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="unitsListView?.customListActions"
        :actions="unitsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="showUnitModal = true"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="units"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Units"
  />
  <UnitsListView
    v-if="units.data && rows.length"
    ref="unitsListView"
    v-model="units.data.page_length_count"
    v-model:list="units"
    :rows="rows"
    :columns="columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: units.data.row_count,
      totalCount: units.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <EmptyState
    v-else-if="units.data && !rows.length"
    name="Units"
    :icon="UnitsIcon"
  />
  <UnitModal
    v-if="showUnitModal"
    v-model="showUnitModal"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import UnitsIcon from '@/components/Icons/UnitsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import UnitModal from '@/components/Modals/UnitModal.vue'
import UnitsListView from '@/components/ListViews/UnitsListView.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import ViewControls from '@/components/ViewControls.vue'
import { formatDate, timeAgo } from '@/utils'
import { ref, computed } from 'vue'

const unitsListView = ref(null)
const showUnitModal = ref(false)

const units = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (!units.value?.data?.data) return []
  const viewType = units.value.data.view_type
  if (viewType && !['list', 'group_by'].includes(viewType)) return []
  return units.value.data.data.map((unit) => {
    let _rows = { name: unit.name }
    units.value.data.rows.forEach((row) => {
      _rows[row] = unit[row]

      if (row === 'title') {
        _rows[row] = {
          label: unit[row],
        }
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(unit[row]),
          timeAgo: __(timeAgo(unit[row])),
        }
      }
    })
    return _rows
  })
})

const columns = computed(() => {
  let _columns = units.value?.data?.columns || []

  if (_columns.length) {
    _columns = _columns.map((col, index) => {
      if (index === _columns.length - 1) {
        return { ...col, align: 'right' }
      }
      return col
    })
  }

  return _columns
})
</script>