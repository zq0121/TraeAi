<template>
  <div class="page records-page">
    <div class="page-head">
      <div>
        <h2 class="page-title">检测记录管理</h2>
        <p>按检测类型、缺陷类别与时间维度追溯钢材表面质量数据。</p>
      </div>
      <div class="head-actions">
        <el-button type="primary">导出报表</el-button>
        <el-button>批量归档</el-button>
      </div>
    </div>

    <div class="grid stat-grid">
      <div class="stat-card"><span>记录总数</span><b>{{ rows.length }}</b></div>
      <div class="stat-card"><span>缺陷总数</span><b>{{ totalDefects }}</b></div>
      <div class="stat-card"><span>最高置信度</span><b>{{ maxConfidence }}%</b></div>
      <div class="stat-card"><span>今日归档</span><b>24</b></div>
    </div>

    <div class="panel box">
      <div class="filters">
        <el-select v-model="params.file_type" clearable placeholder="检测类型" style="width:160px">
          <el-option label="图片" :value="1" />
          <el-option label="视频" :value="2" />
          <el-option label="摄像头" :value="3" />
        </el-select>
        <el-input v-model="params.category" clearable placeholder="缺陷类别" style="width:180px" />
        <el-date-picker v-model="dateRange" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" />
        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>
      <el-table :data="rows" height="520">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="original_file_name" label="检测文件" min-width="180" />
        <el-table-column prop="file_type_name" label="类型" width="100" />
        <el-table-column prop="defect_count" label="缺陷数" width="100" />
        <el-table-column label="最高置信度" width="120">
          <template #default="s">{{ Math.round((s.row.max_confidence || 0) * 100) }}%</template>
        </el-table-column>
        <el-table-column prop="detection_time" label="检测时间" min-width="180" />
        <el-table-column label="质量结论" width="120">
          <template #default="s"><el-tag :type="s.row.defect_count > 3 ? 'danger' : 'success'">{{ s.row.defect_count > 3 ? '建议复检' : '正常放行' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="s">
            <el-button link type="primary" @click="detail=s.row">详情</el-button>
            <el-button link type="primary">报告</el-button>
            <el-button link type="danger" @click="remove(s.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="show" title="检测详情" width="760px">
      <div v-if="detail" class="detail-box">
        <div><span>检测文件</span><b>{{ detail.original_file_name }}</b></div>
        <div><span>检测类型</span><b>{{ detail.file_type_name }}</b></div>
        <div><span>缺陷数量</span><b>{{ detail.defect_count }}</b></div>
        <div><span>最高置信度</span><b>{{ Math.round((detail.max_confidence || 0) * 100) }}%</b></div>
        <div><span>检测时间</span><b>{{ detail.detection_time }}</b></div>
        <div><span>处理建议</span><b>{{ detail.defect_count > 3 ? '建议人工复检并追溯产线参数' : '质量状态稳定，可正常放行' }}</b></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { deleteRecord, getRecords } from '../api/detection.js'

const rows = ref([])
const dateRange = ref([])
const params = reactive({ file_type: null, category: '' })
const detail = ref(null)
const show = computed({ get: () => !!detail.value, set: value => { if (!value) detail.value = null } })
const totalDefects = computed(() => rows.value.reduce((sum, item) => sum + (item.defect_count || 0), 0))
const maxConfidence = computed(() => Math.round(Math.max(...rows.value.map(item => item.max_confidence || 0), 0) * 100))

async function load() {
  rows.value = await getRecords(params)
}

function reset() {
  params.file_type = null
  params.category = ''
  dateRange.value = []
  load()
}

async function remove(id) {
  await ElMessageBox.confirm('确定删除该检测记录？', '操作确认')
  await deleteRecord(id)
  load()
}

onMounted(load)
</script>

<style scoped>
.records-page { color: #e5eefb; }
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head p { color: #94a3b8; margin: 4px 0 0; }
.head-actions { display: flex; gap: 10px; }
.stat-grid { grid-template-columns: repeat(4, 1fr); margin-bottom: 16px; }
.stat-card { padding: 18px; border-radius: 14px; background: linear-gradient(135deg, rgba(15,47,84,.72), rgba(15,23,42,.7)); border: 1px solid rgba(56,189,248,.18); }
.stat-card span { color: #94a3b8; }
.stat-card b { display: block; margin-top: 8px; color: #38bdf8; font-size: 28px; }
.box { padding: 18px; }
.filters { display: flex; gap: 12px; margin-bottom: 14px; align-items: center; flex-wrap: wrap; }
.detail-box { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.detail-box div { padding: 14px; border-radius: 10px; background: rgba(15,23,42,.72); border: 1px solid rgba(56,189,248,.18); }
.detail-box span { display: block; color: #94a3b8; margin-bottom: 6px; }
.detail-box b { color: #e0f2fe; }
</style>
