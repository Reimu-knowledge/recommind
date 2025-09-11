import type { Question, WeakKnowledgePoint } from '../types'

// 后端API基础配置
const API_BASE_URL = 'http://localhost:5000'

// 学生相关API
export const studentApi = {
  // 创建学生
  createStudent: async (studentData: {
    id: string
    name: string
    email?: string
    grade?: string
  }): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/students`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(studentData)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '创建学生失败')
      }
      
      return result.data
    } catch (error) {
      console.error('创建学生失败:', error)
      throw error
    }
  },

  // 开始学习会话
  startLearningSession: async (studentId: string, sessionName?: string): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/students/${studentId}/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_name: sessionName || '学习会话'
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '开始学习会话失败')
      }
      
      return result.data
    } catch (error) {
      console.error('开始学习会话失败:', error)
      throw error
    }
  },

  // 获取学生信息
  getStudentInfo: async (studentId: string): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/students/${studentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '获取学生信息失败')
      }
      
      return result.data
    } catch (error) {
      console.error('获取学生信息失败:', error)
      throw error
    }
  },
  // 获取推荐题目
  getRecommendedQuestions: async (studentId: string, knowledgePoints?: string[]): Promise<Question[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/students/${studentId}/recommendations?num_questions=5`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '请求失败')
      }
      
      // 转换API响应格式到前端Question类型
      return result.recommendations.map((q: any, index: number) => ({
        id: parseInt(q.qid.replace('Q', '')), // Q1 -> 1
        title: q.content,
        type: '选择题',
        options: q.options.map((opt: any, optIndex: number) => ({
          key: String.fromCharCode(65 + optIndex), // A, B, C, D
          text: opt
        })),
        correctAnswer: '', // 前端不应该知道正确答案
        explanation: '', // 前端不应该预先获得解析
        knowledgePoint: Object.keys(q.knowledge_points)[0] || 'unknown'
      }))
    } catch (error) {
      console.error('获取推荐题目失败:', error)
      throw error
    }
  },

  // 提交答案
  submitAnswer: async (data: {
    questionId: string
    studentId: string
    selectedOption: string
  }): Promise<{ isCorrect: boolean; correctAnswer: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/students/${data.studentId}/answers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          answers: [{
            qid: `Q${data.questionId}`,
            selected: data.selectedOption
          }]
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '提交答案失败')
      }
      
      // 从答题详情中获取结果
      const answerDetail = result.answer_details[0]
      return {
        isCorrect: answerDetail.correct,
        correctAnswer: answerDetail.correct_answer
      }
    } catch (error) {
      console.error('提交答案失败:', error)
      throw error
    }
  },

  // 获取题目解析（错因分析）
  getExplanation: async (data: {
    questionId: string
    studentId: string
    selectedOption: string
  }): Promise<{ explanation: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/error-analysis/Q${data.questionId}/${data.selectedOption}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '获取解析失败')
      }
      
      // 构建错因分析解析文本
      const analysis = result.data
      let explanation = `您选择了选项${analysis.selected_option}。\n\n`
      
      if (analysis.knowledge_points_to_review.length > 0) {
        explanation += '需要巩固的知识点：\n'
        analysis.knowledge_points_to_review.forEach((kp: any) => {
          const priority = kp.priority === 'high' ? '🔴 重点' : '🟡 加强'
          explanation += `• ${priority} ${kp.knowledge_point}\n`
        })
      } else {
        explanation += '✅ 没有需要特别巩固的知识点'
      }
      
      return {
        explanation: explanation
      }
    } catch (error) {
      console.error('获取解析失败:', error)
      throw error
    }
  },

  // 获取薄弱知识点
  getWeakKnowledgePoints: async (studentId: string): Promise<WeakKnowledgePoint[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/students/${studentId}/weak-points?threshold=0.3`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '获取薄弱知识点失败')
      }
      
      // 转换API响应格式到前端WeakKnowledgePoint类型
      return result.weak_knowledge_points.map((point: any) => ({
        id: point.id, // 知识点ID
        name: point.name, // 知识点名称
        description: `${point.name}掌握程度较低，建议加强练习`,
        score: point.accuracy // 直接使用正确率（已经是百分比）
      }))
    } catch (error) {
      console.error('获取薄弱知识点失败:', error)
      throw error
    }
  },

  // 根据知识点获取题目
  getQuestionsByKnowledgePoint: async (knowledgePointId: string): Promise<Question[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/questions/by-knowledge-point/${knowledgePointId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status !== 'success') {
        throw new Error(result.message || '获取题目失败')
      }
      
      // 转换API响应格式到前端Question类型
      return result.questions.map((q: any) => ({
        id: parseInt(q.qid.replace('Q', '')), // Q1 -> 1
        title: q.content,
        type: '选择题',
        options: q.options.map((opt: any, optIndex: number) => ({
          key: String.fromCharCode(65 + optIndex), // A, B, C, D
          text: opt
        })),
        correctAnswer: '', // 前端不应该知道正确答案
        explanation: '', // 前端不应该预先获得解析
        knowledgePoint: knowledgePointId
      }))
    } catch (error) {
      console.error('获取知识点题目失败:', error)
      throw error
    }
  }
}
