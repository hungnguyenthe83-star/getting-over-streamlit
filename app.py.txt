import streamlit as st

# Cấu hình trang web Streamlit
st.set_page_config(page_title="Getting Over It Mini", page_icon="⚒️", layout="centered")

st.title("⚒️ Getting Over It - Phiên bản Mini Ức Chế")
st.write("Cách chơi: **Nhấn và giữ chuột** vào đầu cây búa (vòng tròn nhỏ), sau đó **kéo và thả** để tạo lực đẩy chiếc chum leo qua các chướng ngại vật lên đỉnh núi!")

# Nhúng mã nguồn HTML/JS tích hợp thư viện vật lý Matter.js
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
            background: #1a1a2e;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        #canvas-container {
            position: relative;
            width: 800px;
            height: 600px;
            border: 4px solid #e94560;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        #win-screen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(26, 26, 46, 0.95);
            border: 3px solid #00fff0;
            padding: 30px;
            text-align: center;
            color: #00fff0;
            font-size: 28px;
            font-weight: bold;
            display: none;
            border-radius: 10px;
            z-index: 10;
        }
        button {
            background: #e94560;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 15px;
        }
    </style>
    <!-- Tải thư viện mô phỏng vật lý Matter.js từ CDN -->
    <script src="https://cloudflare.com"></script>
</head>
<body>

    <div id="canvas-container">
        <div id="win-screen">
            🎉 BẠN ĐÃ LÊN ĐỈNH NÚI THÀNH CÔNG! 🎉<br>
            <span style="font-size: 16px; color: #fff;">Bạn có một sự kiên nhẫn phi thường.</span><br>
            <button onclick="window.location.reload()">Chơi Lại 🔄</button>
        </div>
    </div>

    <script>
        // Khai báo các mô-đun của Matter.js
        const { Engine, Render, Runner, Bodies, Composite, Constraint, Mouse, MouseConstraint, Events } = Matter;

        // 1. Khởi tạo Engine vật lý và bộ dựng hình Render
        const engine = Engine.create();
        const container = document.getElementById('canvas-container');
        
        const render = Render.create({
            element: container,
            engine: engine,
            options: {
                width: 800,
                height: 600,
                wireframes: false,
                background: '#161623'
            }
        });

        Render.run(render);
        const runner = Runner.create();
        Runner.run(runner, engine);

        // 2. Tạo nhân vật: Chum nước và chiếc Búa leo núi
        // Thân dưới (Chiếc chum)
        const pot = Bodies.circle(150, 500, 30, { 
            density: 0.005,
            friction: 0.2,
            render: { fillStyle: '#e94560' }
        });

        // Cán búa và Đầu búa
        const handle = Bodies.rectangle(150, 440, 10, 90, {
            density: 0.001,
            collisionFilter: { group: -1 }, // Không tự va chạm với chum
            render: { fillStyle: '#ffffff' }
        });

        const hammerHead = Bodies.circle(150, 390, 15, {
            density: 0.01,
            friction: 0.8,
            render: { fillStyle: '#00fff0' }
        });

        // Liên kết các bộ phận lại thành một khối thống nhất bằng Constraint
        const joint1 = Constraint.create({
            bodyA: pot,
            bodyB: handle,
            pointA: { x: 0, y: -20 },
            pointB: { x: 0, y: 45 },
            stiffness: 0.9,
            length: 0,
            render: { visible: false }
        });

        const joint2 = Constraint.create({
            bodyA: handle,
            bodyB: hammerHead,
            pointA: { x: 0, y: -45 },
            pointB: { x: 0, y: 0 },
            stiffness: 0.9,
            length: 0,
            render: { visible: false }
        });

        Composite.add(engine.world, [pot, handle, hammerHead, joint1, joint2]);

        // 3. Xây dựng bản đồ địa hình (Các vách đá ức chế)
        const ground = Bodies.rectangle(400, 590, 800, 20, { isStatic: true, render: { fillStyle: '#0f0e17' } });
        
        // Các bậc đá từ thấp lên cao
        const rock1 = Bodies.rectangle(300, 480, 160, 30, { isStatic: true, render: { fillStyle: '#a7a9be' } });
        const rock2 = Bodies.rectangle(500, 380, 140, 30, { isStatic: true, render: { fillStyle: '#a7a9be' } });
        const rock3 = Bodies.rectangle(300, 260, 120, 30, { isStatic: true, render: { fillStyle: '#a7a9be' } });
        const rock4 = Bodies.rectangle(550, 150, 200, 30, { isStatic: true, render: { fillStyle: '#ffd803' } }); // Đỉnh núi chiến thắng

        // Tường bao quanh để không bay ra ngoài màn hình
        const leftWall = Bodies.rectangle(5, 300, 10, 600, { isStatic: true, render: { fillStyle: '#0f0e17' } });
        const rightWall = Bodies.rectangle(795, 300, 10, 600, { isStatic: true, render: { fillStyle: '#0f0e17' } });

        Composite.add(engine.world, [ground, rock1, rock2, rock3, rock4, leftWall, rightWall]);

        // 4. Cho phép người dùng dùng chuột tương tác kéo/thả đầu búa
        const mouse = Mouse.create(render.canvas);
        const mouseConstraint = MouseConstraint.create(engine, {
            mouse: mouse,
            constraint: {
                stiffness: 0.2,
                render: { visible: true, color: '#00fff0' }
            }
        });

        Composite.add(engine.world, mouseConstraint);
        render.mouse = mouse;

        // 5. Kiểm tra điều kiện chiến thắng (Khi cái chum leo lên tới đỉnh rock4)
        Events.on(engine, 'afterUpdate', function() {
            if (pot.position.y < 120 && pot.position.x > 450) {
                document.getElementById('win-screen').style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

# Render trò chơi vào Streamlit
st.components.v1.html(html_game, height=620, width=820)
