import request from '../utils/request.js'
export const getRoles = () => request({ url: '/system/roles', method: 'get' })
export const createRole = data => request({ url: '/system/roles', method: 'post', data })
export const updateRole = (id, data) => request({ url: `/system/roles/${id}`, method: 'put', data })
export const deleteRole = id => request({ url: `/system/roles/${id}`, method: 'delete' })
export const getSettings = () => request({ url: '/system/settings', method: 'get' })
export const updateSetting = (key, data) => request({ url: `/system/settings/${key}`, method: 'put', data })
export const getLoginLogs = () => request({ url: '/system/logs/login', method: 'get' })
export const getOperationLogs = () => request({ url: '/system/logs/operation', method: 'get' })
