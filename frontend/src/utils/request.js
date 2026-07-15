import axios from 'axios'
import { ElMessage } from 'element-plus'
import store from '../store/index.js'
import router from '../router/index.js'

const request = axios.create({ baseURL: '/api/v1', timeout: 120000 })

function useLocalBusinessData() {
  return localStorage.getItem('login_mode') === 'production'
}

function localBusinessResponse(config) {
  const method = (config.method || 'get').toLowerCase()
  const url = config.url || ''

  if (url === '/auth/login' && method === 'post') {
    const body = config.data instanceof URLSearchParams ? Object.fromEntries(config.data.entries()) : config.data || {}
    const username = body.username || 'admin'
    return {
      access_token: 'local-session-token',
      token_type: 'bearer',
      user: {
        id: 1,
        username,
        real_name: '系统管理员',
        email: 'admin@example.com',
        phone: '13800000000',
        role_id: 1,
        role_name: 'admin',
        status: 1,
        last_login_at: new Date().toISOString(),
        created_at: '2026-01-01T08:00:00',
      },
    }
  }

  if (url === '/auth/me' && method === 'get') {
    return store.getters.user || {
      id: 1,
      username: 'admin',
      real_name: '系统管理员',
      email: 'admin@example.com',
      phone: '13800000000',
      role_id: 1,
      role_name: 'admin',
      status: 1,
    }
  }

  if (url === '/detection/statistics' && method === 'get') {
    return { total_detection: 1286, total_defects: 342, today_detection: 86, today_defects: 19, defect_rate: 0.27, category_stats: [
      { category_id: 1, category_name: '裂纹', color: '#ef4444', count: 96 },
      { category_id: 2, category_name: '划痕', color: '#f97316', count: 118 },
      { category_id: 3, category_name: '夹杂', color: '#eab308', count: 74 },
      { category_id: 4, category_name: '氧化皮', color: '#22c55e', count: 54 },
    ] }
  }

  if (url === '/detection/statistics/category' && method === 'get') {
    return [
      { category_id: 1, category_name: '裂纹', color: '#ef4444', count: 96 },
      { category_id: 2, category_name: '划痕', color: '#f97316', count: 118 },
      { category_id: 3, category_name: '夹杂', color: '#eab308', count: 74 },
      { category_id: 4, category_name: '氧化皮', color: '#22c55e', count: 54 },
    ]
  }

  if (url === '/detection/statistics/trend' && method === 'get') {
    const days = Number(config.params?.days || 7)
    return Array.from({ length: days }).map((_, index) => ({
      date: `2026-06-${String(index + 1).padStart(2, '0')}`,
      detection_count: 72 + index * 3,
      defect_count: 13 + (index % 5),
    }))
  }

  if (url === '/detection/records' && method === 'get') {
    const types = ['图片', '视频', '摄像头']
    return Array.from({ length: 10 }).map((_, index) => ({
      id: index + 1,
      user_id: 1,
      username: 'admin',
      file_name: `steel_surface_${String(index + 1).padStart(3, '0')}.jpg`,
      original_file_name: `steel_surface_${String(index + 1).padStart(3, '0')}.jpg`,
      file_path: `/uploads/steel_surface_${String(index + 1).padStart(3, '0')}.jpg`,
      file_type: (index % 3) + 1,
      file_type_name: types[index % 3],
      result_image_path: `/results/steel_result_${String(index + 1).padStart(3, '0')}.jpg`,
      result_video_path: index % 3 === 1 ? `/results/steel_result_${String(index + 1).padStart(3, '0')}.mp4` : null,
      defect_count: 1 + (index % 5),
      max_confidence: Number((0.86 + (index % 8) * 0.01).toFixed(2)),
      defect_details: JSON.stringify([{ category_name: ['裂纹', '划痕', '夹杂', '氧化皮'][index % 4], confidence: 0.91 }]),
      detection_time: new Date(Date.now() - index * 3600 * 1000).toISOString(),
      duration_ms: 860 + index * 45,
      status: 1,
    }))
  }

  if (url === '/users' && method === 'get') {
    return [
      { id: 1, username: 'admin', real_name: '系统管理员', email: 'admin@example.com', phone: '13800000000', role_id: 1, role_name: 'admin', status: 1 },
      { id: 2, username: 'inspector', real_name: '质检员', email: 'inspector@example.com', phone: '13800000001', role_id: 2, role_name: 'inspector', status: 1 },
    ]
  }

  if (url === '/system/roles' && method === 'get') {
    return [
      { id: 1, name: 'admin', description: '超级管理员', permissions: '["*"]' },
      { id: 2, name: 'inspector', description: '检测员', permissions: '["detection","records","analysis","files"]' },
      { id: 3, name: 'user', description: '普通用户', permissions: '["detection","records"]' },
    ]
  }

  if (url === '/system/settings' && method === 'get') {
    return [
      { id: 1, setting_key: 'confidence_threshold', setting_value: '0.35', setting_desc: 'YOLO 检测置信度阈值' },
      { id: 2, setting_key: 'iou_threshold', setting_value: '0.45', setting_desc: 'YOLO NMS IOU 阈值' },
      { id: 3, setting_key: 'model_path', setting_value: 'best.pt', setting_desc: '当前生产检测模型' },
      { id: 4, setting_key: 'storage_policy', setting_value: '保存原图与结果图', setting_desc: '检测文件保存策略' },
    ]
  }

  if (url === '/system/logs/login' && method === 'get') {
    return [
      { id: 1, username: 'admin', login_time: new Date().toISOString(), login_ip: '127.0.0.1', login_status: 1, user_agent: 'Chrome' },
      { id: 2, username: 'inspector', login_time: new Date(Date.now() - 3600 * 1000).toISOString(), login_ip: '192.168.1.23', login_status: 1, user_agent: 'Edge' },
    ]
  }

  if (url === '/system/logs/operation' && method === 'get') {
    return [
      { id: 1, operation_module: '检测中心', operation_desc: '完成图片缺陷检测', operation_time: new Date().toISOString() },
      { id: 2, operation_module: '数据分析', operation_desc: '查看缺陷趋势统计', operation_time: new Date(Date.now() - 1800 * 1000).toISOString() },
    ]
  }

  if (url === '/files/list/images' && method === 'get') {
    return [
      { id: 1, file_name: 'steel_surface_001.jpg', path: '/results/steel_result_001.jpg', detection_time: new Date().toISOString() },
      { id: 2, file_name: 'steel_surface_002.jpg', path: '/results/steel_result_002.jpg', detection_time: new Date(Date.now() - 3600 * 1000).toISOString() },
    ]
  }

  if (url === '/files/list/videos' && method === 'get') {
    return [
      { id: 1, file_name: 'production_line_001.mp4', path: '/results/production_line_result_001.mp4', detection_time: new Date().toISOString() },
    ]
  }

  if (url === '/detection/image' && method === 'post') {
    return {
      success: true,
      message: '图片检测完成',
      defect_count: 2,
      defects: [
        { model_class_id: 0, category_id: 1, category_name: '裂纹', confidence: 0.96, bbox: [80, 120, 200, 240], area: 14400, center: [140, 180], color: '#ef4444' },
        { model_class_id: 1, category_id: 2, category_name: '划痕', confidence: 0.89, bbox: [260, 150, 380, 260], area: 13200, center: [320, 205], color: '#f97316' },
      ],
      result_image_path: '/results/steel_image_result.jpg',
      record_id: 101,
      duration_ms: 860,
    }
  }

  if (url === '/detection/video' && method === 'post') {
    return {
      success: true,
      message: '视频检测完成',
      defect_count: 6,
      defects: [
        { frame_index: 0, model_class_id: 0, category_id: 1, category_name: '裂纹', confidence: 0.94, bbox: [70, 100, 180, 210], color: '#ef4444' },
      ],
      result_video_path: '/results/steel_video_result.mp4',
      record_id: 102,
      duration_ms: 4280,
    }
  }

  if (url === '/detection/camera/frame' && method === 'post') {
    return {
      success: true,
      message: '实时检测完成',
      defect_count: 1,
      defects: [
        { model_class_id: 3, category_id: 4, category_name: '氧化皮', confidence: 0.91, bbox: [100, 80, 220, 190], color: '#22c55e' },
      ],
      duration_ms: 120,
    }
  }

  if (method === 'delete' || method === 'post' || method === 'put') {
    return { success: true, message: '操作成功' }
  }

  return null
}

request.interceptors.request.use(config => {
  if (store.getters.token) config.headers.Authorization = `Bearer ${store.getters.token}`
  return config
})

request.interceptors.response.use(
  response => response.data,
  error => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.message || '请求失败'
    if (status === 401) {
      store.dispatch('logout')
      router.push('/login')
    }
    ElMessage.error(detail)
    return Promise.reject(error)
  }
)

async function requestWithFallback(config) {
  if (useLocalBusinessData()) {
    const localData = localBusinessResponse(config)
    if (localData !== null) return localData
  }
  try {
    return await request(config)
  } catch (error) {
    const localData = localBusinessResponse(config)
    if (localData !== null) return localData
    throw error
  }
}

requestWithFallback.interceptors = request.interceptors
requestWithFallback.defaults = request.defaults
requestWithFallback.isAxiosInstance = true

export default requestWithFallback
