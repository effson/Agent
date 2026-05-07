<template>
  <div class="gemini-container">
    <header class="header">
      <div class="header-left">
        <div class="menu-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
        </div>
        <div class="model-name">Data Agent</div>
      </div>
      <div class="header-right">
        <div class="user-profile">JS</div>
      </div>
    </header>

    <main ref="messagesEl" class="chat-viewport">
      <div class="chat-content">
        <div v-if="messages.length === 0" class="welcome-screen">
          <h1 class="gradient-text">你好，我是 Data Agent</h1>
          <p class="subtitle">我可以帮你分析数据或回答复杂的查询问题。</p>
          
          <div class="suggested-cards">
            <div class="card">分析上季度的销售数据</div>
            <div class="card">查询各地区数据</div>
            <div class="card">检查库存状态</div>
          </div>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-row', msg.role]"
        >
          <div class="avatar-col">
            <div v-if="msg.role === 'assistant'" class="avatar-gemini">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L14.85 8.65L22 10.82L16.29 15.12L18.18 22L12 18.06L5.82 22L7.71 15.12L2 10.82L9.15 8.65L12 2Z" fill="url(#grad)"/><defs><linearGradient id="grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#4285F4"/><stop offset="1" stop-color="#9B72CB"/></linearGradient></defs></svg>
            </div>
          </div>

          <div class="content-col">
            <div class="message-body">
              <div v-if="msg.type === 'text'" class="text-content">
                {{ msg.content }}
              </div>

              <div v-else-if="msg.type === 'steps'" class="steps-container">
                <template v-for="(step, sIdx) in msg.steps" :key="sIdx">
                  <div class="step-item">
                    <div class="status-indicator" :class="step.status">
                      <div v-if="step.status === 'running'" class="spinner"></div>
                      <div v-else-if="step.status === 'success'" class="check">✓</div>
                    </div>
                    <span class="step-text">{{ step.text }}</span>
                  </div>
                  <div v-if="sIdx < msg.steps.length - 1" class="step-arrow">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14m-7-7 7 7-7 7"/>
                    </svg>
                  </div>
                </template>
              </div>

              <div v-else-if="msg.type === 'table'" class="table-card">
                <div class="table-scroll">
                  <table class="gemini-table">
                    <thead>
                      <tr>
                        <th v-for="col in msg.columns" :key="col">{{ col }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rIdx) in msg.rows" :key="rIdx">
                        <td v-for="col in msg.columns" :key="col">{{ row[col] }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-if="msg.role === 'assistant' && msg.type === 'table'" class="feedback-row">
                <button 
                  @click="handleFeedback(index, 1)" 
                  :class="['feedback-btn', { 'active-up': msg.feedback === 1 }]"
                  :disabled="msg.feedback !== undefined"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
                </button>
                <button 
                  @click="handleFeedback(index, 0)" 
                  :class="['feedback-btn', { 'active-down': msg.feedback === 0 }]"
                  :disabled="msg.feedback !== undefined"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.37-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/></svg>
                </button>
                <span v-if="msg.feedback !== undefined" class="feedback-thanks">感谢您的反馈！</span>
              </div>
              <div v-else-if="msg.type === 'error'" class="error-msg">
                <span class="error-icon">⚠️</span> {{ msg.content }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="bottom-padding"></div>
    </main>

    <footer class="input-area">
      <div class="input-container">
        <div class="input-wrapper-inner">
          <input
            v-model="question"
            @keyup.enter="sendQuestion"
            placeholder="在这里输入提示词"
            :disabled="loading"
          />
          <div class="actions">
            <button @click="sendQuestion" :disabled="loading || !question" class="send-btn">
              <svg v-if="!loading" viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
              <div v-else class="dot-loading"></div>
            </button>
          </div>
        </div>
        <p class="disclaimer">Data Agent 可能会显示不准确的信息，请验证其回答。</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { nextTick, ref } from "vue";

const API_URL = "/api/query";
const FEEDBACK_URL = "/api/feedback";
const question = ref("");
const loading = ref(false);
const messages = ref([]);
const messagesEl = ref(null);

function scrollToBottom() {
  const el = messagesEl.value;
  if (!el) return;
  el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
}

async function sendQuestion() {
  if (!question.value || loading.value) return;
  const q = question.value;
  question.value = "";
  loading.value = true;

  const clientMsgId = Date.now();

  messages.value.push({ id: clientMsgId + '_u', role: "user", type: "text", content: q });
  const assistantMsgId = clientMsgId + '_a';
  const stepIndex = messages.value.push({ id: assistantMsgId, role: "assistant", type: "steps", steps: [], feedback: undefined}) - 1;
  await nextTick();
  scrollToBottom();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
    });
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop();
      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;
        let data = JSON.parse(line.replace(/^data:\s*/, ""));
        const steps = messages.value[stepIndex].steps;
        if (data.type === "progress") {
          let step = steps.find((s) => s.text === data.step);
          if (!step) {
            steps.push({ text: data.step, status: data.status });
          } else { step.status = data.status; }
        } else if (data.type === "result") {
          //messages.value.push({
          //  role: "assistant",
          //  type: "table",
          //  columns: Object.keys(data.data[0] || {}),
          //  rows: data.data,
          //  runId: data.run_id, // 确保 FastAPI 后端返回了这个字段
          //  feedback: undefined // 初始化反馈状态
          //});
          const msg = messages.value[stepIndex];
          msg.type = "table";
          msg.columns = Object.keys(data.data[0] || {});
          msg.rows = data.data;
          msg.runId = data.run_id;
        } else if (data.type === "error") {
          messages.value.push({ role: "assistant", type: "error", content: data.message });
        }
        await nextTick();
        scrollToBottom();
      }
    }
  } catch (e) {
    messages.value.push({ role: "assistant", type: "error", content: "请求失败" });
  } finally {
    loading.value = false;
    await nextTick();
    scrollToBottom();
  }
}

async function handleFeedback(index, score) {
  const msg = messages.value[index];
  if (!msg.runId) return;

  // 立即更新 UI 状态
  msg.feedback = score;

  try {
    await fetch(FEEDBACK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        run_id: msg.runId,
        score: score, // 1 为赞，0 为踩
      }),
    });
  } catch (e) {
    console.error("反馈提交失败", e);
    // 如果失败了可以恢复状态让用户重试
    msg.feedback = undefined;
  }
}
</script>

<style scoped>
.gemini-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  color: #1f1f1f;
  font-family: 'Google Sans', Roboto, Arial, sans-serif;
  overflow: hidden;
}

.header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.menu-icon { color: #5f6368; cursor: pointer; }
.model-name { font-size: 20px; font-weight: 500; color: #444746; }
.user-profile {
  width: 32px;
  height: 32px;
  background: #7b1fa2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.chat-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 0 40px;
}

.chat-content {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding-top: 40px;
}

.welcome-screen {
  margin-top: 80px;
  max-width: 800px;
}
.gradient-text {
  font-size: 56px;
  line-height: 1.2;
  font-weight: 500;
  background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}
.subtitle {
  font-size: 24px;
  color: #c4c7c5;
  margin-bottom: 48px;
}
.suggested-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.card {
  padding: 20px;
  background: #f0f4f9;
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.card:hover { background: #e5eaf1; }

.message-row {
  display: flex;
  margin-bottom: 40px;
}
.message-row.user {
  flex-direction: row-reverse;
}
.avatar-col {
  width: 40px;
  flex-shrink: 0;
  margin: 0 16px;
}
.avatar-gemini svg { width: 32px; height: 32px; }

.message-body {
  max-width: 90%;
  font-size: 16px;
  line-height: 1.6;
}
.user .message-body {
  background: #f0f4f9;
  padding: 12px 24px;
  border-radius: 24px;
}

/* --- 优化后的步骤条样式 --- */
.steps-container {
  display: flex;
  flex-wrap: wrap; /* 允许自动换行，但保持每行内元素对齐 */
  align-items: center;
  gap: 12px;
  background: #f8f9fa;
  border: 1px solid #f0f0f0;
  border-radius: 16px;
  padding: 16px 20px;
  margin: 12px 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #444746;
  white-space: nowrap; /* 核心：防止步骤内部文字换行 */
}

.step-arrow {
  display: flex;
  align-items: center;
  color: #c4c7c5;
}

.status-indicator {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #ddd;
  border-top-color: #4285f4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.check {
  color: #1e8e3e;
  font-weight: bold;
}

@keyframes spin { to { transform: rotate(360deg); } }
/* ------------------------ */

.table-card {
  margin-top: 16px;
  border: 1px solid #e3e3e3;
  border-radius: 16px;
  background: white;
  overflow: hidden;
}
.table-scroll {
  overflow-x: auto;
}
.gemini-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}
.gemini-table th {
  background: #fdfdfd;
  padding: 14px;
  text-align: left;
  border-bottom: 1px solid #eee;
  font-weight: 500;
  color: #444746;
}
.gemini-table td {
  padding: 14px;
  border-bottom: 1px solid #f9f9f9;
  color: #1f1f1f;
}

.input-area {
  padding: 24px 40px 32px;
  background: #fff;
}
.input-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}
.input-wrapper-inner {
  display: flex;
  align-items: center;
  background: #f0f4f9;
  border-radius: 32px;
  padding: 10px 16px 10px 28px;
}
.input-wrapper-inner input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 16px;
  height: 48px;
}
.send-btn {
  background: transparent;
  border: none;
  padding: 12px;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.send-btn:hover:not(:disabled) { background: #e2e7ed; }
.disclaimer {
  text-align: center;
  font-size: 12px;
  color: #70757a;
  margin-top: 12px;
}

.bottom-padding { height: 120px; }

.error-msg {
  color: #d93025;
  background: #fce8e6;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 修改反馈行布局 */
.feedback-row {
  display: flex;
  align-items: center;
  gap: 16px; /* 增加图标间距 */
  margin-top: 12px;
  padding-left: 4px;
}

.feedback-btn {
  background: transparent;
  border: none;         /* 关键：去掉外边框 */
  padding: 0;           /* 去掉内边距 */
  cursor: pointer;
  color: #5f6368;       /* 默认灰色图标 */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, color 0.2s;
  outline: none;
}

/* 悬停微动效 */
.feedback-btn:hover:not(:disabled) {
  color: #1f1f1f;
  transform: scale(1.1); /* 鼠标悬停时稍微放大 */
}

/* 点赞激活态：绿色 */
.active-up {
  color: #1e8e3e !important; 
}

/* 点踩激活态：红色 */
.active-down {
  color: #d93025 !important;
}

.feedback-btn:disabled {
  cursor: default;
}

.feedback-thanks {
  font-size: 12px;
  color: #70757a;
  margin-left: 4px;
}
</style>