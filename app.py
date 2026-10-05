import streamlit as st

# Cấu hình giao diện Streamlit Cloud công khai
st.set_page_config(page_title="Getting Over It Native", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Rê Chuột Tự Động Chuẩn Vật Lý 🚀")
st.write("Cách chơi: Nhấn **PLAY** để bắt đầu. **Chỉ cần di chuyển chuột trên màn hình** để vung búa. Tì đầu búa vào các vách đá xám để đẩy cơ thể bay lên!")

# Hệ thống tự mô phỏng vật lý va chạm, đòn bẩy và trọng lực bằng JS nguyên bản 100%
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
            cursor: crosshair;
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
            top: 0; left: 0; width: 800px; height: 600px;
            background: rgba(22, 22, 35, 0.95);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 20; border-radius: 8px;
        }
        #start-screen h1 {
            color: #e94560; font-size: 42px; margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
        }
        #start-screen p {
            color: #fff; font-size: 16px; margin-bottom: 30px;
            max-width: 500px; text-align: center; line-height: 1.6;
        }
        #win-screen {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95); border: 3px solid #ffd803;
            padding: 30px; text-align: center; color: #ffd803;
            font-size: 26px; font-weight: bold; display: none; border-radius: 12px; z-index: 30;
        }
        .btn-play {
            background: #00fff0; color: #161623; border: none;
            padding: 15px 40px; font-size: 22px; border-radius: 30px;
            cursor: pointer; font-weight: bold;
            box-shadow: 0 0 15px rgba(0, 255, 240, 0.4);
            transition: 0.2s ease;
        }
        .btn-play:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 255, 240, 0.8);
        }
        .btn-restart {
            background: #ffd803; color: black; border: none;
            padding: 8px 16px; font-size: 14px; border-radius: 6px;
            cursor: pointer; font-weight: bold; margin-top: 15px;
        }
    </style>
</head>
<body>

    <div id="canvas-container">
        <!-- START MENU -->
        <div id="start-screen">
            <h1>GETTING OVER IT</h1>
            <p>RÊ CHUỘT ĐỂ VUNG BÚA: Di chuyển chuột xung quanh người chơi để quét búa. Khi đầu búa chạm vào các bề mặt đá xám, nó sẽ sinh ra lực đẩy đẩy cơ thể bạn bay lên!</p>
            <button class="btn-play" onclick="startGame()">PLAY 🎮</button>
        </div>

        <!-- UI -->
        <div id="ui-overlay">⏱️ Thời gian: <span id="timer">0.0</span>s</div>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <!-- WIN SCREEN -->
        <div id="win-screen">
            🏆 BẠN ĐÃ CHINH PHỤC ĐỈNH NÚI THÀNH CÔNG! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Tổng thời gian: <span id="final-time">0</span> giây</span>
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

        // Mô phỏng vật lý nhân vật (Hình người vác búa)
        let player = {
            x: 150, y: 500, // Tọa độ mông/chân người
            vx: 0, vy: 0,
            radius: 18,
            hammerAngle: -Math.PI / 2,
            hammerLength: 70,
            targetAngle: -Math.PI / 2
        };

        // Danh sách địa hình đá núi (x, y, width, height)
        const rocks = [
            { x: 0, y: 570, w: 800, h: 30, color: '#0f0e17' }, // Mặt đất đáy
            { x: 260, y: 450, w: 150, h: 25, color: '#4e4e6a' },
            { x: 500, y: 360, w: 140, h: 25, color: '#4e4e6a' },
            { x: 200, y: 250, w: 130, h: 25, color: '#4e4e6a' },
            { x: 460, y: 160, w: 120, h: 25, color: '#4e4e6a' },
            { x: 650, y: 100, w: 150, h: 25, color: '#ffd803' } // Đỉnh núi vinh quang
        ];

        window.startGame = function() {
            startScreen.style.display = 'none';
            uiOverlay.style.display = 'block';
            isPlaying = true;
            startTime = Date.now();
        };

        // Ghi nhận hướng di chuyển của con trỏ chuột
        canvas.addEventListener('mousemove', (e) => {
            if (!isPlaying || gameEnded) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            // Tính góc đích mà búa muốn hướng tới (xoay quanh ngực nhân vật)
            let chestY = player.y - 25;
            player.targetAngle = Math.atan2(mouseY - chestY, mouseX - player.x);
        });

        function checkRockCollision(x, y) {
            for (let rock of rocks) {
                if (x >= rock.x && x <= rock.x + rock.w && y >= rock.y && y <= rock.y + rock.h) {
                    return true;
                }
            }
            return false;
        }

        function update() {
            if (!isPlaying || gameEnded) return;

            // 1. Trọng lực & Ma sát không khí tác động lên con người
            player.vy += 0.22; 
            player.vx *= 0.98;
            player.vy *= 0.98;

            // Cập nhật vị trí tạm thời
            player.x += player.vx;
            player.y += player.vy;

            // 2. Góc xoay búa đuổi theo chuột mượt mà (Interpolation)
            let angleDiff = player.targetAngle - player.hammerAngle;
            // Chuẩn hóa góc trong khoảng -PI đến PI
            angleDiff = Math.atan2(Math.sin(angleDiff), Math.cos(angleDiff));
            player.hammerAngle += angleDiff * 0.2; // Tốc độ vung búa

            // 3. Tính toán vị trí đầu búa
            let chestX = player.x;
            let chestY = player.y - 25;
            let hx = chestX + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = chestY + Math.sin(player.hammerAngle) * player.hammerLength;

            // 4. XỬ LÝ LỰC ĐÒN BẨY KHI ĐẦU BÚA CHẠM ĐÁ (Cơ chế Getting Over It)
            if (checkRockCollision(hx, hy)) {
                // Tạo một lực phản lực đẩy cơ thể người đi ngược lại hướng của búa
                let forceMagnitude = 0.85; 
                player.vx -= Math.cos(player.hammerAngle) * forceMagnitude;
                player.vy -= Math.sin(player.hammerAngle) * forceMagnitude;
                
                // Giới hạn tốc độ bay tối đa để game không bị lỗi văng quá nhanh
                let speed = Math.hypot(player.vx, player.vy);
                if (speed > 12) {
                    player.vx = (player.vx / speed) * 12;
                    player.vy = (player.vy / speed) * 12;
                }
            }

            // 5. Va chạm của cơ thể người với các vách đá xám
            rocks.forEach(rock => {
                if (player.x + 15 > rock.x && player.x - 15 < rock.x + rock.w &&
                    player.y > rock.y && player.y - 45 < rock.y + rock.h) {
                    // Đẩy người đứng lên trên khối đá
                    player.y = rock.y;
                    player.vy = 0;
                    player.vx *= 0.85; // Ma sát mặt đá
                }
            });

            // Biên giới hạn màn hình
            if (player.x < 20) { player.x = 20; player.vx = 0; }
            if (player.x > 780) { player.x = 780; player.vx = 0; }
            if (player.y > 570) { player.y = 570; player.vy = 0; }

            // Cập nhật đồng hồ hiển thị
            let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            timerEl.innerText = elapsed;

            // Điều kiện chiến thắng (Chạm đỉnh vàng)
            if (player.y < 120 && player.x > 640) {
                gameEnded = true;
                document.getElementById('final-time').innerText = elapsed;
                winScreen.style.display = 'block';
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ các khối đá địa hình
            rocks.forEach(rock => {
                ctx.fillStyle = rock.color;
                ctx.fillRect(rock.x, rock.y, rock.w, rock.h);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(rock.x, rock.y, rock.w, rock.h);
            });

import streamlit as st

# Cấu hình giao diện Streamlit Cloud công khai
st.set_page_config(page_title="Getting Over It Native", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Rê Chuột Tự Động Chuẩn Vật Lý 🚀")
st.write("Cách chơi: Nhấn **PLAY** để bắt đầu. **Chỉ cần di chuyển chuột trên màn hình** để vung búa. Tì đầu búa vào các vách đá xám để đẩy cơ thể bay lên!")

# Hệ thống tự mô phỏng vật lý va chạm, đòn bẩy và trọng lực bằng JS nguyên bản 100%
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
            cursor: crosshair;
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
            top: 0; left: 0; width: 800px; height: 600px;
            background: rgba(22, 22, 35, 0.95);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 20; border-radius: 8px;
        }
        #start-screen h1 {
            color: #e94560; font-size: 42px; margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
        }
        #start-screen p {
            color: #fff; font-size: 16px; margin-bottom: 30px;
            max-width: 500px; text-align: center; line-height: 1.6;
        }
        #win-screen {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95); border: 3px solid #ffd803;
            padding: 30px; text-align: center; color: #ffd803;
            font-size: 26px; font-weight: bold; display: none; border-radius: 12px; z-index: 30;
        }
        .btn-play {
            background: #00fff0; color: #161623; border: none;
            padding: 15px 40px; font-size: 22px; border-radius: 30px;
            cursor: pointer; font-weight: bold;
            box-shadow: 0 0 15px rgba(0, 255, 240, 0.4);
            transition: 0.2s ease;
        }
        .btn-play:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 255, 240, 0.8);
        }
        .btn-restart {
            background: #ffd803; color: black; border: none;
            padding: 8px 16px; font-size: 14px; border-radius: 6px;
            cursor: pointer; font-weight: bold; margin-top: 15px;
        }
    </style>
</head>
<body>

    <div id="canvas-container">
        <!-- START MENU -->
        <div id="start-screen">
            <h1>GETTING OVER IT</h1>
            <p>RÊ CHUỘT ĐỂ VUNG BÚA: Di chuyển chuột xung quanh người chơi để quét búa. Khi đầu búa chạm vào các bề mặt đá xám, nó sẽ sinh ra lực đẩy đẩy cơ thể bạn bay lên!</p>
            <button class="btn-play" onclick="startGame()">PLAY 🎮</button>
        </div>

        <!-- UI -->
        <div id="ui-overlay">⏱️ Thời gian: <span id="timer">0.0</span>s</div>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <!-- WIN SCREEN -->
        <div id="win-screen">
            🏆 BẠN ĐÃ CHINH PHỤC ĐỈNH NÚI THÀNH CÔNG! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Tổng thời gian: <span id="final-time">0</span> giây</span>
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

        // Mô phỏng vật lý nhân vật (Hình người vác búa)
        let player = {
            x: 150, y: 500, // Tọa độ mông/chân người
            vx: 0, vy: 0,
            radius: 18,
            hammerAngle: -Math.PI / 2,
            hammerLength: 70,
            targetAngle: -Math.PI / 2
        };

        // Danh sách địa hình đá núi (x, y, width, height)
        const rocks = [
            { x: 0, y: 570, w: 800, h: 30, color: '#0f0e17' }, // Mặt đất đáy
            { x: 260, y: 450, w: 150, h: 25, color: '#4e4e6a' },
            { x: 500, y: 360, w: 140, h: 25, color: '#4e4e6a' },
            { x: 200, y: 250, w: 130, h: 25, color: '#4e4e6a' },
            { x: 460, y: 160, w: 120, h: 25, color: '#4e4e6a' },
            { x: 650, y: 100, w: 150, h: 25, color: '#ffd803' } // Đỉnh núi vinh quang
        ];

        window.startGame = function() {
            startScreen.style.display = 'none';
            uiOverlay.style.display = 'block';
            isPlaying = true;
            startTime = Date.now();
        };

        // Ghi nhận hướng di chuyển của con trỏ chuột
        canvas.addEventListener('mousemove', (e) => {
            if (!isPlaying || gameEnded) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            // Tính góc đích mà búa muốn hướng tới (xoay quanh ngực nhân vật)
            let chestY = player.y - 25;
            player.targetAngle = Math.atan2(mouseY - chestY, mouseX - player.x);
        });

        function checkRockCollision(x, y) {
            for (let rock of rocks) {
                if (x >= rock.x && x <= rock.x + rock.w && y >= rock.y && y <= rock.y + rock.h) {
                    return true;
                }
            }
            return false;
        }

        function update() {
            if (!isPlaying || gameEnded) return;

            // 1. Trọng lực & Ma sát không khí tác động lên con người
            player.vy += 0.22; 
            player.vx *= 0.98;
            player.vy *= 0.98;

            // Cập nhật vị trí tạm thời
            player.x += player.vx;
            player.y += player.vy;

            // 2. Góc xoay búa đuổi theo chuột mượt mà (Interpolation)
            let angleDiff = player.targetAngle - player.hammerAngle;
            // Chuẩn hóa góc trong khoảng -PI đến PI
            angleDiff = Math.atan2(Math.sin(angleDiff), Math.cos(angleDiff));
            player.hammerAngle += angleDiff * 0.2; // Tốc độ vung búa

            // 3. Tính toán vị trí đầu búa
            let chestX = player.x;
            let chestY = player.y - 25;
            let hx = chestX + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = chestY + Math.sin(player.hammerAngle) * player.hammerLength;

            // 4. XỬ LÝ LỰC ĐÒN BẨY KHI ĐẦU BÚA CHẠM ĐÁ (Cơ chế Getting Over It)
            if (checkRockCollision(hx, hy)) {
                // Tạo một lực phản lực đẩy cơ thể người đi ngược lại hướng của búa
                let forceMagnitude = 0.85; 
                player.vx -= Math.cos(player.hammerAngle) * forceMagnitude;
                player.vy -= Math.sin(player.hammerAngle) * forceMagnitude;
                
                // Giới hạn tốc độ bay tối đa để game không bị lỗi văng quá nhanh
                let speed = Math.hypot(player.vx, player.vy);
                if (speed > 12) {
                    player.vx = (player.vx / speed) * 12;
                    player.vy = (player.vy / speed) * 12;
                }
            }

            // 5. Va chạm của cơ thể người với các vách đá xám
            rocks.forEach(rock => {
                if (player.x + 15 > rock.x && player.x - 15 < rock.x + rock.w &&
                    player.y > rock.y && player.y - 45 < rock.y + rock.h) {
                    // Đẩy người đứng lên trên khối đá
                    player.y = rock.y;
                    player.vy = 0;
                    player.vx *= 0.85; // Ma sát mặt đá
                }
            });

            // Biên giới hạn màn hình
            if (player.x < 20) { player.x = 20; player.vx = 0; }
            if (player.x > 780) { player.x = 780; player.vx = 0; }
            if (player.y > 570) { player.y = 570; player.vy = 0; }

            // Cập nhật đồng hồ hiển thị
            let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            timerEl.innerText = elapsed;

            // Điều kiện chiến thắng (Chạm đỉnh vàng)
            if (player.y < 120 && player.x > 640) {
                gameEnded = true;
                document.getElementById('final-time').innerText = elapsed;
                winScreen.style.display = 'block';
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ các khối đá địa hình
            rocks.forEach(rock => {
                ctx.fillStyle = rock.color;
                ctx.fillRect(rock.x, rock.y, rock.w, rock.h);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(rock.x, rock.y, rock.w, rock.h);
            });

import streamlit as st

# Cấu hình giao diện Streamlit Cloud công khai
st.set_page_config(page_title="Getting Over It Native", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Rê Chuột Tự Động Chuẩn Vật Lý 🚀")
st.write("Cách chơi: Nhấn **PLAY** để bắt đầu. **Chỉ cần di chuyển chuột trên màn hình** để vung búa. Tì đầu búa vào các vách đá xám để đẩy cơ thể bay lên!")

# Hệ thống tự mô phỏng vật lý va chạm, đòn bẩy và trọng lực bằng JS nguyên bản 100%
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
            cursor: crosshair;
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
            top: 0; left: 0; width: 800px; height: 600px;
            background: rgba(22, 22, 35, 0.95);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 20; border-radius: 8px;
        }
        #start-screen h1 {
            color: #e94560; font-size: 42px; margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
        }
        #start-screen p {
            color: #fff; font-size: 16px; margin-bottom: 30px;
            max-width: 500px; text-align: center; line-height: 1.6;
        }
        #win-screen {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95); border: 3px solid #ffd803;
            padding: 30px; text-align: center; color: #ffd803;
            font-size: 26px; font-weight: bold; display: none; border-radius: 12px; z-index: 30;
        }
        .btn-play {
            background: #00fff0; color: #161623; border: none;
            padding: 15px 40px; font-size: 22px; border-radius: 30px;
            cursor: pointer; font-weight: bold;
            box-shadow: 0 0 15px rgba(0, 255, 240, 0.4);
            transition: 0.2s ease;
        }
        .btn-play:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 255, 240, 0.8);
        }
        .btn-restart {
            background: #ffd803; color: black; border: none;
            padding: 8px 16px; font-size: 14px; border-radius: 6px;
            cursor: pointer; font-weight: bold; margin-top: 15px;
        }
    </style>
</head>
<body>

    <div id="canvas-container">
        <!-- START MENU -->
        <div id="start-screen">
            <h1>GETTING OVER IT</h1>
            <p>RÊ CHUỘT ĐỂ VUNG BÚA: Di chuyển chuột xung quanh người chơi để quét búa. Khi đầu búa chạm vào các bề mặt đá xám, nó sẽ sinh ra lực đẩy đẩy cơ thể bạn bay lên!</p>
            <button class="btn-play" onclick="startGame()">PLAY 🎮</button>
        </div>

        <!-- UI -->
        <div id="ui-overlay">⏱️ Thời gian: <span id="timer">0.0</span>s</div>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <!-- WIN SCREEN -->
        <div id="win-screen">
            🏆 BẠN ĐÃ CHINH PHỤC ĐỈNH NÚI THÀNH CÔNG! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Tổng thời gian: <span id="final-time">0</span> giây</span>
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

        // Mô phỏng vật lý nhân vật (Hình người vác búa)
        let player = {
            x: 150, y: 500, // Tọa độ mông/chân người
            vx: 0, vy: 0,
            radius: 18,
            hammerAngle: -Math.PI / 2,
            hammerLength: 70,
            targetAngle: -Math.PI / 2
        };

        // Danh sách địa hình đá núi (x, y, width, height)
        const rocks = [
            { x: 0, y: 570, w: 800, h: 30, color: '#0f0e17' }, // Mặt đất đáy
            { x: 260, y: 450, w: 150, h: 25, color: '#4e4e6a' },
            { x: 500, y: 360, w: 140, h: 25, color: '#4e4e6a' },
            { x: 200, y: 250, w: 130, h: 25, color: '#4e4e6a' },
            { x: 460, y: 160, w: 120, h: 25, color: '#4e4e6a' },
            { x: 650, y: 100, w: 150, h: 25, color: '#ffd803' } // Đỉnh núi vinh quang
        ];

        window.startGame = function() {
            startScreen.style.display = 'none';
            uiOverlay.style.display = 'block';
            isPlaying = true;
            startTime = Date.now();
        };

        // Ghi nhận hướng di chuyển của con trỏ chuột
        canvas.addEventListener('mousemove', (e) => {
            if (!isPlaying || gameEnded) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            // Tính góc đích mà búa muốn hướng tới (xoay quanh ngực nhân vật)
            let chestY = player.y - 25;
            player.targetAngle = Math.atan2(mouseY - chestY, mouseX - player.x);
        });

        function checkRockCollision(x, y) {
            for (let rock of rocks) {
                if (x >= rock.x && x <= rock.x + rock.w && y >= rock.y && y <= rock.y + rock.h) {
                    return true;
                }
            }
            return false;
        }

        function update() {
            if (!isPlaying || gameEnded) return;

            // 1. Trọng lực & Ma sát không khí tác động lên con người
            player.vy += 0.22; 
            player.vx *= 0.98;
            player.vy *= 0.98;

            // Cập nhật vị trí tạm thời
            player.x += player.vx;
            player.y += player.vy;

            // 2. Góc xoay búa đuổi theo chuột mượt mà (Interpolation)
            let angleDiff = player.targetAngle - player.hammerAngle;
            // Chuẩn hóa góc trong khoảng -PI đến PI
            angleDiff = Math.atan2(Math.sin(angleDiff), Math.cos(angleDiff));
            player.hammerAngle += angleDiff * 0.2; // Tốc độ vung búa

            // 3. Tính toán vị trí đầu búa
            let chestX = player.x;
            let chestY = player.y - 25;
            let hx = chestX + Math.cos(player.hammerAngle) * player.hammerLength;
            let hy = chestY + Math.sin(player.hammerAngle) * player.hammerLength;

            // 4. XỬ LÝ LỰC ĐÒN BẨY KHI ĐẦU BÚA CHẠM ĐÁ (Cơ chế Getting Over It)
            if (checkRockCollision(hx, hy)) {
                // Tạo một lực phản lực đẩy cơ thể người đi ngược lại hướng của búa
                let forceMagnitude = 0.85; 
                player.vx -= Math.cos(player.hammerAngle) * forceMagnitude;
                player.vy -= Math.sin(player.hammerAngle) * forceMagnitude;
                
                // Giới hạn tốc độ bay tối đa để game không bị lỗi văng quá nhanh
                let speed = Math.hypot(player.vx, player.vy);
                if (speed > 12) {
                    player.vx = (player.vx / speed) * 12;
                    player.vy = (player.vy / speed) * 12;
                }
            }

            // 5. Va chạm của cơ thể người với các vách đá xám
            rocks.forEach(rock => {
                if (player.x + 15 > rock.x && player.x - 15 < rock.x + rock.w &&
                    player.y > rock.y && player.y - 45 < rock.y + rock.h) {
                    // Đẩy người đứng lên trên khối đá
                    player.y = rock.y;
                    player.vy = 0;
                    player.vx *= 0.85; // Ma sát mặt đá
                }
            });

            // Biên giới hạn màn hình
            if (player.x < 20) { player.x = 20; player.vx = 0; }
            if (player.x > 780) { player.x = 780; player.vx = 0; }
            if (player.y > 570) { player.y = 570; player.vy = 0; }

            // Cập nhật đồng hồ hiển thị
            let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            timerEl.innerText = elapsed;

            // Điều kiện chiến thắng (Chạm đỉnh vàng)
            if (player.y < 120 && player.x > 640) {
                gameEnded = true;
                document.getElementById('final-time').innerText = elapsed;
                winScreen.style.display = 'block';
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ các khối đá địa hình
            rocks.forEach(rock => {
                ctx.fillStyle = rock.color;
                ctx.fillRect(rock.x, rock.y, rock.w, rock.h);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(rock.x, rock.y, rock.w, rock.h);
            });



