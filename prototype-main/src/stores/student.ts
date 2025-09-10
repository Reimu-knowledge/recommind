import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Question, WeakKnowledgePoint } from '../types'

// 简化的模拟数据
const mockWeakPoints: WeakKnowledgePoint[] = [
  { id: 'sets', name: '集合论', description: '集合运算掌握不够', score: 45 },
  { id: 'logic', name: '数理逻辑', description: '命题逻辑需要加强', score: 52 },
  { id: 'graph', name: '图论', description: '图的遍历算法', score: 38 }
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
    correctAnswer: 'B', explanation: '正确答案是交集', knowledgePoint: 'sets'
  }
]

export const useStudentStore = defineStore('student', () => {
  // 基础状态
  const currentView = ref('default')
  const loading = ref(false)
  
  // 数据状态
  const weakKnowledgePoints = ref(mockWeakPoints)
  const questions = ref(mockQuestions)
  const selectedWeakPoint = ref<WeakKnowledgePoint | null>(null)

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

  const refreshRecommendations = async () => {
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    loading.value = false
    currentView.value = 'smart'
  }

  return {
    // 状态
    currentView, loading, weakKnowledgePoints, questions, selectedWeakPoint,
    // 计算属性
    smartQuestions, weakPointQuestions,
    // 方法
    setCurrentView, selectWeakPoint, refreshRecommendations
  }
})
