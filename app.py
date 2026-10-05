import streamlit as st

# Cấu hình giao diện Streamlit Cloud
st.set_page_config(page_title="Getting Over It Native", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Siêu Cấp Chống Chặn 🚀")
st.write("Cách chơi: **Bấm giữ chuột trái** vào chiếc chum màu đỏ, **kéo rê** để di chuyển và móc chiếc búa vào các vách đá để leo lên đỉnh!")

# Game sử dụng mã HTML5 Canvas nguyên bản, không cần tải bất kỳ thư viện nào từ mạng
html_game = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #161623;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        #canvas-container {
            position: relative;
            width: 800px;
            height: 600px;
            border: 4px solid #e94560;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            background: #1a1a2e;
        }
        canvas {
            display: block;
            border-radius: 8px;
        }
        #ui-overlay {
            position: absolute;
            top: 15px;
            left: 15px;
            color: #00fff0;
            font-size: 18px;
            font-weight: bold;
            pointer-events: none;
            background: rgba(26, 26, 46, 0.8);
            padding: 8px 15px;
            border-radius: 8px;
            border: 1px solid #00fff0;
        }
        #win-screen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95);
            border: 3px solid #ffd803;
            padding: 30px;
            text-align: center;
            color: #ffd803;
            font-size: 26px;
            font-weight: bold;
            display: none;
            border-radius: 12px;
        }
        button {
            background: #ffd803;
            color: black;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
</head>
<body>

    <div id="canvas-container">
        <div id="ui-overlay">⏱️ Thời gian: <span id="timer">0.0</span>s</div>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div id="win-screen">
            🏆 BẠN ĐÃ LÊN ĐỈNH NÚI SUẤT SẮC! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Kỷ lục của bạn: <span id="final-time">0</span> giây</span>
            <button onclick="window.location.reload()">Chơi Lượt Mới 🔄</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const timerEl = document.getElementById('timer');
        const winScreen = document.getElementById('win-screen');

        // Vật lý và thông số nhân vật
        let player = {
            x: 150, y: 500,
            vx: 0, vy: 0,
            radius: 25,
            hammerAngle: 0,
            hammerLength: 70
        };

        // Các vách đá cố định (x, y, width, height)
        const rocks = [
            { x: 0, y: 580, w: 800, h: 20, color: '#0f0e17' }, // Đất nền
            { x: 250, y: 460, w: 150, h: 25, color: '#4e4e6a' },
            { x: 500, y: 370, w: 140, h: 25, color: '#4e4e6a' },
            { x: 200, y: 260, w: 130, h: 25, color: '#4e4e6a' },
            { x: 450, y: 160, w: 110, h: 25, color: '#4e4e6a' },
            { x: 650, y: 100, w: 150, h: 25, color: '#ffd803' }  // Bậc chiến thắng màu vàng
        ];

        let isDragging = false;
        let startTime = Date.now();
        let gameEnded = false;

        // Bắt sự kiện chuột tương tác kéo búa
        canvas.addEventListener('mousedown', (e) => {
            if (gameEnded) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            // Nếu bấm chuột gần vị trí chiếc chum
            let dist = Math.hypot(mouseX - player.x, mouseY - player.y);
            if (dist < 80) {
                isDragging = true;
            }
        });

        canvas.addEventListener('mousemove', (e) => {
            if (!isDragging || gameEnded) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            // Tính toán góc của cây búa dựa trên vị trí chuột kéo
            player.hammerAngle = Math.atan2(mouseY - player.y, mouseX - player.x);
            
            // Đầu búa dựa theo góc xoay
            let hx = player.x + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = player.y + Math.sin(player.hammerAngle) * player.hammerLength;

            // Kiểm tra đầu búa có tì vào đá không để tạo lực đẩy
            rocks.forEach(rock => {
                if (hx >= rock.x && hx <= rock.x + rock.w && hy >= rock.y && hy <= rock.y + rock.h) {
                    // Tạo lực đẩy ngược lại hướng kéo của búa
                    player.vx -= Math.cos(player.hammerAngle) * 0.8;
                    player.vy -= Math.sin(player.hammerAngle) * 0.8;
                }
            });
        });

        window.addEventListener('mouseup', () => { isDragging = false; });

        // Vòng lặp cập nhật chuyển động cơ bản
        function update() {
            if (gameEnded) return;

            // Áp dụng trọng lực và ma sát cơ bản
            player.vy += 0.25; 
            player.vx *= 0.98;
            player.vy *= 0.98;

            player.x += player.vx;
            player.y += player.vy;

            // Xử lý va chạm của chiếc chum với các khối vách đá
            rocks.forEach(rock => {
                // Kiểm tra va chạm hộp chữ nhật cơ bản
                if (player.x + player.radius > rock.x && player.x - player.radius < rock.x + rock.w &&
                    player.y + player.radius > rock.y && player.y - player.radius < rock.y + rock.h) {
                    
                    // Đẩy nhân vật ra khỏi vách đá nếu lún sâu
                    player.y = rock.y - player.radius;
                    player.vy = -player.vy * 0.2; // Nảy nhẹ
                    player.vx *= 0.8;
                }
            });

            // Giới hạn biên màn hình
            if (player.x - player.radius < 0) { player.x = player.radius; player.vx = 0; }
            if (player.x + player.radius > 800) { player.x = 800 - player.radius; player.vx = 0; }

            // Cập nhật đồng hồ thời gian
            let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            timerEl.innerText = elapsed;

            // Điều kiện chiến thắng (Chạm vào bậc đá màu vàng trên cùng bên phải)
            if (player.y < 120 && player.x > 640) {
                gameEnded = true;
                document.getElementById('final-time').innerText = elapsed;
                winScreen.style.display = 'block';
            }
        }

        // Vẽ đồ họa lên màn hình
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ các vách đá địa hình
            rocks.forEach(rock => {
                ctx.fillStyle = rock.color;
                ctx.fillRect(rock.x, rock.y, rock.w, rock.h);
                // Vẽ viền đá
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                ctx.strokeRect(rock.x, rock.y, rock.w, rock.h);
            });

            // 2. Vẽ cán búa và đầu búa
            let hx = player.x + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = player.y + Math.sin(player.hammerAngle) * player.hammerLength;

            ctx.beginPath();
            ctx.moveTo(player.x, player.y);
            ctx.lineTo(hx, hy);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 5;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(hx, hy, 10, 0, Math.PI * 2);
            ctx.fillStyle = '#00fff0';
            ctx.fill();

            // 3. Vẽ chiếc chum nước (Nhân vật chính)
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
            ctx.fillStyle = '#e94560';
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }

        // Khởi động vòng lặp trò chơi
        gameLoop();
    </script>
</body>
</html>
"""

# Render đoạn code nguyên bản chống mọi bộ chặn lên trang web Streamlit
st.components.v1.html(html_game, height=620, width=820, scrolling=False)
