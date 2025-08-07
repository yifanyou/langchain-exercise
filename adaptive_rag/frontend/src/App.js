import React, { useState } from 'react';
import './App.css';

function App() {
  // 存储用户输入的问题
  const [question, setQuestion] = useState(''); 
  // 存储后端返回的回答
  const [response, setResponse] = useState(''); 

  // 处理提交事件，调用后端接口
  const handleSubmit = async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResponse(data.answer);
    } catch (error) {
      console.error('请求错误:', error);
      setResponse('请求失败，请稍后再试');
    }
  };

  return (
    <div className="container">
      <h1>Ask a Question</h1>
      <input
        type="text"
        placeholder="What player at the Bears ex..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={handleSubmit}>Submit</button>
      <div className="response">
        <h2>Response:</h2>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default App;