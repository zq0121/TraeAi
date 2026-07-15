<template>
  <div class="page video-page">
    <h2 class="page-title">视频缺陷检测</h2>
    <div class="panel header-card">
      <div>
        <b>生产线视频智能检测</b>
        <p>支持产线视频上传、逐帧抽检、缺陷汇总、检测记录生成与质量复核。</p>
      </div>
      <el-button type="primary" :disabled="!file" :loading="loading" @click="start">开始视频检测</el-button>
    </div>

    <div class="grid video-grid">
      <div class="panel video-box">
        <div class="box-title">视频源</div>
        <el-upload drag :auto-upload="false" :show-file-list="false" :on-change="onFile" accept="video/*">
          <el-icon size="48"><VideoCamera /></el-icon>
          <div>上传钢材产线检测视频</div>
          <small>支持 mp4 / avi / mov 等格式</small>
        </el-upload>
        <video v-if="preview" :src="preview" controls class="video"></video>
        <div v-else class="video-placeholder">
          <div class="scan-line"></div>
          <span>等待接入产线视频</span>
        </div>
      </div>

      <div class="panel result-box">
        <div class="box-title">检测流程</div>
        <el-steps :active="activeStep" finish-status="success" align-center>
          <el-step title="上传视频" />
          <el-step title="抽帧检测" />
          <el-step title="结果汇总" />
          <el-step title="记录归档" />
        </el-steps>
        <el-progress :percentage="progress" :stroke-width="14" class="progress" />
        <div v-if="result" class="summary-cards">
          <div><b>{{ result.defect_count }}</b><span>缺陷总数</span></div>
          <div><b>{{ result.duration_ms }}ms</b><span>检测耗时</span></div>
          <div><b>{{ qualityLevel }}</b><span>质量判定</span></div>
        </div>
        <div ref="barRef" class="chart"></div>
      </div>
    </div>

    <div class="panel detail-panel">
      <div class="box-title">视频缺陷明细</div>
      <el-table :data="defects" height="260">
        <el-table-column prop="frame_index" label="帧序号" width="100" />
        <el-table-column prop="category_name" label="缺陷类别" />
        <el-table-column label="置信度" width="110">
          <template #default="s">{{ Math.round((s.row.confidence || 0) * 100) }}%</template>
        </el-table-column>
        <el-table-column prop="bbox" label="位置坐标" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import * as echarts from 'echarts'
import { VideoCamera } from '@element-plus/icons-vue'
import { detectVideo } from '../../api/detection.js'

const file = ref(null)
const preview = ref('')
const result = ref(null)
const loading = ref(false)
const progress = ref(0)
const activeStep = ref(0)
const barRef = ref()

const defects = computed(() => result.value?.defects || [])
const qualityLevel = computed(() => (result.value?.defect_count || 0) > 5 ? '建议复检' : '正常放行')

function onFile(uploadFile) {
  file.value = uploadFile.raw
  preview.value = URL.createObjectURL(uploadFile.raw)
  result.value = null
  progress.value = 0
  activeStep.value = 1
}

async function start() {
  if (!file.value) return
  loading.value = true
  progress.value = 18
  activeStep.value = 1
  const timer = setInterval(() => {
    if (progress.value < 88) progress.value += 8
    if (progress.value > 35) activeStep.value = 2
    if (progress.value > 68) activeStep.value = 3
  }, 260)
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    result.value = await detectVideo(fd)
    progress.value = 100
    activeStep.value = 4
    await nextTick()
    renderChart()
  } finally {
    clearInterval(timer)
    loading.value = false
  }
}

function renderChart() {
  if (!barRef.value) return
  const data = [
    { name: '裂纹', value: 2 },
    { name: '划痕', value: 3 },
    { name: '夹杂', value: 1 },
    { name: '氧化皮', value: 2 },
  ]
  echarts.init(barRef.value).setOption({
    grid: { left: 40, right: 16, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: data.map(i => i.name), axisLabel: { color: '#cbd5e1' } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(56,189,248,.12)' } } },
    series: [{ type: 'bar', data: data.map(i => i.value), itemStyle: { color: '#38bdf8' } }],
  })
}
</script>

<style scoped>
.header-card { display: flex; align-items: center; justify-content: space-between; padding: 18px 22px; margin-bottom: 16px; }
.header-card b { font-size: 18px; }
.header-card p { color: #94a3b8; margin: 6px 0 0; }
.video-grid { grid-template-columns: 1.1fr .9fr; }
.video-box, .result-box, .detail-panel { padding: 20px; }
.box-title { font-size: 18px; font-weight: 800; margin-bottom: 16px; color: #dbeafe; }
.video { width: 100%; max-height: 460px; margin-top: 18px; border-radius: 14px; background: #000; border: 1px solid rgba(56,189,248,.25); }
.video-placeholder { height: 360px; margin-top: 18px; border-radius: 14px; border: 1px solid rgba(56,189,248,.25); background: linear-gradient(135deg, rgba(15,23,42,.92), rgba(30,64,175,.28)); display: flex; align-items: center; justify-content: center; color: #94a3b8; position: relative; overflow: hidden; }
.scan-line { position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #38bdf8; box-shadow: 0 0 22px #38bdf8; animation: scan 2.4s infinite linear; }
@keyframes scan { from { transform: translateY(0); } to { transform: translateY(360px); } }
.progress { margin: 26px 0; }
.summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 14px; }
.summary-cards div { padding: 14px; border-radius: 12px; background: rgba(15,23,42,.72); border: 1px solid rgba(56,189,248,.18); text-align: center; }
.summary-cards b { display: block; color: #38bdf8; font-size: 24px; }
.summary-cards span { color: #94a3b8; font-size: 12px; }
.chart { height: 260px; }
.detail-panel { margin-top: 16px; }
</style>
