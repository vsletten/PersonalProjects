const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Sound effects
const thrustSound = document.getElementById('thrustSound');
const shootSound = document.getElementById('shootSound');
const explosionSound = document.getElementById('explosionSound');

// Game objects
class Ship {
    constructor() {
        this.x = canvas.width / 2;
        this.y = canvas.height / 2;
        this.radius = 15;
        this.angle = 0;
        this.rotation = 0;
        this.thrust = 0;
        this.dx = 0;
        this.dy = 0;
        this.thrusting = false;
        this.invincible = false;
        this.invincibilityTime = 0;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        
        ctx.beginPath();
        ctx.moveTo(20, 0);
        ctx.lineTo(-15, 15);
        ctx.lineTo(-5, 0);
        ctx.lineTo(-15, -15);
        ctx.closePath();
        ctx.strokeStyle = this.invincible ? 'rgba(255, 255, 255, 0.5)' : 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.fill();

        if (this.thrusting) {
            ctx.beginPath();
            ctx.moveTo(-5, 0);
            ctx.lineTo(-15 - Math.random() * 10, 5);
            ctx.lineTo(-15 - Math.random() * 10, -5);
            ctx.closePath();
            ctx.fillStyle = 'rgba(255, 165, 0, 0.7)';
            ctx.fill();
        }

        ctx.restore();
    }

    update() {
        this.angle += this.rotation;
        if (this.thrust) {
            this.dx += Math.cos(this.angle) * 0.1;
            this.dy += Math.sin(this.angle) * 0.1;
            this.thrusting = true;
            if (!thrustSound.paused) thrustSound.currentTime = 0;
            else thrustSound.play();
        } else {
            this.thrusting = false;
            thrustSound.pause();
        }
        this.x += this.dx;
        this.y += this.dy;

        if (this.x < -20) this.x = canvas.width + 20;
        if (this.x > canvas.width + 20) this.x = -20;
        if (this.y < -20) this.y = canvas.height + 20;
        if (this.y > canvas.height + 20) this.y = -20;

        this.dx *= 0.99;
        this.dy *= 0.99;

        if (this.invincible) {
            this.invincibilityTime--;
            if (this.invincibilityTime <= 0) this.invincible = false;
        }
    }

    setInvincible() {
        this.invincible = true;
        this.invincibilityTime = 180; // 3 seconds at 60 FPS
    }
}

class Asteroid {
    constructor(x, y, radius) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.dx = (Math.random() - 0.5) * 2;
        this.dy = (Math.random() - 0.5) * 2;
        this.rotation = (Math.random() - 0.5) * 0.02;
        this.angle = 0;
        this.points = this.generatePoints();
    }

    generatePoints() {
        const points = [];
        const numPoints = 8 + Math.floor(Math.random() * 4);
        for (let i = 0; i < numPoints; i++) {
            const angle = (i / numPoints) * Math.PI * 2;
            const r = this.radius * (0.7 + Math.random() * 0.3);
            points.push({ x: Math.cos(angle) * r, y: Math.sin(angle) * r });
        }
        return points;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        ctx.beginPath();
        ctx.moveTo(this.points[0].x, this.points[0].y);
        for (let i = 1; i < this.points.length; i++) {
            ctx.lineTo(this.points[i].x, this.points[i].y);
        }
        ctx.closePath();
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
    }

    update() {
        this.x += this.dx;
        this.y += this.dy;
        this.angle += this.rotation;

        if (this.x < -this.radius) this.x = canvas.width + this.radius;
        if (this.x > canvas.width + this.radius) this.x = -this.radius;
        if (this.y < -this.radius) this.y = canvas.height + this.radius;
        if (this.y > canvas.height + this.radius) this.y = -this.radius;
    }
}

class Bullet {
    constructor(x, y, angle) {
        this.x = x;
        this.y = y;
        this.dx = Math.cos(angle) * 5;
        this.dy = Math.sin(angle) * 5;
        this.radius = 2;
        this.life = 140;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
    }

    update() {
        this.x += this.dx;
        this.y += this.dy;
        this.life--;

        if (this.x < 0) this.x = canvas.width;
        if (this.x > canvas.width) this.x = 0;
        if (this.y < 0) this.y = canvas.height;
        if (this.y > canvas.height) this.y = 0;
    }
}

// Game state
const ship = new Ship();
let asteroids = [];
let bullets = [];
let score = 0;
let lives = 3;
let level = 1;
let flicker = 0;
let lastFrameTime = performance.now();
const targetFPS = 60;
const frameInterval = 1000 / targetFPS;

spawnAsteroids(level + 4);

function spawnAsteroids(count) {
    asteroids = [];
    for (let i = 0; i < count; i++) {
        let x, y;
        do {
            x = Math.random() * canvas.width;
            y = Math.random() * canvas.height;
        } while (distance(x, y, ship.x, ship.y) < 100);
        asteroids.push(new Asteroid(x, y, 80));
    }
}

// Controls
const keys = {};
window.addEventListener('keydown', (e) => keys[e.code] = true);
window.addEventListener('keyup', (e) => keys[e.code] = false);

function handleControls() {
    if (keys['ArrowLeft']) ship.rotation = -0.05;
    else if (keys['ArrowRight']) ship.rotation = 0.05;
    else ship.rotation = 0;

    ship.thrust = keys['ArrowUp'] ? 0.1 : 0;

    if (keys['Space'] && !keys['spacePressed']) {
        bullets.push(new Bullet(
            ship.x + Math.cos(ship.angle) * 20,
            ship.y + Math.sin(ship.angle) * 20,
            ship.angle
        ));
        shootSound.currentTime = 0;
        shootSound.play();
        keys['spacePressed'] = true;
    }
    if (!keys['Space']) keys['spacePressed'] = false;
}

// Utility functions
function distance(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

function checkCollisions() {
    for (let i = bullets.length - 1; i >= 0; i--) {
        const bullet = bullets[i];
        for (let j = asteroids.length - 1; j >= 0; j--) {
            const asteroid = asteroids[j];
            if (distance(bullet.x, bullet.y, asteroid.x, asteroid.y) < asteroid.radius) {
                bullets.splice(i, 1);
                if (asteroid.radius > 10) {
                    for (let i = 0; i < Math.min(level + 1, 4); i++) {
                        asteroids.push(new Asteroid(asteroid.x, asteroid.y, asteroid.radius / 2));
                    }
                }
                asteroids.splice(j, 1);
                score += 10;
                explosionSound.currentTime = 0;
                explosionSound.play();
                break;
            }
        }
    }

    if (!ship.invincible) {
        for (let i = asteroids.length - 1; i >= 0; i--) {
            const asteroid = asteroids[i];
            if (distance(ship.x, ship.y, asteroid.x, asteroid.y) < asteroid.radius + 15) {
                lives--;
                explosionSound.currentTime = 0;
                explosionSound.play();
                ship.x = canvas.width / 2;
                ship.y = canvas.height / 2;
                ship.dx = 0;
                ship.dy = 0;
                ship.angle = 0;
                ship.setInvincible();
                if (lives <= 0) {
                    alert(`Game Over! Final Score: ${score}`);
                    document.location.reload();
                }
                break;
            }
        }
    }

    if (asteroids.length === 0) {
        level++;
        spawnAsteroids(level + 4);
        ship.setInvincible();
    }
}

// Game loop
function gameLoop(currentTime) {
    const deltaTime = currentTime - lastFrameTime;

    if (deltaTime >= frameInterval) {
        lastFrameTime = currentTime - (deltaTime % frameInterval);

        flicker = (flicker + 1) % 10;
        ctx.fillStyle = flicker < 2 ? 'rgba(0, 0, 0, 0.95)' : 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        handleControls();

        ship.update();
        ship.draw();

        asteroids.forEach(asteroid => {
            asteroid.update();
            asteroid.draw();
        });

        bullets = bullets.filter(bullet => bullet.life > 0);
        bullets.forEach(bullet => {
            bullet.update();
            bullet.draw();
        });

        ctx.fillStyle = 'white';
        ctx.font = '24px Orbitron';
        ctx.fillText(`SCORE: ${score}`, 20, 40);
        ctx.fillText(`LIVES: ${lives}`, 20, 70);
        ctx.fillText(`LEVEL: ${level}`, 20, 100);

        checkCollisions();
    }

    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);

setInterval(() => {}, 1000);