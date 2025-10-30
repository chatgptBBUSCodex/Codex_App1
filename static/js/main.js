const state = {
    rainInterval: null,
    audioPlayed: false,
};

document.addEventListener('DOMContentLoaded', () => {
    const heroTitle = document.getElementById('hero-title');
    const audioElement = document.getElementById('hero-audio');
    const rainContainer = document.getElementById('rain-container');
    const menuToggle = document.getElementById('menu-toggle');
    const slideMenu = document.getElementById('slide-menu');
    const closeMenu = document.getElementById('close-menu');
    const consultationTrigger = document.getElementById('consultation-trigger');
    const modal = document.getElementById('consultation-modal');
    const modalClose = document.getElementById('modal-close');
    const pianoTypeGrid = document.getElementById('piano-type-grid');
    const pianoTypeInput = document.getElementById('piano_type');
    const inquiryForm = document.getElementById('inquiry-form');
    const toast = document.getElementById('toast');

    function startRain() {
        if (state.rainInterval || !rainContainer) return;
        state.rainInterval = setInterval(() => {
            const drop = document.createElement('span');
            drop.className = 'rain-drop';
            drop.style.left = `${Math.random() * 100}%`;
            drop.style.animationDuration = `${1 + Math.random()}s`;
            rainContainer.appendChild(drop);
            setTimeout(() => drop.remove(), 2000);
        }, 120);
    }

    function stopRain() {
        if (state.rainInterval) {
            clearInterval(state.rainInterval);
            state.rainInterval = null;
        }
        rainContainer?.querySelectorAll('.rain-drop').forEach((drop) => drop.remove());
    }

    function playAudioOnce() {
        if (!audioElement) return;
        audioElement.currentTime = 0;
        audioElement.play().catch(() => {
            /* ignore autoplay restrictions */
        });
    }

    if (heroTitle) {
        heroTitle.addEventListener('mouseenter', () => {
            if (!state.audioPlayed) {
                playAudioOnce();
                state.audioPlayed = true;
            }
            startRain();
        });

        heroTitle.addEventListener('mouseleave', () => {
            stopRain();
        });
    }

    function openMenu() {
        slideMenu.classList.add('open');
    }

    function closeMenuPanel() {
        slideMenu.classList.remove('open');
    }

    menuToggle?.addEventListener('click', openMenu);
    closeMenu?.addEventListener('click', closeMenuPanel);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMenuPanel();
            closeModal();
        }
    });

    function openModal() {
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }

    function closeModal() {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }

    consultationTrigger?.addEventListener('click', () => {
        openModal();
    });

    modalClose?.addEventListener('click', () => {
        closeModal();
    });

    modal?.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    pianoTypeGrid?.addEventListener('click', (event) => {
        const target = event.target;
        if (target instanceof HTMLButtonElement && target.dataset.slug) {
            pianoTypeGrid.querySelectorAll('.piano-type-btn').forEach((btn) => btn.classList.remove('active'));
            target.classList.add('active');
            pianoTypeInput.value = target.dataset.slug;
        }
    });

    function showErrors(errors) {
        document.querySelectorAll('.error').forEach((el) => {
            const field = el.dataset.errorFor;
            if (field && errors[field]) {
                el.textContent = errors[field].join(' ');
            } else {
                el.textContent = '';
            }
        });
    }

    function showToast(message) {
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }

    inquiryForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(inquiryForm);
        try {
            const response = await fetch(inquiryForm.action, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                showErrors({});
                inquiryForm.reset();
                pianoTypeGrid?.querySelectorAll('.piano-type-btn').forEach((btn) => btn.classList.remove('active'));
                pianoTypeInput.value = '';
                closeModal();
                showToast('Cảm ơn bạn! Chúng tôi sẽ liên hệ sớm.');
                if (window.dataLayer) {
                    window.dataLayer.push({ event: 'inquiry_submitted' });
                }
            } else {
                const data = await response.json().catch(() => ({ errors: {} }));
                showErrors(data.errors || {});
            }
        } catch (error) {
            console.error('Inquiry submission failed', error);
            showToast('Có lỗi xảy ra. Vui lòng thử lại.');
        }
    });
});
