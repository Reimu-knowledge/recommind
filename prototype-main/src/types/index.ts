/**
 * 全局类型定义
 */

// 用户角色类型
export type UserRole = 'student' | 'teacher'

// 答题相关类型
export interface QuestionOption {
  key: string
  text: string
}

export interface Question {
  id: number
  title: string
  description?: string
  type: string
  options: QuestionOption[]
  correctAnswer: string
  explanation: string
  knowledgePoint: string
}

export interface AnswerResult {
  questionId: number
  selectedAnswer: string
  isCorrect: boolean
  knowledgePoint: string
}

// 知识点相关类型
export interface KnowledgePoint {
  id: string
  name: string
}

export interface WeakKnowledgePoint extends KnowledgePoint {
  description: string
  score: number
}

// 学生相关类型
export interface Student {
  id: string
  name: string
  class: string
  scores: number[]
  totalQuestions: number
  correctRate: number
  lastActive: string
}

// 用户相关类型
export interface User {
  token: string
  role: UserRole
  username: string
}

// 统计数据类型
export interface Statistics {
  totalStudents: number
  completedQuestions: number
  averageScore: number
  activeStudents: number
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页类型
export interface Pagination {
  current: number
  pageSize: number
  total: number
}

export interface PaginatedData<T> {
  list: T[]
  pagination: Pagination
}
