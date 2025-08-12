<template>
  <div class="max-w-3xl mx-auto p-4 md:p-6 lg:p-8">
    <header class="mb-8">
      <h1 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-primary mb-2">Hierarchical Agent Teams AI</h1>
    </header>

    <div class="bg-white rounded-xl shadow-md overflow-hidden mb-6">
      <div 
        id="chat-container" 
        class="p-4 md:p-6 max-h-[60vh] overflow-y-auto space-y-6"
      >
        <!-- System prompt -->
        <div class="bg-secondary p-4 rounded-lg">
          <div class="flex items-start gap-3">
            <div class="bg-primary text-white p-2 rounded-md">
              <i class="fa fa-robot"></i>
            </div>
            <div>
              <p class="text-gray-700">Hierarchical Agent Teams AI assistants will collaborate to answer your questions. The Supervisor coordinates the work, while the Research Team and Writing Team handle different tasks respectively.</p>
            </div>
          </div>
        </div>

        <!-- Chat message list -->
        <transition-group name="message" tag="div">
          <div 
            v-for="(msg, index) in messages" 
            :key="msg.id" 
            class="p-4 rounded-lg" 
            :class="msg.role === 'user' ? 'bg-primary/10' : roleUtils.getClass(msg.role)"
          >
            <div class="flex items-start gap-3">
              <div :class="roleUtils.getColorClass(msg.role)" class="text-white p-2 rounded-md flex-shrink-0">
                <i :class="roleUtils.getIcon(msg.role)"></i>
              </div>
              <div class="flex-1">
                <div class="font-semibold text-sm mb-1 capitalize">{{ msg.role }}</div>
                
                <!-- Content display area -->
                <p class="whitespace-pre-wrap">{{ msg.displayContent }}</p>
                
                <!-- Loading animation -->
                <div v-if="msg.isLoading" class="typing-indicator mt-1">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
        </transition-group>

        <!-- Error recovery section -->
        <div v-if="hasError" class="bg-red-50 p-4 rounded-lg mb-4">
          <p class="text-red-700 flex items-center">
            <i class="fa fa-exclamation-circle mr-2"></i>
            An error occurred during processing. Please try again.
          </p>
          <button 
            @click="retryLastRequest"
            class="mt-2 text-primary hover:text-primary/80 text-sm font-medium"
          >
            <i class="fa fa-refresh mr-1"></i> Retry
          </button>
        </div>
      </div>
    </div>

    <div class="flex gap-3">
      <input 
        type="text" 
        v-model="userInput"
        placeholder="Enter your question..." 
        class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
        @keypress.enter="sendMessage"
        :disabled="isProcessing"
      >
      <button 
        @click="sendMessage"
        class="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isProcessing || !userInput.trim()"
      >
        <i class="fa fa-paper-plane mr-2"></i>Send
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue';

// Role utility module
const roleUtils = {
  getClass: (role) => {
    const roleClasses = {
      'Supervisor': 'bg-purple-50',
      'Research Team': 'bg-blue-50',
      'Writing Team': 'bg-green-50',
      'Answer': 'bg-gray-50',
      'System': 'bg-secondary'
    };
    return roleClasses[role] || 'bg-secondary';
  },
  getIcon: (role) => {
    const roleIcons = {
      'Supervisor': 'fa-tasks',
      'Research Team': 'fa-search',
      'Writing Team': 'fa-pencil',
      'Answer': 'fa-check-circle',
      'user': 'fa-user',
      'System': 'fa-robot'
    };
    return roleIcons[role] || 'fa-robot';
  },
  getColorClass: (role) => {
    const roleColors = {
      'Supervisor': 'bg-purple-500',
      'Research Team': 'bg-blue-500',
      'Writing Team': 'bg-green-500',
      'Answer': 'bg-gray-500',
      'user': 'bg-blue-500',
      'System': 'bg-primary'
    };
    return roleColors[role] || 'bg-primary';
  }
};

// State management
const userInput = ref('');
const messages = ref([]);
const isProcessing = ref(false);
const currentMessage = ref(null);
const pendingRole = ref(null);
const isDebug = ref(true);
const loadingMessageId = ref(null);
const processId = ref(null);
const hasError = ref(false);
const lastQuestion = ref('');

// Monitor state changes
watch([isProcessing, pendingRole, () => currentMessage.value?.id, loadingMessageId], 
  ([processing, pending, currentId, loadingId]) => {
    console.log(`[State update] Processing: ${processing} | Waiting for role: ${pending} | Current message ID: ${currentId} | Loading message ID: ${loadingId}`);
  }
);

// Send message with Supervisor initial loading state
const sendMessage = () => {
  const message = userInput.value.trim();
  if (!message || isProcessing.value) {
    // Provide visual feedback for disabled state
    if (isProcessing.value) {
      const input = document.querySelector('input');
      input?.classList.add('shake');
      setTimeout(() => input?.classList.remove('shake'), 500);
    }
    return;
  }

  // Generate unique process ID
  const newProcessId = Date.now();
  processId.value = newProcessId;
  console.log(`[New process started] ID: ${newProcessId}, Question: ${message}`);
  
  // Reset all states
  messages.value = [];
  isProcessing.value = true;
  currentMessage.value = null;
  pendingRole.value = null;
  loadingMessageId.value = null;
  hasError.value = false;
  lastQuestion.value = message;
  
  // Add user message
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: message,
    displayContent: message,
    isLoading: false,
    isStreaming: false
  });
  
  // Add Supervisor initial loading state
  const supervisorLoadingId = Date.now();
  loadingMessageId.value = supervisorLoadingId;
  pendingRole.value = 'Supervisor';
  
  const supervisorLoadingMsg = {
    id: supervisorLoadingId,
    role: 'Supervisor',
    content: '',
    displayContent: '',
    isLoading: true,
    isStreaming: false
  };
  
  messages.value.push(supervisorLoadingMsg);
  currentMessage.value = supervisorLoadingMsg;
  console.log(`[Supervisor loading state initialized] ID: ${supervisorLoadingId}`);
  
  userInput.value = '';
  scrollToBottom();
  
  // Call API
  fetchStreamingResponse(message, newProcessId);
};

// Retry last request
const retryLastRequest = () => {
  if (!lastQuestion.value) return;
  
  // Reset state and resend
  isProcessing.value = true;
  hasError.value = false;
  messages.value = messages.value.filter(msg => msg.role === 'user');
  fetchStreamingResponse(lastQuestion.value, Date.now());
};

// Get streaming response
const fetchStreamingResponse = async (question, currentProcessId) => {
  try {
    console.log(`[API call] Process ID: ${currentProcessId}`);
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question })
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    if (!response.body) throw new Error('Response does not support streaming');

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    while (true) {
      if (processId.value !== currentProcessId) {
        console.log(`[Process terminated] Ignoring remaining data`);
        break;
      }

      const { done, value } = await reader.read();
      if (done) {
        console.log(`[Stream reading complete] Process ID: ${currentProcessId}`);
        clearLoadingMessage();
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      console.log(`[Received data chunk] Process ID: ${currentProcessId}, Length: ${chunk.length}`);
      
      const lines = chunk.split('\n\n').filter(line => line.trim());
      
      for (const line of lines) {
        const dataStr = line.replace(/^data: /, '').trim();
        if (!dataStr) continue;

        try {
          const parsedData = JSON.parse(dataStr);
          await processParsedData(parsedData, currentProcessId);
        } catch (e) {
          console.error(`[Parsing error]`, e, 'Raw data:', dataStr);
          addSystemMessage(`[Parsing error]: ${dataStr}`);
        }
      }
    }
  } catch (error) {
    console.error(`[Request error]`, error);
    addSystemMessage(`[Request failed]: ${error.message || 'Unknown error'}`);
    hasError.value = true;
    isProcessing.value = false;
  } finally {
    if (processId.value === currentProcessId) {
      isProcessing.value = false;
    }
    scrollToBottom();
  }
};

// Process parsed data - Fixed __end__ handling
const processParsedData = async (parsedData, currentProcessId) => {
  if (processId.value !== currentProcessId) {
    console.log(`[Ignoring stale data]`);
    return;
  }

  console.log(`[Processing data] Waiting for current message completion: ${currentMessage.value?.role || 'none'}`);
  
  // Wait for current message to complete processing
  const maxWaitIterations = 30;
  let waitIterations = 0;
  
  while (currentMessage.value && (currentMessage.value.isStreaming || currentMessage.value.isLoading)) {
    if (waitIterations >= maxWaitIterations) {
      console.warn(`[Forcing state reset] Message ${currentMessage.value.id}(${currentMessage.value.role})`);
      currentMessage.value.isLoading = false;
      currentMessage.value.isStreaming = false;
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 100));
    waitIterations++;
  }

  // Handle Supervisor responses - with special handling for __end__
  if (parsedData.supervisor) {
    console.log('[Processing Supervisor response]', parsedData.supervisor);
    
    // Extract next team from the Supervisor's response
    const nextTeamKey = parsedData.supervisor.next;
    let nextTeam = null;
    let supervisorMessage = '';
    
    // Determine message based on next team key
    if (nextTeamKey === 'research_team') {
      nextTeam = 'Research Team';
      supervisorMessage = `The next step will be handled by ${nextTeam}`;
    } else if (nextTeamKey === 'writing_team') {
      nextTeam = 'Writing Team';
      supervisorMessage = `The next step will be handled by ${nextTeam}`;
    } else if (nextTeamKey === '__end__') {
      // Explicit message for end state - ensures content isn't empty
      supervisorMessage = 'All tasks have been completed.';
    } else {
      // Default message for unknown states
      supervisorMessage = 'Processing completed.';
    }
    
    // Update existing Supervisor loading message
    if (loadingMessageId.value && pendingRole.value === 'Supervisor') {
      const loadingMsgIndex = messages.value.findIndex(
        msg => msg.id === loadingMessageId.value && msg.role === 'Supervisor'
      );
      
      if (loadingMsgIndex !== -1) {
        console.log(`[Updating Supervisor from loading to content] ID: ${loadingMessageId.value}`);
        
        // Replace loading state with actual content
        messages.value[loadingMsgIndex] = {
          id: loadingMessageId.value,
          role: 'Supervisor',
          content: supervisorMessage,  // Ensure message is set even for __end__
          displayContent: '',
          isLoading: false,
          isStreaming: true
        };
        
        currentMessage.value = messages.value[loadingMsgIndex];
        
        // Clear loading state tracking
        pendingRole.value = null;
        const msgId = loadingMessageId.value;
        loadingMessageId.value = null;
        
        // Stream the Supervisor's message - even for end state
        await startStreamingOutput(currentMessage.value, currentProcessId);
      }
    } else {
      // Fallback: add new Supervisor message if no loading message found
      console.log('[No existing Supervisor loading message, adding new one]');
      await addStreamingMessage('Supervisor', supervisorMessage, nextTeamKey != '__end__', currentProcessId);
    }
    
    // If there's a next team, show its loading state (won't trigger for __end__)
    if (nextTeam) {
      pendingRole.value = nextTeam;
      const loadingMsgId = Date.now();
      loadingMessageId.value = loadingMsgId;
      
      currentMessage.value = {
        id: loadingMsgId,
        role: nextTeam,
        content: '',
        displayContent: '',
        isLoading: true,
        isStreaming: false
      };
      
      messages.value.push(currentMessage.value);
      console.log(`[Showing ${nextTeam} loading state] ID: ${loadingMsgId}`);
      scrollToBottom();
    }
    return;
  }

  // Handle Research Team response
  if (parsedData.research_team) {
    console.log('[Received Research Team response]', { pendingRole: pendingRole.value });
    
    if (pendingRole.value === 'Research Team') {
      return handleTeamResponse('Research Team', parsedData.research_team, currentProcessId);
    } else {
      console.warn('[Research Team response mismatch]');
      addSystemMessage(`[Order error]: Received Research Team response but waiting for ${pendingRole.value || 'none'}`);
    }
    return;
  }

  // Handle Writing Team response
  if (parsedData.writing_team) {
    console.log('[Received Writing Team response]', { pendingRole: pendingRole.value });
    
    if (pendingRole.value === 'Writing Team') {
      return handleTeamResponse('Writing Team', parsedData.writing_team, currentProcessId);
    } else {
      console.warn('[Writing Team response mismatch]');
      addSystemMessage(`[Order error]: Received Writing Team response but waiting for ${pendingRole.value || 'none'}`);
    }
    return;
  }

  // Handle final answer
  if (parsedData.answer) {
    console.log('[Received final answer]');
    clearLoadingMessage();
    return addStreamingMessage('Answer', parsedData.answer, true, currentProcessId);
  }

  // Handle unmatched response data
  if (Object.keys(parsedData).length > 0) {
    console.log('[Received unprocessed data]', parsedData);
    addSystemMessage(`Received unprocessed data: ${JSON.stringify(parsedData)}`);
  }
};

// Handle team responses
const handleTeamResponse = async (team, content, currentProcessId) => {
  if (processId.value !== currentProcessId) {
    console.log(`[Ignoring team response] Process mismatch`);
    return;
  }
  
  if (loadingMessageId.value) {
    const loadingMsgIndex = messages.value.findIndex(
      msg => msg.id === loadingMessageId.value
    );
    
    if (loadingMsgIndex !== -1) {
      console.log(`[Updating ${team} loading message] ID: ${loadingMessageId.value}`);
      messages.value[loadingMsgIndex] = {
        ...messages.value[loadingMsgIndex],
        content,
        displayContent: '',
        isLoading: false,
        isStreaming: true
      };
      currentMessage.value = messages.value[loadingMsgIndex];
      
      pendingRole.value = null;
      const msgId = loadingMessageId.value;
      loadingMessageId.value = null;
      
      await startStreamingOutput(currentMessage.value, currentProcessId);
      return;
    }
  }
  
  console.warn(`[No loading message found] Creating new ${team} message`);
  pendingRole.value = null;
  loadingMessageId.value = null;
  return addStreamingMessage(team, content, true, currentProcessId);
};

// Clear loading message
const clearLoadingMessage = () => {
  if (loadingMessageId.value) {
    const loadingMsgIndex = messages.value.findIndex(
      msg => msg.id === loadingMessageId.value
    );
    
    if (loadingMsgIndex !== -1) {
      const removedMsg = messages.value.splice(loadingMsgIndex, 1)[0];
      console.log(`[Clearing loading message] ${removedMsg.role}, ID: ${loadingMessageId.value}`);
    }
    
    loadingMessageId.value = null;
  }
};

// Add system message
const addSystemMessage = (content) => {
  const newMessage = {
    id: Date.now(),
    role: 'System',
    content: content,
    displayContent: content,
    isLoading: false,
    isStreaming: false
  };
  messages.value.push(newMessage);
  scrollToBottom();
};

// Add streaming message
const addStreamingMessage = async (role, fullContent, shouldStream = true, currentProcessId) => {
  if (processId.value !== currentProcessId) {
    console.log(`[Ignoring message addition] Process mismatch`);
    return;
  }
  
  console.log(`[Adding streaming message] ${role}, Length: ${fullContent.length}`);
  
  if (currentMessage.value && currentMessage.value.role === role) {
    currentMessage.value = null;
  }
  
  const newMessage = {
    id: Date.now(),
    role,
    content: fullContent,
    displayContent: shouldStream ? '' : fullContent,
    isLoading: false,
    isStreaming: shouldStream
  };
  
  messages.value.push(newMessage);
  currentMessage.value = newMessage;
  scrollToBottom();
  
  if (shouldStream) {
    await startStreamingOutput(newMessage, currentProcessId);
  }
  
  return new Promise(resolve => {
    const checkComplete = () => {
      const messageExists = messages.value.some(m => m.id === newMessage.id);
      if (!messageExists || processId.value !== currentProcessId) {
        resolve();
        return;
      }
      
      if (!newMessage.isStreaming && !newMessage.isLoading) {
        console.log(messages)
        resolve();
      } else {
        setTimeout(checkComplete, 50);
      }
    };
    checkComplete();
  });
};

// Streaming output implementation
const startStreamingOutput = (message, currentProcessId) => {
  return new Promise(resolve => {
    let index = 0;
    const fullText = message.content;
    const baseDelay = 30;
    const variance = 20;
    const messageId = message.id;
    
    const typeNextCharacter = () => {
      if (
        processId.value !== currentProcessId ||
        currentMessage.value?.id !== messageId ||
        !message.isStreaming ||
        !messages.value.some(m => m.id === messageId)
      ) {
        const msgIndex = messages.value.findIndex(m => m.id === messageId);
        if (msgIndex !== -1) {
          messages.value[msgIndex].displayContent = fullText;
          messages.value[msgIndex].isStreaming = false;
        }
        resolve();
        return;
      }
      
      if (index < fullText.length) {
        const chunkSize = Math.min(Math.floor(Math.random() * 3) + 1, fullText.length - index);
        message.displayContent = fullText.substring(0, index + chunkSize);
        index += chunkSize;
        console.log(message.displayContent)
        const delay = baseDelay + Math.random() * variance;
        setTimeout(typeNextCharacter, delay);
        scrollToBottom();
      } else {
        message.isStreaming = false;
        console.log(`${message.role} streaming output complete`);
        resolve();
      }
    };
    
    setTimeout(typeNextCharacter, 50);
  });
};

// Scroll to latest message
const scrollToBottom = () => {
  nextTick(() => {
    const container = document.getElementById('chat-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
};
</script>

<style scoped>
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Message appearance animation */
.message-enter {
  opacity: 0;
  transform: translateY(10px);
}
.message-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 300ms, transform 300ms;
}

/* Loading animation */
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 0.5rem;
  height: 0.5rem;
  background-color: #6b7280;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Button and input styles */
button:disabled {
  transition: all 0.3s ease;
}

input:focus {
  transition: all 0.2s ease;
  box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.3);
}

.shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translateX(-1px); }
  20%, 80% { transform: translateX(2px); }
  30%, 50%, 70% { transform: translateX(-3px); }
  40%, 60% { transform: translateX(3px); }
}

:root {
  --primary: #10a37f;
  --secondary: #f7f6f3;
}

@layer utilities {
  .content-auto {
    content-visibility: auto;
  }
  
  .bg-primary\/10 {
    background-color: rgba(16, 163, 127, 0.1);
  }
  
  .bg-purple-50 {
    background-color: rgba(124, 58, 237, 0.05);
  }
  
  .bg-blue-50 {
    background-color: rgba(59, 130, 246, 0.05);
  }
  
  .bg-green-50 {
    background-color: rgba(16, 185, 129, 0.05);
  }
  
  .bg-gray-50 {
    background-color: rgba(156, 163, 175, 0.05);
  }
}
</style>
