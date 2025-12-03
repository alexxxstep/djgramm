// Post form functionality - Image upload, drag & drop, reordering
(function() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const newImagesSection = document.getElementById('new-images-section');
    const newImagesPreview = document.getElementById('new-images-preview');
    const formsetContainer = document.getElementById('formset-container');
    const form = document.getElementById('post-form');
    const captionInput = document.getElementById('caption-input');
    const charCount = document.getElementById('char-count');
    const existingImagesContainer = document.getElementById('existing-images');

    if (!form) return;

    let newFiles = [];
    const MAX_FILES = 10;
    const existingImagesCount = existingImagesContainer ? existingImagesContainer.querySelectorAll('[data-image-id]').length : 0;
    const postId = window.POST_ID || null;

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.content || '';
    }

    // Character counter
    if (captionInput && charCount) {
        captionInput.addEventListener('input', function() {
            charCount.textContent = captionInput.value.length;
        });
    }

    // =========================================================================
    // DRAG & DROP REORDER FOR EXISTING IMAGES
    // =========================================================================
    if (existingImagesContainer) {
        let draggedItem = null;

        existingImagesContainer.querySelectorAll('[data-image-id]').forEach(function(item) {
            item.addEventListener('dragstart', function(e) {
                draggedItem = this;
                this.classList.add('opacity-50');
                e.dataTransfer.effectAllowed = 'move';
            });

            item.addEventListener('dragend', function() {
                this.classList.remove('opacity-50');
                draggedItem = null;
                updateCoverBadge();
                saveImageOrder();
            });

            item.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });

            item.addEventListener('dragenter', function(e) {
                e.preventDefault();
                if (this !== draggedItem) {
                    this.classList.add('border-primary', 'border-2');
                }
            });

            item.addEventListener('dragleave', function() {
                this.classList.remove('border-primary');
            });

            item.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('border-primary');
                if (this !== draggedItem && draggedItem) {
                    const allItems = Array.from(existingImagesContainer.children);
                    const draggedIndex = allItems.indexOf(draggedItem);
                    const targetIndex = allItems.indexOf(this);

                    if (draggedIndex < targetIndex) {
                        this.parentNode.insertBefore(draggedItem, this.nextSibling);
                    } else {
                        this.parentNode.insertBefore(draggedItem, this);
                    }
                }
            });
        });

        function updateCoverBadge() {
            existingImagesContainer.querySelectorAll('.cover-badge').forEach(function(badge) {
                badge.remove();
            });
            const firstImage = existingImagesContainer.querySelector('[data-image-id]');
            if (firstImage) {
                const badge = document.createElement('div');
                badge.className = 'cover-badge absolute top-1 left-1 bg-primary text-white text-xs px-2 py-0.5 rounded z-10';
                badge.textContent = 'Cover';
                firstImage.appendChild(badge);
            }
        }

        function saveImageOrder() {
            if (!postId) return;

            const order = [];
            existingImagesContainer.querySelectorAll('[data-image-id]').forEach(function(item) {
                order.push(parseInt(item.dataset.imageId));
            });

            fetch('/post/' + postId + '/reorder-images/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ order: order })
            }).then(function(response) {
                if (!response.ok) {
                    console.error('Failed to save image order');
                }
            }).catch(function(error) {
                console.error('Error:', error);
            });
        }
    }

    // =========================================================================
    // DELETE CHECKBOX HANDLING
    // =========================================================================
    document.querySelectorAll('.delete-checkbox').forEach(function(checkbox) {
        const container = checkbox.closest('[data-image-id]');
        const label = checkbox.closest('label');
        const indicator = container.querySelector('.delete-indicator');
        const deleteLabel = label.querySelector('.delete-label');

        label.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            checkbox.checked = !checkbox.checked;

            if (checkbox.checked) {
                container.classList.add('opacity-50');
                container.setAttribute('draggable', 'false');
                indicator.classList.remove('hidden');
                indicator.classList.add('flex');
                deleteLabel.textContent = 'Restore';
                deleteLabel.classList.remove('bg-red-500');
                deleteLabel.classList.add('bg-green-500');
            } else {
                container.classList.remove('opacity-50');
                container.setAttribute('draggable', 'true');
                indicator.classList.add('hidden');
                indicator.classList.remove('flex');
                deleteLabel.textContent = 'Delete';
                deleteLabel.classList.add('bg-red-500');
                deleteLabel.classList.remove('bg-green-500');
            }

            var index = checkbox.dataset.index;
            var hiddenCb = document.querySelector('.existing-delete-cb[data-index="' + index + '"]');
            if (hiddenCb) hiddenCb.checked = checkbox.checked;
        });
    });

    // =========================================================================
    // FILE UPLOAD HANDLING
    // =========================================================================
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
        dropzone.addEventListener(eventName, function(e) { e.preventDefault(); e.stopPropagation(); }, false);
    });

    ['dragenter', 'dragover'].forEach(function(eventName) {
        dropzone.addEventListener(eventName, function() { dropzone.classList.add('border-primary', 'bg-primary/5'); });
    });

    ['dragleave', 'drop'].forEach(function(eventName) {
        dropzone.addEventListener(eventName, function() { dropzone.classList.remove('border-primary', 'bg-primary/5'); });
    });

    dropzone.addEventListener('drop', function(e) { handleFiles(e.dataTransfer.files); });

    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
        fileInput.value = '';
    });

    function handleFiles(files) {
        var deletedCount = document.querySelectorAll('.delete-checkbox:checked').length;
        var totalAllowed = MAX_FILES - existingImagesCount + deletedCount;
        var remainingSlots = totalAllowed - newFiles.length;

        if (remainingSlots <= 0) {
            alert('Maximum ' + MAX_FILES + ' images allowed per post.');
            return;
        }

        Array.from(files).slice(0, remainingSlots).forEach(function(file) {
            if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
                alert(file.name + ' is not a valid image type. Please use JPEG, PNG, or WebP.');
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                alert(file.name + ' is too large. Maximum size is 10MB.');
                return;
            }
            newFiles.push(file);
            addPreview(file, newFiles.length - 1);
        });
        updateFormset();
    }

    function addPreview(file, index) {
        newImagesSection.classList.remove('hidden');
        var reader = new FileReader();
        reader.onload = function(e) {
            var div = document.createElement('div');
            div.className = 'relative group';
            div.dataset.newIndex = index;
            div.innerHTML = '<img src="' + e.target.result + '" alt="' + file.name + '" class="w-full h-24 object-cover rounded-lg border border-gray-200">' +
                '<button type="button" class="remove-new-image absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">' +
                '<span class="text-white text-xs font-medium px-2 py-1 bg-red-500 rounded">Remove</span></button>' +
                '<div class="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-1 rounded-b-lg truncate">' + file.name + '</div>';
            newImagesPreview.appendChild(div);
            div.querySelector('.remove-new-image').addEventListener('click', function() { removeNewImage(index); });
        };
        reader.readAsDataURL(file);
    }

    function removeNewImage(index) {
        newFiles.splice(index, 1);
        rebuildPreviews();
        updateFormset();
    }

    function rebuildPreviews() {
        newImagesPreview.innerHTML = '';
        if (newFiles.length === 0) {
            newImagesSection.classList.add('hidden');
        } else {
            newFiles.forEach(function(file, index) { addPreview(file, index); });
        }
    }

    function updateFormset() {
        var totalFormsInput = formsetContainer.querySelector('[name$="-TOTAL_FORMS"]');
        var existingCount = formsetContainer.querySelectorAll('.existing-delete-cb').length;
        var totalNeeded = existingCount + newFiles.length;

        if (totalNeeded > parseInt(totalFormsInput.value)) {
            var currentTotal = parseInt(totalFormsInput.value);
            for (var i = currentTotal; i < totalNeeded; i++) {
                var div = document.createElement('div');
                div.className = 'image-form';
                div.dataset.formIndex = i;
                div.innerHTML = '<input type="file" name="images-' + i + '-image" class="new-image-input" accept="image/*">';
                formsetContainer.appendChild(div);
            }
            totalFormsInput.value = totalNeeded;
        }
    }

    // =========================================================================
    // FORM SUBMIT
    // =========================================================================
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var existingCount = formsetContainer.querySelectorAll('.existing-delete-cb').length;

        newFiles.forEach(function(file, index) {
            var inputIndex = existingCount + index;
            var input = formsetContainer.querySelector('[name="images-' + inputIndex + '-image"]');
            if (!input) {
                var div = document.createElement('div');
                div.className = 'image-form';
                div.innerHTML = '<input type="file" name="images-' + inputIndex + '-image" class="new-image-input" accept="image/*">';
                formsetContainer.appendChild(div);
                input = div.querySelector('input');
            }
            var dt = new DataTransfer();
            dt.items.add(file);
            input.files = dt.files;
        });

        var totalFormsInput = formsetContainer.querySelector('[name$="-TOTAL_FORMS"]');
        totalFormsInput.value = existingCount + newFiles.length;
        form.submit();
    });
})();

