<template>
  <div class="screen-page">
    <div class="screen-frame">
      <header class="screen-header">
        <div class="title-block">
          <div class="main-title">钢材表面缺陷智能识别与分析平台</div>
          <div class="sub-title">智能识别 · 质量追溯 · 产线分析 · 缺陷预警</div>
        </div>
        <nav class="nav-tabs">
          <span class="active">生产总览</span>
          <span>智能检测</span>
          <span>质量趋势</span>
          <span>系统管理</span>
        </nav>
        <div class="time-box">
          <span>{{ currentTime }}</span>
          <span class="status-dot"></span>
          <span>模型在线</span>
        </div>
      </header>

      <main class="screen-body">
        <aside class="left-panels">
          <div class="data-panel">
            <div class="panel-title">今日检测趋势</div>
            <div ref="trendRef" class="chart"></div>
          </div>
          <div class="data-panel">
            <div class="panel-title">缺陷类别占比</div>
            <div ref="pieRef" class="chart small"></div>
          </div>
          <div class="data-panel quality-panel">
            <div class="panel-title">产线质量评分</div>
            <div class="score-ring">
              <span>96.8</span>
              <em>综合评分</em>
            </div>
            <ul>
              <li><span>一号酸洗线</span><b>98.2</b></li>
              <li><span>二号冷轧线</span><b>95.7</b></li>
              <li><span>三号涂镀线</span><b>96.4</b></li>
            </ul>
          </div>
        </aside>

        <section class="center-scene">
          <section class="kpi-row">
            <div v-for="item in kpis" :key="item.label" class="kpi-card">
              <div class="kpi-value">{{ item.value }}</div>
              <div class="kpi-label">{{ item.label }}</div>
            </div>
          </section>
          <div class="scene-glow"></div>
          <div class="point p1"><span>酸洗线</span><b>运行正常</b></div>
          <div class="point p2"><span>冷轧线</span><b>发现划痕 2 处</b></div>
          <div class="point p3"><span>质检中心</span><b>AI 模型运行中</b></div>
          <div class="center-summary">
            <div><b>1286</b><span>累计检测</span></div>
            <div><b>26.6%</b><span>缺陷检出率</span></div>
            <div><b>99.2%</b><span>系统可用率</span></div>
          </div>
        </section>

        <aside class="right-panels">
          <div class="data-panel">
            <div class="panel-title">产线实时状态</div>
            <div class="line-list">
              <div v-for="line in lines" :key="line.name" class="line-item">
                <div><span>{{ line.name }}</span><b>{{ line.status }}</b></div>
                <el-progress :percentage="line.value" :stroke-width="8" :show-text="false" />
              </div>
            </div>
          </div>
          <div class="data-panel">
            <div class="panel-title">最近质量告警</div>
            <div class="alarm-list">
              <div v-for="alarm in alarms" :key="alarm.text" class="alarm-item">
                <span>{{ alarm.level }}</span>
                <div>{{ alarm.text }}</div>
                <em>{{ alarm.time }}</em>
              </div>
            </div>
          </div>
          <div class="data-panel">
            <div class="panel-title">检测记录追溯</div>
            <el-table :data="records" height="180">
              <el-table-column prop="original_file_name" label="文件" min-width="110" />
              <el-table-column prop="defect_count" label="缺陷" width="70" />
              <el-table-column prop="max_confidence" label="置信度" width="80" />
            </el-table>
          </div>
        </aside>
      </main>

      <footer class="screen-footer">
        <router-link to="/detection/image">图片检测</router-link>
        <router-link to="/detection/video">视频检测</router-link>
        <router-link to="/detection/camera">实时检测</router-link>
        <router-link to="/records">检测记录</router-link>
        <router-link to="/analysis">统计分析</router-link>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getRecords, getStatistics, getTrend } from '../api/detection.js'

const stats = ref({})
const records = ref([])
const trend = ref([])
const currentTime = ref('')
const trendRef = ref()
const pieRef = ref()
let timer = null

const lines = [
  { name: '一号酸洗线', status: '正常', value: 92 },
  { name: '二号冷轧线', status: '巡检', value: 78 },
  { name: '三号涂镀线', status: '正常', value: 88 },
  { name: '成品质检线', status: '在线', value: 96 },
]

const alarms = [
  { level: 'Ⅰ级', text: '二号冷轧线检测到连续划痕', time: '09:42' },
  { level: 'Ⅱ级', text: '酸洗线出现轻微氧化皮', time: '10:18' },
  { level: 'Ⅲ级', text: '质检中心完成模型复核', time: '11:06' },
]

const kpis = computed(() => [
  { label: '今日检测量', value: stats.value.today_detection || 0 },
  { label: '今日缺陷数', value: stats.value.today_defects || 0 },
  { label: '累计检测量', value: stats.value.total_detection || 0 },
  { label: '缺陷检出率', value: `${Math.round((stats.value.defect_rate || 0) * 100)}%` },
])

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', { hour12: false })
}

async function load() {
  stats.value = await getStatistics()
  records.value = await getRecords({ limit: 6 })
  trend.value = await getTrend(7)
  renderCharts()
}

function renderCharts() {
  const trendChart = echarts.init(trendRef.value)
  trendChart.setOption({
    grid: { left: 38, right: 12, top: 28, bottom: 30 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trend.value.map(i => i.date.slice(5)), axisLabel: { color: '#8fb8df' }, axisLine: { lineStyle: { color: '#24496f' } } },
    yAxis: { type: 'value', axisLabel: { color: '#8fb8df' }, splitLine: { lineStyle: { color: 'rgba(56,189,248,.12)' } } },
    series: [
      { name: '检测量', type: 'line', smooth: true, data: trend.value.map(i => i.detection_count), areaStyle: { color: 'rgba(56,189,248,.18)' }, lineStyle: { color: '#38bdf8', width: 3 } },
      { name: '缺陷数', type: 'bar', data: trend.value.map(i => i.defect_count), itemStyle: { color: '#f97316' } },
    ],
  })

  const pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '52%'],
      data: (stats.value.category_stats || []).map(i => ({ name: i.category_name, value: i.count, itemStyle: { color: i.color } })),
      label: { color: '#dbeafe', formatter: '{b}\n{d}%' },
    }],
  })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  load()
})

onUnmounted(() => timer && clearInterval(timer))
</script>

<style scoped>
.screen-page { min-height: calc(100vh - 64px); padding: 10px; background: #020617; overflow: hidden; }
.screen-frame { position: relative; height: calc(100vh - 84px); border: 1px solid rgba(56,189,248,.35); border-radius: 16px; background-image: radial-gradient(circle at center, rgba(2,6,23,.08), rgba(2,6,23,.58) 70%, rgba(2,6,23,.9) 100%), linear-gradient(180deg, rgba(2,6,23,.72), rgba(2,6,23,.18) 38%, rgba(2,6,23,.86) 100%), url('/assets/factory-3d.png'); background-size: cover, cover, cover; background-position: center, center, center bottom; background-repeat: no-repeat; box-shadow: inset 0 0 70px rgba(2,6,23,.8), inset 0 0 60px rgba(56,189,248,.12), 0 0 40px rgba(0,0,0,.45); overflow: hidden; }
.screen-frame::before { content: ''; position: absolute; inset: 0; background: linear-gradient(rgba(56,189,248,.04) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,.04) 1px, transparent 1px); background-size: 36px 36px; pointer-events: none; opacity:.72; }
.screen-header { position: relative; z-index: 2; height: 88px; display: grid; grid-template-columns: 1.35fr 1fr 1fr; align-items: center; padding: 0 28px; border-bottom: 1px solid rgba(56,189,248,.22); background: linear-gradient(180deg, rgba(7,18,38,.72), rgba(7,18,38,.22)); backdrop-filter: blur(3px); }
.main-title { font-size: 26px; line-height: 1.18; font-weight: 900; letter-spacing: 1px; color: #e0f2fe; text-shadow: 0 0 16px rgba(56,189,248,.55); }
.sub-title { margin-top: 7px; color: #60a5fa; font-size: 12px; letter-spacing: 4px; }
.nav-tabs { display: flex; justify-content: center; gap: 34px; color: #94a3b8; font-size: 17px; font-weight: 800; }
.nav-tabs .active { color: #e0f2fe; border-bottom: 2px solid #38bdf8; padding-bottom: 8px; text-shadow: 0 0 16px #38bdf8; }
.time-box { display: flex; justify-content: flex-end; align-items: center; gap: 10px; color: #cbd5e1; font-size: 18px; }
.status-dot { width: 9px; height: 9px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 14px #22c55e; }
.kpi-row { position: absolute; z-index: 4; top: 16px; left: 50%; transform: translateX(-50%); width: 66%; display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; pointer-events: none; }
.kpi-card { text-align: center; color: #cbd5e1; }
.kpi-value { font-size: 34px; font-weight: 900; color: #f8fafc; text-shadow: 0 0 16px rgba(56,189,248,.45); }
.kpi-label { margin-top: 4px; color: #8fb8df; font-size: 15px; }
.screen-body { position: relative; z-index: 2; height: calc(100% - 88px); display: grid; grid-template-columns: 25% 50% 25%; gap: 18px; padding: 18px 22px 72px; }
.left-panels, .right-panels { display: flex; flex-direction: column; gap: 14px; }
.data-panel { background: linear-gradient(180deg, rgba(15,47,84,.46), rgba(15,23,42,.24)); border: 1px solid rgba(56,189,248,.24); box-shadow: inset 0 0 24px rgba(56,189,248,.06), 0 0 18px rgba(2,6,23,.18); border-radius: 10px; padding: 12px; backdrop-filter: blur(3px); }
.panel-title { color: #dbeafe; font-weight: 800; border-left: 4px solid #38bdf8; padding-left: 10px; margin-bottom: 8px; text-shadow: 0 0 10px rgba(56,189,248,.6); }
.chart { height: 200px; }
.chart.small { height: 190px; }
.quality-panel { min-height: 220px; }
.score-ring { margin: 12px auto; width: 126px; height: 126px; border-radius: 50%; border: 8px solid rgba(56,189,248,.25); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 0 22px rgba(56,189,248,.28), 0 0 22px rgba(56,189,248,.18); }
.score-ring span { font-size: 28px; font-weight: 900; color: #38bdf8; }
.score-ring em { font-style: normal; font-size: 12px; color: #94a3b8; }
ul { padding: 0; margin: 0; list-style: none; }
.quality-panel li, .line-item > div { display: flex; justify-content: space-between; color: #cbd5e1; margin: 8px 0; }
.quality-panel b, .line-item b { color: #38bdf8; }
.center-scene { position: relative; height: 100%; display: flex; align-items: center; justify-content: center; overflow: visible; padding-top: 90px; border-radius: 12px; }
.scene-glow { position: absolute; width: 86%; height: 240px; bottom: 72px; border-radius: 50%; background: radial-gradient(circle, rgba(56,189,248,.18), transparent 70%); filter: blur(12px); }
.point { position: absolute; padding: 10px 14px; min-width: 128px; color: #e0f2fe; background: rgba(15,23,42,.52); border: 1px solid rgba(56,189,248,.32); border-radius: 8px; box-shadow: 0 0 20px rgba(56,189,248,.14); backdrop-filter: blur(3px); }
.point::before { content: ''; position: absolute; width: 10px; height: 10px; left: -18px; top: 50%; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 16px #f59e0b; }
.p2::before { left: auto; right: -22px; top: 58%; }
.point span { display: block; font-size: 13px; color: #93c5fd; }
.point b { font-size: 14px; }
.p1 { left: 8%; top: 58%; }
.p2 { right: 6%; top: 63%; }
.p3 { left: 43%; bottom: 13%; }
.center-summary { position: absolute; bottom: 14px; display: flex; gap: 16px; padding: 12px 24px; background: rgba(15,23,42,.46); border: 1px solid rgba(56,189,248,.26); border-radius: 12px; backdrop-filter: blur(3px); }
.center-summary div { width: 120px; text-align: center; }
.center-summary b { display: block; color: #38bdf8; font-size: 24px; }
.center-summary span { color: #94a3b8; font-size: 12px; }
.line-list { display: flex; flex-direction: column; gap: 18px; padding-top: 8px; }
.alarm-list { display: flex; flex-direction: column; gap: 10px; }
.alarm-item { display: grid; grid-template-columns: 46px 1fr 44px; gap: 8px; align-items: center; padding: 9px; border-radius: 8px; background: rgba(15,23,42,.34); color: #cbd5e1; }
.alarm-item span { color: #f97316; font-weight: 800; }
.alarm-item em { color: #94a3b8; font-style: normal; }
.screen-footer { position: absolute; z-index: 3; left: 50%; bottom: 18px; transform: translateX(-50%); display: flex; gap: 22px; padding: 10px 26px; background: rgba(15,23,42,.48); border: 1px solid rgba(56,189,248,.26); border-radius: 999px; backdrop-filter: blur(3px); }
.screen-footer a { color: #cbd5e1; padding: 5px 12px; border-radius: 999px; }
.screen-footer a:hover { color: #38bdf8; background: rgba(56,189,248,.12); }
:deep(.el-table) { font-size: 12px; }
:deep(.el-progress-bar__outer) { background: rgba(30,41,59,.85); }
:deep(.el-progress-bar__inner) { background: linear-gradient(90deg, #38bdf8, #22c55e); }
@media (max-width: 1300px) { .screen-body { grid-template-columns: 25% 50% 25%; } .main-title { font-size: 26px; } .nav-tabs { gap: 22px; font-size: 16px; } .kpi-row { width: 70%; } }
</style>
