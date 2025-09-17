import React from 'react';
import '../styles/ChatBox.css'; // переиспользуем стили

const ModelSelector = ({ selectedModel, onSelect }) => {
  const models = ["mistral:7b-instruct", "qwen2:0.5b-instruct"];

  return (
    <div className="model-selector">
      {models.map(model => (
        <button
          key={model}
          className={selectedModel === model ? "active" : ""}
          onClick={() => onSelect(model)}
        >
          {model}
        </button>
      ))}
    </div>
  );
};

export default ModelSelector;