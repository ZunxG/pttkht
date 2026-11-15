# ThesisHub – Hệ thống quản lý đồ án tốt nghiệp

Phần mềm minh họa cho bài tập lớn học phần **Phân tích và thiết kế phần mềm** – đề tài *Phát triển phần mềm quản lý đồ án tốt nghiệp*.
Ứng dụng web cài đặt 24 use-case (UC1.1–UC5.5) cho 5 vai trò: Quản trị viên, Giáo vụ khoa, Trưởng khoa, Giảng viên, Sinh viên.
Dữ liệu lưu trong cơ sở dữ liệu SQLite trên máy chủ.

## Chạy nhanh
Cần Python 3.8+ (không phải cài thêm thư viện nào).

```bash
git clone https://github.com/ZunxG/pttkht.git
cd pttkht
python seed_mockup.py              # tạo thesishub.db và nạp dữ liệu minh họa
python server.py                   # mở http://localhost:8000
```

Tùy chọn khác:
```bash
python server.py --port 9000       # đổi cổng
python server.py --host 0.0.0.0    # cho máy khác cùng mạng LAN truy cập (http://<IP-máy-bạn>:8000)
```

Lần chạy đầu tiên tạo file `thesishub.db` và một tài khoản quản trị:
`admin@phenikaa-uni.edu.vn` / `Admin@123` (bắt buộc đổi mật khẩu khi đăng nhập lần đầu).

### Tài khoản dùng thử (nút "Đăng nhập nhanh" ở trang đăng nhập)
Mỗi lần khởi động, máy chủ tạo các tài khoản còn thiếu, không ghi đè tài khoản đã có. Mật khẩu chung: `Thesis@2026`.
Các tài khoản này là nhân vật trong giao diện minh họa của tài liệu đặc tả.

| Vai trò | Email | Họ tên |
|---|---|---|
| Quản trị viên | quantri.demo@phenikaa-uni.edu.vn | Nguyễn Văn Quản |
| Giáo vụ khoa | ha.nt@phenikaa-uni.edu.vn | Nguyễn Thị Hà |
| Trưởng khoa (kiêm GV) | vinh.dq@phenikaa-uni.edu.vn | PGS.TS. Đỗ Quang Vinh |
| Giảng viên | nga.mt@phenikaa-uni.edu.vn | TS. Mai Thúy Nga |
| Sinh viên (mã 24100188) | tung.nd24100188@st.phenikaa-uni.edu.vn | Nguyễn Đình Tùng |

### Dữ liệu minh họa theo tài liệu đặc tả
`python seed_mockup.py` nạp dữ liệu của các giao diện minh họa (Hình 1.12 – 1.51): 4 đợt đồ án, 12 giảng viên và hạn mức,
16 đề tài, 23 sinh viên, nguyện vọng, kế hoạch, báo cáo tiến độ, quyển đồ án, 5 hội đồng, lịch bảo vệ, phiếu phản biện,
phiếu chấm, kết quả đã công bố, kho lưu trữ và thông báo. Mọi tài khoản trong dữ liệu này dùng mật khẩu `Thesis@2026`.
Ví dụ: `trang.pt@`, `hang.pt@`, `duc.nm@` (giảng viên phản biện), `23010120@st.phenikaa-uni.edu.vn`...

Nạp lại dữ liệu (xóa và nạp lại các đợt DA2025-1, DA2025-2, DA2026-1, DA2026-2; tài khoản khác được giữ):
```bash
python seed_mockup.py
```

Khi triển khai thật, đặt `DEMO_SHORTCUTS = False` ở đầu `server.py` để ẩn các nút đăng nhập nhanh.

Muốn xóa sạch dữ liệu để làm lại từ đầu: dừng máy chủ, xóa file `thesishub.db` rồi chạy lại.

## Thứ tự nhập dữ liệu
1. **Quản trị viên** → Tài khoản người dùng: tạo tài khoản giáo vụ khoa, trưởng khoa (chọn cả *Giảng viên* + *Trưởng khoa*), giảng viên.
   Mật khẩu tạm của mọi tài khoản mới là `Phenikaa@123`, người dùng phải đổi ở lần đăng nhập đầu.
2. **Giáo vụ khoa** → Đợt đồ án: tạo đợt (đợt đầu tiên tự thành đợt hiện hành) → Giảng viên & hạn mức: thêm giảng viên vào đợt
   → Sinh viên: thêm từng người hoặc nhập file CSV. Tài khoản sinh viên được tạo tự động: `<mã SV>@st.phenikaa-uni.edu.vn`.
3. **Giảng viên** đề xuất đề tài → **Trưởng khoa** duyệt → **Sinh viên** đăng ký nguyện vọng → giảng viên chấp nhận / TK phân công.
4. Sinh viên lập kế hoạch, nộp báo cáo tiến độ, nộp quyển → GVHD duyệt, đánh giá, xác nhận đủ điều kiện bảo vệ.
5. Giáo vụ lập hội đồng, phân công phản biện và xếp lịch → giảng viên gửi phiếu phản biện, chấm điểm → giáo vụ công bố kết quả và lưu trữ.

Lưu ý: các chức năng mở theo mốc thời gian của đợt (ví dụ chỉ đề xuất đề tài / thêm sinh viên trong giai đoạn đăng ký),
nên khi tạo đợt hãy đặt giai đoạn "Đăng ký đề tài" bao gồm ngày hôm nay.

Quên mật khẩu: bản chạy cục bộ chưa nối dịch vụ email, liên kết đặt lại mật khẩu được in ra cửa sổ đang chạy `server.py`.

## Kiến trúc
```
Trình duyệt (HTML/CSS/JS)  ──REST/JSON──►  server.py (Python, http.server)  ──►  thesishub.db (SQLite)
```

| API | Chức năng |
|---|---|
| `POST /api/login`, `/api/logout`, `/api/role`, `/api/change-password`, `/api/forgot`, `/api/reset` | UC1.1 đăng nhập, phiên, mật khẩu |
| `GET /api/me`, `GET /api/state` | thông tin người dùng, dữ liệu của đợt hiện hành (lọc theo vai trò) |
| `POST /api/sync` | ghi các thay đổi (thêm/sửa/xóa bản ghi) trong một giao dịch, có kiểm tra quyền |
| `POST /api/users`, `PUT /api/users/{id}`, `POST /api/users/{id}/lock\|unlock\|reset-password` | UC1.2 quản lý tài khoản |

Máy chủ đảm nhận:
- **Bảo mật:** băm mật khẩu bằng PBKDF2, cookie phiên HttpOnly, hết phiên sau 30 phút, khóa 15 phút khi sai 5 lần.
- **Phân quyền:** mỗi vai trò chỉ ghi được loại dữ liệu của mình. Sinh viên chỉ đọc/ghi dữ liệu của chính mình. Không ai tự duyệt hay tự đánh giá cho chính mình.
- **Ràng buộc:** khóa ngoại giữa các bảng, ví dụ không xóa được đợt đã có dữ liệu.

Bảng dữ liệu (xem `SCHEMA` trong `server.py`): `users, sessions, reset_tokens, login_log, settings, periods, period_phases,
lecturers, topics, students, requests, plans, plan_milestones, reports, theses, councils, council_members, defenses,
reviews, scores, archive, notifications`. Các bảng nghiệp vụ có cột `period_id` để tách dữ liệu theo đợt.

```
server.py                máy chủ, REST API, lược đồ CSDL, phân quyền
index.html, css/         giao diện
js/data.js               hằng số dùng chung (vai trò, mẫu kế hoạch, tiêu chí chấm)
js/app.js                gọi API, đồng bộ dữ liệu, phiên đăng nhập, điều hướng, khung trang
js/views-student.js      UC2.3, UC3.1, UC3.2, UC4.1, UC5.3
js/views-lecturer.js     UC2.1, UC2.2, UC2.4, UC2.5, UC3.3, UC4.2, UC4.5, UC5.1
js/views-admin.js        UC1.2–UC1.5, UC3.4, UC4.3, UC4.4, UC5.2, UC5.4, UC5.5
```

Giới hạn: tệp tải lên (báo cáo, quyển đồ án) hiện chỉ ghi nhận tên và dung lượng, chưa lưu nội dung tệp.
Phần lớn quy tắc nghiệp vụ chi tiết (hạn mức, số mốc kế hoạch…) được kiểm tra ở giao diện.
