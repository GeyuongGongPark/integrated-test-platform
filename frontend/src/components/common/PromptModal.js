import React, { useState, useEffect } from 'react';
import './Modal.css';

const PromptModal = ({ isOpen, onClose, title, message, defaultValue = '', onConfirm, placeholder = '' }) => {
  const [inputValue, setInputValue] = useState(defaultValue);

  useEffect(() => {
    if (isOpen) {
      setInputValue(defaultValue);
    }
  }, [isOpen, defaultValue]);

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm(inputValue);
    }
    onClose();
  };

  const handleCancel = () => {
    if (onConfirm) {
      onConfirm(null);
    }
    onClose();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleConfirm();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="common-modal-overlay" onClick={handleCancel}>
      <div className="modal modal-small" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title || '입력'}</h3>
          <button className="modal-close" onClick={handleCancel}>
            ×
          </button>
        </div>
        <div className="modal-body">
          {message && <p style={{ marginBottom: '16px' }}>{message}</p>}
          <input
            type="text"
            className="form-control"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={placeholder}
            autoFocus
            style={{
              width: '100%',
              padding: '12px 16px',
              border: '2px solid #e9ecef',
              borderRadius: '8px',
              fontSize: '14px',
              marginBottom: '16px'
            }}
          />
        </div>
        <div className="modal-actions">
          <button
            className="btn btn-secondary"
            onClick={handleCancel}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500',
              backgroundColor: '#6c757d',
              color: 'white'
            }}
          >
            취소
          </button>
          <button
            className="btn btn-primary"
            onClick={handleConfirm}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500',
              backgroundColor: '#007bff',
              color: 'white'
            }}
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
};

export default PromptModal;

