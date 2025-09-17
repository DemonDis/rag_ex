import React from 'react';
import '../styles/UploadForm.css';

const UploadForm = ({ onFileUploaded }) => {
  const handleUpload = async (e) => {
    e.preventDefault();
    const fileInput = e.target.elements.file;
    const file = fileInput.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        alert('Файл обработан!');
        onFileUploaded();
        fileInput.value = '';
      } else {
        alert('Ошибка загрузки');
      }
    } catch (err) {
      alert('Ошибка сети');
    }
  };

  return (
    <form onSubmit={handleUpload} className="upload-form">
      <input type="file" name="file" accept=".pdf,.docx,.txt" required />
      <button type="submit">Загрузить документ</button>
    </form>
  );
};

export default UploadForm;