import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    await axios.post('http://localhost:8000/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert('Файл загружен!');
  };

  const handleAsk = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/ask', { question });
      setAnswer(res.data.answer);
    } catch (err) {
      setAnswer('Ошибка: ' + err.response?.data?.error || 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>RAG-ассистент</h1>

      <h3>Загрузи документ (PDF)</h3>
      <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Загрузить</button>

      <hr />

      <h3>Задай вопрос</h3>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Что говорится в документе?"
        style={{ width: '70%', padding: '8px' }}
      />
      <button onClick={handleAsk} disabled={loading}>
        {loading ? 'Подожди...' : 'Отправить'}
      </button>

      {answer && (
        <div style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '5px' }}>
          <strong>Ответ:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default App;