import type { Question, WeakKnowledgePoint } from '../types'

// 后端API基础配置
const API_BASE_URL = 'http://localhost:5000'

// 学生相关API
export const studentApi = {
  // 获取推荐题目
  getRecommendedQuestions: async (studentId: string, knowledgePoints?: string[]): Promise<Question[]> => {
    // 真实API调用代码
    try {
      const response = await fetch(`${API_BASE_URL}/api/student/recommend-questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          studentId,
          knowledgePoints: knowledgePoints || []
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code !== 200) {
        throw new Error(result.message || '请求失败')
      }
      
      // 转换API响应格式到前端Question类型
      return result.data.questions.map((q: any) => ({
        id: parseInt(q.questionId.replace('Q', '')), // 将Q1转换为1
        title: q.description,
        type: '选择题',
        options: q.options.map((opt: any) => ({
          key: opt.id,
          text: opt.text
        })),
        correctAnswer: q.correctAnswer, // 现在可以获取正确答案用于判分
        explanation: '', // 解析需要单独获取
        knowledgePoint: q.knowledgePoint,
        difficulty: q.difficulty || 0.5,
        score: q.score || 0.0
      }))
    } catch (error) {
      console.error('获取推荐题目失败:', error)
      // 如果API调用失败，返回空数组而不是抛出错误
      return []
    }
  },

  // 提交答案
  submitAnswer: async (data: {
    questionId: string
    studentId: string
    selectedOption: string
  }): Promise<{ isCorrect: boolean; correctAnswer: string; currentMastery?: any }> => {
    // 真实API调用代码
    try {
      const response = await fetch(`${API_BASE_URL}/api/student/submit-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          questionId: `Q${data.questionId}`, // 转换为Q1格式
          studentId: data.studentId,
          selectedOption: data.selectedOption
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code !== 200) {
        throw new Error(result.message || '提交答案失败')
      }
      
      return {
        isCorrect: result.data.isCorrect,
        correctAnswer: result.data.correctAnswer,
        currentMastery: result.data.currentMastery
      }
    } catch (error) {
      console.error('提交答案失败:', error)
      // 如果API调用失败，返回模拟结果
      return {
        isCorrect: data.selectedOption === 'B',
        correctAnswer: 'B'
      }
    }
  },

  // 获取题目解析
  getExplanation: async (data: {
    questionId: string
    studentId: string
    selectedOption: string
  }): Promise<{ explanation: string }> => {
    // 真实API调用代码
    try {
      const response = await fetch(`${API_BASE_URL}/api/student/get-explanation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          questionId: `Q${data.questionId}`, // 转换为Q1格式
          studentId: data.studentId,
          selectedOption: data.selectedOption
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code !== 200) {
        throw new Error(result.message || '获取解析失败')
      }
      
      return {
        explanation: result.data.explanation
      }
    } catch (error) {
      console.error('获取解析失败:', error)
      // 如果API调用失败，返回默认解析
      return {
        explanation: '这是一道关于图论基础知识的题目，需要理解相关概念和定理。'
      }
    }
  },

  // 获取薄弱知识点
  getWeakKnowledgePoints: async (studentId: string): Promise<WeakKnowledgePoint[]> => {
    // 真实API调用代码
    try {
      const response = await fetch(`${API_BASE_URL}/api/student/weak-knowledge-points?studentId=${encodeURIComponent(studentId)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code !== 200) {
        throw new Error(result.message || '获取薄弱知识点失败')
      }
      
      // 转换API响应格式到前端WeakKnowledgePoint类型
      return result.data.weakKnowledgePoints.map((point: any) => ({
        id: point.id,
        name: point.name,
        description: point.description,
        score: point.currentScore
      }))
    } catch (error) {
      console.error('获取薄弱知识点失败:', error)
      // 如果API调用失败，返回空数组
      return []
    }
  },

  // 获取错因分析
  getErrorAnalysis: async (data: {
    questionId: string
    studentId: string
    selectedOption: string
  }): Promise<{
    isCorrect: boolean
    analysis: string
    errorConcepts?: string[]
    questionConcepts?: string[]
    suggestions?: string[]
  }> => {
    // 真实API调用代码
    try {
      const response = await fetch(`${API_BASE_URL}/api/student/error-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          questionId: `Q${data.questionId}`, // 转换为Q1格式
          studentId: data.studentId,
          selectedOption: data.selectedOption
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code !== 200) {
        throw new Error(result.message || '获取错因分析失败')
      }
      
      return {
        isCorrect: result.data.isCorrect,
        analysis: result.data.analysis,
        errorConcepts: result.data.errorConcepts,
        questionConcepts: result.data.questionConcepts,
        suggestions: result.data.suggestions
      }
    } catch (error) {
      console.error('获取错因分析失败:', error)
      // 如果API调用失败，返回默认分析
      return {
        isCorrect: false,
        analysis: '抱歉，暂时无法获取详细的错因分析，建议您复习相关知识点。'
      }
    }
  }
}
