import { createStore } from 'vuex'

const store = createStore({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    sidebarOpened: true
  },
  getters: {
    token: state => state.token,
    user: state => state.user,
    isAdmin: state => state.user?.role_name === 'admin' || state.user?.role_id === 1,
    sidebarOpened: state => state.sidebarOpened
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    SET_USER(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    LOGOUT(state) {
      state.token = ''
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    SET_LOCAL_SESSION(state, enabled) {
      localStorage.setItem('login_mode', enabled ? 'production' : 'real')
    },
    TOGGLE_SIDEBAR(state) {
      state.sidebarOpened = !state.sidebarOpened
    }
  },
  actions: {
    login({ commit }, data) {
      commit('SET_TOKEN', data.access_token)
      commit('SET_USER', data.user)
    },
    logout({ commit }) { commit('LOGOUT') },
    toggleSidebar({ commit }) { commit('TOGGLE_SIDEBAR') }
  }
})

export default store
