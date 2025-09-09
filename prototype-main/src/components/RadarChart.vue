<template>
  <div class="radar-chart-container">
    <div class="chart-header">
      <h4>{{ title }}</h4>
      <div class="chart-controls">
        <el-select v-model="selectedStudent" @change="updateChart" style="width: 150px">
          <el-option label="班级平均" value="average" />
          <el-option 
            v-for="student in students" 
            :key="student.id"
            :label="student.name" 
            :value="student.id" 
          />
        </el-select>
      </div>
    </div>
    <div id="radar-chart" class="chart-content"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';

interface Student {
  id: string;
  name: string;
  scores: number[];
}

interface Props {
  title?: string;
  students?: Student[];
}

const props = withDefaults(defineProps<Props>(), {
  title: '知识点掌握度分析',
  students: () => [
    { id: '001', name: '张三', scores: [85, 78, 92, 67, 89, 74] },
    { id: '002', name: '李四', scores: [72, 85, 69, 78, 83, 76] },
    { id: '003', name: '王五', scores: [90, 88, 85, 92, 87, 91] }
  ]
});

const selectedStudent = ref('average');
let chartInstance: echarts.ECharts | null = null;

// 知识点标签
const knowledgeLabels = [
  '图的基本概念',
  '欧拉图',
  '哈密顿图',
  '树',
  '平面图',
  '着色'
];

// 计算班级平均分
const getAverageScores = () => {
  const sums = new Array(knowledgeLabels.length).fill(0);
  props.students.forEach(student => {
    student.scores.forEach((score, index) => {
      sums[index] += score;
    });
  });
  return sums.map(sum => Math.round(sum / props.students.length));
};

const initChart = () => {
  const chartElement = document.getElementById('radar-chart');
  if (!chartElement) return;
  
  chartInstance = echarts.init(chartElement);
  updateChart();
};

const updateChart = () => {
  if (!chartInstance) return;
  
  let data: number[];
  let seriesName: string;
  
  if (selectedStudent.value === 'average') {
    data = getAverageScores();
    seriesName = '班级平均';
  } else {
    const student = props.students.find(s => s.id === selectedStudent.value);
    data = student ? student.scores : getAverageScores();
    seriesName = student ? student.name : '班级平均';
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params: any) {
        return `${params.name}: ${params.value}分`;
      }
    },
    radar: {
      indicator: knowledgeLabels.map(label => ({
        name: label,
        max: 100,
        min: 0
      })),
      axisName: {
        fontSize: 13,
        color: '#666',
        padding: [0, 0, 0, 0],
        lineHeight: 16,
        overflow: 'none'
      },
      splitLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLine: {
        lineStyle: {
          color: '#ccc'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(255, 255, 255, 0)', 'rgba(0, 0, 0, 0.05)']
        }
      }
    },
    series: [{
      name: seriesName,
      type: 'radar',
      data: [{
        value: data,
        name: seriesName,
        areaStyle: {
          opacity: 0.3,
          color: selectedStudent.value === 'average' ? '#409EFF' : '#67C23A'
        },
        lineStyle: {
          color: selectedStudent.value === 'average' ? '#409EFF' : '#67C23A',
          width: 2
        },
        itemStyle: {
          color: selectedStudent.value === 'average' ? '#409EFF' : '#67C23A'
        }
      }]
    }],
    color: [selectedStudent.value === 'average' ? '#409EFF' : '#67C23A']
  };
  
  chartInstance.setOption(option);
};

onMounted(() => {
  initChart();
});

watch(() => props.students, () => {
  updateChart();
}, { deep: true });
</script>

<style scoped>
.radar-chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 0 16px;
}

.chart-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.chart-content {
  flex: 1;
  min-height: 300px;
}

#radar-chart {
  width: 100%;
  height: 100%;
}
</style>
