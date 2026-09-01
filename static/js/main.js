document.addEventListener("DOMContentLoaded", () => {
    // Tab Elements
    const tabVerify = document.getElementById("tabVerify");
    const tabRegister = document.getElementById("tabRegister");
    const verifyTabContent = document.getElementById("verifyTabContent");
    const registerTabContent = document.getElementById("registerTabContent");

    // Verification Elements
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("signatureFile");
    const previewContainer = document.getElementById("previewContainer");
    const imagePreview = document.getElementById("imagePreview");
    const removeFileBtn = document.getElementById("removeFileBtn");
    
    const verifyForm = document.getElementById("verifyForm");
    const submitBtn = document.getElementById("submitBtn");
    const btnSpinner = document.getElementById("spinner");
    const btnText = document.getElementById("btnText");
    const uidInput = document.getElementById("uid");

    const resultsWelcome = document.getElementById("resultsWelcome");
    const resultsContent = document.getElementById("resultsContent");
    const statusCard = document.getElementById("statusCard");
    const statusIcon = document.getElementById("statusIcon");
    const statusTitle = document.getElementById("statusTitle");
    const statusMessage = document.getElementById("statusMessage");

    const refImage = document.getElementById("refImage");
    const queryImage = document.getElementById("queryImage");
    const comparisonOverlay = document.getElementById("comparisonOverlay");
    const featureMatchBox = document.getElementById("featureMatchBox");

    const progressRing = document.getElementById("progressRing");
    const scorePercentage = document.getElementById("scorePercentage");
    const ssimScore = document.getElementById("ssimScore");
    const ssimBar = document.getElementById("ssimBar");
    const orbScore = document.getElementById("orbScore");
    const orbBar = document.getElementById("orbBar");
    const nccScore = document.getElementById("nccScore");
    const nccBar = document.getElementById("nccBar");
    const metaKp = document.getElementById("metaKp");
    const metaMatches = document.getElementById("metaMatches");

    // Registration Elements
    const regDropZone = document.getElementById("regDropZone");
    const regFileInput = document.getElementById("regSignatureFile");
    const regPreviewContainer = document.getElementById("regPreviewContainer");
    const regImagePreview = document.getElementById("regImagePreview");
    const regRemoveFileBtn = document.getElementById("regRemoveFileBtn");

    const registerForm = document.getElementById("registerForm");
    const regSubmitBtn = document.getElementById("regSubmitBtn");
    const regSpinner = document.getElementById("regSpinner");
    const regBtnText = document.getElementById("regBtnText");
    const regUidInput = document.getElementById("regUid");
    const regNameInput = document.getElementById("regName");
    const registerAlert = document.getElementById("registerAlert");
    const registerAlertIcon = document.getElementById("registerAlertIcon");
    const registerAlertMsg = document.getElementById("registerAlertMsg");

    // Progress Ring Circumference: 2 * PI * r = 2 * 3.14159 * 50 = 314.16
    const RING_CIRCUMFERENCE = 314.16;
    progressRing.style.strokeDasharray = RING_CIRCUMFERENCE;
    progressRing.style.strokeDashoffset = RING_CIRCUMFERENCE;

    /* --------------------------------------------------
       Tab Switching Handlers
    -------------------------------------------------- */
    
    tabVerify.addEventListener("click", () => {
        tabVerify.classList.add("active");
        tabRegister.classList.remove("active");
        verifyTabContent.classList.remove("hidden");
        registerTabContent.classList.add("hidden");
    });

    tabRegister.addEventListener("click", () => {
        tabRegister.classList.add("active");
        tabVerify.classList.remove("active");
        registerTabContent.classList.remove("hidden");
        verifyTabContent.classList.add("hidden");
        
        // Hide verification results when switching to registration
        resultsContent.classList.add("hidden");
        resultsWelcome.classList.remove("hidden");
    });

    /* --------------------------------------------------
       Verify: Drag & Drop Event Handlers
    -------------------------------------------------- */
    
    dropZone.addEventListener("click", (e) => {
        if (e.target.closest("#removeFileBtn")) return;
        fileInput.click();
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        }, false);
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });

    function handleFiles(files) {
        const file = files[0];
        if (!file.type.startsWith("image/")) {
            alert("Please upload an image file only.");
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewContainer.classList.remove("hidden");
        };
        reader.readAsDataURL(file);

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
    }

    removeFileBtn.addEventListener("click", () => {
        fileInput.value = "";
        imagePreview.src = "";
        previewContainer.classList.add("hidden");
    });

    /* --------------------------------------------------
       Register: Drag & Drop Event Handlers
    -------------------------------------------------- */
    
    regDropZone.addEventListener("click", (e) => {
        if (e.target.closest("#regRemoveFileBtn")) return;
        regFileInput.click();
    });

    ["dragenter", "dragover"].forEach(eventName => {
        regDropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            regDropZone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        regDropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            regDropZone.classList.remove("dragover");
        }, false);
    });

    regDropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleRegFiles(files);
        }
    });

    regFileInput.addEventListener("change", () => {
        if (regFileInput.files.length > 0) {
            handleRegFiles(regFileInput.files);
        }
    });

    function handleRegFiles(files) {
        const file = files[0];
        if (!file.type.startsWith("image/")) {
            alert("Please upload an image file only.");
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            regImagePreview.src = e.target.result;
            regPreviewContainer.classList.remove("hidden");
        };
        reader.readAsDataURL(file);

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        regFileInput.files = dataTransfer.files;
    }

    regRemoveFileBtn.addEventListener("click", () => {
        regFileInput.value = "";
        regImagePreview.src = "";
        regPreviewContainer.classList.add("hidden");
    });

    /* --------------------------------------------------
       Verification Form Submission
    -------------------------------------------------- */

    verifyForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const uid = uidInput.value.trim();
        const file = fileInput.files[0];
        
        if (!uid) {
            alert("Please enter a User ID.");
            return;
        }
        if (!file) {
            alert("Please select or drop a signature specimen image.");
            return;
        }

        setLoading(true);
        resultsWelcome.classList.add("hidden");
        resultsContent.classList.add("hidden");

        const formData = new FormData();
        formData.append("uid", uid);
        formData.append("signature", file);

        fetch("/verify", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok && response.status !== 401) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            setLoading(false);
            resultsContent.classList.remove("hidden");
            
            if (data.success) {
                showSuccessState(data);
            } else {
                showErrorState(data);
            }
        })
        .catch(error => {
            console.error("Verification error:", error);
            setLoading(false);
            resultsContent.classList.remove("hidden");
            showErrorState({
                message: "Server Error. Please ensure the backend is running and dataset is generated."
            });
        });
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            uidInput.disabled = true;
            fileInput.disabled = true;
            removeFileBtn.disabled = true;
            btnSpinner.classList.remove("hidden");
            btnText.textContent = "Processing Signature...";
        } else {
            submitBtn.disabled = false;
            uidInput.disabled = false;
            fileInput.disabled = false;
            removeFileBtn.disabled = false;
            btnSpinner.classList.add("hidden");
            btnText.textContent = "Verify Specimen";
        }
    }

    /* --------------------------------------------------
       Registration Form Submission
    -------------------------------------------------- */

    registerForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const uid = regUidInput.value.trim();
        const name = regNameInput.value.trim();
        const file = regFileInput.files[0];

        if (!uid || !name) {
            showRegAlert(false, "User ID and Full Name are required.");
            return;
        }
        if (!file) {
            showRegAlert(false, "Please upload a reference signature specimen.");
            return;
        }

        setRegLoading(true);
        registerAlert.classList.add("hidden");

        const formData = new FormData();
        formData.append("uid", uid);
        formData.append("name", name);
        formData.append("signature", file);

        fetch("/register", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok && response.status !== 401) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            setRegLoading(false);
            if (data.success) {
                showRegAlert(true, data.message);
                // Clear form inputs
                regUidInput.value = "";
                regNameInput.value = "";
                regFileInput.value = "";
                regImagePreview.src = "";
                regPreviewContainer.classList.add("hidden");
            } else {
                showRegAlert(false, data.message);
            }
        })
        .catch(error => {
            console.error("Registration error:", error);
            setRegLoading(false);
            showRegAlert(false, "Server Error. Failed to register user profile.");
        });
    });

    function setRegLoading(isLoading) {
        if (isLoading) {
            regSubmitBtn.disabled = true;
            regUidInput.disabled = true;
            regNameInput.disabled = true;
            regFileInput.disabled = true;
            regRemoveFileBtn.disabled = true;
            regSpinner.classList.remove("hidden");
            regBtnText.textContent = "Registering Profile...";
        } else {
            regSubmitBtn.disabled = false;
            regUidInput.disabled = false;
            regNameInput.disabled = false;
            regFileInput.disabled = false;
            regRemoveFileBtn.disabled = false;
            regSpinner.classList.add("hidden");
            regBtnText.textContent = "Register Profile";
        }
    }

    function showRegAlert(isSuccess, message) {
        registerAlert.className = isSuccess ? "alert alert-success" : "alert alert-error";
        registerAlertIcon.className = isSuccess ? "fa-solid fa-circle-check" : "fa-solid fa-triangle-exclamation";
        registerAlertMsg.textContent = message;
        registerAlert.classList.remove("hidden");
    }

    /* --------------------------------------------------
       Result Display & State Renderers
    -------------------------------------------------- */

    function showSuccessState(data) {
        // Card styling
        statusCard.className = "result-status-card status-card-success";
        statusIcon.className = "status-icon status-icon-success";
        statusIcon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
        
        statusTitle.textContent = "Signature Match Verified";
        statusTitle.style.color = "var(--success)";
        statusMessage.innerHTML = `Specimen matches records for user <strong>${data.user_name} (ID: ${data.user_id})</strong>.`;

        // Load Images
        refImage.src = data.ref_url;
        refImage.parentElement.parentElement.style.display = "flex"; // show reference container
        queryImage.src = imagePreview.src;
        
        if (data.comparison_url) {
            comparisonOverlay.src = data.comparison_url;
            featureMatchBox.classList.remove("hidden");
        } else {
            featureMatchBox.classList.add("hidden");
        }

        // Animate metrics
        animateResults(data.details);
    }

    function showErrorState(data) {
        // Card styling
        statusCard.className = "result-status-card status-card-error";
        statusIcon.className = "status-icon status-icon-error";
        statusIcon.innerHTML = '<i class="fa-solid fa-circle-xmark"></i>';
        
        statusTitle.textContent = "Verification Mismatch";
        statusTitle.style.color = "var(--error)";
        // The core message requested: "user id or signature not matching"
        statusMessage.innerHTML = `<strong style="font-size: 1.1rem; text-transform: uppercase;">user id or signature not matching</strong>`;

        // For error/mismatch:
        // Hide reference signature (or keep empty/placeholder to protect database)
        refImage.src = "";
        refImage.parentElement.parentElement.style.display = "none";
        
        queryImage.src = imagePreview.src;
        
        // Hide comparison box or show it if we have details
        if (data.comparison_url) {
            comparisonOverlay.src = data.comparison_url;
            featureMatchBox.classList.remove("hidden");
        } else {
            featureMatchBox.classList.add("hidden");
        }

        // Zero out or animate with lower values if details exist
        if (data.details) {
            animateResults(data.details);
        } else {
            animateResults({
                combined_score: 0,
                ssim_score: 0,
                orb_score: 0,
                ncc_score: 0,
                keypoints_detected: { reference: 0, query: 0 },
                good_matches_count: 0
            });
        }
    }

    function animateResults(details) {
        const combined = details.combined_score || 0;
        const ssim = details.ssim_score || 0;
        const orb = details.orb_score || 0;
        const ncc = details.ncc_score || 0;

        // 1. Progress Ring
        const offset = RING_CIRCUMFERENCE - (combined / 100) * RING_CIRCUMFERENCE;
        progressRing.style.strokeDashoffset = offset;
        
        // Change color based on score
        if (combined >= 70.0) {
            progressRing.style.stroke = "var(--success)";
        } else {
            progressRing.style.stroke = "var(--error)";
        }

        // Counter animation for text percentage
        animateValue(scorePercentage, 0, Math.round(combined), 800, "%");

        // 2. Metric progress bars
        setTimeout(() => {
            ssimBar.style.width = `${ssim}%`;
            ssimScore.textContent = `${ssim}%`;

            orbBar.style.width = `${orb}%`;
            orbScore.textContent = `${orb}%`;

            nccBar.style.width = `${ncc}%`;
            nccScore.textContent = `${ncc}%`;
        }, 100);

        // 3. Metadata footer
        const refKps = details.keypoints_detected ? details.keypoints_detected.reference : 0;
        const queryKps = details.keypoints_detected ? details.keypoints_detected.query : 0;
        metaKp.textContent = `${refKps} / ${queryKps}`;
        metaMatches.textContent = details.good_matches_count || 0;
    }

    // Number counting utility
    function animateValue(element, start, end, duration, suffix = "") {
        if (start === end) {
            element.textContent = start + suffix;
            return;
        }
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start) + suffix;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
