<template>
  <div class="page image-page">
    <h2 class="page-title">图片缺陷检测</h2>
    <div class="top-actions panel">
      <div>
        <b>钢材表面图片智能检测</b>
        <p>支持裂纹、划痕、夹杂、氧化皮、点蚀等缺陷识别，输出类别、置信度、位置与质量判定。</p>
      </div>
      <el-button type="primary" :disabled="!file" :loading="loading" @click="start">开始检测</el-button>
    </div>

    <div class="sample-strip">
      <div v-for="sample in samples" :key="sample.path" class="sample-card" @click="chooseSample(sample)">
        <img :src="sample.path" />
        <span>{{ sample.name }}</span>
      </div>
    </div>

    <div class="grid wrap">
      <div class="panel box">
        <div class="box-title">待检测图片</div>
        <el-upload drag :auto-upload="false" :show-file-list="false" :on-change="onFile" accept="image/*">
          <el-icon size="48"><UploadFilled /></el-icon>
          <div>拖拽或点击上传钢材表面图片</div>
        </el-upload>
        <div v-if="preview" class="image-stage">
          <img :src="preview" class="preview" />
        </div>
      </div>

      <div class="panel box">
        <div class="box-title">检测结果</div>
        <div v-if="preview && result" class="image-stage result-stage">
          <img :src="preview" class="preview" />
          <div
            v-for="defect in normalizedDefects"
            :key="defect.category_name + defect.confidence"
            class="defect-box"
            :style="boxStyle(defect)"
          >
            <span>{{ defect.category_name }} {{ Math.round(defect.confidence * 100) }}%</span>
          </div>
        </div>
        <el-empty v-else description="请上传图片或选择样本后开始检测" />
        <div v-if="result" class="summary-cards">
          <div><b>{{ result.defect_count }}</b><span>缺陷数量</span></div>
          <div><b>{{ result.duration_ms || 0 }}ms</b><span>检测耗时</span></div>
          <div><b>{{ qualityLevel }}</b><span>质量判定</span></div>
        </div>
        <el-table v-if="result" :data="normalizedDefects" height="220">
          <el-table-column prop="category_name" label="缺陷类别" />
          <el-table-column label="置信度" width="100">
            <template #default="s">{{ Math.round(s.row.confidence * 100) }}%</template>
          </el-table-column>
          <el-table-column prop="area" label="面积" width="90" />
          <el-table-column prop="bbox" label="坐标位置" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { detectImage } from '../../api/detection.js'

const samples = [
  { name: '裂纹', path: '/samples/crazing_1.jpg' },
  { name: '夹杂', path: '/samples/inclusion_29.jpg' },
  { name: '斑块', path: '/samples/patches_31.jpg' },
  { name: '点蚀表面', path: '/samples/pitted_surface_173.jpg' },
  { name: '氧化皮', path: '/samples/rolled-in_scale_5.jpg' },
  { name: '划痕', path: '/samples/scratches_71.jpg' },
]

const file = ref(null)
const preview = ref('')
const result = ref(null)
const loading = ref(false)

const normalizedDefects = computed(() => result.value?.defects || [])
const qualityLevel = computed(() => {
  const count = result.value?.defect_count || 0
  if (count === 0) return '合格'
  if (count <= 2) return '关注'
  return '复检'
})

function onFile(uploadFile) {
  file.value = uploadFile.raw
  preview.value = URL.createObjectURL(uploadFile.raw)
  result.value = null
}

async function chooseSample(sample) {
  preview.value = sample.path
  const response = await fetch(sample.path)
  const blob = await response.blob()
  file.value = new File([blob], sample.path.split('/').pop(), { type: blob.type || 'image/jpeg' })
  result.value = null
}

async function start() {
  if (!file.value) return
  const fd = new FormData()
  fd.append('file', file.value)
  loading.value = true
  try {
    result.value = await detectImage(fd)
  } finally {
    loading.value = false
  }
}

function boxStyle(defect) {
  const [x1, y1, x2, y2] = defect.bbox || [30, 30, 130, 130]
  const scale = 200
  return {
    left: `${(x1 / scale) * 100}%`,
    top: `${(y1 / scale) * 100}%`,
    width: `${((x2 - x1) / scale) * 100}%`,
    height: `${((y2 - y1) / scale) * 100}%`,
    borderColor: defect.color || '#38bdf8',
  }
}
</script>

<style scoped>
.image-page { color: #e5eefb; }
.top-actions { display: flex; justify-content: space-between; align-items: center; padding: 18px 22px; margin-bottom: 16px; }
.top-actions b { font-size: 18px; }
.top-actions p { margin: 6px 0 0; color: #94a3b8; }
.sample-strip { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }
.sample-card { cursor: pointer; padding: 10px; border-radius: 12px; background: rgba(15,23,42,.82); border: 1px solid rgba(56,189,248,.2); transition: .2s; }
.sample-card:hover { transform: translateY(-3px); border-color: #38bdf8; box-shadow: 0 0 18px rgba(56,189,248,.18); }
.sample-card img { width: 100%; height: 96px; object-fit: cover; border-radius: 8px; }
.sample-card span { display: block; text-align: center; margin-top: 8px; color: #cbd5e1; }
.wrap { grid-template-columns: 1fr 1fr; }
.box { padding: 20px; min-height: 620px; }
.box-title { font-size: 18px; font-weight: 800; margin-bottom: 14px; color: #dbeafe; }
.image-stage { position: relative; margin-top: 18px; border-radius: 14px; overflow: hidden; border: 1px solid rgba(56,189,248,.25); background: #020617; }
.preview { width: 100%; max-height: 440px; object-fit: contain; display: block; }
.result-stage { min-height: 260px; display: flex; align-items: center; justify-content: center; }
.defect-box { position: absolute; border: 3px solid #38bdf8; box-shadow: 0 0 14px rgba(56,189,248,.4); }
.defect-box span { position: absolute; left: 0; top: -28px; white-space: nowrap; padding: 4px 8px; background: rgba(15,23,42,.88); color: #fff; border-radius: 6px; font-size: 12px; }
.summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0; }
.summary-cards div { padding: 14px; border-radius: 12px; background: rgba(15,23,42,.72); border: 1px solid rgba(56,189,248,.18); text-align: center; }
.summary-cards b { display: block; color: #38bdf8; font-size: 24px; }
.summary-cards span { color: #94a3b8; font-size: 12px; }
</style>
