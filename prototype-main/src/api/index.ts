// 简化的API配置
import { auth } from '../utils/auth'

// 模拟API基础配置
export const apiConfig = {
  baseURL: '/api',
  timeout: 10000
}

// 模拟请求方法
export const request = {
  post: async (url: string, data: any) => {
    const user = auth.getUser()
    console.log('API请求:', { url, data, user })
    
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 这里应该是真实的axios调用
    return { code: 200, message: '成功', data: {} }
  },
  
  get: async (url: string, params?: any) => {
    const user = auth.getUser()
    console.log('API请求:', { url, params, user })
    
    await new Promise(resolve => setTimeout(resolve, 500))
    return { code: 200, message: '成功', data: {} }
  }
}
