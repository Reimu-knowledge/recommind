<template>
  <div class="student-layout">
    <el-header class="student-header">
      <div class="header-content">
        <h2>CSrecomMIND</h2>
        <div class="header-actions">
          <el-button type="primary" @click="logout">退出登录</el-button>
        </div>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 左侧导航栏 -->
      <el-aside width="300px" class="knowledge-aside">
        <!-- 智能推荐 -->
        <el-card class="smart-recommend-card clickable-card" :class="{ active: currentView === 'smart' }" shadow="never" @click="currentView = 'smart'">
          <template #header>
            <div class="nav-header">
              <el-icon><MagicStick /></el-icon>
              <span>智能推荐</span>
            </div>
          </template>
          
          <div class="recommend-content">
            <p class="recommend-desc">基于您的学习情况，为您智能推荐练习题目</p>
            <el-button 
              type="primary" 
              @click.stop="refreshSmartRecommendations"
              :loading="recommendLoading"
              class="recommend-btn"
            >
              重新获取推荐题目
            </el-button>
          </div>
        </el-card>

        <!-- 薄弱知识点导航 -->
        <el-card class="weak-points-card clickable-card" :class="{ active: currentView === 'weak' }" shadow="never">
          <template #header>
            <div class="nav-header">
              <el-icon><Warning /></el-icon>
              <span>薄弱知识点导航</span>
            </div>
          </template>
          
          <div class="weak-points-list">
            <div 
              v-for="point in weakKnowledgePoints" 
              :key="point.id"
              class="weak-point-item"
              @click="selectWeakPoint(point)"
            >
              <div class="weak-point-info">
                <h4>{{ point.name }}</h4>
                <p>{{ point.description }}</p>
              </div>
              <div class="weak-point-score">
                <el-progress 
                  :percentage="point.score" 
                  :stroke-width="6"
                  :show-text="false"
                  color="#F56C6C"
                />
                <span class="score-text">{{ point.score }}%</span>
              </div>
            </div>
            
            <!-- 空状态 -->
            <div v-if="weakKnowledgePoints.length === 0" class="empty-weak-points">
              <el-icon><CircleCheck /></el-icon>
              <p>暂无薄弱知识点</p>
            </div>
          </div>
        </el-card>

        <!-- 知识图谱 -->
        <el-card class="graph-card clickable-card" :class="{ active: currentView === 'graph' }" shadow="never">
          <template #header>
            <div class="nav-header">
              <el-icon><TrendCharts /></el-icon>
              <span>知识图谱</span>
            </div>
          </template>
          <div @click="currentView = 'graph'">
            <KnowledgeGraph />
          </div>
        </el-card>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="questions-main">
        <!-- 智能推荐内容 -->
        <div v-if="currentView === 'smart'" class="smart-content">
          <div class="questions-header">
            <h3>智能推荐</h3>
          </div>
          <div class="questions-container">
            <QuestionCard 
              v-for="question in smartRecommendedQuestions" 
              :key="question.id"
              :question="question"
              @answer-submitted="handleAnswerSubmitted"
            />
            <el-empty 
              v-if="smartRecommendedQuestions.length === 0"
              description="暂无智能推荐题目"
              :image-size="120"
            />
          </div>
        </div>

        <!-- 薄弱知识点内容 -->
        <div v-else-if="currentView === 'weak'" class="weak-content">
          <div class="questions-header">
            <h3>{{ selectedWeakPoint ? selectedWeakPoint.name + ' 强化' : '薄弱知识点强化' }}</h3>
          </div>
          <div class="questions-container">
            <QuestionCard 
              v-for="question in weakPointQuestions" 
              :key="question.id"
              :question="question"
              @answer-submitted="handleAnswerSubmitted"
            />
            <el-empty 
              v-if="weakPointQuestions.length === 0"
              description="暂无薄弱知识点题目"
              :image-size="120"
            />
          </div>
        </div>

        <!-- 知识图谱内容 -->
        <div v-else-if="currentView === 'graph'" class="graph-content">
          <div class="questions-header">
            <h3>知识图谱</h3>
          </div>
          <div class="questions-container">
            <LargeKnowledgeGraph />
          </div>
        </div>

        <!-- 默认题目推荐 -->
        <div v-else class="default-content">
          <div class="questions-header">
            <h3>个性化题目推荐</h3>
            <div class="filter-controls">
              <el-button @click="refreshQuestions" :icon="Refresh">刷新题目</el-button>
            </div>
          </div>
          <div class="questions-container">
            <QuestionCard 
              v-for="question in filteredQuestions" 
              :key="question.id"
              :question="question"
              @answer-submitted="handleAnswerSubmitted"
            />
            <el-empty 
              v-if="filteredQuestions.length === 0"
              description="暂无推荐题目"
              :image-size="120"
            />
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Refresh, TrendCharts, MagicStick, Warning, CircleCheck } from '@element-plus/icons-vue';
import KnowledgeGraph from '../components/KnowledgeGraph.vue';
import QuestionCard from '../components/QuestionCard.vue';
import LargeKnowledgeGraph from '../components/LargeKnowledgeGraph.vue';
import { studentApi } from '../api/student';
import { auth } from '../utils/auth';

const router = useRouter();

// 响应式数据
const recommendLoading = ref(false);
const weakPointLoading = ref(false);
const currentView = ref('default'); // 'default', 'smart', 'weak', 'graph'
const selectedWeakPoint = ref<any>(null); // 当前选中的薄弱知识点
const currentStudentId = ref(''); // 当前学生ID
const currentSessionId = ref<number | null>(null); // 当前学习会话ID

// 薄弱知识点数据
const weakKnowledgePoints = ref<any[]>([]);

// 题目数据
const questions = ref<any[]>([]);
const smartRecommendedQuestions = ref<any[]>([]);

// 计算属性
const filteredQuestions = computed(() => {
  return questions.value;
});

// 薄弱知识点题目  
const weakPointQuestions = computed(() => {
  // 直接返回通过selectWeakPoint获取的题目
  return questions.value;
});

const handleAnswerSubmitted = (result: any) => {
  console.log('答题结果:', result);
  // TODO: 更新知识点掌握度
};

const refreshQuestions = () => {
  ElMessage.success('题目已刷新');
  // TODO: 从后端获取新的推荐题目
};

const refreshSmartRecommendations = async () => {
  if (!currentStudentId.value) {
    ElMessage.error('学生ID不存在，请重新登录');
    return;
  }
  
  recommendLoading.value = true;
  ElMessage.info('正在重新获取智能推荐题目...');
  
  try {
    const recommendedQuestions = await studentApi.getRecommendedQuestions(currentStudentId.value);
    smartRecommendedQuestions.value = recommendedQuestions;
    ElMessage.success('已为您重新推荐合适的题目！');
    currentView.value = 'smart';
  } catch (error) {
    console.error('获取智能推荐失败:', error);
    ElMessage.error('获取推荐题目失败，请重试');
  } finally {
    recommendLoading.value = false;
  }
};

const selectWeakPoint = async (point: any) => {
  if (!currentStudentId.value) {
    ElMessage.error('学生ID不存在，请重新登录');
    return;
  }
  
  weakPointLoading.value = true;
  selectedWeakPoint.value = point;
  ElMessage.info(`正在获取"${point.name}"的专项练习题目...`);
  
  try {
    // 根据知识点ID获取相关题目
    const relatedQuestions = await studentApi.getQuestionsByKnowledgePoint(point.id);
    questions.value = relatedQuestions;
    ElMessage.success(`已获取"${point.name}"的${relatedQuestions.length}道练习题目！`);
    currentView.value = 'weak';
  } catch (error) {
    console.error('获取薄弱知识点题目失败:', error);
    ElMessage.error('获取专项练习题目失败，请重试');
  } finally {
    weakPointLoading.value = false;
  }
};

const logout = () => {
  localStorage.removeItem('userToken');
  localStorage.removeItem('userRole');
  localStorage.removeItem('username');
  router.push('/login');
};

// 初始化学生数据
const initializeStudent = async () => {
  const user = auth.getUser();
  if (!user) {
    ElMessage.error('用户未登录');
    router.push('/login');
    return;
  }
  
  currentStudentId.value = user.username;
  
  try {
    // 检查学生是否存在，如果不存在则创建
    try {
      await studentApi.getStudentInfo(currentStudentId.value);
    } catch (error) {
      // 学生不存在，创建新学生
      ElMessage.info('正在创建学生档案...');
      await studentApi.createStudent({
        id: currentStudentId.value,
        name: user.username,
        grade: '大学'
      });
      ElMessage.success('学生档案创建成功！');
    }
    
    // 开始学习会话
    const session = await studentApi.startLearningSession(currentStudentId.value, '学习会话');
    currentSessionId.value = session.id;
    
    // 获取薄弱知识点
    await loadWeakKnowledgePoints();
    
    // 获取初始推荐题目
    await loadInitialQuestions();
    
  } catch (error) {
    console.error('初始化学生数据失败:', error);
    ElMessage.error('初始化失败，请刷新页面重试');
  }
};

// 加载薄弱知识点
const loadWeakKnowledgePoints = async () => {
  try {
    const weakPoints = await studentApi.getWeakKnowledgePoints(currentStudentId.value);
    weakKnowledgePoints.value = weakPoints;
  } catch (error) {
    console.error('获取薄弱知识点失败:', error);
    ElMessage.warning('获取薄弱知识点失败');
  }
};

// 加载初始题目
const loadInitialQuestions = async () => {
  try {
    const recommendedQuestions = await studentApi.getRecommendedQuestions(currentStudentId.value);
    questions.value = recommendedQuestions;
    smartRecommendedQuestions.value = recommendedQuestions.slice(0, 3);
  } catch (error) {
    console.error('获取推荐题目失败:', error);
    ElMessage.warning('获取推荐题目失败');
  }
};

onMounted(() => {
  initializeStudent();
});
</script>

<style scoped>
.student-layout {
  width: 100vw;
  height: 100vh;
  background: #f5f7fa;
}

.student-header {
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

.knowledge-aside {
  background: transparent;
  padding: 20px 10px 20px 10px;
}

.smart-recommend-card {
  margin-bottom: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.smart-recommend-card.active {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.weak-points-card {
  margin-bottom: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.weak-points-card.active {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.graph-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.graph-card.active {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.nav-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.recommend-content {
  text-align: center;
  padding: 16px;
  margin: -16px;
  border-radius: 8px;
}

.recommend-desc {
  color: #6c757d;
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.recommend-btn {
  width: 100%;
}

.recommend-btn:focus {
  outline: none !important;
  box-shadow: none !important;
}

.weak-points-list {
  max-height: 300px;
  overflow-y: auto;
}

.weak-point-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #fef2f2;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #fecaca;
}

.weak-point-item:hover {
  background: #fee2e2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
}

.weak-point-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #dc2626;
}

.weak-point-info p {
  margin: 0;
  font-size: 12px;
  color: #7f1d1d;
  line-height: 1.4;
}

.weak-point-score {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-text {
  font-size: 12px;
  color: #dc2626;
  font-weight: 600;
  min-width: 35px;
}

.empty-weak-points {
  text-align: center;
  padding: 32px 16px;
  color: #6c757d;
}

.empty-weak-points .el-icon {
  font-size: 48px;
  color: #67C23A;
  margin-bottom: 16px;
}

.empty-weak-points p {
  margin: 0;
  font-size: 14px;
}

.graph-card {
  border-radius: 12px;
  height: 450px;
}

.clickable-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.questions-main {
  padding: 20px 30px 30px 20px;
  background: transparent;
}

.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 4px;
}

.questions-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.questions-container {
  max-height: calc(100vh - 140px);
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.questions-container::-webkit-scrollbar {
  width: 6px;
}

.questions-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.questions-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.questions-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
