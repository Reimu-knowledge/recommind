<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>CSrecomMIND</h1>
        <p>基于知识图谱的学习推荐系统</p>
      </div>
      
      <el-card class="login-card" shadow="always">
        <template #header>
          <div class="card-header">
            <span>用户登录</span>
          </div>
        </template>
        
        <el-form :model="loginForm" :rules="rules" ref="loginFormRef" size="large">
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名"
              prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="role">
            <div class="role-buttons">
              <div 
                class="role-button" 
                :class="{ active: loginForm.role === 'student' }"
                @click="loginForm.role = 'student'"
              >
                <el-icon><UserFilled /></el-icon>
                <span>学生</span>
              </div>
              <div 
                class="role-button" 
                :class="{ active: loginForm.role === 'teacher' }"
                @click="loginForm.role = 'teacher'"
              >
                <el-icon><Avatar /></el-icon>
                <span>教师</span>
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-btn"
              @click="handleLogin"
              :loading="loading"
              size="large"
            >
              登录系统
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { UserFilled, Avatar } from '@element-plus/icons-vue';

const router = useRouter();
const loading = ref(false);
const loginFormRef = ref();

const loginForm = reactive({
  username: '',
  password: '',
  role: 'student'
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  await loginFormRef.value.validate((valid: boolean) => {
    if (valid) {
      loading.value = true;
      
      // 模拟登录延迟
      setTimeout(() => {
        // 设置认证状态
        localStorage.setItem('userToken', 'mock-token-' + Date.now());
        localStorage.setItem('userRole', loginForm.role);
        localStorage.setItem('username', loginForm.username);
        
        ElMessage.success('登录成功！');
        
        // 根据角色跳转
        if (loginForm.role === 'student') {
          router.push('/student');
        } else {
          router.push('/teacher');
        }
        
        loading.value = false;
      }, 1000);
    } else {
      ElMessage.error('请填写完整信息');
    }
  });
};
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #f5f7fa;
}

.login-box {
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #2c3e50;
}

.login-header p {
  font-size: 16px;
  color: #6c757d;
}

.login-card {
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.role-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
}

.role-button {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.role-button:hover {
  border-color: #409eff;
  color: #409eff;
}

.role-button.active {
  border-color: #409eff;
  background: #ecf5ff;
  color: #409eff;
}

.role-button .el-icon {
  font-size: 16px;
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}
</style>
