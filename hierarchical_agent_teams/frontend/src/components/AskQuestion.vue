<template>
  <div class="ask-question-container">
    <h2>Ask a Question</h2>
    <div class="input-section">
      <input
        v-model="inputValue"
        :disabled="isRequesting"
        placeholder="Welcome to ask questions"
        class="question-input"
      />
      <button
        @click="handleSubmit"
        :disabled="isRequesting || inputValue.trim() === ''"
        class="submit-button"
      >
        {{ isRequesting ? 'Submitting...' : 'Submit' }}
      </button>
      <p v-if="inputEmptyError" class="error-message">Input cannot be empty!</p>
    </div>
    <h3>Response</h3>
    <div class="response-section">
      <div
  v-for="(chunk, index) in displayedResponse"
  :key="index"
  class="response-paragraph"
>
  <div v-if="chunk.role === 'Supervisor'" class="supervisor-line">
    <span class="role-bold">{{ chunk.role }}:</span>
    <span class="content-inline">{{ chunk.content }}</span>
  </div>
  <div v-else-if="['Research Team', 'Writing Team'].includes(chunk.role)">
    <div class="role-bold">{{ chunk.role }}:</div>
    <div class="markdown-display">
      <VMarkdownView :mode="mode" :content="chunk.content"></VMarkdownView>
    </div>
  </div>
  
</div>
      <p v-if="isRequesting && !isAllDataReceived" class="waiting-message">
        Waiting to get more results
        <span v-for="i in ellipsisLength" :key="i">.</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue';
import { VMarkdownView } from 'vue3-markdown'
import 'vue3-markdown/dist/vue3-markdown.css'

// 基础配置
const inputValue = ref('');
const isRequesting = ref(false);
const inputEmptyError = ref(false);
const responseChunks = ref([]);
const isAllDataReceived = ref(false);

// 动态省略号长度（1-3个点循环）
const ellipsisLength = ref(0);
// 省略号定时器
let ellipsisTimer = null;
// 监听请求状态变化以启动/停止定时器
watch([isRequesting, isAllDataReceived], () => {
  if (isRequesting.value && !isAllDataReceived.value) {
    ellipsisTimer = setInterval(() => {
      ellipsisLength.value = (ellipsisLength.value % 3) + 1;
    }, 500);
  } else {
    clearInterval(ellipsisTimer);
    ellipsisLength.value = 0;
  }
});
// 组件卸载时清理定时器
onUnmounted(() => {
  clearInterval(ellipsisTimer);
});

const handleSubmit = async () => {
  // 输入验证
  if (inputValue.value.trim() === '') {
    inputEmptyError.value = true;
    setTimeout(() => inputEmptyError.value = false, 3000);
    return;
  }

  // 重置状态
  inputEmptyError.value = false;
  isRequesting.value = true;
  responseChunks.value = [];
  isAllDataReceived.value = false;

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: inputValue.value.trim() }),
    });

    // 检查响应是否成功
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 确认响应是可读流
    if (!response.body) {
      throw new Error('响应不支持流式传输');
    }

    // 获取流读取器
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    // 循环读取流数据
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // 解码二进制数据为字符串
      const chunk = decoder.decode(value, { stream: true });

      // 处理 SSE 格式（每个数据块以 "data: " 开头，以 "\n\n" 结尾）
      const lines = chunk.split('\n\n').filter(line => line.trim());
      lines.forEach(line => {
        // 移除 "data: " 前缀
        const dataStr = line.replace(/^data: /, '').trim();
        if (!dataStr) return;

        // 解析 JSON 数据
        try {
          const parsedData = JSON.parse(dataStr);

          // 处理不同类型的响应
          if (parsedData.supervisor?.next === '__end__') {
            isAllDataReceived.value = true;
            responseChunks.value.push({ role: 'Supervisor', content: 'Completed' });
          } else if (parsedData.research_team) {
            responseChunks.value.push({ role: 'Research Team', content: parsedData.research_team });
          } else if (parsedData.writing_team) {
            responseChunks.value.push({ role: 'Writing Team', content: parsedData.writing_team });
          } else if (parsedData.supervisor) {
            const nextTarget = parsedData.supervisor.next == 'research_team' ? 'Research Team' : 'Writing Team';
            responseChunks.value.push({ role: 'Supervisor', content: `The next step will be handled by ${nextTarget}.` });
          } else if (parsedData.answer) {
            responseChunks.value.push({ role: 'Answer', content: parsedData.answer });
          }
        } catch (e) {
          console.error('解析数据失败:', e, '原始数据:', dataStr);
          responseChunks.value.push(`[Parse Error]: ${dataStr}`);
        }
      });
    }
  } catch (error) {
    console.error('请求出错:', error);
    responseChunks.value.push(`[Request Failed]: ${error.message || 'Unknown Error'}`);
  } finally {
    isRequesting.value = false;
  }
};

// 展示响应内容
const displayedResponse = computed(() => responseChunks.value);
</script>

<style scoped>
.ask-question-container {
  text-align: center;
  margin: 20px;
}

.input-section {
  margin-bottom: 20px;
}

.question-input {
  padding: 8px;
  margin-right: 10px;
  width: 400px;
}

.submit-button {
  padding: 8px 16px;
  cursor: pointer;
}

.error-message {
  color: red;
  margin-top: 5px;
}

.response-section {
  text-align: left;
  margin-top: 10px;
  padding-left: 200px;
  padding-right: 200px;
}

.response-paragraph {
  margin: 5px 0;
}

.waiting-message {
  color: #999;
  font-style: italic;
}

.markdown-display {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
}

.supervisor-line {
  display: flex;
  align-items: center;
  gap: 8px;
}
.role-bold {
  font-weight: bold;
}
.content-inline {
  display: inline;
}
</style>