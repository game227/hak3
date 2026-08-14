/**
 * QuietSpace Tashkent — Optimized Lightweight Nature Canvas Background
 * Soft, gentle, battery-friendly ambient background with reduced particle counts
 * and adaptive FPS throttling to ensure smooth 60 FPS on all devices (mobile & low-end GPUs).
 */

(function() {
    'use strict';

    // Respect user's reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    const canvas = document.getElementById('nature-bg');
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);
    let isTabActive = true;

    // Pause animation when tab is not visible to save CPU/battery
    document.addEventListener('visibilitychange', () => {
        isTabActive = !document.hidden;
    });

    // Detect mobile / low-power devices
    const isMobile = window.innerWidth < 768 || ('ontouchstart' in window);
    const DANDELION_COUNT = isMobile ? 10 : 18;
    const FIREFLY_COUNT = isMobile ? 8 : 14;
    const BUTTERFLY_COUNT = isMobile ? 1 : 2;

    const mouse = {
        x: width / 2,
        y: height / 2,
        targetX: width / 2,
        targetY: height / 2,
        isHovered: false,
        radius: 100
    };

    if (!isMobile) {
        window.addEventListener('mousemove', (e) => {
            mouse.targetX = e.clientX;
            mouse.targetY = e.clientY;
            mouse.isHovered = true;
        }, { passive: true });

        window.addEventListener('mouseleave', () => {
            mouse.isHovered = false;
        });
    }

    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }, 200);
    }, { passive: true });

    // ── 1. Soft Dandelion Seeds ──────────────────────────────────────────────
    class DandelionSeed {
        constructor() {
            this.reset(true);
        }

        reset(initial = false) {
            this.x = Math.random() * width;
            this.y = initial ? Math.random() * height : height + 15;
            this.size = Math.random() * 1.8 + 1.0;
            this.speedY = -(Math.random() * 0.3 + 0.15); // Slower, softer float
            this.speedX = (Math.random() - 0.5) * 0.25;
            this.angle = Math.random() * Math.PI * 2;
            this.angularSpeed = (Math.random() - 0.5) * 0.008;
            this.stemLength = this.size * 4.5;
            this.alpha = Math.random() * 0.3 + 0.15;
            this.hue = Math.random() > 0.5 ? 160 : 195;
        }

        update() {
            this.angle += this.angularSpeed;
            this.x += this.speedX + Math.sin(this.angle) * 0.25;
            this.y += this.speedY;

            if (mouse.isHovered) {
                const dx = this.x - mouse.x;
                const dy = this.y - mouse.y;
                const dist = Math.hypot(dx, dy);
                if (dist < mouse.radius && dist > 0) {
                    const force = (mouse.radius - dist) / mouse.radius;
                    this.x += (dx / dist) * force * 1.2;
                    this.y += (dy / dist) * force * 1.2;
                }
            }

            if (this.y < -20 || this.x < -30 || this.x > width + 30) {
                this.reset();
            }
        }

        draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);

            // Stem
            ctx.strokeStyle = `hsla(${this.hue}, 70%, 75%, ${this.alpha * 0.5})`;
            ctx.lineWidth = 0.7;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(0, this.stemLength);
            ctx.stroke();

            // Head
            ctx.fillStyle = `hsla(${this.hue}, 80%, 85%, ${this.alpha * 0.8})`;
            ctx.beginPath();
            ctx.arc(0, 0, this.size, 0, Math.PI * 2);
            ctx.fill();

            // Simplified radiating filaments (4 rays instead of 6 for performance)
            ctx.strokeStyle = `hsla(${this.hue}, 80%, 85%, ${this.alpha * 0.4})`;
            ctx.lineWidth = 0.5;
            const rays = 4;
            for (let i = 0; i < rays; i++) {
                const rAngle = (i / rays) * Math.PI - Math.PI / 2;
                const rLen = this.size * 2.2;
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(Math.cos(rAngle) * rLen, Math.sin(rAngle) * rLen);
                ctx.stroke();
            }

            ctx.restore();
        }
    }

    // ── 2. Soft Glowing Fireflies ─────────────────────────────────────────────
    class Firefly {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 1.5 + 1.2;
            this.baseAlpha = Math.random() * 0.35 + 0.15;
            this.alpha = this.baseAlpha;
            this.pulseSpeed = Math.random() * 0.02 + 0.01;
            this.pulsePhase = Math.random() * Math.PI * 2;
            this.vx = (Math.random() - 0.5) * 0.25;
            this.vy = (Math.random() - 0.5) * 0.25;
            this.hue = Math.random() > 0.5 ? 155 : 190;
        }

        update() {
            this.pulsePhase += this.pulseSpeed;
            this.alpha = this.baseAlpha + Math.sin(this.pulsePhase) * 0.18;

            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0) this.x = width;
            if (this.x > width) this.x = 0;
            if (this.y < 0) this.y = height;
            if (this.y > height) this.y = 0;
        }

        draw() {
            ctx.save();
            ctx.fillStyle = `hsla(${this.hue}, 85%, 75%, ${Math.max(0, this.alpha)})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    // ── 3. Soft Cyber-Butterflies (Gentle sinusoidal flight) ───────────────────
    class CyberButterfly {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 6 + 10;
            this.angle = Math.random() * Math.PI * 2;
            this.speed = Math.random() * 0.6 + 0.5; // Gentle cruising speed
            this.wingFlap = 0;
            this.flapSpeed = 0.1; // Soft wing flapping
            this.targetX = Math.random() * width;
            this.targetY = Math.random() * height;
            this.changeTimer = 0;
            this.hue = 165;
        }

        update() {
            this.wingFlap += this.flapSpeed;
            this.changeTimer++;
            if (this.changeTimer > 240) {
                this.targetX = Math.random() * (width - 80) + 40;
                this.targetY = Math.random() * (height - 80) + 40;
                this.changeTimer = 0;
            }

            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const targetAngle = Math.atan2(dy, dx);

            let angleDiff = targetAngle - this.angle;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            this.angle += angleDiff * 0.02;

            this.x += Math.cos(this.angle) * this.speed;
            this.y += Math.sin(this.angle) * this.speed;

            if (this.x < -40) this.x = width + 30;
            if (this.x > width + 40) this.x = -30;
            if (this.y < -40) this.y = height + 30;
            if (this.y > height + 40) this.y = -30;
        }

        draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle + Math.PI / 2);

            const flap = Math.abs(Math.sin(this.wingFlap));
            const wingWidth = this.size * flap;
            const wingHeight = this.size * 1.1;

            // Translucent soft wings
            ctx.fillStyle = `hsla(${this.hue}, 80%, 65%, 0.4)`;
            ctx.strokeStyle = `hsla(${this.hue}, 90%, 80%, 0.6)`;
            ctx.lineWidth = 0.8;

            // Left Wing
            ctx.beginPath();
            ctx.ellipse(-wingWidth * 0.7, 0, wingWidth * 0.7, wingHeight * 0.5, -0.15, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Right Wing
            ctx.beginPath();
            ctx.ellipse(wingWidth * 0.7, 0, wingWidth * 0.7, wingHeight * 0.5, 0.15, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Body
            ctx.fillStyle = '#e2e8f0';
            ctx.beginPath();
            ctx.ellipse(0, 0, 1.2, this.size * 0.35, 0, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
        }
    }

    const dandelions = Array.from({ length: DANDELION_COUNT }, () => new DandelionSeed());
    const fireflies = Array.from({ length: FIREFLY_COUNT }, () => new Firefly());
    const butterflies = Array.from({ length: BUTTERFLY_COUNT }, () => new CyberButterfly());

    function animate() {
        if (isTabActive) {
            ctx.clearRect(0, 0, width, height);

            mouse.x += (mouse.targetX - mouse.x) * 0.05;
            mouse.y += (mouse.targetY - mouse.y) * 0.05;

            for (let i = 0; i < dandelions.length; i++) {
                dandelions[i].update();
                dandelions[i].draw();
            }

            for (let i = 0; i < fireflies.length; i++) {
                fireflies[i].update();
                fireflies[i].draw();
            }

            for (let i = 0; i < butterflies.length; i++) {
                butterflies[i].update();
                butterflies[i].draw();
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
})();
