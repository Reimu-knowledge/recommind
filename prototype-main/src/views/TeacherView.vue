<template>
  <div class="teacher-layout">
    <!-- 顶部导航 -->
    <el-header class="teacher-header">
      <div class="header-content">
        <h2>CSrecomMIND</h2>
        <div class="header-actions">
          <el-button type="primary" @click="logout">退出登录</el-button>
        </div>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 左侧统计面板 -->
      <el-aside width="350px" class="stats-aside">
        <!-- 总体统计卡片 -->
        <el-card class="stats-overview" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Odometer /></el-icon>
              <span>总体统计</span>
            </div>
          </template>
          
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ totalStudents }}</div>
              <div class="stat-label">学生总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ completedQuestions }}</div>
              <div class="stat-label">完成题目</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ averageScore }}%</div>
              <div class="stat-label">平均分</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ activeStudents }}</div>
              <div class="stat-label">活跃学生</div>
            </div>
          </div>
        </el-card>

        <!-- 知识点筛选器 -->
        <el-card class="filter-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Filter /></el-icon>
              <span>筛选条件</span>
            </div>
          </template>
          
          <div class="filter-content">
            <el-form label-width="80px" size="small">
              <el-form-item label="知识点">
                <el-select v-model="selectedKnowledge" @change="applyFilters">
                  <el-option label="全部" value="" />
                  <el-option 
                    v-for="point in knowledgePoints" 
                    :key="point.id"
                    :label="point.name" 
                    :value="point.id" 
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="章节">
                <el-select v-model="selectedChapter" @change="applyFilters">
                  <el-option label="全部" value="" />
                  <el-option label="第一章" value="chapter1" />
                  <el-option label="第二章" value="chapter2" />
                  <el-option label="第三章" value="chapter3" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <!-- 雷达图 -->
        <el-card class="radar-card" shadow="never">
          <RadarChart :students="students" />
        </el-card>
      </el-aside>

      <!-- 右侧学生群体数据表格 -->
      <el-main class="data-main">
        <div class="data-header">
          <h3>学生学情数据</h3>
          <div class="data-actions">
            <el-button @click="refreshData" :icon="Refresh">刷新数据</el-button>
            <el-button @click="exportData" :icon="Download">导出数据</el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <el-card class="table-card" shadow="never">
          <el-table 
            :data="filteredStudents" 
            style="width: 100%"
            stripe
            border
            height="600"
          >
            <el-table-column prop="id" label="学号" width="120" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="class" label="班级" width="100" />
            
            <!-- 知识点得分列 -->
            <el-table-column label="知识点得分" min-width="200">
              <template #default="scope">
                <div class="score-summary">
                  <span 
                    v-for="(item, index) in getLowestScores(scope.row.knowledge_scores)" 
                    :key="index"
                    class="score-tag"
                    :class="{ 'weak': item.score < 70 }"
                  >
                    {{ item.knowledge_point_name }} {{ item.score }}%
                  </span>
                  <span v-if="scope.row.knowledge_scores.length > 2" class="more-indicator">
                    +{{ scope.row.knowledge_scores.length - 2 }}项
                  </span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="total_questions" label="完成题目" width="100" />
            <el-table-column prop="correct_rate" label="正确率" width="100">
              <template #default="scope">
                <el-tag :type="getCorrectRateType(scope.row.correct_rate)">
                  {{ scope.row.correct_rate }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_active" label="最后活跃" width="150" />
            
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button size="small" @click="viewStudentDetail(scope.row)">
                    查看详情
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="students.length"
              layout="total, sizes, prev, pager, next, jumper"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>


    <!-- 学生详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="学生详细信息" 
      width="600px"
      :before-close="() => { detailDialogVisible = false; studentDetail = null; }"
    >
      <div v-if="studentDetail" class="student-detail-content">
        <div class="basic-info">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">姓名:</span>
              <span class="value">{{ studentDetail.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">学号:</span>
              <span class="value">{{ studentDetail.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">班级:</span>
              <span class="value">{{ studentDetail.class }}</span>
            </div>
            <div class="info-item">
              <span class="label">完成题目:</span>
              <span class="value">{{ studentDetail.total_questions }}题</span>
            </div>
            <div class="info-item">
              <span class="label">正确率:</span>
              <span class="value">{{ studentDetail.correct_rate }}%</span>
            </div>
            <div class="info-item">
              <span class="label">最后活跃:</span>
              <span class="value">{{ studentDetail.last_active }}</span>
            </div>
          </div>
        </div>
        
        <div class="knowledge-scores">
          <h4>知识点掌握详情</h4>
          <div class="score-detail-list">
            <div 
              v-for="kp in studentDetail.knowledge_scores" 
              :key="kp.knowledge_point_id"
              class="score-detail-item"
            >
              <div class="score-detail-header">
                <span class="knowledge-name">{{ kp.knowledge_point_name }}</span>
                <el-tag 
                  :type="getScoreTagType(kp.score)"
                  size="small"
                >
                  {{ kp.score }}分
                </el-tag>
              </div>
              <el-progress 
                :percentage="kp.score" 
                :stroke-width="6"
                :color="getProgressColor(kp.score)"
                :show-text="false"
              />
              <div v-if="kp.score < 70" class="weakness-note">
                <el-icon><Warning /></el-icon>
                <span>薄弱知识点，建议重点练习</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Odometer, Filter, Refresh, Download, Warning } from '@element-plus/icons-vue';
import RadarChart from '../components/RadarChart.vue';
import { teacherApi } from '../api/teacher';

const router = useRouter();

// 响应式数据
const selectedKnowledge = ref('');
const selectedChapter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);


// 学生详情对话框相关数据
const detailDialogVisible = ref(false);
const studentDetail = ref<any>(null);

// 统计数据
const totalStudents = ref(0);
const completedQuestions = ref(0);
const averageScore = ref(0);
const activeStudents = ref(0);

// 知识点数据
const knowledgePoints = ref<any[]>([]);

// 学生数据
const students = ref<any[]>([]);

// 加载状态
const loading = ref(false);

// 计算属性
const filteredStudents = computed(() => {
  let filtered = students.value;
  
  // 根据筛选条件过滤数据
  if (selectedKnowledge.value) {
    filtered = filtered.filter(student => 
      student.knowledge_scores.some((kp: any) => kp.knowledge_point_id === selectedKnowledge.value)
    );
  }
  
  // 返回分页数据
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filtered.slice(start, end);
});

// 方法
const getCorrectRateType = (rate: number) => {
  if (rate >= 80) return 'success';
  if (rate >= 60) return 'warning';
  return 'danger';
};

const applyFilters = () => {
  currentPage.value = 1;
  ElMessage.success('筛选条件已应用');
};

const refreshData = async () => {
  loading.value = true;
  try {
    await loadAllData();
    ElMessage.success('数据已刷新');
  } catch (error) {
    ElMessage.error('数据刷新失败');
  } finally {
    loading.value = false;
  }
};

const exportData = async () => {
  try {
    const blob = await teacherApi.exportStudentData('csv');
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'students_data.csv';
    link.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success('数据导出成功');
  } catch (error) {
    ElMessage.error('数据导出失败');
  }
};

const viewStudentDetail = (student: any) => {
  studentDetail.value = student;
  detailDialogVisible.value = true;
};

const getProgressColor = (score: number) => {
  if (score >= 80) return '#67C23A';
  if (score >= 70) return '#409EFF';
  if (score >= 60) return '#E6A23C'; 
  return '#F56C6C';
};

const getLowestScores = (knowledgeScores: any[]) => {
  if (!knowledgeScores || knowledgeScores.length === 0) {
    return [];
  }
  
  // 按分数从低到高排序，取前两个
  return knowledgeScores
    .sort((a, b) => a.score - b.score)
    .slice(0, 2);
};



const getScoreTagType = (score: number) => {
  if (score >= 80) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
};




const logout = () => {
  localStorage.removeItem('userToken');
  localStorage.removeItem('userRole');
  localStorage.removeItem('username');
  router.push('/login');
};

// 数据加载方法
const loadAllData = async () => {
  try {
    // 并行加载所有数据
    const [statsData, studentsData, knowledgePointsData] = await Promise.all([
      teacherApi.getOverallStats(),
      teacherApi.getAllStudents(),
      teacherApi.getKnowledgePoints()
    ]);
    
    // 更新统计数据
    const stats = statsData.data;
    totalStudents.value = stats.total_students;
    completedQuestions.value = stats.total_questions;
    averageScore.value = stats.average_score;
    activeStudents.value = stats.active_students;
    
    // 更新学生数据
    students.value = studentsData.map(student => ({
      ...student,
      class: student.grade || '未知班级', // 使用grade字段作为班级
      scores: student.knowledge_scores.map((kp: any) => kp.score) // 提取分数数组用于雷达图
    }));
    
    // 更新知识点数据
    knowledgePoints.value = knowledgePointsData;
    
    console.log('教师端数据加载完成:', {
      stats: stats,
      studentsCount: students.value.length,
      knowledgePointsCount: knowledgePoints.value.length
    });
    
  } catch (error) {
    console.error('加载教师端数据失败:', error);
    ElMessage.error('数据加载失败，请检查网络连接');
  }
};

onMounted(() => {
  // 初始化数据
  loadAllData();
});
</script>

<style scoped>
.teacher-layout {
  width: 100vw;
  height: 100vh;
  background: #f5f7fa;
}

.teacher-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-content h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-container {
  height: calc(100vh - 60px);
}

.stats-aside {
  background: transparent;
  padding: 20px 10px 20px 10px;
}

.stats-overview {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-content {
  padding: 8px 0;
}

.radar-card {
  border-radius: 12px;
  height: 400px;
}

.data-main {
  padding: 20px 30px 30px 20px;
  background: transparent;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.data-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.data-actions {
  display: flex;
  gap: 12px;
}

.table-card {
  border-radius: 12px;
}

.score-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  font-size: 12px;
  color: #6c757d;
  min-width: 60px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}


.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-buttons .el-button {
  width: 100%;
  margin: 0;
}

.score-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.score-tag {
  display: inline-block;
  padding: 2px 8px;
  background: #e8f4fd;
  color: #409eff;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
}

.score-tag.weak {
  background: #fef0f0;
  color: #f56c6c;
}

.more-indicator {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

.student-detail-content {
  padding: 16px 0;
}

.basic-info {
  margin-bottom: 24px;
}

.basic-info h4,
.knowledge-scores h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 16px;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.info-item .value {
  color: #303133;
}

.score-detail-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-detail-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.score-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.knowledge-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.weakness-note {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 12px;
  color: #f56c6c;
}

.weakness-note .el-icon {
  font-size: 14px;
}
</style>
