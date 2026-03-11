<template>
  <div id="app">
    <el-container>
      <!-- 头部 -->
      <el-header>
        <h1>📋 DemandTest Platform</h1>
        <p>需求提取与测试用例生成平台</p>
      </el-header>

      <!-- 主内容 -->
      <el-main>
        <!-- 步骤条 -->
        <el-steps :active="activeStep" finish-status="success" align-center>
          <el-step title="提交URL" description="输入原型链接"></el-step>
          <el-step title="爬取页面" description="提取目录结构"></el-step>
          <el-step title="选择需求" description="勾选需要的内容"></el-step>
          <el-step title="生成用例" description="自动生成测试用例"></el-step>
          <el-step title="导出文件" description="下载Excel文件"></el-step>
        </el-steps>

        <!-- Step 1: 提交URL -->
        <div v-if="activeStep === 0" class="step-content">
          <el-card>
            <template #header>
              <span>📥 提交原型链接</span>
            </template>
            <el-form :model="form" label-width="100px">
              <el-form-item label="原型链接">
                <el-input 
                  v-model="form.url" 
                  placeholder="请输入墨刀/蓝湖/Axure等平台分享链接"
                  size="large"
                  clearable
                >
                  <template #append>
                    <el-button type="primary" @click="crawlUrl" :loading="crawling">
                      {{ crawling ? '爬取中...' : '开始爬取' }}
                    </el-button>
                  </template>
                </el-input>
              </el-form-item>
            </el-form>

            <!-- 支持平台 -->
            <el-divider>支持平台</el-divider>
            <el-space wrap>
              <el-tag>墨刀</el-tag>
              <el-tag>蓝湖</el-tag>
              <el-tag>Axure</el-tag>
              <el-tag>Figma</el-tag>
              <el-tag>幕客</el-tag>
              <el-tag>即时设计</el-tag>
            </el-space>
          </el-card>
        </div>

        <!-- Step 2: 爬取结果 -->
        <div v-if="activeStep === 1" class="step-content">
          <el-card>
            <template #header>
              <span>📊 爬取结果</span>
            </template>
            
            <!-- 统计信息 -->
            <el-descriptions :column="3" border>
              <el-descriptions-item label="期望页面数">{{ crawlResult.expected }}</el-descriptions-item>
              <el-descriptions-item label="提取页面数">{{ crawlResult.extracted }}</el-descriptions-item>
              <el-descriptions-item label="匹配率">
                <el-tag :type="parseFloat(crawlResult.match_rate) >= 90 ? 'success' : 'warning'">
                  {{ crawlResult.match_rate }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 页面列表 -->
            <el-divider>页面目录</el-divider>
            <el-tree
              ref="treeRef"
              :data="treeData"
              show-checkbox
              node-key="id"
              :default-checked-keys="checkedKeys"
              @check="handleCheck"
            >
              <template #default="{ node, data }">
                <span>
                  {{ data.name }}
                  <el-tag v-if="data.status" size="small" :type="data.status === '新增' ? 'success' : 'warning'">
                    {{ data.status }}
                  </el-tag>
                </span>
              </template>
            </el-tree>

            <!-- 操作按钮 -->
            <el-divider></el-divider>
            <el-space>
              <el-button @click="activeStep = 0">返回</el-button>
              <el-button type="primary" @click="nextStep" :disabled="checkedPages.length === 0">
                下一步：选择测试类型
              </el-button>
            </el-space>
          </el-card>
        </div>

        <!-- Step 3: 选择测试类型 -->
        <div v-if="activeStep === 2" class="step-content">
          <el-card>
            <template #header>
              <span>⚙️ 选择测试类型</span>
            </template>
            
            <el-form :model="form" label-width="100px">
              <el-form-item label="测试类型">
                <el-checkbox-group v-model="form.testTypes">
                  <el-checkbox label="positive">正向测试</el-checkbox>
                  <el-checkbox label="negative">逆向测试</el-checkbox>
                  <el-checkbox label="boundary">边界测试</el-checkbox>
                  <el-checkbox label="security">安全测试</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="优先级">
                <el-radio-group v-model="form.priority">
                  <el-radio label="P0">P0 - 最高</el-radio>
                  <el-radio label="P1">P1 - 高</el-radio>
                  <el-radio label="P2">P2 - 中</el-radio>
                  <el-radio label="P3">P3 - 低</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="选中页面">
                <el-tag v-for="page in checkedPages" :key="page.id" style="margin: 2px;">
                  {{ page.name }}
                </el-tag>
              </el-form-item>
            </el-form>

            <!-- 操作按钮 -->
            <el-divider></el-divider>
            <el-space>
              <el-button @click="activeStep = 1">返回</el-button>
              <el-button type="primary" @click="generateTestCases" :loading="generating">
                {{ generating ? '生成中...' : '生成测试用例' }}
              </el-button>
            </el-space>
          </el-card>
        </div>

        <!-- Step 4: 测试用例结果 -->
        <div v-if="activeStep === 3" class="step-content">
          <el-card>
            <template #header>
              <span>📝 测试用例（共 {{ testCases.length }} 个）</span>
            </template>
            
            <el-table :data="testCases" border stripe max-height="500">
              <el-table-column prop="id" label="用例编号" width="120"></el-table-column>
              <el-table-column prop="title" label="用例标题" width="200"></el-table-column>
              <el-table-column prop="preconditions" label="前置条件" show-overflow-tooltip></el-table-column>
              <el-table-column prop="steps" label="测试步骤" show-overflow-tooltip></el-table-column>
              <el-table-column prop="expected_results" label="预期结果" show-overflow-tooltip></el-table-column>
              <el-table-column prop="priority" label="优先级" width="80"></el-table-column>
              <el-table-column prop="type" label="类型" width="100"></el-table-column>
            </el-table>

            <!-- 操作按钮 -->
            <el-divider></el-divider>
            <el-space>
              <el-button @click="activeStep = 2">返回</el-button>
              <el-button type="success" @click="exportExcel" :loading="exporting">
                {{ exporting ? '导出中...' : '导出 Excel' }}
              </el-button>
            </el-space>
          </el-card>
        </div>
      </el-main>

      <!-- 页脚 -->
      <el-footer>
        <p>Made with ❤️ by nandujia | 
          <a href="https://github.com/nandujia/DemandTest" target="_blank">GitHub</a>
        </p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const activeStep = ref(0)
    const crawling = ref(false)
    const generating = ref(false)
    const exporting = ref(false)
    const treeRef = ref(null)
    
    const form = ref({
      url: '',
      testTypes: ['positive', 'negative'],
      priority: 'P1'
    })
    
    const crawlResult = ref({
      success: false,
      expected: 0,
      extracted: 0,
      match_rate: '0%',
      pages: []
    })
    
    const checkedKeys = ref([])
    const testCases = ref([])
    
    // 树形数据
    const treeData = computed(() => {
      return [{
        id: 'root',
        name: '全部页面',
        children: crawlResult.value.pages.map(p => ({
          id: p.id,
          name: p.name,
          status: p.status
        }))
      }]
    })
    
    // 选中的页面
    const checkedPages = computed(() => {
      return crawlResult.value.pages.filter(p => checkedKeys.value.includes(p.id))
    })
    
    // 爬取URL
    const crawlUrl = async () => {
      if (!form.value.url) {
        ElMessage.warning('请输入原型链接')
        return
      }
      
      crawling.value = true
      
      try {
        const response = await axios.post('/api/v1/crawl', {
          url: form.value.url
        })
        
        crawlResult.value = response.data
        
        if (response.data.success) {
          ElMessage.success(`爬取成功！提取 ${response.data.extracted} 个页面`)
          activeStep.value = 1
          // 默认全选
          checkedKeys.value = response.data.pages.map(p => p.id)
        } else {
          ElMessage.error(response.data.error || '爬取失败')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '爬取失败')
      } finally {
        crawling.value = false
      }
    }
    
    // 处理勾选
    const handleCheck = (data, { checkedKeys: keys }) => {
      checkedKeys.value = keys.filter(k => k !== 'root')
    }
    
    // 下一步
    const nextStep = () => {
      if (checkedPages.value.length === 0) {
        ElMessage.warning('请至少选择一个页面')
        return
      }
      activeStep.value = 2
    }
    
    // 生成测试用例
    const generateTestCases = async () => {
      generating.value = true
      
      try {
        const response = await axios.post('/api/v1/generate', {
          pages: checkedPages.value.map(p => p.name),
          types: form.value.testTypes,
          priority: form.value.priority
        })
        
        testCases.value = response.data.test_cases
        ElMessage.success(`生成 ${response.data.total} 个测试用例`)
        activeStep.value = 3
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '生成失败')
      } finally {
        generating.value = false
      }
    }
    
    // 导出Excel
    const exportExcel = async () => {
      exporting.value = true
      
      try {
        const response = await axios.post('/api/v1/export', {
          format: 'xlsx',
          test_cases: testCases.value
        }, {
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '测试用例.xlsx')
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        ElMessage.success('导出成功！')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '导出失败')
      } finally {
        exporting.value = false
      }
    }
    
    return {
      activeStep,
      crawling,
      generating,
      exporting,
      treeRef,
      form,
      crawlResult,
      checkedKeys,
      treeData,
      checkedPages,
      testCases,
      crawlUrl,
      handleCheck,
      nextStep,
      generateTestCases,
      exportExcel
    }
  }
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 20px;
}

.el-header h1 {
  margin: 0;
  font-size: 24px;
}

.el-header p {
  margin: 5px 0 0;
  opacity: 0.8;
}

.el-main {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.step-content {
  margin-top: 30px;
}

.el-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.el-footer a {
  color: #667eea;
  text-decoration: none;
}
</style>
