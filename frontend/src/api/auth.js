import request from '../utils/request.js'

export function login(username, password) {
  const data = new URLSearchParams()
  data.append('username', username)
  data.append('password', password)
  return request({ url: '/auth/login', method: 'post', data })
}
export function getMe() { return request({ url: '/auth/me', method: 'get' }) }
