/**
 * AI碳枢算 - 前端认证工具
 */

const API_BASE = 'http://127.0.0.1:8000/api/v1'

export function getToken() {
  return localStorage.getItem('token')
}

export function getUser() {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

export function setAuth(token, user) {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
}

export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export function isAuthenticated() {
  return !!getToken()
}

/**
 * 带认证的fetch封装
 */
export async function authFetch(url, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers
  })

  // 401自动跳转登录
  if (response.status === 401) {
    clearAuth()
    window.location.href = '/login'
    throw new Error('认证已过期，请重新登录')
  }

  return response
}

/**
 * 检查认证状态（调后端API验证token有效性）
 */
export async function checkAuthStatus() {
  const token = getToken()
  if (!token) return { authenticated: false, user: null }

  try {
    const res = await fetch(`${API_BASE}/auth/status`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if (data.authenticated) {
      // 更新本地用户信息
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    }
    clearAuth()
    return { authenticated: false, user: null }
  } catch {
    return { authenticated: false, user: null }
  }
}
