import request from '../utils/request.js'
export const getUsers = params => request({ url: '/users', method: 'get', params })
export const createUser = data => request({ url: '/users', method: 'post', data })
export const updateUser = (id, data) => request({ url: `/users/${id}`, method: 'put', data })
export const deleteUser = id => request({ url: `/users/${id}`, method: 'delete' })
