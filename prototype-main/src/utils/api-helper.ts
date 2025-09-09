import { studentApi } from '../api/student'
import { auth } from './auth'
import type { Question } from '../types'

// API调用辅助函数
export const apiHelper = {
  // 提交答案的完整流程
  submitAnswer: async (question: Question, selectedOption: string) => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const response = await studentApi.submitAnswer({
        questionId: question.id.toString(), // 转换为string
        studentId: user.username,
        selectedOption
      })
      
      return response
    } catch (error) {
      console.error('提交答案失败:', error)
      throw error
    }
  },

  // 获取解析的完整流程
  getExplanation: async (question: Question, selectedOption: string) => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const response = await studentApi.getExplanation({
        questionId: question.id.toString(), // 转换为string
        studentId: user.username,
        selectedOption
      })
      
      return response.explanation
    } catch (error) {
      console.error('获取解析失败:', error)
      throw error
    }
  },

  // 获取推荐题目
  getRecommendedQuestions: async (knowledgePoints?: string[]) => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const questions = await studentApi.getRecommendedQuestions(
        user.username,
        knowledgePoints
      )
      
      return questions
    } catch (error) {
      console.error('获取推荐题目失败:', error)
      throw error
    }
  },

  // 获取薄弱知识点
  getWeakKnowledgePoints: async () => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const weakPoints = await studentApi.getWeakKnowledgePoints(user.username)
      return weakPoints
    } catch (error) {
      console.error('获取薄弱知识点失败:', error)
      throw error
    }
  },

  // 获取错因分析
  getErrorAnalysis: async (question: Question, selectedOption: string) => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const analysis = await studentApi.getErrorAnalysis({
        questionId: question.id.toString(),
        studentId: user.username,
        selectedOption
      })
      return analysis
    } catch (error) {
      console.error('获取错因分析失败:', error)
      throw error
    }
  }
}
