import type { User } from '../types'

// 用户认证工具
export const auth = {
  // 获取当前用户
  getUser: (): User | null => {
    const token = localStorage.getItem('userToken')
    const role = localStorage.getItem('userRole') as 'student' | 'teacher'
    const username = localStorage.getItem('username')
    
    return (token && role && username) ? { token, role, username } : null
  },

  // 设置用户信息
  setUser: (user: User) => {
    localStorage.setItem('userToken', user.token)
    localStorage.setItem('userRole', user.role)
    localStorage.setItem('username', user.username)
  },

  // 清除用户信息
  clearUser: () => {
    localStorage.removeItem('userToken')
    localStorage.removeItem('userRole')
    localStorage.removeItem('username')
  },

  // 检查登录状态
  isLoggedIn: () => !!localStorage.getItem('userToken'),

  // 检查用户角色
  hasRole: (role: 'student' | 'teacher') => localStorage.getItem('userRole') === role
}
