import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Student, KnowledgePoint } from '../types'

// 简化的模拟数据
const mockStudents: Student[] = [
  {
    id: '2022001', name: '张三', class: '计科1班',
    scores: [85, 78, 92, 67], totalQuestions: 45, correctRate: 78,
    lastActive: '2024-08-29 14:30'
  },
  {
    id: '2022002', name: '李四', class: '计科1班', 
    scores: [72, 85, 69, 78], totalQuestions: 38, correctRate: 82,
    lastActive: '2024-08-29 13:45'
  }
]

const mockKnowledgePoints: KnowledgePoint[] = [
  { id: 'sets', name: '集合论' },
  { id: 'logic', name: '数理逻辑' },
  { id: 'graph', name: '图论' },
  { id: 'algebra', name: '代数系统' }
]

export const useTeacherStore = defineStore('teacher', () => {
  // 基础状态
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  
  // 数据状态
  const students = ref(mockStudents)
  const knowledgePoints = ref(mockKnowledgePoints)
  const statistics = ref({
    totalStudents: 45, completedQuestions: 1284,
    averageScore: 78, activeStudents: 32
  })

  // 筛选状态
  const selectedKnowledge = ref('')
  const selectedChapter = ref('')

  // 计算属性
  const filteredStudents = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return students.value.slice(start, start + pageSize.value)
  })

  // 工具方法
  const getScoreType = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'danger'
  }

  // 动作
  const updateRecommendDirection = async (studentId: string, knowledgeIds: string[]) => {
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    loading.value = false
    console.log('更新推荐方向:', { studentId, knowledgeIds })
  }

  return {
    // 状态
    currentPage, pageSize, loading, students, knowledgePoints, statistics,
    selectedKnowledge, selectedChapter,
    // 计算属性
    filteredStudents,
    // 方法
    getScoreType, updateRecommendDirection
  }
})
