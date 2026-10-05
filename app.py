import streamlit as st

# Cấu hình giao diện Streamlit Cloud
st.set_page_config(page_title="Getting Over It Web", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Nút Bấm Chống Chặn Tuyệt Đối 🚀")
st.write("Cách chơi: Nhấp vào nút **PLAY** để bắt đầu. **Chỉ cần click vào các khối đá màu xám** để bẩy người đàn ông tiến lên đỉnh núi màu vàng!")

# Trò chơi dùng nút bấm HTML thuần túy, loại bỏ hoàn toàn Canvas đồ họa để chống lỗi trắng màn hình
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
        #game-container {
            position: relative;
            width: 800px;
            height: 600px;
            border: 4px solid #e94560;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            background: #1a1a2e;
            overflow: hidden;
        }
        /* MÀN HÌNH CHÀO MỪNG */
        #start-screen {
            position: absolute;
            top: 0; left: 0; width: 800px; height: 600px;
            background: rgba(22, 22, 35, 0.98);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 100;
        }
        #start-screen h1 { color: #e94560; font-size: 38px; margin-bottom: 10px; }
        #start-screen p { color: #fff; font-size: 15px; margin-bottom: 25px; text-align: center; max-width: 500px; }
        
        /* NHÂN VẬT CON NGƯỜI (CSS DOM) */
        #player {
            position: absolute;
            width: 30px;
            height: 50px;
            left: 100px;
            top: 500px;
            background: #ff5722; /* Áo màu cam */
            border-radius: 5px;
            transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
            z-index: 10;
            border: 2px solid #fff;
        }
        #player-head {
            position: absolute;
            width: 20px; height: 20px;
            background: #ffdbac; top: -22px; left: 3px;
            border-radius: 50%; border: 2px solid #fff;
        }

        /* ĐỊA HÌNH VÁCH ĐÁ BẰNG HTML BUTTON */
        .rock-btn {
            position: absolute;
            background: #4e4e6a;
            border: 2px solid #fff;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .rock-btn:hover {
            background: #00fff0;
            color: #000;
        }
        #finish-gate {
            position: absolute;
            background: #ffd803;
            border: 3px dashed #fff;
            color: #000;
            font-weight: bold;
            text-align: center;
            line-height: 40px;
            cursor: pointer;
            border-radius: 8px;
        }

        /* GIAO DIỆN UI */
        #ui-time {
            position: absolute; top: 15px; left: 15px;
            color: #00fff0; font-size: 18px; font-weight: bold;
            background: rgba(26, 26, 46, 0.8); padding: 8px 15px;
            border-radius: 8px; border: 1px solid #00fff0; z-index: 50;
        }
        #win-screen {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95); border: 3px solid #ffd803;
            padding: 30px; text-align: center; color: #ffd803;
            font-size: 26px; font-weight: bold; display: none; border-radius: 12px; z-index: 110;
        }
        .btn-action {
            background: #00fff0; color: #161623; border: none;
            padding: 12px 35px; font-size: 18px; border-radius: 20px;
            cursor: pointer; font-weight: bold;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <!-- MENU CHÀO MỪNG -->
        <div id="start-screen">
            <h1>GETTING OVER IT NATIVE</h1>
            <p>PHIÊN BẢN KHÔNG THỂ BỊ CHẶN: Hãy click chuột vào các vách đá xám gần nhân vật để bẩy người đàn ông áo cam nhảy dần lên đỉnh núi màu vàng!</p>
            <button class="btn-action" onclick="pressPlay()">PLAY 🎮</button>
        </div>

        <!-- THANH ĐỒNG HỒ -->
        <div id="ui-time" style="display: none;">⏱️ Thời gian: <span id="timer">0.0</span>s</div>

        <!-- NHÂN VẬT CON NGƯỜI -->
        <div id="player" style="display: none;">
            <div id="player-head"></div>
        </div>

        <!-- ĐỊA HÌNH VÁCH ĐÁ CHỐNG CHẶN -->
        <button class="rock-btn" style="left: 200px; top: 450px; width: 140px; height: 35px;" onclick="jumpTo(250, 390)">Vách Đá 1 ⛰️</button>
        <button class="rock-btn" style="left: 450px; top: 360px; width: 140px; height: 35px;" onclick="jumpTo(500, 300)">Vách Đá 2 ⛰️</button>
        <button class="rock-btn" style="left: 180px; top: 250px; width: 140px; height: 35px;" onclick="jumpTo(230, 190)">Vách Đá 3 ⛰️</button>
        <button class="rock-btn" style="left: 420px; top: 160px; width: 140px; height: 35px;" onclick="jumpTo(470, 100)">Vách Đá 4 ⛰️</button>
        
        <!-- ĐÍCH ĐẾN CHIẾN THẮNG -->
        <div id="finish-gate" style="left: 630px; top: 80px; width: 130px; height: 45px;" onclick="reachGoal()">ĐỈNH VÀNG 🏆</div>

        <!-- MÀN HÌNH CHIẾN THẮNG -->
        <div id="win-screen">
            🏆 BẠN ĐÃ LÊN ĐỈNH NÚI XUẤT SẮC! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Kỷ lục của bạn: <span id="final-time">0</span> giây</span>
            <button class="btn-action" style="background:#ffd803;" onclick="window.location.reload()">Chơi Lượt Mới 🔄</button>
        </div>
    </div>

    <script>
        const player = document.getElementById('player');
        const timerEl = document.getElementById('timer');
        const uiTime = document.getElementById('ui-time');
        const startScreen = document.getElementById('start-screen');
        const winScreen = document.getElementById('win-screen');

        let startTime = 0;
        let isPlaying = false;
        let timerInterval;

        // Bấm nút Play ban đầu
        window.pressPlay = function() {
            startScreen.style.display = 'none';
            player.style.display = 'block';
            uiTime.style.display = 'block';
            isPlaying = true;
            startTime = Date.now();
            
            // Chạy đồng hồ đếm thời gian thực
            timerInterval = setInterval(() => {
                let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                timerEl.innerText = elapsed;
            }, 100);
        };

        // Hàm xử lý nhảy nhân vật bằng hiệu ứng CSS mượt mà
        window.jumpTo = function(targetX, targetY) {
            if (!isPlaying) return;

            // Lấy vị trí hiện tại của nhân vật
            let currentX = parseInt(player.style.left) || 100;
            let currentY = parseInt(player.style.top) || 500;

            // Tính toán khoảng cách (chỉ cho phép nhảy sang vách đá ở gần)
            let distance = Math.hypot(targetX - currentX, targetY - currentY);
            
            if (distance < 350) {
                // Nhảy thành công lên vách đá tiếp theo
                player.style.left = targetX + 'px';
                player.style.top = targetY + 'px';
            } else {
                // Nhảy hụt do quá xa, rơi tự do lại xuống đáy bãi biển đúng tính chất ức chế!
                player.style.left = '100px';
                player.style.top = '500px';
            }
        };

        // Hàm xử lý khi bấm trúng Đỉnh Vàng
        window.reachGoal = function() {
            if (!isPlaying) return;
            
            let currentY = parseInt(player.style.top) || 500;
            // Chỉ được phép thắng khi đang đứng ở vách đá cao nhất (Vách đá 4)
            if (currentY <= 150) {
                isPlaying = false;
                clearInterval(timerInterval);
                player.style.left = '680px';
                player.style.top = '75px';
                
                let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                document.getElementById('final-time').innerText = elapsed;
                winScreen.style.display = 'block';
            } else {
                // Nếu gian lận click đỉnh vàng từ dưới đất -> rơi về vạch xuất phát
                player.style.left = '100px';
                player.style.top = '500px';
            }
        };
    </script>
</body>
</html>
"""

# Xuất bản giao diện game bằng Iframe thuần, đảm bảo không thể bị trắng trang
st.components.v1.html(html_game, height=620, width=820, scrolling=False)

