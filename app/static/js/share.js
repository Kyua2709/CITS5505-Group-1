
function selectAnalysis(element) {
  document.querySelectorAll('.list-group-item').forEach(el => el.classList.remove('active'));
  
  element.classList.add('active');

  const title = element.getAttribute('data-title');
  const platform = element.getAttribute('data-platform');

  const badge = document.getElementById('selectedAnalysis');
  badge.textContent = `${title} - ${platform}`;
}