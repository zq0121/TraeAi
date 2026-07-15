<template>
  <div class="page analysis-page">
    <div class="page-head">
      <div>
        <h2 class="page-title">缺陷统计分析</h2>
        <p>围绕缺陷类别、检测趋势、质量波动和产线稳定性进行综合分析。</p>
      </div>
      <el-radio-group v-model="range" size="large" @change="load">
        <el-radio-button :label="7">近7天</el-radio-button>
        <el-radio-button :label="30">近30天</el-radio-button>
        <el-radio-button :label="90">近90天</el-radio-button>
      </el-radio-group>
    </div>

    <div class="grid stat-grid">
      <div class="stat-card"><span>缺陷类别</span><b>{{ categoryCount }}</b></div>
      <div class="stat-card"><span>累计缺陷</span><b>{{ totalDefects }}</b></div>
      <div class="stat-card"><span>平均日检测</span><b>{{ avgDetection }}</b></div>
      <div class="stat-card"><span>质量稳定性</span><b>96.4%</b></div>
    </div>

    <div class="grid charts">
      <div class="panel chart-card"><div ref="barRef" class="chart"></div></div>
      <div class="panel chart-card"><div ref="lineRef" class="chart"></div></div>
    </div>

    <div class="grid bottom-grid">
      <div class="panel list-panel">
        <h3>高发缺陷排行</h3>
        <div v-for="item in sortedCategories" :key="item.category_name" class="rank-item">
          <span>{{ item.category_name }}</span>
          <el-progress :percentage="rankPercent(item.count)" :stroke-width="8" />
          <b>{{ item.count }}</b>
        </div>
      </div>
      <div class="panel advice-panel">
        <h3>质量分析建议</h3>
        <p>当前缺陷以划痕和裂纹为主，建议重点检查冷轧线辊面状态、带钢张力波动与表面清洁度。</p>
        <p>若连续批次出现氧化皮，应同步复核酸洗工艺参数和表面残留处理流程。</p>
        <p>建议将高置信度缺陷记录纳入人工复检闭环，形成可追溯质量档案。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getCategoryStats, getTrend } from '../api/detection.js'

const barRef = ref()
const lineRef = ref()
const range = ref(30)
const categories = ref([])
const trend = ref([])

const categoryCount = computed(() => categories.value.length)
const totalDefects = computed(() => categories.value.reduce((sum, item) => sum + item.count, 0))
const avgDetection = computed(() => {
  if (!trend.value.length) return 0
  return Math.round(trend.value.reduce((sum, item) => sum + item.detection_count, 0) / trend.value.length)
})
const sortedCategories = computed(() => [...categories.value].sort((a, b) => b.count - a.count))

function rankPercent(count) {
  const max = Math.max(...categories.value.map(item => item.count), 1)
  return Math.round((count / max) * 100)
}

async function load() {
  categories.value = await getCategoryStats()
  trend.value = await getTrend(range.value)
  await nextTick()
  render()
}

function render() {
  echarts.init(barRef.value).setOption({
    title: { text: '缺陷类别数量', textStyle: { color: '#e5eefb', fontSize: 16 } },
    tooltip: {},
    grid: { left: 42, right: 20, bottom: 36, top: 52 },
    xAxis: { type: 'category', data: categories.value.map(i => i.category_name), axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(56,189,248,.12)' } } },
    series: [{ type: 'bar', data: categories.value.map(i => i.count), itemStyle: { color: '#38bdf8', borderRadius: [6, 6, 0, 0] } }],
  })
  echarts.init(lineRef.value).setOption({
    title: { text: `${range.value}天检测趋势`, textStyle: { color: '#e5eefb', fontSize: 16 } },
    tooltip: { trigger: 'axis' },
    grid: { left: 42, right: 20, bottom: 36, top: 52 },
    xAxis: { type: 'category', data: trend.value.map(i => i.date), axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(56,189,248,.12)' } } },
    series: [
      { name: '检测量', type: 'line', smooth: true, data: trend.value.map(i => i.detection_count), lineStyle: { color: '#38bdf8', width: 3 }, areaStyle: { color: 'rgba(56,189,248,.15)' } },
      { name: '缺陷数', type: 'line', smooth: true, data: trend.value.map(i => i.defect_count), lineStyle: { color: '#f97316', width: 3 } },
    ],
  })
}

onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head p { color: #94a3b8; margin: 4px 0 0; }
.stat-grid { grid-template-columns: repeat(4, 1fr); margin-bottom: 16px; }
.stat-card { padding: 18px; border-radius: 14px; background: linear-gradient(135deg, rgba(15,47,84,.72), rgba(15,23,42,.7)); border: 1px solid rgba(56,189,248,.18); }
.stat-card span { color: #94a3b8; }
.stat-card b { display: block; margin-top: 8px; color: #38bdf8; font-size: 28px; }
.charts { grid-template-columns: 1fr 1fr; }
.chart-card { padding: 18px; }
.chart { height: 420px; }
.bottom-grid { grid-template-columns: 1fr 1fr; margin-top: 16px; }
.list-panel, .advice-panel { padding: 20px; }
h3 { margin: 0 0 14px; color: #e0f2fe; }
.rank-item { display: grid; grid-template-columns: 100px 1fr 60px; gap: 12px; align-items: center; margin: 14px 0; color: #cbd5e1; }
.rank-item b { color: #38bdf8; text-align: right; }
.advice-panel p { color: #cbd5e1; line-height: 1.9; margin: 10px 0; padding-left: 12px; border-left: 3px solid rgba(56,189,248,.45); }
</style>
