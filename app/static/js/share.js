function selectAnalysis(element) {
  // Clear 'active' class from all list items
  document.querySelectorAll('.list-group-item').forEach(el => el.classList.remove('active'));
  
  // Add 'active' class to the current element
  element.classList.add('active');

  // Get data attributes
  const title = element.getAttribute('data-title');
  const platform = element.getAttribute('data-platform');
  const uploadId = element.getAttribute('data-id'); // Get upload ID

  // Update the displayed title
  const badge = document.getElementById('selectedAnalysis');
  if (badge) {
    badge.textContent = `${title} - ${platform}`;
  }
  
  // Store the currently selected analysis ID for PDF export and email sharing
  window.currentUploadId = uploadId;
  console.log('Selected analysis ID:', window.currentUploadId);
}

// Export PDF function
function exportPDF() {
  console.log('Export PDF clicked, upload ID:', window.currentUploadId);
  
  if (!window.currentUploadId) {
    alert('Please select an analysis first');
    return;
  }
  
  // Open analysis result page in new window with export_pdf parameter
  window.open(`/analyze/result/${window.currentUploadId}?export_pdf=true`, '_blank');
}

// Send email function
function shareByEmail(event) {
  event.preventDefault();
  console.log('Share by email triggered');
  
  if (!window.currentUploadId) {
    alert('Please select an analysis first');
    return;
  }
  
  const emails = document.getElementById('collaboratorEmails').value.trim();
  if (!emails) {
    alert('Please enter at least one email address');
    return;
  }
  
  const message = document.getElementById('shareMessage').value.trim();
  
  console.log('Sharing analysis:', {
    uploadId: window.currentUploadId,
    emails: emails,
    message: message
  });
  
  // Show loading state
  const submitBtn = document.querySelector('#shareForm button[type="submit"]');
  const originalBtnText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';
  
  // Use send_email endpoint
  fetch('/share/send_email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      uploadId: window.currentUploadId,
      emails: emails,
      message: message
    })
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
    if (data.success) {
      // Successfully sent
      alert(`Analysis shared successfully!`);
      
      // Clear form
      document.getElementById('collaboratorEmails').value = '';
      document.getElementById('shareMessage').value = '';
      
      // Refresh the page to show updated Recently Shared list
      window.location.reload();
    } else {
      // Send failed
      alert(`Error: ${data.message}`);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('An error occurred while sharing. Please try again.');
  })
  .finally(() => {
    // Restore button state
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalBtnText;
  });
}

// Add event listeners when the file loads
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded - initializing event listeners');
  
  // Get the export PDF button
  const exportPdfBtn = document.getElementById('exportPdfBtn');
  if (exportPdfBtn) {
    console.log('Export button found');
    exportPdfBtn.addEventListener('click', exportPDF);
  } else {
    console.log('Export button not found!');
  }
  
  // Get the share form
  const shareForm = document.getElementById('shareForm');
  if (shareForm) {
    console.log('Share form found');
    shareForm.addEventListener('submit', function(e) {
      e.preventDefault();
      console.log('Form submit event triggered');
      shareByEmail(e);
    });
  } else {
    console.log('Share form not found!');
  }
  
  // Select the first analysis by default
  const firstAnalysis = document.querySelector('.list-group-item');
  if (firstAnalysis) {
    console.log('First analysis found');
    selectAnalysis(firstAnalysis);
  } else {
    console.log('No analysis found in the list!');
  }
});

// Add immediately executing code to avoid script loading sequence issues
(function() {
  // Check if DOM is already loaded
  if (document.readyState === 'loading') {
    console.log('Document still loading, waiting for DOMContentLoaded');
    return; // Wait for DOMContentLoaded event
  }
  
  console.log('Document already loaded, initializing immediately');
  
  // Directly bind form submit event
  const shareForm = document.getElementById('shareForm');
  if (shareForm) {
    console.log('Initializing form directly');
    
    if (!shareForm._hasSubmitListener) {
      shareForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Direct form submit handler triggered');
        shareByEmail(e);
      });
      shareForm._hasSubmitListener = true;
    }
  }
  
  // Bind export button
  const exportPdfBtn = document.getElementById('exportPdfBtn');
  if (exportPdfBtn && !exportPdfBtn._hasClickListener) {
    exportPdfBtn.addEventListener('click', exportPDF);
    exportPdfBtn._hasClickListener = true;
  }
})();