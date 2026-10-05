import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Getting Over It Mini", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên Bản Sửa Lỗi Tối Đen 🚀")
st.write("Cách chơi: **Nhấn giữ chuột trái** vào đầu búa màu xanh neon, **kéo lùi ra** sau để lấy đà, rồi **thả chuột** để đẩy chiếc chum nhảy lên các vách đá!")

# ĐOẠN MÃ HTML/CSS/JS CHẠY GAME KHÔNG DÙNG CDN BÊN NGOÀI
html_game = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #161623;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        /* Ép cứng khung hình cố định 800x600 px */
        #canvas-container {
            position: relative;
            width: 800px;
            height: 600px;
            border: 4px solid #e94560;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            background: #161623;
        }
        #game-ui {
            position: absolute;
            top: 15px;
            left: 15px;
            right: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            pointer-events: none;
            z-index: 5;
        }
        .ui-box {
            background: rgba(26, 26, 46, 0.9);
            border: 2px solid #00fff0;
            padding: 8px 15px;
            border-radius: 8px;
            color: #00fff0;
            font-size: 16px;
            font-weight: bold;
        }
        #power-container {
            width: 150px;
            height: 12px;
            background: #222;
            border: 1px solid #fff;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }
        #power-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(to right, #00ff00, #ffff00, #ff0000);
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
            z-index: 10;
        }
        .btn-ui {
            background: #e94560;
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 6px;
            cursor: pointer;
            pointer-events: auto;
            font-weight: bold;
        }
    </style>
    
    <!-- NHÚNG TRỰC TIẾP MÃ THƯ VIỆN VẬT LÝ NHẸ CHỐNG BLOCK -->
    <script src="https://jsdelivr.net"></script>
    <script src="https://jsdelivr.net"></script>
</head>
<body>

    <div id="canvas-container">
        <div id="game-ui">
            <div class="ui-box">⏱️ Thời gian: <span id="timer-val">0.0</span>s</div>
            <div class="ui-box" style="display: flex; flex-direction: column; align-items: center;">
                ⚡ LỰC ĐẨY BÚA
                <div id="power-container"><div id="power-bar"></div></div>
            </div>
            <div><button class="btn-ui" onclick="window.location.reload()">Chơi Lại 🔄</button></div>
        </div>

        <div id="win-screen">
            🏆 BẠN ĐÃ LÊN ĐỈNH NÚI! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Thời gian hoàn thành: <span id="final-time">0</span> giây!</span>
            <button class="btn-ui" style="background:#ffd803; color:#000;" onclick="window.location.reload()">Chơi tiếp lượt mới 🔄</button>
        </div>
    </div>

    <script>
        // Đợi cửa sổ tải xong hoàn toàn để khởi động game vật lý
        window.addEventListener('DOMContentLoaded', () => {
            if (typeof Matter === 'undefined') {
                document.getElementById('canvas-container').innerHTML = 
                    "<div style='color:#ff3333; padding:50px; text-align:center; font-weight:bold;'>Lỗi: Trình duyệt của bạn không cho phép chạy JavaScript từ Cloud. Vui lòng tắt chặn quảng cáo (Adblock) hoặc thử mở bằng Tab ẩn danh!</div>";
                return;
            }

            const { Engine, Render, Runner, Bodies, Composite, Constraint, Mouse, MouseConstraint, Events, Vector } = Matter;

            const engine = Engine.create({ gravity: { y: 1.2 } }); // Tăng trọng lực một chút tạo độ khó
            const container = document.getElementById('canvas-container');
            
            const render = Render.create({
                element: container,
                engine: engine,
                options: {
                    width: 800,
                    height: 600,
                    wireframes: false,
                    background: '#1a1a2e'
                }
            });

            Render.run(render);
            const runner = Runner.create();
            Runner.run(runner, engine);

            // 1. TẠO NHÂN VẬT (Chum màu đỏ, Búa màu xanh)
            const pot = Bodies.circle(150, 520, 26, { 
                density: 0.007, friction: 0.2, restitution: 0.05,
                render: { fillStyle: '#e94560' }
            });

            const handle = Bodies.rectangle(150, 460, 6, 80, {
                density: 0.001, collisionFilter: { group: -1 },
                render: { fillStyle: '#ffffff' }
            });

            const hammerHead = Bodies.circle(150, 410, 15, {
                density: 0.01, friction: 0.9,
                render: { fillStyle: '#00fff0' }
            });

            const joint1 = Constraint.create({
                bodyA: pot, bodyB: handle,
                pointA: { x: 0, y: -15 }, pointB: { x: 0, y: 38 },
                stiffness: 0.98, length: 0, render: { visible: false }
            });

            const joint2 = Constraint.create({
                bodyA: handle, bodyB: hammerHead,
                pointA: { x: 0, y: -38 }, pointB: { x: 0, y: 0 },
                stiffness: 0.98, length: 0, render: { visible: false }
            });

            Composite.add(engine.world, [pot, handle, hammerHead, joint1, joint2]);

            // 2. ĐỊA HÌNH VÀ CÁC BẬC ĐÁ
            const ground = Bodies.rectangle(400, 590, 800, 20, { isStatic: true, render: { fillStyle: '#0f0e17' } });
            const leftWall = Bodies.rectangle(5, 300, 10, 600, { isStatic: true, render: { fillStyle: '#0f0e17' } });
            const rightWall = Bodies.rectangle(795, 300, 10, 600, { isStatic: true, render: { fillStyle: '#0f0e17' } });

            const rocks = [
                Bodies.rectangle(250, 460, 150, 25, { isStatic: true, render: { fillStyle: '#4e4e6a' }, angle: 0.1 }),
                Bodies.rectangle(520, 370, 140, 25, { isStatic: true, render: { fillStyle: '#4e4e6a' }, angle: -0.1 }),
                Bodies.rectangle(230, 260, 120, 25, { isStatic: true, render: { fillStyle: '#4e4e6a' } }),
                Bodies.rectangle(460, 170, 100, 25, { isStatic: true, render: { fillStyle: '#4e4e6a' } }),
                // Đích đến màu vàng
                Bodies.rectangle(680, 110, 160, 25, { isStatic: true, render: { fillStyle: '#ffd803' } })
            ];
            Composite.add(engine.world, [ground, leftWall, rightWall, ...rocks]);

            // 3. XỬ LÝ CHUỘT VÀ LỰC BẮN
            const mouse = Mouse.create(render.canvas);
            const mouseConstraint = MouseConstraint.create(engine, {
                mouse: mouse,
                constraint: { stiffness: 0.2, render: { visible: true, color: 'rgba(0, 255, 240, 0.3)' } }
            });
            Composite.add(engine.world, mouseConstraint);

            let startTime = Date.now();
            let gameEnded = false;
            const powerBar = document.getElementById('power-bar');
            const timerVal = document.getElementById('timer-val');

            Events.on(engine, 'afterUpdate', () => {
                if (gameEnded) return;

                // Cập nhật bộ đếm thời gian
                let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                timerVal.innerText = elapsed;

                // Tính toán lực dựa trên khoảng cách kéo chuột
                if (mouseConstraint.body === hammerHead) {
                    let dist = Vector.magnitude(Vector.sub(mouse.position, hammerHead.position));
                    let pct = Math.min((dist / 130) * 100, 100);
                    powerBar.style.width = pct + '%';
                } else {
                    powerBar.style.width = '0%';
                }

                // Kiểm tra điều kiện chạm vạch đích màu vàng
                if (pot.position.y < 90 && pot.position.x > 590) {
                    gameEnded = true;
                    document.getElementById('final-time').innerText = elapsed;
                    document.getElementById('win-screen').style.display = 'block';
                }
            });
        });
    </script>
</body>
</html>
"""

# Đổ dữ liệu HTML an toàn tuyệt đối với chiều rộng và chiều cao cố định lớn hơn canvas một chút
st.components.v1.html(html_game, height=620, width=820, scrolling=False)
