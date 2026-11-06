# REAL-TIME NETWORK TRAFFIC CLASSIFICATION SYSTEM USING ONLINE MACHINE LEARNING
## Hệ Thống Phân Loại Lưu Lượng Mạng Thời Gian Thực Sử Dụng Online Machine Learning

---

## 1. Giới Thiệu Đề Tài & Bối Cảnh Nghiên Cứu

Trong kỷ nguyên chuyển đổi số và bùng nổ hạ tầng Internet, lưu lượng mạng máy tính không ngừng gia tăng cả về quy mô lẫn độ phức tạp. Việc giám sát và phân loại lưu lượng mạng (Network Traffic Classification) đóng vai trò sống còn trong quản trị hệ thống, tối ưu chất lượng dịch vụ (QoS), kiểm soát băng thông và phát hiện sớm các nguy cơ an ninh mạng.

### 1.1. Hạn chế của các phương pháp truyền thống
* **Phương pháp dựa vào cổng (Port-based Classification):** Đối chiếu số hiệu cổng mạng (Port) với danh mục IANA. Phương pháp này không còn hiệu quả do các ứng dụng hiện đại sử dụng cơ chế cấp phát cổng động (Dynamic Ports) hoặc ngụy trang truyền thông qua các cổng phổ biến (như Port 443 của HTTPS).
* **Phương pháp thanh tra gói tin sâu (Deep Packet Inspection - DPI):** Quét phần nội dung (Payload) để tìm chuỗi nhận dạng đặc trưng. Phương pháp này tiêu tốn rất lớn tài nguyên xử lý (CPU/RAM), và hoàn toàn thất bại trước xu thế mã hóa dữ liệu đầu cuối toàn cầu (TLS/SSL, HTTPS, giao thức VPN).

### 1.2. Hướng tiếp cận hiện đại
Hệ thống giải quyết triệt để bài toán lưu lượng mã hóa bằng cách không can thiệp hay giải mã nội dung Payload, đảm bảo tuyệt đối quyền riêng tư. Thay vào đó, hệ thống tập trung phân tích các **đặc trưng hình thái, cấu trúc thống kê luồng (Flow-level Statistical Features)** kết hợp cùng kỹ thuật **Trí tuệ nhân tạo** để nhận diện và phân loại luồng dữ liệu thời gian thực.

---

## 2. Kiến Trúc Hệ Thống Tổng Thể

Hệ thống được thiết kế theo mô hình phân tán 3 phân hệ độc lập:

```
+-----------------------------------------------------------------------------------+
|                                  NGUỒN DỮ LIỆU                                    |
|             Card mạng trực tiếp (NIC Live)   /   Tệp tin PCAP/PCAPNG               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        PHÂN HỆ TRẠM TÁC VỤ (NETWORK AGENT)                        |
|  * Packet Sniffer (Scapy / PyShark / TShark)                                      |
|  * Packet-to-Flow Aggregator (Gom luồng chuẩn 5-Tuple, Quản lý Timeout & FIN/RST) |
|  * Feature Extractor (Trích xuất vector 81 đặc trưng thống kê luồng)              |
|  * Lõi AI: Hybrid Inference (Rule-based SNI + ResNet-18) & Online Machine Learning|
+-----------------------------------------+-----------------------------------------+
                                          | HTTP POST (JSON Log)
                                          v
+-----------------------------------------------------------------------------------+
|                     PHÂN HỆ MÁY CHỦ TRUNG TÂM (BACKEND SERVER)                    |
|  * Framework: FastAPI (Xử lý I/O bất đồng bộ hiệu năng cao)                       |
|  * Bảo mật: Xác thực người dùng bằng JSON Web Token (JWT)                         |
|  * Cơ sở dữ liệu: PostgreSQL (Lưu trữ lịch sử luồng, tài khoản quản trị)          |
|  * Real-time Engine: WebSocket Broadcast đẩy dữ liệu tức thì xuống Dashboard      |
|  * PCAP Processor: Endpoint tiếp nhận và xử lý tệp PCAP tải lên                   |
+-----------------------------------------+-----------------------------------------+
                                          | WebSocket / REST API
                                          v
+-----------------------------------------------------------------------------------+
|                    PHÂN HỆ GIAO DIỆN NGƯỜI DÙNG (FRONTEND DASHBOARD)               |
|  * Công nghệ: ReactJS, Vite, Recharts, Tailwind CSS                               |
|  * Bảng điều khiển thời gian thực (Real-time Dashboard & KPI Cards)               |
|  * Phân tích tệp PCAP trực tuyến (Kéo thả file & hiển thị phân tách Flow)         |
|  * Quản trị hệ thống: Bật/Tắt Agent từ xa, Lịch sử lưu lượng, Xuất báo cáo CSV    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Các Tính Năng Hiện Có Của Hệ Thống

1. **Thu thập dữ liệu mạng thời gian thực:** Lắng nghe trực tiếp trên các giao diện mạng vật lý (Ethernet, Wi-Fi) bằng Scapy với cơ chế kiểm soát bộ nhớ chống tràn RAM.
2. **Trích xuất đặc trưng thống kê:** Tích hợp bộ tính toán CICFlowMeter trích xuất vector 81 đặc trưng toán học (thời gian hoạt động, IAT, độ dài gói tin, cờ TCP,...).
3. **Lõi suy luận AI lai (Hybrid AI Core):**
   * **Tầng 1 (Rule-based SNI/DNS):** Bóc tách tên miền máy chủ từ bản tin TLS Client Hello và truy vấn DNS để nhận dạng tức thì các ứng dụng phổ thông.
   * **Tầng 2 (Mạng nơ-ron ResNet-18):** Chuyển đổi vector đặc trưng thành ma trận ảnh $9 \times 9 \times 3$, đưa qua mạng CNN nhận dạng luồng mã hóa phức tạp (VPN).
   * **Động cơ dung hợp quyết định (Parallel Decision-Level Fusion):** Phân xử xung đột giữa AI và Rule-based (phân biệt Chat vs VoIP gọi thoại, CDN hệ sinh thái Google/Microsoft).
4. **Hỗ trợ nhận diện 11 nhãn lưu lượng:**
   `Streaming`, `VPN-VoIP`, `VPN-chat`, `VPN-email`, `VPN-file_transfer`, `VPN-p2p`, `VPN-streaming`, `VoIP`, `chat`, `email`, `file_transfer`.
5. **Máy chủ API & Giao diện Dashboard:**
   * Tiếp nhận log qua API bất đồng bộ FastAPI, lưu trữ vào cơ sở dữ liệu.
   * Phát sóng dữ liệu tức thời qua WebSocket (`/ws/realtime`) lên Dashboard ReactJS không có độ trễ.
   * Cung cấp các chức năng xem lịch sử, quản lý tài khoản, bật/tắt trạm thu thập mạng và xuất dữ liệu báo cáo ra tệp CSV.

---

## 4. Nội Dung Và Yêu Cầu Nâng Cấp Cho Đồ Án Tốt Nghiệp

Dựa trên định hướng nâng cấp chuyên sâu cho đồ án tốt nghiệp, hệ thống tập trung hoàn thiện và mở rộng các trụ cột kỹ thuật trọng tâm sau:

### 4.1. Chuyển dịch sang Học máy trực tuyến (Online Machine Learning)
* **Vấn đề của mô hình cũ:** Mô hình học sâu truyền thống được huấn luyện ngoại tuyến (Offline Batch Training). Khi môi trường mạng thực tế biến đổi, xuất hiện các dịch vụ hoặc giao thức mới, mô hình không có khả năng tự thích ứng và gặp hiện tượng suy giảm độ chính xác (**Concept Drift**).
* **Nội dung nâng cấp:**
  * Ứng dụng các thuật toán **Online / Incremental Machine Learning** (thích hợp với luồng dữ liệu stream liên tục như: *Hoeffding Tree, Adaptive Random Forest, SGDClassifier / PassiveAggressive Classifier*, tích hợp thư viện chuyên dụng như `River`).
  * Xây dựng cơ chế phát hiện trôi dạt khái niệm (**Concept Drift Detection** - sử dụng thuật toán ADWIN / DDM) để nhận diện khi đặc tính lưu lượng thay đổi.
  * Thiết lập chu trình tự thích ứng và cập nhật trọng số trực tiếp theo thời gian thực (*Incremental Fit / Partial Fit*) trên từng luồng mạng mới mà không cần huấn luyện lại toàn bộ dữ liệu từ đầu.

### 4.2. Xử lý đa nguồn dữ liệu (Card mạng trực tiếp & Tệp tin PCAP)
* **Thu thập trực tiếp từ card mạng (Live Capture):** Tối ưu hóa hiệu năng bắt gói tin từ card mạng của máy tính hoặc thiết bị giám sát chuyên dụng, hạn chế tối đa rớt gói khi lưu lượng tăng đột biến.
* **Đọc và phân tích tệp tin PCAP (Offline PCAP Processing):**
  * Xây dựng chức năng cho phép người dùng kéo thả hoặc tải lên các tệp tin lưu lượng mạng định dạng `.pcap`, `.pcapng` từ Wireshark.
  * Tự động bóc tách các luồng trong file, trích xuất đặc trưng và đưa qua mô hình phân loại để xuất kết quả kiểm tra nhanh chóng.

### 4.3. Xây dựng bộ gom Packet thành Flow chuẩn mạng (Packet-to-Flow Aggregator)
* **Định danh luồng chuẩn 5-Tuple:** Xây dựng cơ chế gom nhóm các gói tin thô thành các luồng mạng hoàn chỉnh dựa trên 5 thông số:
  $$\text{Flow ID} = \langle \text{Source IP}, \text{Destination IP}, \text{Source Port}, \text{Destination Port}, \text{Protocol} \rangle$$
* **Quản lý vòng đời luồng mạng (Flow Lifecycle Management):**
  * Quản lý trạng thái luồng song phương (Bi-directional forward/backward).
  * Xử lý đóng luồng chủ động khi phát hiện các cờ điều khiển TCP `FIN` hoặc `RST`.
  * Cơ chế ngắt luồng theo ngưỡng thời gian không hoạt động (*Idle Timeout*) và thời gian hoạt động tối đa (*Active Timeout*).
* **Công cụ hỗ trợ:** Tận dụng và phối hợp linh hoạt các công cụ: Wireshark/TShark, Scapy, PyShark hoặc CICFlowMeter.

### 4.4. Mở rộng phân hệ quản trị, thống kê và cảnh báo
* **Phân hệ quản trị:**
  * Quản lý danh mục loại lưu lượng và nhãn phân loại tùy chỉnh.
  * Thiết lập các tiêu chuẩn và ngưỡng phân loại phù hợp với từng môi trường mạng.
  * Duyệt và kiểm soát tính hợp lệ của dữ liệu lưu lượng đầu vào.
* **Phân hệ báo cáo thống kê:**
  * Báo cáo phân phối lưu lượng mạng theo loại ứng dụng và giao thức theo thời gian (ngày, tuần, tháng).
  * Báo cáo theo dõi hiệu năng của mô hình phân loại (độ chính xác, độ trễ suy luận) theo dữ liệu vận hành thực tế.
  * Hỗ trợ xuất báo cáo toàn diện dưới dạng file CSV và PDF.

---

## 5. Cấu Trúc Thư Mục Dự Án (Project Structure)

```
Network-Monitoring/
├── README.md                           # Tài liệu tổng quan kiến trúc và hướng dẫn đồ án
├── .gitignore                          # Cấu hình loại trừ file rác, bộ nhớ tạm, dữ liệu nhạy cảm
│
├── backend_api/                        # PHÂN HỆ MÁY CHỦ TRUNG TÂM (FASTAPI)
│   ├── requirements.txt                # Danh mục thư viện Python phía backend
│   ├── .env.example                    # Tệp mẫu cấu hình môi trường (DB URL, JWT Secret)
│   ├── app/
│   │   ├── main.py                     # Entry point khởi tạo ứng dụng FastAPI và WebSocket
│   │   ├── core/                       # Cấu hình hệ thống cốt lõi
│   │   │   ├── config.py               # Quản lý tập trung biến môi trường và cài đặt
│   │   │   ├── database.py             # Cấu hình engine kết nối PostgreSQL / SQLite
│   │   │   └── security.py             # Logic băm mật khẩu và cấp phát/giải mã JWT
│   │   ├── models/                     # Các bảng cơ sở dữ liệu SQLAlchemy ORM
│   │   │   ├── user.py                 # Model bảng người dùng (users)
│   │   │   └── traffic.py              # Model bảng lịch sử phân loại (classification_history)
│   │   ├── schemas/                    # Pydantic Schemas xác thực dữ liệu đầu vào/ra
│   │   │   ├── auth.py                 # Schema đăng ký, đăng nhập, token
│   │   │   ├── traffic.py              # Schema payload log mạng và lịch sử
│   │   │   └── pcap.py                 # Schema kết quả phân tích file PCAP
│   │   ├── services/                   # Tầng xử lý nghiệp vụ độc lập
│   │   │   ├── agent_service.py        # Quản lý tiến trình chạy ngầm của Network Agent
│   │   │   ├── traffic_service.py      # Xử lý lưu log, truy vấn dữ liệu, xuất file CSV
│   │   │   └── pcap_service.py         # Xử lý bóc tách 5-tuple từ tệp tin PCAP
│   │   ├── api/                        # Định tuyến các cổng giao tiếp API
│   │   │   ├── deps.py                 # Dependency Injection (Database session, Auth)
│   │   │   └── v1/
│   │   │       ├── api_router.py       # Gom cụm các router API v1
│   │   │       └── endpoints/          # Chi tiết từng endpoint (auth, traffic, agent, pcap, ws)
│   │   └── utils/
│   │       ├── socket_manager.py       # Quản lý danh sách kết nối WebSocket tập trung
│   │       └── label_mapping.py        # Từ điển ánh xạ 11 nhãn mạng
│   └── scripts/
│       └── create_admin.py             # Script khởi tạo tài khoản quản trị viên mặc định
│
├── network_agent/                      # PHÂN HỆ TRẠM TÁC VỤ MẠNG (NETWORK AGENT)
│   ├── requirements.txt                # Danh mục thư viện cho Agent (Torch, Scapy, River,...)
│   ├── main.py                         # Điểm khởi chạy CLI (Hỗ trợ --mode live và --mode pcap)
│   ├── live_pipeline.py                # Pipeline thu thập và phân loại trực tiếp thời gian thực
│   ├── ai_core.py                      # Wrapper tương thích ngược cho các module AI
│   ├── core/                           # Các module xử lý mạng cấp thấp
│   │   ├── config.py                   # Cấu hình tham số Agent (cổng mạng, chu kỳ, đường dẫn)
│   │   └── flow_aggregator.py          # Bộ gom Packet thành Flow chuẩn 5-Tuple & quản lý Timeout
│   ├── ai/                             # Lõi Trí tuệ Nhân tạo
│   │   ├── rules.py                    # Danh mục nhãn và bộ từ điển phân tích tên miền SNI/DNS
│   │   ├── resnet_model.py             # Kiến trúc mạng nơ-ron ResNet-18 và tiền xử lý tensor
│   │   ├── fusion_engine.py            # Động cơ dung hợp quyết định song song (Parallel Fusion)
│   │   └── online_learner.py           # Module Online Machine Learning & Incremental Learning
│   ├── models/                         # Nơi lưu trữ trọng số mô hình đã huấn luyện (.pth)
│   ├── data/                           # Dữ liệu thu thập và tệp mạng
│   │   ├── csv/                        # Các bộ dữ liệu đặc trưng đã bóc tách
│   │   └── pcaps/                      # Thư mục chứa các file PCAP thử nghiệm
│   └── evaluation/                     # Công cụ đánh giá hiệu năng mô hình
│       ├── Evaluate_Model.ipynb        # Jupyter Notebook kiểm thử và đánh giá chi tiết
│       ├── test_model.py               # Kịch bản kiểm thử tự động
│       └── Confusion_Matrix_Parallel_Fusion.png # Ma trận nhầm lẫn của mô hình
│
└── frontend-dashboard/                 # PHÂN HỆ GIAO DIỆN BẢNG ĐIỀU KHIỂN (REACTJS + VITE)
    ├── package.json                    # Cấu hình các gói phụ thuộc giao diện
    ├── vite.config.js                  # Cấu hình công cụ đóng gói Vite
    ├── src/
    │   ├── main.jsx                    # Điểm khởi chạy ứng dụng React
    │   ├── App.jsx                     # Định tuyến các trang (Router) và bọc AuthProvider
    │   ├── context/
    │   │   └── AuthContext.jsx         # Context quản lý phiên đăng nhập và token
    │   ├── layouts/
    │   │   └── MainLayout.jsx          # Khung layout chung tích hợp Navbar và Sidebar
    │   ├── components/                 # Các thành phần giao diện tái sử dụng
    │   │   ├── Navbar.jsx              # Thanh tiêu đề trên cùng
    │   │   ├── Sidebar.jsx             # Thanh menu điều hướng bên trái
    │   │   └── ControlPanel.jsx        # Bảng điều khiển bật/tắt trạm thu thập Agent
    │   ├── pages/                      # Các trang màn hình chính
    │   │   ├── Dashboard.jsx           # Bảng điều khiển lưu lượng và biểu đồ thời gian thực
    │   │   ├── PcapAnalysis.jsx        # Giao diện kéo thả và phân tích tệp tin PCAP
    │   │   ├── History.jsx             # Bảng tra cứu lịch sử lưu lượng đã phân loại
    │   │   ├── Account.jsx             # Trang quản lý thông tin tài khoản
    │   │   ├── Settings.jsx            # Cài đặt tham số hệ thống
    │   │   └── Login.jsx               # Cổng đăng nhập xác thực
    │   └── services/
    │       ├── api.js                  # Module gọi các API RESTful
    │       └── websocket.js            # Module duy trì và quản lý luồng WebSocket
```

---

## 6. Hướng Dẫn Cài Đặt & Vận Hành Hệ Thống

### 6.1. Yêu cầu môi trường
* **Hệ điều hành:** Linux (Ubuntu 22.04+ khuyên dùng cho sniffing trực tiếp) hoặc Windows 10/11 (kèm Npcap để bắt gói tin).
* **Python:** Phiên bản 3.10 trở lên.
* **Node.js:** Phiên bản 18.x trở lên cùng `npm`.
* **Cơ sở dữ liệu:** PostgreSQL (hoặc tự động dùng SQLite tích hợp sẵn khi chạy thử nghiệm).

### 6.2. Khởi chạy Phân hệ Backend (`backend_api`)
1. Di chuyển vào thư mục backend và cài đặt thư viện:
   ```bash
   cd backend_api
   pip install -r requirements.txt
   ```
2. Cấu hình biến môi trường trong file `.env` (tạo từ `.env.example` nếu cần tùy chỉnh Database).
3. Khởi tạo tài khoản quản trị viên mặc định:
   ```bash
   python scripts/create_admin.py
   ```
4. Chạy máy chủ FastAPI:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   * Tài liệu API Swagger UI có sẵn tại: `http://localhost:8000/docs`

### 6.3. Khởi chạy Phân hệ Giao diện (`frontend-dashboard`)
1. Di chuyển vào thư mục frontend và cài đặt gói phụ thuộc:
   ```bash
   cd frontend-dashboard
   npm install
   ```
2. Khởi chạy máy chủ phát triển Vite:
   ```bash
   npm run dev
   ```
   * Truy cập giao diện tại: `http://localhost:5173`

### 6.4. Vận hành Phân hệ Trạm tác vụ mạng (`network_agent`)
1. Di chuyển vào thư mục agent và cài đặt thư viện:
   ```bash
   cd network_agent
   pip install -r requirements.txt
   ```
2. Chạy trạm thu thập theo các chế độ:
   * **Chế độ 1: Bắt gói tin trực tiếp từ card mạng (Live Mode):**
     *(Cần quyền Administrator trên Windows hoặc `sudo` trên Linux để truy cập card mạng thô)*
     ```bash
     python main.py --mode live
     # hoặc chạy trực tiếp pipeline:
     python live_pipeline.py
     ```
   * **Chế độ 2: Đọc và bóc tách luồng từ file PCAP (Offline PCAP Mode):**
     ```bash
     python main.py --mode pcap --file data/pcaps/sample.pcap
     ```

