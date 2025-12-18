// Post form functionality - Image upload, drag & drop, reordering
import { getCsrfToken } from './utils/csrf.js';
import { ajaxPost } from './utils/ajax.js';

// Export initialization function for dynamic import
export function initPostForm() {
    console.log('post_form.js: Initializing...');

    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const newImagesSection = document.getElementById('new-images-section');
    const newImagesPreview = document.getElementById('new-images-preview');
    const formsetContainer = document.getElementById('formset-container');
    const form = document.getElementById('post-form');
    const captionInput = document.getElementById('caption-input');
    const charCount = document.getElementById('char-count');
    const existingImagesContainer = document.getElementById('existing-images');

    console.log('post_form.js: Elements found', {
        dropzone: !!dropzone,
        fileInput: !!fileInput,
        form: !!form,
        formsetContainer: !!formsetContainer
    });

    if (!form) {
        console.warn('post_form.js: Form not found, exiting');
        return;
    }

    console.log('post_form.js: Form found, continuing initialization');

    let newFiles = [];
    const MAX_FILES = 10;
    const existingImagesCount = existingImagesContainer ? existingImagesContainer.querySelectorAll('[data-image-id]').length : 0;
    const postId = window.POST_ID || null;

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

            ajaxPost('/post/' + postId + '/reorder-images/', { order: order }, {
                errorMessage: 'Failed to save image order.'
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
        // Don't prevent default if there are no new files - let form submit normally
        if (newFiles.length === 0) {
            return true;
        }

        e.preventDefault();
        var existingCount = formsetContainer.querySelectorAll('.existing-delete-cb').length;

        // Ensure we have enough form fields for all new files
        var totalNeeded = existingCount + newFiles.length;
        var totalFormsInput = formsetContainer.querySelector('[name$="-TOTAL_FORMS"]');
        var currentTotal = parseInt(totalFormsInput.value) || 0;

        // Remove all existing new-image-input elements first
        formsetContainer.querySelectorAll('.new-image-input').forEach(function(inp) {
            var parent = inp.parentNode;
            if (parent && parent.classList.contains('image-form')) {
                parent.remove();
            } else {
                inp.remove();
            }
        });

        // Create new file inputs for each file using DataTransfer
        var filesAssigned = 0;
        newFiles.forEach(function(file, index) {
            var inputIndex = existingCount + index;
            var div = document.createElement('div');
            div.className = 'image-form';
            div.dataset.formIndex = inputIndex;

            // Create a new file input
            var input = document.createElement('input');
            input.type = 'file';
            input.name = 'images-' + inputIndex + '-image';
            input.className = 'new-image-input';
            input.accept = 'image/*';
            input.style.display = 'none';
            input.multiple = false;

            // Use DataTransfer to assign the file
            try {
                if (typeof DataTransfer !== 'undefined') {
                    var dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                    filesAssigned++;
                    console.log('✓ File assigned:', file.name, 'to input:', input.name, 'Size:', file.size);
                } else {
                    throw new Error('DataTransfer not supported');
                }
            } catch (error) {
                console.error('✗ Error assigning file:', error, file.name);
                // If DataTransfer fails, we can't proceed - show error
                alert('Error: Your browser does not support file upload. Please use a modern browser.');
                return false;
            }

            div.appendChild(input);
            formsetContainer.appendChild(div);
        });

        // Update total forms count
        totalFormsInput.value = totalNeeded;

        // Debug: verify files are assigned
        var allFileInputs = formsetContainer.querySelectorAll('input[type="file"].new-image-input');
        console.log('Total new file inputs created:', allFileInputs.length);
        var filesWithData = 0;
        allFileInputs.forEach(function(inp) {
            if (inp.files && inp.files.length > 0) {
                filesWithData++;
                console.log('✓ Input with file:', inp.name, 'File:', inp.files[0].name, 'Size:', inp.files[0].size);
            } else {
                console.warn('✗ Input without file:', inp.name);
            }
        });
        console.log('Summary - New files:', newFiles.length, 'Assigned:', filesAssigned, 'With data:', filesWithData);

        // Verify files are assigned before submitting
        if (newFiles.length > 0 && filesWithData === 0) {
            alert('Error: Files were not properly attached to the form. Please try selecting files again or use a different browser.');
            return false;
        }

        // Submit the form normally (not via AJAX, to handle file uploads)
        console.log('Submitting form with', filesWithData, 'file(s)');
        form.submit();
    });
}

// Auto-initialize when loaded directly (not via dynamic import)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPostForm);
} else {
    // DOM is already ready
    initPostForm();
}

