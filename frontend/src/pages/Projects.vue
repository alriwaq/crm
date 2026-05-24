<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Projects" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="projectsListView?.customListActions"
        :actions="projectsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="showProjectModal = true"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="projects"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Project"
  />
  <ProjectsListView
    v-if="projects.data && rows.length"
    ref="projectsListView"
    v-model="projects.data.page_length_count"
    v-model:list="projects"
    :rows="rows"
    :columns="columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: projects.data.row_count,
      totalCount: projects.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <EmptyState
    v-else-if="projects.data && !rows.length"
    name="Projects"
    :icon="ProjectsIcon"
  />
  <ProjectModal
    v-if="showProjectModal"
    v-model="showProjectModal"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ProjectsIcon from '@/components/Icons/ProjectsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ProjectModal from '@/components/Modals/ProjectModal.vue'
import ProjectsListView from '@/components/ListViews/ProjectsListView.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { formatDate, timeAgo } from '@/utils'
import { ref, computed } from 'vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Project')

const projectsListView = ref(null)
const showProjectModal = ref(false)

// projects data is loaded in the ViewControls component
const projects = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (!projects.value?.data?.data) return []
  const viewType = projects.value.data.view_type
  if (viewType && !['list', 'group_by'].includes(viewType)) return []
  return projects.value.data.data.map((project) => {
    let _rows = { name: project.name }
    projects.value.data.rows.forEach((row) => {
      _rows[row] = project[row]

      let fieldType = projects.value.data.columns?.find(
        (col) => (col.key || col.value) == row,
      )?.type

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(
          project[row],
          '',
          true,
          fieldType == 'Datetime',
        )
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, project)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, project)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, project)
      }

      if (['project_code', 'project_name'].includes(row)) {
        _rows[row] = {
          label: project[row],
        }
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(project[row]),
          timeAgo: __(timeAgo(project[row])),
        }
      }
    })
    return _rows
  })
})

const columns = computed(() => {
  let _columns = projects.value?.data?.columns || []

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
