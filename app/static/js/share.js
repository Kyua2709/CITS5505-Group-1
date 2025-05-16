// share.js - Updated to support in-app sharing to registered users
function selectAnalysis(element) {
  // Remove 'active' class from all elements and add to the selected one
  document.querySelectorAll('.list-group-item').forEach(el => el.classList.remove('active'));
  element.classList.add('active');

  const title = element.getAttribute('data-title');
  const platform = element.getAttribute('data-platform');
  const uploadId = element.getAttribute('data-id');

  const badge = document.getElementById('selectedAnalysis');
  if (badge) badge.textContent = `${title} - ${platform}`;

  window.currentUploadId = uploadId;
}

function shareWithCollaborators(event) {
  event.preventDefault();
  // Check if an analysis is selected
  if (!window.currentUploadId) {
    alert('Please select an analysis to share.');
    return;
  }
  // Check if the user has entered at least one email
  const emails = document.getElementById('collaboratorEmails').value.trim();
  if (!emails) {
    alert('Please enter at least one collaborator email.');
    return;
  }

  const message = document.getElementById('shareMessage').value.trim();

  // Validate email format
  const submitBtn = document.querySelector('#shareForm button[type="submit"]');
  const originalBtnText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sharing...';

  fetch('/share/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      upload_id: window.currentUploadId,
      emails: emails,
      message: message
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Analysis shared successfully!');
        document.getElementById('collaboratorEmails').value = '';
        document.getElementById('shareMessage').value = '';
        window.location.reload();
      } else {
        alert(data.message || 'Failed to share analysis.');
      }
    })
    .catch(err => {
      console.error('Error:', err);
      alert('An error occurred while sharing.');
    })
    .finally(() => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    });
}

document.addEventListener('DOMContentLoaded', function () {
  const exportBtn = document.getElementById('exportPdfBtn');
  if (exportBtn) exportBtn.addEventListener('click', () => {
    if (!window.currentUploadId) {
      alert('Please select an analysis first');
      return;
    }
    // Open a new tab with the PDF export
    window.open(`/analyze/result/${window.currentUploadId}?export_pdf=true`, '_blank');
  });

  const form = document.getElementById('shareForm');
  if (form) form.addEventListener('submit', shareWithCollaborators);

  const firstItem = document.querySelector('.list-group-item');
  if (firstItem) selectAnalysis(firstItem);
});
