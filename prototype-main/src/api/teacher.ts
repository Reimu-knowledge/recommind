import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 发送请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ 请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`✅ 响应成功: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ 响应错误:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// 教师端API接口
export const teacherApi = {
  // 获取所有学生列表
  async getAllStudents(): Promise<any[]> {
    try {
      const response = await api.get('/api/teacher/students');
      return response.data.students || [];
    } catch (error) {
      console.error('获取学生列表失败:', error);
      throw error;
    }
  },

  // 获取学生详细信息
  async getStudentDetail(studentId: string): Promise<any> {
    try {
      const response = await api.get(`/api/teacher/students/${studentId}`);
      return response.data;
    } catch (error) {
      console.error('获取学生详情失败:', error);
      throw error;
    }
  },

  // 获取总体统计数据
  async getOverallStats(): Promise<any> {
    try {
      const response = await api.get('/api/teacher/stats');
      return response.data;
    } catch (error) {
      console.error('获取统计数据失败:', error);
      throw error;
    }
  },

  // 获取知识点列表
  async getKnowledgePoints(): Promise<any[]> {
    try {
      const response = await api.get('/api/teacher/knowledge-points');
      return response.data.knowledge_points || [];
    } catch (error) {
      console.error('获取知识点列表失败:', error);
      throw error;
    }
  },

  // 获取所有学生的知识点掌握情况
  async getAllStudentsMastery(): Promise<any[]> {
    try {
      const response = await api.get('/api/teacher/students/mastery');
      return response.data.students || [];
    } catch (error) {
      console.error('获取学生掌握情况失败:', error);
      throw error;
    }
  },

  // 获取知识点总体掌握情况
  async getKnowledgePointStats(): Promise<any[]> {
    try {
      const response = await api.get('/api/teacher/knowledge-points/stats');
      return response.data.knowledge_point_stats || [];
    } catch (error) {
      console.error('获取知识点统计失败:', error);
      throw error;
    }
  },

  // 更新学生推荐方向
  async updateStudentRecommendation(studentId: string, knowledgePoints: string[], priority: string): Promise<any> {
    try {
      const response = await api.post(`/api/teacher/students/${studentId}/recommendation`, {
        knowledge_points: knowledgePoints,
        priority: priority
      });
      return response.data;
    } catch (error) {
      console.error('更新学生推荐方向失败:', error);
      throw error;
    }
  },

  // 获取学生答题记录
  async getStudentAnswerRecords(studentId: string): Promise<any[]> {
    try {
      const response = await api.get(`/api/teacher/students/${studentId}/answers`);
      return response.data.answers || [];
    } catch (error) {
      console.error('获取学生答题记录失败:', error);
      throw error;
    }
  },

  // 导出学生数据
  async exportStudentData(format: string = 'csv'): Promise<Blob> {
    try {
      const response = await api.get(`/api/teacher/export/students?format=${format}`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('导出学生数据失败:', error);
      throw error;
    }
  }
};

export default teacherApi;
