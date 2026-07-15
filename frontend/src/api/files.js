import request from '../utils/request.js'
export const getImageFiles = () => request({ url: '/files/list/images', method: 'get' })
export const getVideoFiles = () => request({ url: '/files/list/videos', method: 'get' })
export const previewUrl = path => `/api/v1/files/preview/${encodeURIComponent(path)}`
export const downloadUrl = path => `/api/v1/files/download/${encodeURIComponent(path)}`
