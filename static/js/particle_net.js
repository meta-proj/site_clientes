// static/js/particle_net.js

document.addEventListener('DOMContentLoaded', () => {
    // Verifica se o container de fundo existe
    const container = document.getElementById('particle-net-bg');
    if (!container) {
        console.error("Container #particle-net-bg não encontrado. A animação não será iniciada.");
        return;
    }

    // --- 1. Configuração e Inicialização do Canvas ---
    let W = window.innerWidth;
    let H = window.innerHeight;
    
    // Cria e configura o elemento Canvas
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    canvas.style.display = 'block'; 
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');

    // Cores da sua paleta (tons suaves de Marrom)
    // Cores ajustadas para MAIOR VISIBILIDADE (Opacidade mais alta)
    const LINE_COLOR = "rgba(90, 51, 52, 1)"; // Linhas discretas, mas mais visíveis (70% opacidade)
    const PARTICLE_COLOR = "rgba(166, 101, 103, 1)"; // Partículas (90% opacidade)
    
    const MAX_PARTICLES = 160;
    const LINE_DISTANCE = 120; 
    const particles = [];

    // --- 2. Classe de Partícula ---
    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * W;
            this.y = Math.random() * H;
            this.radius = Math.random() * 2 + 1; 
            
            // Movimento lento e aleatório
            this.vx = Math.random() * 0.4 - 0.2; 
            this.vy = Math.random() * 0.4 - 0.2;

            // Lógica de pulsação (acende e apaga) - Ajustado para ser mais visível
            this.alpha = Math.random() * 0.5 + 0.4; // Opacidade inicial entre 0.4 e 0.9
            this.pulseRate = Math.random() * 0.005 + 0.001; 
            this.pulsingUp = (Math.random() > 0.5);
        }

        draw() {
            // Atualiza a posição
            this.x += this.vx;
            this.y += this.vy;

            // Mantém a bolinha dentro da tela (rebate nas bordas)
            if (this.x < 0 || this.x > W) this.vx *= -1;
            if (this.y < 0 || this.y > H) this.vy *= -1;
            
            // Lógica de pulsação (modifica o alpha para simular o "acender")
            if (this.pulsingUp) {
                this.alpha += this.pulseRate;
            } else {
                this.alpha -= this.pulseRate;
            }

            // NOVOS LIMITES DE BRILHO (mais visível)
            if (this.alpha > 0.95) this.pulsingUp = false; 
            if (this.alpha < 0.4) this.pulsingUp = true;
            this.alpha = Math.max(0.4, Math.min(0.95, this.alpha)); 

            // Desenha a bolinha
            ctx.fillStyle = PARTICLE_COLOR;
            ctx.globalAlpha = this.alpha;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // --- 3. Conexão das Partículas ---
    function drawLines() {
        ctx.strokeStyle = LINE_COLOR;
        ctx.lineWidth = 0.5;

        for (let i = 0; i < particles.length; i++) {
            for (let j = i; j < particles.length; j++) {
                const p1 = particles[i];
                const p2 = particles[j];
                
                const distance = Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));

                if (distance < LINE_DISTANCE) {
                    // Opacidade da linha decai com a distância
                    const lineAlpha = 1 - (distance / LINE_DISTANCE);
                    
                    ctx.globalAlpha = lineAlpha * 0.7; // Aumentado para 0.7 para linhas mais visíveis
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
    }

    // --- 4. Loop da Animação ---
    function animate() {
        // Limpa a tela com a cor de fundo (F4F4F4)
        ctx.fillStyle = 'rgba(244, 244, 244, 1)'; 
        ctx.fillRect(0, 0, W, H);
        
        drawLines();

        for (const p of particles) {
            p.draw();
        }
        
        requestAnimationFrame(animate);
    }

    // --- 5. Inicialização e Eventos ---
    function init() {
        for (let i = 0; i < MAX_PARTICLES; i++) {
            particles.push(new Particle());
        }
        animate();
    }
    
    // Redimensionamento
    window.addEventListener('resize', () => {
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W;
        canvas.height = H;
    });

    init();
});