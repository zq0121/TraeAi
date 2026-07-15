import request from '../utils/request.js'

export const detectImage = data => request({ url: '/detection/image', method: 'post', data, headers: { 'Content-Type': 'multipart/form-data' }, timeout: 180000 })
export const detectVideo = data => request({ url: '/detection/video', method: 'post', data, headers: { 'Content-Type': 'multipart/form-data' }, timeout: 600000 })
export const detectCameraFrame = data => request({ url: '/detection/camera/frame', method: 'post', data, headers: { 'Content-Type': 'multipart/form-data' }, timeout: 30000 })
export const getRecords = params => request({ url: '/detection/records', method: 'get', params })
export const getRecord = id => request({ url: `/detection/records/${id}`, method: 'get' })
export const deleteRecord = id => request({ url: `/detection/records/${id}`, method: 'delete' })
export const getCategories = () => request({ url: '/detection/categories', method: 'get' })
export const getStatistics = () => request({ url: '/detection/statistics', method: 'get' })
export const getCategoryStats = () => request({ url: '/detection/statistics/category', method: 'get' })
export const getTrend = days => request({ url: '/detection/statistics/trend', method: 'get', params: { days } })
