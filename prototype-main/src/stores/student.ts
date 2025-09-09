import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Question, WeakKnowledgePoint } from '../types'
import { studentApi } from '../api/student'

// 知识点掌握度接口
interface KnowledgeMastery {
  [key: string]: number
}

// 简化的模拟数据（作为备用）
const mockWeakPoints: WeakKnowledgePoint[] = [
  { id: 'K1', name: '集合运算', description: '集合运算掌握不够', score: 45 },
  { id: 'K2', name: '关系映射', description: '关系映射需要加强', score: 52 },
  { id: 'K3', name: '图基本概念', description: '图的基本概念', score: 38 }
]

const mockQuestions: Question[] = [
  {
    id: 1, title: '集合运算题目', type: '选择题',
    options: [
      { key: 'A', text: 'A ∪ B' },
      { key: 'B', text: 'A ∩ B' },
      { key: 'C', text: 'A - B' },
      { key: 'D', text: 'A ⊕ B' }
    ],
    correctAnswer: 'B', explanation: '正确答案是交集', knowledgePoint: 'K1'
  }
]

export const useStudentStore = defineStore('student', () => {
  // 基础状态
  const currentView = ref('default')
  const loading = ref(false)
  
  // 数据状态
  const weakKnowledgePoints = ref<WeakKnowledgePoint[]>([])
  const questions = ref<Question[]>([])
  const selectedWeakPoint = ref<WeakKnowledgePoint | null>(null)
  const knowledgeMastery = ref<KnowledgeMastery>({})
  const currentStudentId = ref<string>('')

  // 计算属性
  const smartQuestions = computed(() => questions.value.slice(0, 3))
  const weakPointQuestions = computed(() => 
    selectedWeakPoint.value 
      ? questions.value.filter(q => q.knowledgePoint === selectedWeakPoint.value?.id)
      : []
  )

  // 动作
  const setCurrentView = (view: string) => {
    currentView.value = view
  }

  const selectWeakPoint = (point: WeakKnowledgePoint) => {
    selectedWeakPoint.value = point
    currentView.value = 'weak'
  }

  const setStudentId = (studentId: string) => {
    currentStudentId.value = studentId
  }

  const updateKnowledgeMastery = (mastery: KnowledgeMastery) => {
    knowledgeMastery.value = { ...mastery }
  }

  // 获取推荐题目
  const getRecommendedQuestions = async (knowledgePoints?: string[]) => {
    if (!currentStudentId.value) {
      console.warn('没有设置学生ID')
      return []
    }

    loading.value = true
    try {
      const recommendedQuestions = await studentApi.getRecommendedQuestions(
        currentStudentId.value, 
        knowledgePoints
      )
      questions.value = recommendedQuestions
      return recommendedQuestions
    } catch (error) {
      console.error('获取推荐题目失败:', error)
      questions.value = mockQuestions // 使用备用数据
      return mockQuestions
    } finally {
      loading.value = false
    }
  }

  // 获取薄弱知识点
  const getWeakKnowledgePoints = async () => {
    if (!currentStudentId.value) {
      console.warn('没有设置学生ID')
      weakKnowledgePoints.value = mockWeakPoints
      return mockWeakPoints
    }

    loading.value = true
    try {
      const weakPoints = await studentApi.getWeakKnowledgePoints(currentStudentId.value)
      weakKnowledgePoints.value = weakPoints
      return weakPoints
    } catch (error) {
      console.error('获取薄弱知识点失败:', error)
      weakKnowledgePoints.value = mockWeakPoints // 使用备用数据
      return mockWeakPoints
    } finally {
      loading.value = false
    }
  }

  // 刷新推荐
  const refreshRecommendations = async () => {
    await getRecommendedQuestions()
    currentView.value = 'smart'
  }

  // 刷新薄弱知识点
  const refreshWeakPoints = async () => {
    await getWeakKnowledgePoints()
  }

  return {
    // 状态
    currentView, loading, weakKnowledgePoints, questions, selectedWeakPoint,
    knowledgeMastery, currentStudentId,
    // 计算属性
    smartQuestions, weakPointQuestions,
    // 方法
    setCurrentView, selectWeakPoint, setStudentId, updateKnowledgeMastery,
    getRecommendedQuestions, getWeakKnowledgePoints, refreshRecommendations, refreshWeakPoints
  }
})
