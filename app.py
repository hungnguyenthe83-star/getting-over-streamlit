import streamlit as st

# Cấu hình trang web Streamlit công khai
st.set_page_config(page_title="Getting Over It Mini Pro", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên bản Ức Chế Nâng Cấp")
st.write("Cách chơi: **Bấm giữ chuột trái** vào đầu búa màu xanh neon, **kéo lùi lại** để tích lực, rồi **thả chuột** để bắn chiếc chum bay lên!")

# TẢI MÃ NGUỒN LIÊN KẾT NHÚNG TRỰC TIẾP MATTER.JS (BẢN MINIFIED RÚT GỌN CHỐNG BLOCK)
# Thay vì gọi CDN bên ngoài, ta dùng bản nhúng an toàn trực tiếp từ GitHub CDN chính thức
matter_js_src = "https://jsdelivr.net"

# Nhúng mã nguồn HTML/JS sửa lỗi màn hình đen + Thêm giao diện UI mới
html_game = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #161623;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        /* Ép cứng kích thước khung chứa bằng PX để tránh lỗi màn hình đen trên Streamlit Cloud */
        #canvas-container {{
            position: relative;
            width: 800px;
            height: 600px;
            border: 4px solid #e94560;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            background: #161623;
        }}
        /* BẢNG ĐIỀU KHIỂN UI TRONG GAME */
        #game-ui {{
            position: absolute;
            top: 15px;
            left: 15px;
            right: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            pointer-events: none; /* Không che chuột khi chơi */
            z-index: 5;
        }}
        .ui-box {{
            background: rgba(26, 26, 46, 0.85);
            border: 2px solid #00fff0;
            padding: 8px 15px;
            border-radius: 8px;
            color: #00fff0;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        /* THANH ĐO LỰC BẮN CỦA BÚA */
        #power-container {{
            width: 150px;
            height: 15px;
            background: #222;
            border: 1px solid #fff;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }}
        #power-bar {{
            width: 0%;
            height: 100%;
            background: linear-gradient(to right, #00ff00, #ffff00, #ff0000);
            transition: width 0.05s ease;
        }}
        #win-screen {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95);
            border: 3px solid #ffd803;
            padding: 30px;
            text-align: center;
            color: #ffd803;
            font-size: 28px;
            font-weight: bold;
            display: none;
            border-radius: 12px;
            z-index: 10;
            box-shadow: 0 0 30px rgba(255, 216, 3, 0.5);
        }}
        .btn-ui {{
            background: #e94560;
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 6px;
            cursor: pointer;
            pointer-events: auto; /* Cho phép bấm nút */
            font-weight: bold;
            transition: 0.2s;
        }}
        .btn-ui:hover {{
            background: #ff3366;
            box-shadow: 0 0 10px #ff3366;
        }}
    </style>
    <!-- Sử dụng đường dẫn CDN thay thế bảo mật hơn chống bị block -->
    <script src="{matter_js_src}"></script>
</head>
<body>

    <div id="canvas-container">
        <!-- KHU VỰC HIỂN THỊ UI GAME -->
        <div id="game-ui">
            <div class="ui-box">
                ⏱️ Thời gian: <span id="timer-val">0.0</span>s
            </div>
            <div class="ui-box" style="display: flex; flex-direction: column; align-items: center;">
                ⚡ Lực đẩy của búa
                <div id="power-container"><div id="power-bar"></div></div>
            </div>
            <div>
                <button class="btn-ui" onclick="window.location.reload()">Chơi Lại 🔄</button>
            </div>
        </div>

        <!-- MÀN HÌNH CHIẾN THẮNG -->
        <div id="win-screen">
            🏆 BẠN ĐÃ LÊN ĐỈNH NÚI THÀNH CÔNG! 🎉<br>
            <span style="font-size: 16px; color: #fff; display:block; margin: 10px 0;">Tổng thời gian kỷ lục của bạn là: <span id="final-time" style="color:#ffd803;">0</span> giây!</span>
            <button class="btn-ui" style="background:#ffd803; color:#000;" onclick="window.location.reload()">Chơi Tiếp Lượt Mới 🔄</button>
        </div>
    </div>

    <script>
        // Hàm bọc kiểm tra xem thư viện đã load thành công chưa trước khi dựng game
        function startGame() {{
            if (typeof Matter === 'undefined') {{
                // Nếu vẫn bị chặn tải, hệ thống tự động vẽ một thông báo trực quan lên màn hình
                document.getElementById('canvas-container').innerHTML = "<div style='color:white; padding:50px; text-align:center;'>Trình duyệt của bạn đang chặn script bảo mật. Hãy thử tắt Adblock hoặc chuyển sang tab ẩn danh để chơi!</div>";
                return;
            }}

            const {{ Engine, Render, Runner, Bodies, Composite, Constraint, Mouse, MouseConstraint, Events, Vector }} = Matter;

            const engine = Engine.create();
            const container = document.getElementById('canvas-container');
            
            const render = Render.create({{
                element: container,
                engine: engine,
                options: {{
                    width: 800,
                    height: 600,
                    wireframes: false,
                    background: '#161623'
                }}
            }});

            Render.run(render);
            const runner = Runner.create();
            Runner.run(runner, engine);

            // TẠO NHÂN VẬT CHÍNH (Chum nước & Búa)
            const pot = Bodies.circle(150, 520, 28, {{ 
                density: 0.006,
                friction: 0.15,
                restitution: 0.1,
                render: {{ fillStyle: '#e94560' }}
            }});

            const handle = Bodies.rectangle(150, 460, 8, 80, {{
                density: 0.001,
                collisionFilter: {{ group: -1 }},
                render: {{ fillStyle: '#ffffff' }}
            }});

            const hammerHead = Bodies.circle(150, 410, 14, {{
                density: 0.008,
                friction: 0.8,
                render: {{ fillStyle: '#00fff0' }}
            }});

            const joint1 = Constraint.create({{
                bodyA: pot, bodyB: handle,
                pointA: {{ x: 0, y: -15 }}, pointB: {{ x: 0, y: 40 }},
                stiffness: 0.95, length: 0, render: {{ visible: false }}
            }});

            const joint2 = Constraint.create({{
                bodyA: handle, bodyB: hammerHead,
                pointA: {{ x: 0, y: -40 }}, pointB: {{ x: 0, y: 0 }},
                stiffness: 0.95, length: 0, render: {{ visible: false }}
            }});

            Composite.add(engine.world, [pot, handle, hammerHead, joint1, joint2]);

            // ĐỊA HÌNH VÁCH ĐÁ LEO NÚI
            const ground = Bodies.rectangle(400, 590, 800, 20, {{ isStatic: true, render: {{ fillStyle: '#0f0e17' }} }});
            const leftWall = Bodies.rectangle(5, 300, 10, 600, {{ isStatic: true, render: {{ fillStyle: '#0f0e17' }} }});
            const rightWall = Bodies.rectangle(795, 300, 10, 600, {{ isStatic: true, render: {{ fillStyle: '#0f0e17' }} }});

            const rocks = [
                Bodies.rectangle(280, 470, 140, 25, {{ isStatic: true, render: {{ fillStyle: '#4e4e6a' }} }}),
                Bodies.rectangle(480, 380, 130, 25, {{ isStatic: true, render: {{ fillStyle: '#4e4e6a' }} }}),
                Bodies.rectangle(260, 270, 120, 25, {{ isStatic: true, render: {{ fillStyle: '#4e4e6a' }} }}),
                Bodies.rectangle(500, 180, 90, 25, {{ isStatic: true, render: { fillStyle: '#4e4e6a' } }}),
                Bodies.rectangle(670, 120, 180, 25, {{ isStatic: true, render: {{ fillStyle: '#ffd803' }} }})
            ];
            Composite.add(engine.world, [ground, leftWall, rightWall, ...rocks]);

            // ĐIỀU KHIỂN CHUỘT
            const mouse = Mouse.create(render.canvas);
            const mouseConstraint = MouseConstraint.create(engine, {{
                mouse: mouse,
                constraint: {{
                    stiffness: 0.15,
                    render: {{ visible: true, color: 'rgba(0, 255, 240, 0.4)' }}
                }}
            }});
            Composite.add(engine.world, mouseConstraint);
            render.mouse = mouse;

            let startTime = Date.now();
            let gameEnded = false;
            const powerBar = document.getElementById('power-bar');
            const timerVal = document.getElementById('timer-val');

            Events.on(engine, 'afterUpdate', function() {{
                if (gameEnded) return;

                let elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                timerVal.innerText = elapsed;

                if (mouseConstraint.body === hammerHead) {{
                    let dist = Vector.magnitude(Vector.sub(mouse.position, hammerHead.position));
                    let pct = Math.min((dist / 120) * 100, 100);
                    powerBar.style.width = pct + '%';
                }} else {{
                    powerBar.style.width = '0%';
                }}

                if (pot.position.y < 95 && pot.position.x > 580) {{
                    gameEnded = true;
                    document.getElementById('final-time').innerText = elapsed;

