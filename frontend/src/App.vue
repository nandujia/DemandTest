<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <div class="brand">Testify AI</div>
          <div class="tagline">Agent 驱动的测试平台</div>
        </div>
        <div class="header-right">
          <el-button text class="icon-button" @click="page = 'settings'">⚙️</el-button>
          <el-tag v-if="showModelWarning" type="warning" class="clickable" @click="page = 'settings'">
            {{ modelWarningText }}
          </el-tag>
          <el-dropdown v-if="isAuthed" trigger="click">
            <el-tag type="success" class="clickable">{{ authUser?.username || '已登录' }}</el-tag>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="page = 'users'">用户管理</el-dropdown-item>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-tag v-else type="primary" class="clickable" @click="goLogin">Login</el-tag>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main>
        <div v-if="page === 'login'" class="auth-page">
          <el-card class="auth-card">
            <template #header>
              <span>登录</span>
            </template>
            <el-form :model="loginForm" label-width="90px">
              <el-form-item label="用户名/手机号">
                <el-input v-model="loginForm.identifier" placeholder="请输入用户名或手机号" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="loginForm.password" type="password" show-password placeholder="测试服默认密码 123456" />
              </el-form-item>
            </el-form>
            <el-button type="primary" style="width: 100%;" :loading="loginLoading" @click="submitLogin">
              登录
            </el-button>
            <div class="auth-links">
              <a href="javascript:void(0)" @click="goForgot">找回密码</a>
              <a href="javascript:void(0)" @click="goRegister">注册</a>
            </div>
          </el-card>
        </div>

        <div v-else-if="page === 'register'" class="auth-page">
          <el-card class="auth-card">
            <template #header>
              <span>注册</span>
            </template>
            <el-form :model="registerForm" label-width="90px">
              <el-form-item label="手机号">
                <el-input v-model="registerForm.phone" placeholder="不超过11位，纯数字" maxlength="11" />
              </el-form-item>
              <el-form-item label="用户名">
                <el-input v-model="registerForm.username" placeholder="请输入用户名" maxlength="64" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="registerForm.password" type="password" show-password placeholder="8-16位：大小写组合或包含特殊符号；测试服可用 123456" />
              </el-form-item>
              <el-form-item label="确认密码">
                <el-input v-model="registerForm.confirm_password" type="password" show-password placeholder="再次输入密码" />
              </el-form-item>
              <el-form-item label="验证码">
                <el-input v-model="registerForm.code" placeholder="预留第三方云服务接入" maxlength="64" />
              </el-form-item>
            </el-form>
            <el-button type="primary" style="width: 100%;" :loading="registerLoading" @click="submitRegister">
              注册并登录
            </el-button>
            <div class="auth-links single">
              <a href="javascript:void(0)" @click="goLogin">返回登录</a>
            </div>
          </el-card>
        </div>

        <div v-else-if="page === 'forgot'" class="auth-page">
          <el-card class="auth-card">
            <template #header>
              <span>找回密码</span>
            </template>
            <el-form :model="forgotForm" label-width="90px">
              <el-form-item label="手机号">
                <el-input v-model="forgotForm.phone" placeholder="请输入手机号" maxlength="11" />
              </el-form-item>
              <el-form-item label="验证码">
                <el-input v-model="forgotForm.code" placeholder="预留第三方云服务接入" maxlength="64" />
              </el-form-item>
              <el-form-item label="新密码">
                <el-input v-model="forgotForm.password" type="password" show-password placeholder="8-16位：大小写组合或包含特殊符号" />
              </el-form-item>
              <el-form-item label="确认密码">
                <el-input v-model="forgotForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
              </el-form-item>
            </el-form>
            <el-button style="width: 100%;" @click="submitForgot">
              提交
            </el-button>
            <div class="auth-links single">
              <a href="javascript:void(0)" @click="goLogin">返回登录</a>
            </div>
          </el-card>
        </div>

        <div v-else-if="page === 'users'" class="admin-page">
          <el-card>
            <template #header>
              <div class="admin-header">
                <span>用户管理</span>
                <div class="admin-actions">
                  <el-button size="small" @click="page = 'agent'">返回</el-button>
                  <el-button size="small" type="primary" :loading="usersLoading" @click="fetchUsers">刷新</el-button>
                </div>
              </div>
            </template>
            <el-table :data="adminUsers" style="width: 100%;">
              <el-table-column prop="username" label="用户名" min-width="160" />
              <el-table-column label="注册时间" min-width="220">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="登录时间" min-width="220">
                <template #default="{ row }">
                  {{ formatTime(row.last_login_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <div v-else-if="page === 'settings'" class="settings-page">
          <el-card>
            <template #header>
              <div class="admin-header">
                <span>设置</span>
                <div class="admin-actions">
                  <el-button size="small" @click="page = 'agent'">返回</el-button>
                </div>
              </div>
            </template>
            <el-card>
              <template #header>
                <span>⚙️ Model / 登录态</span>
              </template>
              <el-alert
                v-if="modelLocked"
                type="info"
                :closable="false"
                title="模型配置已锁定"
                description="当前版本不会从前端接收或修改模型参数，模型由后端统一管理。"
                style="margin-bottom: 12px;"
              />
              <el-form v-else :model="modelSettings" label-width="120px">
                <el-form-item label="Provider">
                  <el-input v-model="modelSettings.provider" placeholder="自定义提供商名称" />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input v-model="modelSettings.base_url" placeholder="例如 https://api.deepseek.com/v1 或 http://localhost:11434/v1" />
                </el-form-item>
                <el-form-item label="API">
                  <el-select v-model="modelSettings.api" style="width: 100%;">
                    <el-option label="openai-completions" value="openai-completions" />
                    <el-option label="anthropic-messages" value="anthropic-messages" />
                  </el-select>
                </el-form-item>
                <el-form-item label="API Key">
                  <el-input v-model="modelSettings.api_key" type="password" show-password placeholder="提供商 API Key" />
                </el-form-item>
                <el-form-item label="Model ID">
                  <el-input v-model="modelSettings.model.id" placeholder="模型唯一标识符" />
                </el-form-item>
                <el-form-item label="Model Name">
                  <el-input v-model="modelSettings.model.name" placeholder="模型显示名称" />
                </el-form-item>
                <el-form-item label="Temperature">
                  <el-input-number v-model="modelSettings.temperature" :min="0" :max="2" :step="0.1" style="width: 100%;" />
                </el-form-item>
                <el-form-item label="Max Tokens">
                  <el-input-number v-model="modelSettings.max_tokens" :min="1" :max="32768" :step="256" style="width: 100%;" />
                </el-form-item>
              </el-form>
              <el-form :model="crawlerSettings" label-width="120px" style="margin-top: 12px;">
                <el-form-item label="storage_state">
                  <el-input v-model="crawlerSettings.playwright_storage_state" placeholder="例如 /abs/path/storage_state.json（需要后端能访问）" />
                </el-form-item>
              </el-form>
              <el-space>
                <el-button type="primary" @click="saveSettings">保存</el-button>
                <el-button @click="testModel" :loading="testingLlm">测试模型</el-button>
              </el-space>
            </el-card>
          </el-card>
        </div>

        <div v-else class="agent-page">
          <el-row :gutter="20" justify="center">
            <el-col :span="24">
              <el-card class="agent-card agent-chat-card">
                <template #header>
                  <span>💬 Agent</span>
                </template>
                <div class="chat-container">
                  <div v-for="(m, idx) in chatMessages" :key="idx" class="chat-message" :class="m.role">
                    <div class="chat-role">{{ m.role === 'user' ? '我' : 'AI' }}</div>
                    <div class="chat-content">{{ m.content }}</div>
                  </div>
                </div>
              <div v-if="crawlResult.success" class="page-directory">
                <div class="page-directory-header">
                  <div class="page-directory-title">
                    页面目录（已选 {{ checkedPages.length }} / {{ crawlResult.pages.length }}）
                  </div>
                  <el-space :size="8">
                    <el-button size="small" @click="selectAllPages">全选</el-button>
                    <el-button size="small" @click="clearAllPages">全不选</el-button>
                    <el-button size="small" @click="invertSelectedPages">反选</el-button>
                    <el-input v-model="pageFilter" size="small" placeholder="搜索页面" style="width: 160px;" />
                  </el-space>
                </div>
                <el-scrollbar height="220px">
                  <el-tree
                    ref="treeRef"
                    :data="treeData"
                    node-key="id"
                    show-checkbox
                    default-expand-all
                    :expand-on-click-node="false"
                    :props="{ label: 'name', children: 'children' }"
                    :filter-node-method="filterTreeNode"
                    :default-checked-keys="checkedKeys"
                    @check="handleCheck"
                  >
                    <template #default="{ data }">
                      <span class="page-node">
                        <span class="page-node-name">{{ data.name }}</span>
                        <el-tag v-if="data.status" size="small" effect="plain">{{ data.status }}</el-tag>
                      </span>
                    </template>
                  </el-tree>
                </el-scrollbar>
              </div>
                <div class="workflow-flat">
                  <div class="workflow-flat-title">🧭 提示</div>
                  <el-space wrap :size="6">
                    <el-tag size="small" effect="plain">1 提交URL</el-tag>
                    <el-tag size="small" effect="plain">2 爬取页面</el-tag>
                    <el-tag size="small" effect="plain">3 选择需求</el-tag>
                    <el-tag size="small" effect="plain">4 生成用例</el-tag>
                    <el-tag size="small" effect="plain">5 导出文件</el-tag>
                  </el-space>
                </div>
                <el-input
                  v-model="chatInput"
                  type="textarea"
                  :rows="3"
                  placeholder="输入消息（可直接粘贴原型链接），Enter 发送，Shift+Enter 换行"
                  @keydown.enter.exact.prevent="sendChat"
                />
                <el-space style="margin-top: 12px;">
                  <el-button type="primary" @click="sendChat" :loading="chatSending" :disabled="!chatInput.trim()">
                    发送
                  </el-button>
                  <el-button @click="clearChat">清空</el-button>
                </el-space>
              </el-card>
            </el-col>
          </el-row>
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
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const page = ref('agent')

    const authToken = ref('')
    const authUser = ref(null)
    const isAuthed = computed(() => Boolean((authToken.value || '').trim()))

    const applyAuthHeader = () => {
      const token = (authToken.value || '').trim()
      if (token) {
        axios.defaults.headers.common.Authorization = `Bearer ${token}`
      } else {
        delete axios.defaults.headers.common.Authorization
      }
    }

    const loadAuth = () => {
      try {
        authToken.value = localStorage.getItem('authToken') || ''
        const raw = localStorage.getItem('authUser')
        authUser.value = raw ? JSON.parse(raw) : null
      } catch {
        authToken.value = ''
        authUser.value = null
      }
      applyAuthHeader()
    }

    const setAuth = (token, user) => {
      authToken.value = token || ''
      authUser.value = user || null
      localStorage.setItem('authToken', authToken.value)
      localStorage.setItem('authUser', JSON.stringify(authUser.value || null))
      applyAuthHeader()
    }

    const logout = () => {
      authToken.value = ''
      authUser.value = null
      localStorage.removeItem('authToken')
      localStorage.removeItem('authUser')
      applyAuthHeader()
      page.value = 'login'
    }

    const goLogin = () => {
      page.value = 'login'
    }
    const goRegister = () => {
      page.value = 'register'
    }
    const goForgot = () => {
      page.value = 'forgot'
    }

    const validatePhone = (phone) => /^\d{1,11}$/.test((phone || '').trim())
    const validatePassword = (pwd) => {
      const p = (pwd || '').trim()
      if (!p) return false
      if (p === '123456') return true
      if (p.length < 8 || p.length > 16) return false
      const hasUpper = /[A-Z]/.test(p)
      const hasLower = /[a-z]/.test(p)
      const hasLetter = /[A-Za-z]/.test(p)
      const hasSpecial = /[^A-Za-z0-9]/.test(p)
      return hasLetter && ((hasUpper && hasLower) || hasSpecial)
    }

    const loginForm = ref({ identifier: '', password: '' })
    const registerForm = ref({
      phone: '',
      username: '',
      password: '',
      confirm_password: '',
      code: ''
    })
    const forgotForm = ref({ phone: '', code: '', password: '', confirm_password: '' })

    const loginLoading = ref(false)
    const registerLoading = ref(false)

    const submitLogin = async () => {
      if (!loginForm.value.identifier.trim()) {
        ElMessage.warning('请输入用户名或手机号')
        return
      }
      if (!loginForm.value.password.trim()) {
        ElMessage.warning('请输入密码')
        return
      }
      loginLoading.value = true
      try {
        const resp = await axios.post('/api/v1/auth/login', {
          identifier: loginForm.value.identifier.trim(),
          password: loginForm.value.password
        })
        setAuth(resp.data.token, resp.data.user)
        ElMessage.success('登录成功')
        page.value = 'agent'
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '登录失败')
      } finally {
        loginLoading.value = false
      }
    }

    const submitRegister = async () => {
      const phone = registerForm.value.phone.trim()
      const username = registerForm.value.username.trim()
      const password = registerForm.value.password
      const confirm = registerForm.value.confirm_password

      if (!validatePhone(phone)) {
        ElMessage.warning('手机号格式不正确')
        return
      }
      if (!username) {
        ElMessage.warning('请输入用户名')
        return
      }
      if (!validatePassword(password)) {
        ElMessage.warning('密码不符合规则')
        return
      }
      if (password !== confirm) {
        ElMessage.warning('两次密码不一致')
        return
      }

      registerLoading.value = true
      try {
        const resp = await axios.post('/api/v1/auth/register', {
          phone,
          username,
          password,
          confirm_password: confirm,
          code: (registerForm.value.code || '').trim() || null
        })
        setAuth(resp.data.token, resp.data.user)
        ElMessage.success('注册成功')
        page.value = 'agent'
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '注册失败')
      } finally {
        registerLoading.value = false
      }
    }

    const submitForgot = async () => {
      const phone = forgotForm.value.phone.trim()
      if (!validatePhone(phone)) {
        ElMessage.warning('手机号格式不正确')
        return
      }
      if (!validatePassword(forgotForm.value.password)) {
        ElMessage.warning('密码不符合规则')
        return
      }
      if (forgotForm.value.password !== forgotForm.value.confirm_password) {
        ElMessage.warning('两次密码不一致')
        return
      }
      ElMessage.info('验证码服务暂未接入')
    }

    const adminUsers = ref([])
    const usersLoading = ref(false)
    const formatTime = (t) => {
      if (!t) return '-'
      try {
        return new Date(t).toLocaleString()
      } catch {
        return String(t)
      }
    }
    const fetchUsers = async () => {
      if (!isAuthed.value) {
        ElMessage.warning('请先登录')
        page.value = 'login'
        return
      }
      usersLoading.value = true
      try {
        const resp = await axios.get('/api/v1/admin/users')
        adminUsers.value = resp.data || []
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '获取用户列表失败')
      } finally {
        usersLoading.value = false
      }
    }

    watch(page, (v) => {
      if (v === 'users') fetchUsers()
    })

    const activeStep = ref(0)
    const crawling = ref(false)
    const generating = ref(false)
    const exporting = ref(false)
    const testingLlm = ref(false)
    const treeRef = ref(null)

    const loadModelSettings = () => {
      try {
        const raw = localStorage.getItem('modelSettings')
        if (!raw) return null
        return JSON.parse(raw)
      } catch {
        return null
      }
    }

    const modelSettings = ref({
      provider: 'custom',
      base_url: '',
      api: 'openai-completions',
      api_key: '',
      model: {
        id: '',
        name: ''
      },
      temperature: 0.7,
      max_tokens: 4096,
      ...(loadModelSettings() || {})
    })

    const loadCrawlerSettings = () => {
      try {
        const raw = localStorage.getItem('crawlerSettings')
        if (!raw) return null
        return JSON.parse(raw)
      } catch {
        return null
      }
    }

    const crawlerSettings = ref({
      playwright_storage_state: '',
      ...(loadCrawlerSettings() || {})
    })

    const modelReady = computed(() => {
      return Boolean((modelSettings.value.base_url || '').trim() && (modelSettings.value.model?.id || '').trim())
    })

    const modelStatus = ref('unknown')
    const modelStatusDetail = ref('')
    const showModelWarning = computed(() => modelStatus.value === 'missing' || modelStatus.value === 'error')
    const modelWarningText = computed(() => {
      if (modelStatus.value === 'missing') return '未配置模型'
      if (modelStatus.value === 'checking') return '模型检测中'
      if (modelStatus.value === 'error') return '模型不可用'
      return ''
    })

    const checkModelConnectivity = async () => {
      modelStatusDetail.value = ''
      if (!modelReady.value) {
        modelStatus.value = 'missing'
        return
      }
      modelStatus.value = 'checking'
      try {
        const resp = await axios.post('/api/v1/chat', {
          messages: [{ role: 'user', content: 'ping' }],
          model: modelSettings.value
        })
        const ok = Boolean((resp.data?.reply || '').trim())
        modelStatus.value = ok ? 'ok' : 'error'
        if (!ok) modelStatusDetail.value = 'empty reply'
      } catch (e) {
        modelStatus.value = 'error'
        modelStatusDetail.value = e.response?.data?.detail || e.message || 'error'
      }
    }

    const saveSettings = () => {
      localStorage.setItem('modelSettings', JSON.stringify(modelSettings.value))
      localStorage.setItem('crawlerSettings', JSON.stringify(crawlerSettings.value))
      ElMessage.success('已保存')
      checkModelConnectivity()
    }
    
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

    const chatMessages = ref([])
    const chatInput = ref('')
    const chatSending = ref(false)
    
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
    
    const getFirstUrl = (text) => {
      const m = text.match(/https?:\/\/[^\s]+/i)
      return m ? m[0] : null
    }

    // 爬取URL
    const crawlUrlInternal = async (url, pushToChat) => {
      crawling.value = true
      
      try {
        const response = await axios.post('/api/v1/crawl', {
          url,
          playwright_storage_state: (crawlerSettings.value.playwright_storage_state || '').trim() || null
        })
        
        crawlResult.value = response.data
        
        if (response.data.success) {
          ElMessage.success(`爬取成功！提取 ${response.data.extracted} 个页面`)
          activeStep.value = 1
          // 默认全选
          checkedKeys.value = response.data.pages.map(p => p.id)
          if (pushToChat) {
            chatMessages.value.push({
              role: 'assistant',
              content: `已爬取到 ${response.data.extracted} 个页面，已默认全选。你可以继续说“生成测试用例”。`
            })
          }
        } else {
          const errMsg = response.data.error || '爬取失败'
          ElMessage.error(errMsg)
          if (pushToChat) {
            chatMessages.value.push({
              role: 'assistant',
              content: `爬取失败：${errMsg}\n\n如果是墨刀的 INVALID_COOKIE，请在“设置”里填写 storage_state 路径（后端可访问的绝对路径），或在后端 .env 配置 PLAYWRIGHT_STORAGE_STATE。`
            })
            page.value = 'settings'
          }
        }
      } catch (error) {
        const errMsg = error.response?.data?.detail || '爬取失败'
        ElMessage.error(errMsg)
        if (pushToChat) {
          chatMessages.value.push({ role: 'assistant', content: `爬取失败：${errMsg}` })
        }
      } finally {
        crawling.value = false
      }
    }

    const crawlUrl = async () => {
      if (!form.value.url) {
        ElMessage.warning('请输入原型链接')
        return
      }
      await crawlUrlInternal(form.value.url, true)
    }
    
    // 处理勾选
    const handleCheck = (data, { checkedKeys: keys }) => {
      checkedKeys.value = keys.filter(k => k !== 'root')
    }

    const pageFilter = ref('')

    const filterTreeNode = (value, data) => {
      if (!value) return true
      return String(data.name || '').includes(value)
    }

    watch(pageFilter, (val) => {
      if (treeRef.value && treeRef.value.filter) treeRef.value.filter(val)
    })

    const applyCheckedKeysToTree = async () => {
      await nextTick()
      if (!treeRef.value || !treeRef.value.setCheckedKeys) return
      treeRef.value.setCheckedKeys(['root', ...checkedKeys.value])
    }

    watch(() => crawlResult.value.pages.length, () => {
      applyCheckedKeysToTree()
    })

    const selectAllPages = () => {
      checkedKeys.value = crawlResult.value.pages.map(p => p.id)
      applyCheckedKeysToTree()
    }

    const clearAllPages = () => {
      checkedKeys.value = []
      applyCheckedKeysToTree()
    }

    const invertSelectedPages = () => {
      const all = crawlResult.value.pages.map(p => p.id)
      const cur = new Set(checkedKeys.value)
      checkedKeys.value = all.filter(id => !cur.has(id))
      applyCheckedKeysToTree()
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
        if (!modelReady.value) {
          ElMessage.warning('请先在“设置”中配置模型')
          page.value = 'settings'
          return
        }
        const response = await axios.post('/api/v1/generate', {
          pages: checkedPages.value.map(p => p.id),
          types: form.value.testTypes,
          priority: form.value.priority,
          model: modelSettings.value
        })
        
        testCases.value = response.data.test_cases
        ElMessage.success(`生成 ${response.data.total} 个测试用例`)
        activeStep.value = 3
        chatMessages.value.push({ role: 'assistant', content: `已生成 ${response.data.total} 个测试用例，可以点击“导出 Excel”。` })
      } catch (error) {
        const errMsg = error.response?.data?.detail || '生成失败'
        ElMessage.error(errMsg)
        chatMessages.value.push({ role: 'assistant', content: `生成失败：${errMsg}` })
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
        chatMessages.value.push({ role: 'assistant', content: '已导出 Excel 文件。' })
      } catch (error) {
        const errMsg = error.response?.data?.detail || '导出失败'
        ElMessage.error(errMsg)
        chatMessages.value.push({ role: 'assistant', content: `导出失败：${errMsg}` })
      } finally {
        exporting.value = false
      }
    }

    const sendChat = async () => {
      const content = chatInput.value.trim()
      if (!content) return

      chatMessages.value.push({ role: 'user', content })
      chatInput.value = ''
      chatSending.value = true

      try {
        const url = getFirstUrl(content)
        if (url) {
          form.value.url = url
          await crawlUrlInternal(url, true)
          return
        }
        
        if ((/生成|用例/.test(content)) && activeStep.value >= 1) {
          await generateTestCases()
          return
        }

        if (!modelReady.value) {
          chatMessages.value.push({
            role: 'assistant',
            content: '当前未配置模型。请先点右上角 ⚙️ 进入“设置”，填写 Base URL 与 Model ID，然后点击“测试模型”。'
          })
          page.value = 'settings'
          return
        }

        const response = await axios.post('/api/v1/chat', { messages: chatMessages.value, model: modelSettings.value })
        chatMessages.value.push({ role: 'assistant', content: response.data.reply })
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '发送失败')
      } finally {
        chatSending.value = false
      }
    }

    const clearChat = () => {
      chatMessages.value = []
    }

    const testModel = async () => {
      if (!modelReady.value) {
        ElMessage.warning('请先填写 Base URL 和 Model ID')
        return
      }
      testingLlm.value = true
      try {
        const response = await axios.post('/api/v1/chat', {
          messages: [{ role: 'user', content: 'ping' }],
          model: modelSettings.value
        })
        ElMessage.success((response.data.reply || '').slice(0, 60) || '连接成功')
        modelStatus.value = 'ok'
        modelStatusDetail.value = ''
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '测试失败')
        modelStatus.value = 'error'
        modelStatusDetail.value = error.response?.data?.detail || '测试失败'
      } finally {
        testingLlm.value = false
      }
    }

    loadAuth()
    onMounted(() => {
      checkModelConnectivity()
    })
    
    return {
      page,
      isAuthed,
      authUser,
      logout,
      goLogin,
      goRegister,
      goForgot,
      showModelWarning,
      modelWarningText,
      loginForm,
      registerForm,
      forgotForm,
      loginLoading,
      registerLoading,
      submitLogin,
      submitRegister,
      submitForgot,
      adminUsers,
      usersLoading,
      fetchUsers,
      formatTime,
      activeStep,
      crawling,
      generating,
      exporting,
      testingLlm,
      treeRef,
      form,
      crawlResult,
      checkedKeys,
      treeData,
      checkedPages,
      testCases,
      chatMessages,
      chatInput,
      chatSending,
      pageFilter,
      filterTreeNode,
      selectAllPages,
      clearAllPages,
      invertSelectedPages,
      crawlUrl,
      handleCheck,
      nextStep,
      generateTestCases,
      exportExcel,
      modelSettings,
      crawlerSettings,
      saveSettings,
      testModel,
      sendChat,
      clearChat
    }
  }
}
</script>

<style>
html {
  overflow-y: scroll;
}

#app {
  background: #f5f7fa;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

.el-input--large .el-input__wrapper {
  min-height: 40px;
}

.el-input--large .el-input__inner {
  height: 40px;
  line-height: 40px;
}

.el-input-group__append {
  display: flex;
  align-items: stretch;
}

.el-input-group__append .el-button {
  height: 40px;
}

.app-header {
  background: white;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.brand {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.tagline {
  font-size: 13px;
  color: #909399;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-button {
  font-size: 18px;
  padding: 0 6px;
}

.clickable {
  cursor: pointer;
}

.el-main {
  padding: 24px;
  max-width: 1680px;
  margin: 0 auto;
}

.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 160px);
}

.auth-card {
  width: 420px;
}

.auth-links {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

.auth-links.single {
  justify-content: center;
}

.admin-page {
  max-width: 1000px;
  margin: 0 auto;
}

.settings-page {
  max-width: 1100px;
  margin: 0 auto;
}

.agent-page {
  width: 90vw;
  margin: 0 auto;
}

.agent-chat-card {
  width: 75%;
  margin: 0 auto;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.admin-actions {
  display: flex;
  gap: 8px;
}

.workflow-hint {
  margin-top: 12px;
  color: #909399;
  font-size: 13px;
}

.agent-card .el-card__header {
  padding: 10px 14px;
}

.agent-card .el-card__body {
  padding: 12px 14px;
}

.agent-chat-card .el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chat-container {
  flex: 1 1 75%;
  overflow-y: auto;
  padding: 10px;
  background: #f6f8fa;
  border-radius: 10px;
  margin-bottom: 10px;
  min-height: 0;
}

.chat-message {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-role {
  font-weight: 600;
  color: #606266;
  min-width: 20px;
  font-size: 12px;
}

.chat-content {
  background: white;
  border-radius: 8px;
  padding: 6px 10px;
  max-width: 72%;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.45;
}

.chat-message.user .chat-role {
  order: 2;
}

.chat-message.user .chat-content {
  order: 1;
  background: #e8f3ff;
}

.page-directory {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  background: white;
}

.page-directory-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.page-directory-title {
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

.page-node {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.page-node-name {
  color: #303133;
}

.workflow-flat {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  background: white;
}

.workflow-flat-title {
  font-weight: 600;
  color: #606266;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .agent-page {
    width: 100%;
  }

  .agent-chat-card {
    width: 100%;
    height: auto;
  }
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
