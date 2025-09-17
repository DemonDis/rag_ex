import React, { useState } from 'react';
import './styles/App.css';
import UploadForm from './components/UploadForm';
import ChatBox from './components/ChatBox';
import ModelSelector from './components/ModelSelector';

function App() {
  const [selectedModel, setSelectedModel] = useState("mistral:7b-instruct");
  const [filesProcessed, setFilesProcessed] = useState(false);

  const handleFileUploaded = () => {
    setFilesProcessed(true);
  };

  return (
    <div className="App">
      <header className="header">
        <h1>RAG Assistant с Ollama</h1>
      </header>

      <div className="container">
        <UploadForm onFileUploaded={handleFileUploaded} />

        <ModelSelector
          selectedModel={selectedModel}
          onSelect={setSelectedModel}
        />

        <ChatBox selectedModel={selectedModel} />
      </div>
    </div>
  );
}

export default App;