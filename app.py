import streamlit as st

# Cấu hình giao diện Streamlit Cloud
st.set_page_config(page_title="Getting Over It Native", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Rê Chuột Tự Động 🚀")
st.write("Cách chơi: Nhấn **PLAY** để bắt đầu. **Chỉ cần di chuyển chuột trên màn hình** (không cần bấm nút), cây búa sẽ tự động tì vào các vách đá xám để đẩy người đi!")

# Game HTML5 Canvas nâng cấp nhân vật con người và cơ chế di chuột tự do
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
            cursor: crosshair; /* Thay đổi con trỏ chuột trong vùng chơi */
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
            display: none;
        }
        #start-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 800px;
            height: 600px;
            background: rgba(22, 22, 35, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 20;
            border-radius: 8px;
        }
        #start-screen h1 {
            color: #e94560;
            font-size: 42px;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
        }
        #start-screen p {
            color: #fff;
            font-size: 16px;
            margin-bottom: 30px;
            max-width: 500px;
            text-align: center;
            line-height: 1.6;
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
            z-index: 30;
        }
        .btn-play {
            background: #00fff0;
            color: #161623;
            border: none;
            padding: 15px 40px;
            font-size: 22px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(0, 255, 240, 0.4);
            transition: 0.2s ease;
        }
        .btn-play:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 255, 240, 0.8);
        }
        .btn-restart {
            background: #ffd803;
            color: black;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 15px;
        }
    </style>
</head>
<body>

    <div id="canvas-container">
        <div id="start-screen">
            <h1>GETTING OVER IT MINI</h1>
            <p>CƠ CHẾ MỚI: Chỉ cần di chuyển con trỏ chuột, chiếc búa trên tay người leo núi sẽ tự động xoay và tì bẩy cơ thể bay lên cao!</p>
            <button class="btn-play" onclick="startGame()">PLAY 🎮</button>
        </div>

        <div id="ui-overlay">⏱️ Thời gian: <span id="timer">0.0</span>s</div>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div id="win-screen">
            🏆 BẠN ĐÃ LÊN ĐỈNH NÚI XUẤT SẮC! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Kỷ lục của bạn: <span id="final-time">0</span> giây</span>
            <button class="btn-restart" onclick="window.location.reload()">Chơi Lượt Mới 🔄</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const timerEl = document.getElementById('timer');
        const winScreen = document.getElementById('win-screen');
        const uiOverlay = document.getElementById('ui-overlay');
        const startScreen = document.getElementById('start-screen');

        let isPlaying = false;
        let gameEnded = false;
        let startTime = 0;

        // Cấu trúc nhân vật hình CON NGƯỜI
        let player = {
            x: 150, y: 500,
            vx: 0, vy: 0,
            height: 50, // Chiều cao cơ thể người
            width: 20,  // Độ rộng thân người
            hammerAngle: -Math.PI/2,
            hammerLength: 75
        };

        // Địa hình vách đá
        const rocks = [
            { x: 0, y: 580, w: 800, h: 20, color: '#0f0e17' },
            { x: 260, y: 460, w: 160, h: 25, color: '#4e4e6a' },
            { x: 520, y: 380, w: 140, h: 25, color: '#4e4e6a' },
            { x: 220, y: 270, w: 130, h: 25, color: '#4e4e6a' },
            { x: 470, y: 170, w: 120, h: 25, color: '#4e4e6a' },
            { x: 650, y: 110, w: 150, h: 25, color: '#ffd803' }
        ];

        function startGame() {
            startScreen.style.display = 'none';
            uiOverlay.style.display = 'block';
            isPlaying = true;
            startTime = Date.now();
        }

        // THAY ĐỔI LỚN: Tự động cập nhật góc búa CHỈ CẦN DI CHUỘT (Không cần click)
        canvas.addEventListener('mousemove', (e) => {
            if (!isPlaying || gameEnded) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            // Góc búa tính từ ngực/tay nhân vật (player.x, player.y - 20)
            player.hammerAngle = Math.atan2(mouseY - (player.y - 20), mouseX - player.x);
            
            let hx = player.x + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = (player.y - 20) + Math.sin(player.hammerAngle) * player.hammerLength;

            // Kiểm tra đầu búa chạm đá để tự tạo lực đẩy liên tục
            rocks.forEach(rock => {
                if (hx >= rock.x && hx <= rock.x + rock.w && hy >= rock.y && hy <= rock.y + rock.h) {
                    player.vx -= Math.cos(player.hammerAngle) * 0.95; // Tạo lực đẩy phản lực sinh động
                    player.vy -= Math.sin(player.hammerAngle) * 0.95;
                }
            });
        });

        function update() {
            if (!isPlaying || gameEnded) return;

            player.vy += 0.28; // Trọng lực nặng hơn một chút tăng độ khó
            player.vx *= 0.97;
            player.vy *= 0.97;

            player.x += player.vx;
            player.y += player.vy;

            // Xử lý va chạm thân người với vách đá
            rocks.forEach(rock => {
                if (player.x + 15 > rock.x && player.x - 15 < rock.x + rock.w &&
                    player.y > rock.y && player.y - player.themeHeight < rock.y + rock.h) {
                    
                    player.y = rock.y;
                    player.vy = -player.vy * 0.1;
                    player.vx *= 0.7;
                }
            });

            // Giới hạn biên màn hình không cho người bay ra ngoài
            if (player.x < 20) { player.x = 20; player.vx = 0; }
            if (player.x > 780) { player.x = 780; player.vx = 0; }
            if (player.y > 580) { player.y = 580; player.vy = 0; }

            let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            timerEl.innerText = elapsed;

            // Chạm đỉnh vàng chiến thắng
            if (player.y < 130 && player.x > 640) {
                gameEnded = true;
                document.getElementById('final-time').innerText = elapsed;
                winScreen.style.display = 'block';
            }
        }

        // VẼ ĐỒ HỌA HÌNH CON NGƯỜI
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ các vách đá địa hình
            rocks.forEach(rock => {
                ctx.fillStyle = rock.color;
                ctx.fillRect(rock.x, rock.y, rock.w, rock.h);
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                ctx.strokeRect(rock.x, rock.y, rock.w, rock.h);
            });

            // Định vị ngực người để vẽ tay và cán búa
            let chestX = player.x;
            let chestY = player.y - 25;

            // 2. Vẽ chiếc búa leo núi
            let hx = chestX + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = chestY + Math.sin(player.hammerAngle) * player.hammerLength;

            ctx.beginPath();
            ctx.moveTo(chestX, chestY);
            ctx.lineTo(hx, hy);
            ctx.strokeStyle = '#d2d2d2';
            ctx.lineWidth = 4;
            ctx.stroke();

            // Vẽ đầu búa lớn hình chữ T
            ctx.save();
            ctx.translate(hx, hy);
            ctx.rotate(player.hammerAngle + Math.PI/2);
            ctx.fillStyle = '#00fff0';
            ctx.fillRect(-12, -4, 24, 8); // Lưỡi búa nằm ngang
            ctx.restore();

            // 3. VẼ MÔ HÌNH CON NGƯỜI (Bằng các nét hình học đơn giản)
            // Vẽ Đầu con người
            ctx.beginPath();

