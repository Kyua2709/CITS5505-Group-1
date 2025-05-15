function selectAnalysis(element) {
  // 清除所有列表项的active类
  document.querySelectorAll('.list-group-item').forEach(el => el.classList.remove('active'));
  
  // 为当前元素添加active类
  element.classList.add('active');

  // 获取数据属性
  const title = element.getAttribute('data-title');
  const platform = element.getAttribute('data-platform');
  const uploadId = element.getAttribute('data-id'); // 获取上传ID

  // 更新显示的标题
  const badge = document.getElementById('selectedAnalysis');
  if (badge) {
    badge.textContent = `${title} - ${platform}`;
  }
  
  // 存储当前选中的分析ID，用于导出PDF
  window.currentUploadId = uploadId;
  console.log('Selected analysis ID:', window.currentUploadId); // 添加调试输出
}

// 导出PDF函数
function exportPDF() {
  console.log('Export PDF clicked, upload ID:', window.currentUploadId); // 添加调试输出
  
  if (!window.currentUploadId) {
    alert('Please select an analysis first');
    return;
  }
  
  // 在新窗口中打开分析结果页面并传递export_pdf参数
  window.open(`/analyze/result/${window.currentUploadId}?export_pdf=true`, '_blank');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded'); // 添加调试输出
  
  // 获取导出PDF按钮
  const exportPdfBtn = document.querySelector('.dashboard-card-body .btn-primary');
  if (exportPdfBtn) {
    console.log('Export button found'); // 添加调试输出
    exportPdfBtn.addEventListener('click', exportPDF);
  } else {
    console.log('Export button not found!'); // 添加调试输出
  }
  
  // 默认选中第一个分析
  const firstAnalysis = document.querySelector('.list-group-item');
  if (firstAnalysis) {
    console.log('First analysis found'); // 添加调试输出
    selectAnalysis(firstAnalysis);
  } else {
    console.log('No analysis found in the list!'); // 添加调试输出
  }
});

// 如果DOM已经加载完成，立即执行初始化
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  const firstAnalysis = document.querySelector('.list-group-item');
  if (firstAnalysis) {
    console.log('Initializing on already loaded page'); // 添加调试输出
    selectAnalysis(firstAnalysis);
  }
  
  const exportPdfBtn = document.querySelector('.dashboard-card-body .btn-primary');
  if (exportPdfBtn) {
    exportPdfBtn.addEventListener('click', exportPDF);
  }
}