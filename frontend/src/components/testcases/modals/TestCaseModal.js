import React from 'react';
import './TestCaseModal.css';
import '../../common/Modal.css';

const TestCaseModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  actions,
  size = 'medium' 
}) => {
  if (!isOpen) return null;

  const sizeClasses = {
    small: 'modal-small',
    medium: 'modal-medium',
    large: 'modal-large',
    fullscreen: 'fullscreen-modal-content'
  };

  return (
    <div className="common-modal-overlay fullscreen-modal">
      <div className={`modal ${sizeClasses[size]}`}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          {children}
        </div>
        {actions && (
          <div className="modal-actions">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};

export default TestCaseModal;
