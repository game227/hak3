/**
 * QuietSpace Tashkent — Interactive Cyber-Nature UI Controllers
 * Soft, gentle, battery-friendly animations and controllers.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── 1. Dynamic Typing Placeholder Effect for AI Search Bar ────────────────
    const aiInput = document.getElementById('ai-search-input');
    if (aiInput) {
        const prompts = [
            "Chorsu atrofida 100 Mbps internet va Zoom uchun tinch joy...",
            "Minor metrosi yaqinida 24/7 ochiq bo‘lgan sokin kovorking...",
            "Mirobod tumanida kitob o‘qish uchun jimjit qahvaxona...",
            "Mutlaq sokin kutubxona yoki arzon study zone..."
        ];
        let pIndex = 0;
        let charIndex = 0;
        let isDeleting = false;

        function typeLoop() {
            const currentText = prompts[pIndex];
            if (isDeleting) {
                aiInput.setAttribute('placeholder', currentText.substring(0, charIndex - 1));
                charIndex--;
            } else {
                aiInput.setAttribute('placeholder', currentText.substring(0, charIndex + 1));
                charIndex++;
            }

            let typeSpeed = isDeleting ? 25 : 55;

            if (!isDeleting && charIndex === currentText.length) {
                typeSpeed = 2600; // Comfortable pause
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                pIndex = (pIndex + 1) % prompts.length;
                typeSpeed = 400;
            }

            setTimeout(typeLoop, typeSpeed);
        }
        typeLoop();
    }

    // ── 2. Soft & Gentle 3D Card Hover on Desktop ─────────────────────────────
    const isMobile = window.innerWidth < 768;
    if (!isMobile) {
        const tiltCards = document.querySelectorAll('.tilt-card-wrap');
        tiltCards.forEach(cardWrap => {
            const card = cardWrap.querySelector('.zen-glass-card');
            if (!card) return;

            cardWrap.addEventListener('mousemove', (e) => {
                const rect = cardWrap.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                // Soft 2.5 degree max tilt
                const rotateX = ((y - centerY) / centerY) * -2.5;
                const rotateY = ((x - centerX) / centerX) * 2.5;

                card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-3px)`;
            }, { passive: true });

            cardWrap.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0)';
            });
        });
    }

    // ── 3. 3D Table Seat Selection with Elevation on Z-Axis ───────────────────
    const seatPods = document.querySelectorAll('.zen-seat-pod');
    seatPods.forEach(pod => {
        pod.addEventListener('click', function() {
            if (this.classList.contains('occupied')) {
                alert("Ushbu stol hozirda band!");
                return;
            }

            // Remove selected class from others in the same group
            const parentGrid = this.closest('.zen-3d-grid');
            if (parentGrid) {
                parentGrid.querySelectorAll('.zen-seat-pod').forEach(s => s.classList.remove('selected'));
            }

            this.classList.add('selected');

            // Update hidden input or booking state if available
            const tableId = this.getAttribute('data-table-id');
            const tableInput = document.getElementById('selected-table-input');
            if (tableInput) {
                tableInput.value = tableId;
            }

            const tableNumDisplay = document.getElementById('selected-table-num-display');
            if (tableNumDisplay) {
                tableNumDisplay.textContent = `#${this.getAttribute('data-table-num') || tableId}`;
            }
        });
    });

    // ── 4. SVG Circular Speed Gauge Animation ────────────────────────────────
    const speedGauges = document.querySelectorAll('.speed-gauge-wrap');
    speedGauges.forEach(gauge => {
        const valCircle = gauge.querySelector('.gauge-val');
        const speed = parseFloat(gauge.getAttribute('data-speed') || 100);
        if (valCircle) {
            const percent = Math.min(100, Math.max(0, (speed / 200) * 100));
            const offset = 100 - (percent * 0.85);
            setTimeout(() => {
                valCircle.style.strokeDashoffset = offset;
            }, 300);
        }
    });
});
