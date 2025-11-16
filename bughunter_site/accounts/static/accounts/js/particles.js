/* ===== ANIMATED PARTICLE BACKGROUND ===== */

class ParticleBackground {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    
    this.options = {
      particleCount: options.particleCount || 50,
      particleSize: options.particleSize || 2,
      particleSpeed: options.particleSpeed || 0.5,
      particleColor: options.particleColor || 'rgba(123, 92, 255, 0.6)',
      connectionDistance: options.connectionDistance || 150,
      connectionColor: options.connectionColor || 'rgba(123, 92, 255, 0.2)',
      ...options
    };
    
    this.particles = [];
    this.mouse = { x: 0, y: 0 };
    this.canvas = null;
    this.ctx = null;
    
    this.init();
  }
  
  init() {
    this.createCanvas();
    this.createParticles();
    this.bindEvents();
    this.animate();
  }
  
  createCanvas() {
    this.canvas = document.createElement('canvas');
    this.canvas.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    `;
    
    this.container.style.position = 'relative';
    this.container.appendChild(this.canvas);
    
    this.ctx = this.canvas.getContext('2d');
    this.resize();
  }
  
  createParticles() {
    for (let i = 0; i < this.options.particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * this.options.particleSpeed,
        vy: (Math.random() - 0.5) * this.options.particleSpeed,
        size: Math.random() * this.options.particleSize + 1,
        opacity: Math.random() * 0.5 + 0.2
      });
    }
  }
  
  bindEvents() {
    window.addEventListener('resize', () => this.resize());
    
    this.container.addEventListener('mousemove', (e) => {
      const rect = this.container.getBoundingClientRect();
      this.mouse.x = e.clientX - rect.left;
      this.mouse.y = e.clientY - rect.top;
    });
    
    this.container.addEventListener('mouseleave', () => {
      this.mouse.x = -1000;
      this.mouse.y = -1000;
    });
  }
  
  resize() {
    const rect = this.container.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Update particles
    this.particles.forEach(particle => {
      // Move particle
      particle.x += particle.vx;
      particle.y += particle.vy;
      
      // Bounce off edges
      if (particle.x < 0 || particle.x > this.canvas.width) {
        particle.vx *= -1;
      }
      if (particle.y < 0 || particle.y > this.canvas.height) {
        particle.vy *= -1;
      }
      
      // Mouse interaction
      const dx = this.mouse.x - particle.x;
      const dy = this.mouse.y - particle.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 100) {
        const force = (100 - distance) / 100;
        particle.x -= dx * force * 0.01;
        particle.y -= dy * force * 0.01;
      }
    });
    
    // Draw connections
    this.drawConnections();
    
    // Draw particles
    this.drawParticles();
    
    requestAnimationFrame(() => this.animate());
  }
  
  drawParticles() {
    this.particles.forEach(particle => {
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fillStyle = this.options.particleColor.replace(/[\d\.]+\)$/g, `${particle.opacity})`);
      this.ctx.fill();
      
      // Add glow effect
      this.ctx.shadowBlur = 10;
      this.ctx.shadowColor = this.options.particleColor;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
    });
  }
  
  drawConnections() {
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < this.options.connectionDistance) {
          const opacity = 1 - (distance / this.options.connectionDistance);
          this.ctx.beginPath();
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx.strokeStyle = this.options.connectionColor.replace(/[\d\.]+\)$/g, `${opacity * 0.3})`);
          this.ctx.lineWidth = 1;
          this.ctx.stroke();
        }
      }
    }
  }
  
  destroy() {
    if (this.canvas) {
      this.canvas.remove();
    }
  }
}

// Gradient Orb Background
class GradientOrbBackground {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    
    this.options = {
      orbCount: options.orbCount || 3,
      colors: options.colors || [
        'rgba(123, 92, 255, 0.3)',
        'rgba(183, 33, 255, 0.3)',
        'rgba(33, 212, 253, 0.3)'
      ],
      ...options
    };
    
    this.init();
  }
  
  init() {
    this.container.style.position = 'relative';
    this.container.style.overflow = 'hidden';
    
    for (let i = 0; i < this.options.orbCount; i++) {
      this.createOrb(i);
    }
  }
  
  createOrb(index) {
    const orb = document.createElement('div');
    const size = Math.random() * 400 + 200;
    const color = this.options.colors[index % this.options.colors.length];
    
    orb.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      background: radial-gradient(circle, ${color} 0%, transparent 70%);
      border-radius: 50%;
      filter: blur(40px);
      pointer-events: none;
      z-index: 1;
      animation: float-orb-${index} ${15 + Math.random() * 10}s ease-in-out infinite;
    `;
    
    // Random starting position
    orb.style.left = Math.random() * 100 + '%';
    orb.style.top = Math.random() * 100 + '%';
    
    this.container.appendChild(orb);
    
    // Create unique animation for each orb
    const style = document.createElement('style');
    style.textContent = `
      @keyframes float-orb-${index} {
        0%, 100% {
          transform: translate(0, 0) scale(1);
        }
        25% {
          transform: translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px) scale(1.1);
        }
        50% {
          transform: translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px) scale(0.9);
        }
        75% {
          transform: translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px) scale(1.05);
        }
      }
    `;
    document.head.appendChild(style);
  }
}

// Auto-initialize on common containers
document.addEventListener('DOMContentLoaded', () => {
  // Initialize particle background on hero sections
  const heroSection = document.querySelector('.hero-section');
  if (heroSection) {
    heroSection.id = heroSection.id || 'hero-particles';
    new ParticleBackground('hero-particles', {
      particleCount: 30,
      particleSize: 3,
      particleSpeed: 0.3
    });
  }
  
  // Initialize gradient orbs on landing page
  const landingPage = document.querySelector('.landing-page');
  if (landingPage) {
    landingPage.id = landingPage.id || 'landing-orbs';
    new GradientOrbBackground('landing-orbs');
  }
});

// Export classes
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ParticleBackground, GradientOrbBackground };
}