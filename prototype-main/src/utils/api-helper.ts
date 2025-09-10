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

  // 创建学生
  createStudent: async (studentData: {
    id: string
    name: string
    email?: string
    grade?: string
  }) => {
    try {
      const student = await studentApi.createStudent(studentData)
      return student
    } catch (error) {
      console.error('创建学生失败:', error)
      throw error
    }
  },

  // 开始学习会话
  startLearningSession: async (sessionName?: string) => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const session = await studentApi.startLearningSession(user.username, sessionName)
      return session
    } catch (error) {
      console.error('开始学习会话失败:', error)
      throw error
    }
  },

  // 获取学生信息
  getStudentInfo: async () => {
    const user = auth.getUser()
    if (!user) {
      throw new Error('用户未登录')
    }

    try {
      const studentInfo = await studentApi.getStudentInfo(user.username)
      return studentInfo
    } catch (error) {
      console.error('获取学生信息失败:', error)
      throw error
    }
  },

  // 根据知识点获取题目
  getQuestionsByKnowledgePoint: async (knowledgePointId: string) => {
    try {
      const questions = await studentApi.getQuestionsByKnowledgePoint(knowledgePointId)
      return questions
    } catch (error) {
      console.error('获取知识点题目失败:', error)
      throw error
    }
  }
}
