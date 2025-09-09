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
                    v-for="(item, index) in getLowestScores(scope.row.scores)" 
                    :key="index"
                    class="score-tag"
                    :class="{ 'weak': item.score < 70 }"
                  >
                    {{ item.name }} {{ item.score }}%
                  </span>
                  <span v-if="scope.row.scores.length > 2" class="more-indicator">
                    +{{ scope.row.scores.length - 2 }}项
                  </span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="totalQuestions" label="完成题目" width="100" />
            <el-table-column prop="correctRate" label="正确率" width="100">
              <template #default="scope">
                <el-tag :type="getCorrectRateType(scope.row.correctRate)">
                  {{ scope.row.correctRate }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastActive" label="最后活跃" width="150" />
            
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button size="small" @click="viewStudentDetail(scope.row)">
                    查看详情
                  </el-button>
                  <el-button size="small" type="primary" @click="changeRecommendDirection(scope.row)">
                    更改推荐方向
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

    <!-- 推荐方向选择对话框 -->
    <el-dialog
      v-model="recommendDialogVisible"
      title="更改推荐方向"
      width="600px"
      :before-close="handleDialogClose"
    >
      <div class="recommend-dialog-content">
        <div class="student-info">
          <h4>学生信息</h4>
          <p><strong>姓名：</strong>{{ selectedStudent?.name }}</p>
          <p><strong>学号：</strong>{{ selectedStudent?.id }}</p>
          <p><strong>班级：</strong>{{ selectedStudent?.class }}</p>
        </div>
        
        <el-divider />
        
        <div class="knowledge-selection">
          <h4>选择推荐的知识点方向</h4>
          <p class="selection-hint">请根据学生的学习情况选择需要加强的知识点：</p>
          
          <div class="knowledge-grid">
            <div 
              v-for="(point, index) in knowledgePoints" 
              :key="point.id"
              class="knowledge-option"
              :class="{ 
                'selected': selectedKnowledgePoints.includes(point.id),
                'weak-point': selectedStudent && selectedStudent.scores[index] < 70
              }"
              @click="toggleKnowledgePoint(point.id)"
            >
              <div class="option-header">
                <el-checkbox 
                  :model-value="selectedKnowledgePoints.includes(point.id)"
                  @change="toggleKnowledgePoint(point.id)"
                />
                <span class="knowledge-name">{{ point.name }}</span>
              </div>
              <div class="current-score" v-if="selectedStudent">
                <span>当前得分：</span>
                <el-tag 
                  :type="getScoreTagType(selectedStudent.scores[index])"
                  size="small"
                >
                  {{ selectedStudent.scores[index] }}分
                </el-tag>
              </div>
              <div class="weak-indicator" v-if="selectedStudent && selectedStudent.scores[index] < 70">
                <el-icon color="#F56C6C"><Warning /></el-icon>
                <span>薄弱知识点</span>
              </div>
            </div>
          </div>
          
          <div class="priority-setting" v-if="selectedKnowledgePoints.length > 0">
            <h5>设置推荐优先级</h5>
            <el-radio-group v-model="recommendPriority">
              <el-radio value="high">高优先级 - 优先推荐相关题目</el-radio>
              <el-radio value="medium">中优先级 - 适量推荐相关题目</el-radio>
              <el-radio value="low">低优先级 - 少量推荐相关题目</el-radio>
            </el-radio-group>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmRecommendDirection"
            :disabled="selectedKnowledgePoints.length === 0"
          >
            确定更改
          </el-button>
        </div>
      </template>
    </el-dialog>

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
              <span class="value">{{ studentDetail.totalQuestions }}题</span>
            </div>
            <div class="info-item">
              <span class="label">正确率:</span>
              <span class="value">{{ studentDetail.correctRate }}%</span>
            </div>
            <div class="info-item">
              <span class="label">最后活跃:</span>
              <span class="value">{{ studentDetail.lastActive }}</span>
            </div>
          </div>
        </div>
        
        <div class="knowledge-scores">
          <h4>知识点掌握详情</h4>
          <div class="score-detail-list">
            <div 
              v-for="(score, index) in studentDetail.scores" 
              :key="index"
              class="score-detail-item"
            >
              <div class="score-detail-header">
                <span class="knowledge-name">{{ knowledgePoints[index]?.name }}</span>
                <el-tag 
                  :type="getScoreTagType(score)"
                  size="small"
                >
                  {{ score }}分
                </el-tag>
              </div>
              <el-progress 
                :percentage="score" 
                :stroke-width="6"
                :color="getProgressColor(score)"
                :show-text="false"
              />
              <div v-if="score < 70" class="weakness-note">
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

const router = useRouter();

// 响应式数据
const selectedKnowledge = ref('');
const selectedChapter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);

// 推荐方向对话框相关数据
const recommendDialogVisible = ref(false);
const selectedStudent = ref<any>(null);
const selectedKnowledgePoints = ref<string[]>([]);
const recommendPriority = ref('medium');

// 学生详情对话框相关数据
const detailDialogVisible = ref(false);
const studentDetail = ref<any>(null);

// 统计数据
const totalStudents = ref(45);
const completedQuestions = ref(1284);
const averageScore = ref(78);
const activeStudents = ref(32);

// 知识点数据
const knowledgePoints = ref([
  { id: 'basic', name: '图的基本概念' },
  { id: 'euler', name: '欧拉图' },
  { id: 'hamilton', name: '哈密顿图' },
  { id: 'tree', name: '树' },
  { id: 'planar', name: '平面图' },
  { id: 'coloring', name: '着色' }
]);

// 学生数据
const students = ref([
  {
    id: '1120220001',
    name: '张三',
    class: '08012201',
    scores: [85, 78, 92, 67, 89, 74],
    totalQuestions: 45,
    correctRate: 78,
    lastActive: '2024-08-29 14:30'
  },
  {
    id: '1120220002', 
    name: '李四',
    class: '08012201',
    scores: [72, 85, 69, 78, 83, 76],
    totalQuestions: 38,
    correctRate: 82,
    lastActive: '2024-08-29 13:45'
  },
  {
    id: '1120220003',
    name: '王五', 
    class: '08012202',
    scores: [90, 88, 85, 92, 87, 91],
    totalQuestions: 52,
    correctRate: 89,
    lastActive: '2024-08-29 15:20'
  },
  {
    id: '1120220004',
    name: '赵六',
    class: '08012202', 
    scores: [65, 70, 75, 68, 71, 69],
    totalQuestions: 35,
    correctRate: 65,
    lastActive: '2024-08-28 16:10'
  },
  {
    id: '1120220005',
    name: '钱七',
    class: '08012201',
    scores: [88, 85, 90, 83, 86, 84],
    totalQuestions: 48,
    correctRate: 85,
    lastActive: '2024-08-29 12:30'
  }
]);

// 计算属性
const filteredStudents = computed(() => {
  let filtered = students.value;
  
  // 这里可以根据筛选条件过滤数据
  // 目前返回分页数据
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

const refreshData = () => {
  ElMessage.success('数据已刷新');
};

const exportData = () => {
  ElMessage.success('数据导出中...');
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

const getLowestScores = (scores: number[]) => {
  // 创建包含分数和对应知识点名称的数组
  const scoreItems = scores.map((score, index) => ({
    score,
    name: knowledgePoints.value[index]?.name || `知识点${index + 1}`,
    index
  }));
  
  // 按分数从低到高排序，取前两个
  return scoreItems
    .sort((a, b) => a.score - b.score)
    .slice(0, 2);
};

const changeRecommendDirection = (student: any) => {
  selectedStudent.value = student;
  selectedKnowledgePoints.value = [];
  recommendPriority.value = 'medium';
  recommendDialogVisible.value = true;
};

const toggleKnowledgePoint = (pointId: string) => {
  const index = selectedKnowledgePoints.value.indexOf(pointId);
  if (index > -1) {
    selectedKnowledgePoints.value.splice(index, 1);
  } else {
    selectedKnowledgePoints.value.push(pointId);
  }
};

const getScoreTagType = (score: number) => {
  if (score >= 80) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
};

const handleDialogClose = () => {
  recommendDialogVisible.value = false;
  selectedStudent.value = null;
  selectedKnowledgePoints.value = [];
};

const confirmRecommendDirection = () => {
  const knowledgeNames = selectedKnowledgePoints.value
    .map(id => knowledgePoints.value.find(point => point.id === id)?.name)
    .join('、');
  
  ElMessage.success(`已为学生 ${selectedStudent.value.name} 设置推荐方向：${knowledgeNames}，优先级：${recommendPriority.value}`);
  handleDialogClose();
};

const logout = () => {
  localStorage.removeItem('userToken');
  localStorage.removeItem('userRole');
  localStorage.removeItem('username');
  router.push('/login');
};

onMounted(() => {
  // 初始化数据
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

/* 推荐方向对话框样式 */
.recommend-dialog-content {
  padding: 20px 0;
}

.student-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.student-info h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 16px;
}

.student-info p {
  margin: 8px 0;
  color: #495057;
}

.knowledge-selection h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 16px;
}

.selection-hint {
  color: #6c757d;
  margin-bottom: 20px;
  font-size: 14px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.knowledge-option {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.knowledge-option:hover {
  border-color: #409EFF;
  background: #f0f9ff;
}

.knowledge-option.selected {
  border-color: #409EFF;
  background: #e3f2fd;
}

.knowledge-option.weak-point {
  border-color: #F56C6C;
  background: #fef2f2;
}

.knowledge-option.weak-point.selected {
  border-color: #F56C6C;
  background: #fee2e2;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.knowledge-name {
  font-weight: 600;
  color: #2c3e50;
}

.current-score {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #6c757d;
}

.weak-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #F56C6C;
}

.priority-setting {
  margin-top: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.priority-setting h5 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
