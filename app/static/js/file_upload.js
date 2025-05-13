let currentPage = 1;
const itemsPerPage = 3;

function refreshUploadsList(page = 1) {
    currentPage = page;

    $.ajax({
        url: `/get_uploads?page=${page}&limit=${itemsPerPage}`,
        method: 'GET',
        success: function (response) {
            const tbody = $('table tbody');
            tbody.empty();

            if (!response.items || response.items.length === 0) {
                tbody.append('<tr><td colspan="6" class="text-center">No uploads found</td></tr>');
                return;
            }

            response.items.forEach(function (upload) {
                const sizeDisplay = (upload.num_comments !== null && upload.num_comments !== undefined)
                    ? `${upload.num_comments} comments`
                    : (upload.file_path
                        ? upload.file_path.split('/').pop()
                        : (upload.comments
                            ? `${upload.comments.split('\n').length} comments`
                            : (upload.url ? 'URL data' : 'N/A')));

                const row = `
                    <tr>
                        <td>${upload.dataset_name}</td>
                        <td>${upload.platform}</td>
                        <td>${new Date(upload.upload_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</td>
                        <td>${sizeDisplay}</td>
                        <td>
                            <span class="badge ${upload.status === 'Completed' ? 'bg-success' : upload.status === 'Processing' ? 'bg-warning' : 'bg-danger'}">
                                ${upload.status}
                            </span>
                        </td>
                        <td>
                            <a href="/analyze/${upload.id}" class="btn btn-sm btn-primary">View Analysis</a>
                        </td>
                    </tr>
                `;
                tbody.append(row);
            });

            renderPagination(response.page, response.pages);
        },
        error: function (err) {
            console.error("Failed to fetch uploads:", err);
        }
    });
}

function renderPagination(current, total) {
    const container = $('#paginationControls');
    container.empty();

    if (total <= 1) return;

    let html = '<nav><ul class="pagination justify-content-center">';

    for (let i = 1; i <= total; i++) {
        html += `
            <li class="page-item ${i === current ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }

    html += '</ul></nav>';
    container.html(html);

    container.find('a.page-link').on('click', function (e) {
        e.preventDefault();
        const page = $(this).data('page');
        refreshUploadsList(page);
    });
}

$(document).ready(function () {
    // Upload manual form
    $('#manualEntryForm form').submit(function (e) {
        e.preventDefault();

        const platform = $('#platformSelect').val();
        const source = $('#commentSource').val();
        const category = $('#commentCategory').val();
        const comments = $('#commentsTextArea').val();
        const datasetName = $('#manualDatasetName').val();

        const formData = new FormData();
        formData.append('dataset_name', datasetName);
        formData.append('platform', platform);
        formData.append('source', source);
        formData.append('category', category);
        formData.append('comments', comments);

        $.ajax({
            type: 'POST',
            url: '/save_upload',
            data: formData,
            contentType: false,
            processData: false,
            success: function () {
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                successModal.show();
                // refreshUploadsList();
            },
            error: function (error) {
                const msg = error.responseJSON?.message || 'Upload failed.';
                alert(msg);
            }
        });
    });

    // Upload file form
    $('#fileUploadForm form').submit(function (e) {
        e.preventDefault();

        const datasetName = $('#datasetName').val();
        const platform = $('#platformSelect2').val();
        const fileInput = $('#fileUpload')[0].files[0];
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();

        if (!datasetName || !platform || !fileInput) {
            alert('Please fill out all required fields.');
            return;
        }

        const formData = new FormData();
        formData.append('dataset_name', datasetName);
        formData.append('platform', platform);
        formData.append('file', fileInput);
        formData.append('start_date', startDate);
        formData.append('end_date', endDate);
        formData.append('source', 'file');

        $.ajax({
            url: '/save_upload',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function () {
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                successModal.show();
                // refreshUploadsList();
            },
            error: function (error) {
                const msg = error.responseJSON?.error || 'File upload failed.';
                alert(msg);
            }
        });
    });

    // Upload url
    $('#urlEntryForm form').submit(function (e) {
        e.preventDefault();

        const platform = $('#platformSelect3').val();
        const datasetName = $('#urlDatasetName').val();
        const urlType = $('#urlType').val();
        const url = $('#urlInput').val();
        const commentLimit = $('#commentLimit').val();

        const formData = new FormData();
        formData.append('dataset_name', datasetName);
        formData.append('platform', platform);
        formData.append('url', url);
        formData.append('url_type', urlType);
        formData.append('comment_limit', commentLimit);

        $.ajax({
            type: 'POST',
            url: '/save_upload',
            data: formData,
            contentType: false,
            processData: false,
            success: function () {
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                successModal.show();
                // refreshUploadsList();
            },
            error: function (error) {
                const msg = error.responseJSON?.message || 'Upload failed.';
                alert(msg);
            }
        });
    });

    // Initial load of uploads list
    refreshUploadsList();
});