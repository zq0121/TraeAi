<template>
  <div class="page module-page">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ meta.title }}</h2>
        <p>{{ meta.desc }}</p>
      </div>
      <div class="head-actions">
        <el-button type="primary">{{ meta.primaryAction || '新建' }}</el-button>
        <el-button>导出数据</el-button>
        <el-button>刷新</el-button>
      </div>
    </div>

    <div class="grid stat-grid">
      <div v-for="item in meta.stats" :key="item.label" class="stat-card">
        <span>{{ item.label }}</span>
        <b :style="{ color: item.color || '#38bdf8' }">{{ item.value }}</b>
        <em>{{ item.sub }}</em>
      </div>
    </div>

    <div class="grid main-grid">
      <div class="panel chart-card">
        <div class="card-title">{{ meta.chartTitle || '运行趋势' }}</div>
        <div ref="chartRef" class="chart"></div>
      </div>
      <div class="panel side-card">
        <div class="card-title">{{ meta.sideTitle || '实时状态' }}</div>
        <div v-for="row in meta.sideList" :key="row.name" class="side-row">
          <div><span>{{ row.name }}</span><b :class="row.tone">{{ row.status }}</b></div>
          <el-progress :percentage="row.value" :stroke-width="8" :show-text="false" />
        </div>
      </div>
    </div>

    <div class="panel table-card">
      <div class="card-title">{{ meta.tableTitle || '明细列表' }}</div>
      <el-table :data="meta.rows" height="360">
        <el-table-column v-for="col in meta.columns" :key="col.prop" :prop="col.prop" :label="col.label" :width="col.width" />
        <el-table-column label="状态" width="120">
          <template #default="s"><el-tag :type="s.row._tone || 'success'">{{ s.row._state || '正常' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default>
            <el-button link type="primary">查看</el-button>
            <el-button link type="primary">编辑</el-button>
            <el-button link type="danger">停用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { MODULE_META } from './moduleMeta.js'

const route = useRoute()
const chartRef = ref()
const meta = ref({})

function buildMeta(key) {
  meta.value = MODULE_META[key] || MODULE_META.default
}

function renderChart() {
  if (!chartRef.value || !meta.value.chartData) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 42, right: 20, top: 30, bottom: 32 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: meta.value.chartData.x, axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(56,189,248,.12)' } } },
    series: [
      { name: meta.value.chartData.name1, type: 'line', smooth: true, data: meta.value.chartData.s1, lineStyle: { color: '#38bdf8', width: 3 }, areaStyle: { color: 'rgba(56,189,248,.15)' } },
      { name: meta.value.chartData.name2, type: 'bar', data: meta.value.chartData.s2, itemStyle: { color: '#f97316' } },
    ],
  })
}

function refresh() {
  buildMeta(route.meta.moduleKey)
  nextTick(renderChart)
}

watch(() => route.fullPath, refresh)
onMounted(refresh)
</script>

<style scoped>
.module-page { color: #e5eefb; }
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head p { color: #94a3b8; margin: 4px 0 0; }
.head-actions { display: flex; gap: 10px; }
.stat-grid { grid-template-columns: repeat(4, 1fr); margin-bottom: 16px; }
.stat-card { padding: 18px; border-radius: 14px; background: linear-gradient(135deg, rgba(15,47,84,.72), rgba(15,23,42,.7)); border: 1px solid rgba(56,189,248,.18); }
.stat-card span { color: #94a3b8; }
.stat-card b { display: block; margin: 8px 0 2px; font-size: 28px; }
.stat-card em { font-style: normal; color: #64748b; font-size: 12px; }
.main-grid { grid-template-columns: 1.4fr .9fr; margin-bottom: 16px; }
.chart-card, .side-card, .table-card { padding: 18px; }
.card-title { font-size: 16px; font-weight: 800; color: #dbeafe; margin-bottom: 14px; border-left: 4px solid #38bdf8; padding-left: 10px; }
.chart { height: 320px; }
.side-row { margin: 14px 0; }
.side-row > div { display: flex; justify-content: space-between; margin-bottom: 6px; color: #cbd5e1; }
.side-row b { color: #22c55e; }
.side-row b.warn { color: #f59e0b; }
.side-row b.bad { color: #ef4444; }
</style>
