#!/usr/bin/env python3
"""Nạp dữ liệu minh họa theo các giao diện (Hình 1.12 – 1.51) của tài liệu đặc tả ThesisHub.

Chạy:  python3 seed_mockup.py          (ghi vào thesishub.db cạnh file này, hoặc biến môi trường THESISHUB_DB)

- Chạy lại nhiều lần được: dữ liệu nghiệp vụ của các đợt DA2025-1, DA2025-2, DA2026-1, DA2026-2 bị xóa rồi nạp lại;
  tài khoản được cập nhật theo mã (id), tài khoản khác do người dùng tự tạo được giữ nguyên.
- Mật khẩu chung của mọi tài khoản trong dữ liệu minh họa: Thesis@2026 (riêng TS. Vũ Thanh Bình vừa được tạo ở
  Hình 1.17 nên dùng mật khẩu mặc định Phenikaa@123 và phải đổi ở lần đăng nhập đầu).
- Các hình minh họa chụp ở những thời điểm khác nhau của cùng một đợt. Cơ sở dữ liệu chỉ giữ được một trạng thái, nên
  khi hai hình mâu thuẫn, trạng thái ở bước sau của quy trình được giữ; trạng thái trước được lưu lại dưới dạng lịch sử
  (nguyện vọng bị từ chối/hủy, các lần nộp báo cáo, góp ý kế hoạch, thông báo).
"""
import math
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server  # noqa: E402  (dùng chung lược đồ và hàm băm mật khẩu)

PW = server.hash_pw('Thesis@2026')
PW_DEFAULT = server.hash_pw(server.DEFAULT_PASSWORD)
P = 'DA2026-1'
PERIOD_IDS = ['DA2025-1', 'DA2025-2', 'DA2026-1', 'DA2026-2']


def r1(x):  # làm tròn 0,1 giống Math.round của giao diện
    return math.floor(x * 10 + 0.5) / 10


def split(total):
    """Chia tổng điểm thành viên hội đồng thành 4 tiêu chí (tối đa 4,0 / 1,5 / 2,0 / 2,5)."""
    c = [r1(total * 0.4), r1(total * 0.15), r1(total * 0.2)]
    c.append(r1(total - sum(c)))
    assert r1(sum(c)) == total and c[3] <= 2.5, (total, c)
    return c


# ------------------------------------------------------------------ tài khoản (Hình 1.16, 1.17 và các hình khác)
# (id, mã, họ tên, email, vai trò, đơn vị)
STAFF = [
    ('demo-gvu', 'CB0045', 'Nguyễn Thị Hà', 'ha.nt@phenikaa-uni.edu.vn', 'GVU', 'Văn phòng khoa'),
    ('demo-tbm', 'GV0087', 'PGS.TS. Đỗ Quang Vinh', 'vinh.dq@phenikaa-uni.edu.vn', 'GV,TK', 'BM KTPM'),
    ('demo-gv', 'GV0123', 'TS. Mai Thúy Nga', 'nga.mt@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
    ('u-gv0156', 'GV0156', 'ThS. Phạm Thu Trang', 'trang.pt@phenikaa-uni.edu.vn', 'GV', 'BM HTTT'),
    ('u-gv0172', 'GV0172', 'TS. Vũ Thanh Bình', 'binh.vt@phenikaa-uni.edu.vn', 'GV', 'BM KHMT'),
    ('u-gv0181', 'GV0181', 'ThS. Hoàng Minh Đức', 'duc.hm@phenikaa-uni.edu.vn', 'GV', 'BM MMT'),
    ('u-gv0164', 'GV0164', 'TS. Nguyễn Thị Hồng', 'hong.nt@phenikaa-uni.edu.vn', 'GV', 'BM HTTT'),
    ('u-gv0195', 'GV0195', 'ThS. Ngô Thanh Tùng', 'tung.nt@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
    ('u-gv0142', 'GV0142', 'TS. Vũ Hoàng Long', 'long.vh@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
    ('u-gv0118', 'GV0118', 'TS. Trần Thị Mai', 'mai.tt@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
    ('u-gv0203', 'GV0203', 'ThS. Phạm Thu Hằng', 'hang.pt@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
    ('u-gv0131', 'GV0131', 'TS. Ngô Minh Đức', 'duc.nm@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
    ('u-gv0149', 'GV0149', 'TS. Trần Thị Lan', 'lan.tt@phenikaa-uni.edu.vn', 'GV', 'BM KTPM'),
]
HUNG, VINH, TRANG, BINH, HMDUC, HONG, NTTUNG, LONG, MAI, HANG, NMDUC, LAN = (
    'demo-gv', 'demo-tbm', 'u-gv0156', 'u-gv0172', 'u-gv0181', 'u-gv0164', 'u-gv0195', 'u-gv0142', 'u-gv0118',
    'u-gv0203', 'u-gv0131', 'u-gv0149')
GVU = 'demo-gvu'

# Giảng viên tham gia đợt DA2026-1 (Hình 1.24, 1.25): uid, học vị, hạn mức
LECTURERS = [(HUNG, 'TS', 8), (VINH, 'PGS.TS', 10), (TRANG, 'ThS', 5), (BINH, 'TS', 10), (HMDUC, 'ThS', 5), (HONG, 'TS', 8),
             (NTTUNG, 'ThS', 5), (LONG, 'TS', 8), (MAI, 'TS', 8), (HANG, 'ThS', 5), (NMDUC, 'TS', 8), (LAN, 'TS', 8)]

# Sinh viên: mã, họ tên, lớp, số TC, GPA, email riêng (nếu hình có ghi), trong đợt?, GVHD, mã đề tài
STUDENTS = [
    # Hình 1.12–1.22, 1.30–1.32, 1.36–1.49
    ('24100188', 'Nguyễn Đình Tùng', 'K17-CNTT1', 132, 3.21, 'tung.nd24100188@st.phenikaa-uni.edu.vn', True, HUNG, 'DT-CNTT-015'),
    # Hình 1.16, 1.22 (mã 23010231), 1.33 (23010211), 1.40, 1.41, 1.45, 1.47, 1.48, 1.50 (23010120) – gộp làm một người
    ('23010120', 'Trần Đức Huy', 'K17-CNTT2', 135, 2.98, 'huy.td23010120@st.phenikaa-uni.edu.vn', True, HUNG, 'DT-CNTT-016'),
    ('23010078', 'Lê Hoàng Nam', 'K17-KHMT', 130, 3.45, 'nam.lh23010078@st.phenikaa-uni.edu.vn', True, VINH, 'DT-CNTT-007'),
    ('23010312', 'Phạm Thị Lan', 'K17-HTTT', 131, 3.02, None, True, None, None),
    ('23010099', 'Vũ Quốc Bảo', 'K17-CNTT1', 134, 2.76, None, True, TRANG, 'DT-CNTT-005'),
    ('23010189', 'Đặng Thu Hương', 'K17-CNTT2', 133, 3.60, None, False, None, None),  # "Đã rút" khỏi đợt (Hình 1.22)
    # Hình 1.23 – 4 dòng hợp lệ sau khi "Xác nhận nhập"
    ('23010402', 'Ngô Văn Khánh', 'K17-CNTT1', 131, 3.05, None, True, None, None),
    ('23010417', 'Bùi Thị Mai', 'K17-HTTT', 130, 3.12, None, True, None, None),
    ('23010455', 'Đinh Quang Minh', 'K17-CNTT2', 133, 2.88, None, True, None, None),
    ('23010461', 'Trịnh Ngọc Ánh', 'K17-KHMT', 131, 3.30, None, True, None, None),
    # Hình 1.33, 1.34
    ('23010079', 'Lê Thị Ngọc Bích', 'K17-HTTT', 129, 2.98, None, True, None, None),
    ('23010302', 'Phạm Quốc Bảo', 'K17-CNTT1', 128, 2.71, None, True, None, None),
    # Hình 1.35 – sinh viên chưa có GVHD
    ('23010098', 'Đặng Văn Khoa', 'K17-CNTT1', 130, 2.95, None, True, None, None),
    ('23010156', 'Hoàng Thu Hằng', 'K17-KHMT', 132, 3.28, None, True, None, None),
    ('23010187', 'Bùi Tiến Dũng', 'K17-CNTT2', 128, 2.67, None, True, None, None),
    ('23010234', 'Vũ Ngọc Lan', 'K17-CNTT1', 131, 3.08, None, True, None, None),
    ('23010264', 'Đỗ Minh Quân', 'K17-CNTT2', 130, 2.84, None, True, None, None),
    ('23010290', 'Phan Thị Yến', 'K17-HTTT', 129, 3.15, None, True, None, None),
    # Hình 1.40, 1.41, 1.45, 1.47, 1.48, 1.50
    ('23010188', 'Phạm Thu Trang', 'K17-CNTT2', 131, 2.85, None, True, HUNG, 'DT-CNTT-012'),
    ('23010057', 'Vũ Hải Yến', 'K17-CNTT1', 130, 2.92, None, True, HUNG, 'DT-CNTT-012'),
    ('23010089', 'Lê Quốc Bảo', 'K17-CNTT1', 134, 3.40, None, True, HUNG, 'DT-CNTT-017'),
    ('23010166', 'Đặng Văn Long', 'K17-CNTT2', 132, 3.10, None, True, HUNG, 'DT-CNTT-013'),
    ('23010233', 'Hoàng Gia Khánh', 'K17-CNTT1', 128, 2.55, None, True, HANG, 'DT-CNTT-034'),
    ('23010301', 'Bùi Thanh Tùng', 'K17-CNTT2', 129, 2.70, None, True, VINH, 'DT-CNTT-031'),
]
LOCKED = {'23010120'}  # Hình 1.16: tài khoản Trần Đức Huy "Bị khóa"

# ------------------------------------------------------------------ đề tài (Hình 1.26–1.30, 1.35, 1.36, 1.50)
# id, tên, GV, số SV, trạng thái, góp ý TK, mô tả, yêu cầu, giữ chỗ
TOPICS = [
    ('DT-CNTT-012', 'Hệ thống quản lý phòng khám nha khoa trên nền web', HUNG, 2, 'Đã duyệt', '',
     'Lĩnh vực: Kỹ thuật phần mềm. Quản lý hồ sơ bệnh nhân, lịch hẹn, phác đồ điều trị và thanh toán cho phòng khám nha khoa. '
     'Kết quả dự kiến: ứng dụng web, tài liệu phân tích thiết kế, quyển ĐATN.',
     'Nắm vững một framework web (Spring Boot/Node.js), có kiến thức CSDL quan hệ.', 0),
    ('DT-CNTT-013', 'Ứng dụng di động đặt lịch sân thể thao', HUNG, 2, 'Đã duyệt', '',
     'Lĩnh vực: Phát triển di động. Ứng dụng cho phép tìm sân, xem khung giờ trống, đặt và thanh toán sân thể thao; trang quản trị cho chủ sân. '
     'Kết quả dự kiến: ứng dụng di động, API, quyển ĐATN.',
     'Biết Flutter hoặc React Native; có kiến thức REST API.', 0),
    ('DT-CNTT-015', 'Phân tích và thiết kế hệ thống', HUNG, 1, 'Đã duyệt', '',
     'Lĩnh vực: Kỹ thuật phần mềm, Hệ khuyến nghị. Thu thập tin tuyển dụng, xây dựng module gợi ý việc làm (lọc cộng tác) và trang web '
     'tìm kiếm việc làm cho sinh viên CNTT. Kết quả dự kiến: hệ thống web + API gợi ý top-10, quyển ĐATN.',
     'Lập trình Python/JavaScript, có kiến thức học máy cơ bản.', 0),
    ('DT-CNTT-016', 'Ứng dụng nhận dạng biển số xe bằng YOLOv8', HUNG, 1, 'Đã duyệt', '',
     'Lĩnh vực: Trí tuệ nhân tạo. Phát hiện và nhận dạng biển số xe Việt Nam từ ảnh/camera bằng YOLOv8, tích hợp vào ứng dụng quản lý bãi xe.',
     'Python, PyTorch; biết xử lý ảnh cơ bản.', 0),
    ('DT-CNTT-017', 'Hệ thống quản lý phòng gym trên nền web', HUNG, 1, 'Đã duyệt', '',
     'Lĩnh vực: Kỹ thuật phần mềm. Quản lý hội viên, gói tập, lịch huấn luyện viên và thanh toán cho phòng gym.',
     'Nắm vững một framework web; CSDL quan hệ.', 0),
    ('DT-CNTT-018', 'Chatbot hỗ trợ tư vấn tuyển sinh dùng RAG', HUNG, 3, 'Yêu cầu sửa',
     'Cần làm rõ nguồn dữ liệu tuyển sinh dùng để truy hồi và tiêu chí đánh giá chất lượng câu trả lời của chatbot.',
     'Lĩnh vực: Trí tuệ nhân tạo. Chatbot trả lời câu hỏi tuyển sinh dựa trên tài liệu quy chế, đề án tuyển sinh bằng kỹ thuật RAG.',
     'Python; hiểu biết về mô hình ngôn ngữ lớn và vector database.', 0),
    ('DT-CNTT-021', 'Kiểm thử tự động API cho hệ thống thương mại điện tử', HUNG, 1, 'Chờ duyệt', '',
     'Lĩnh vực: Kiểm thử phần mềm. Xây dựng bộ kiểm thử tự động API (chức năng, hiệu năng) và tích hợp CI cho một hệ thống TMĐT. '
     '(Gửi duyệt 29/09/2026)',
     'Biết Postman/RestAssured hoặc k6; có kiến thức kiểm thử phần mềm.', 0),
    ('DT-CNTT-024', 'Nền tảng quản lý CLB sinh viên', HUNG, 2, 'Nháp', '',
     'Lĩnh vực: Kỹ thuật phần mềm. Quản lý thành viên, sự kiện, điểm rèn luyện và truyền thông nội bộ cho các câu lạc bộ sinh viên.',
     'Nắm vững một framework web.', 0),
    ('DT-CNTT-026', 'Hệ thống quản lý thư viện số cho trường THPT', TRANG, 2, 'Đã duyệt',
     'Đề tài trùng một phần với đề tài năm 2024. Đề nghị bổ sung chức năng gợi ý sách theo lịch sử mượn để tăng tính mới.',
     'Lĩnh vực: Kỹ thuật phần mềm. Xây dựng hệ thống web cho phép quản lý đầu sách, mượn/trả sách điện tử, tra cứu tài liệu và thống kê '
     'lượt mượn cho thư viện trường THPT. Kết quả dự kiến: sản phẩm web chạy được, tài liệu phân tích thiết kế, quyển báo cáo ĐATN. '
     'Tên tiếng Anh: Building a digital library management system for high schools. Tài liệu tham khảo: yeu_cau_thu_vien.pdf. '
     '(Gửi duyệt 30/09/2026)',
     'Nắm vững Java/Spring Boot hoặc Node.js, ReactJS; có kiến thức cơ sở dữ liệu quan hệ.', 0),
    ('DT-CNTT-027', 'Ứng dụng quản lý chi tiêu cá nhân đa nền tảng', NTTUNG, 2, 'Chờ duyệt', '',
     'Lĩnh vực: Phát triển di động. Ứng dụng ghi chép thu chi, lập ngân sách và báo cáo tài chính cá nhân, đồng bộ trên di động và web. '
     '(Gửi duyệt 30/09/2026)',
     'Flutter hoặc React Native.', 0),
    ('DT-CNTT-029', 'Phát hiện mã độc Android bằng học máy', LONG, 1, 'Chờ duyệt', '',
     'Lĩnh vực: An toàn thông tin, Học máy. Trích xuất đặc trưng từ tệp APK và huấn luyện mô hình phân loại ứng dụng Android độc hại. '
     '(Gửi duyệt 01/10/2026)',
     'Python, học máy cơ bản.', 0),
    ('DT-CNTT-030', 'Nền tảng thi trắc nghiệm trực tuyến', MAI, 3, 'Đã duyệt', '',
     'Lĩnh vực: Kỹ thuật phần mềm. Tạo ngân hàng câu hỏi, đề thi ngẫu nhiên, tổ chức thi trực tuyến và chấm điểm tự động. (Gửi duyệt 02/10/2026)',
     'Nắm vững một framework web.', 3),  # Hình 1.30: "0/3 – Hết chỗ"
    ('DT-CNTT-031', 'Phần mềm quản lý kho cho cửa hàng điện máy', VINH, 2, 'Đã duyệt', '',
     'Lĩnh vực: Hệ thống thông tin. Quản lý nhập – xuất – tồn kho, bảo hành và báo cáo doanh thu cho chuỗi cửa hàng điện máy.',
     'CSDL quan hệ, một framework web.', 0),
    ('DT-CNTT-007', 'Nhận dạng chữ viết tay tiếng Việt bằng học sâu', VINH, 1, 'Đã duyệt', '',
     'Lĩnh vực: Khoa học máy tính. Xây dựng mô hình học sâu nhận dạng chữ viết tay tiếng Việt có dấu.',
     'Python, PyTorch.', 0),
    ('DT-CNTT-005', 'Website quản lý nhà hàng và đặt bàn trực tuyến', TRANG, 1, 'Đã duyệt', '',
     'Lĩnh vực: Hệ thống thông tin. Quản lý thực đơn, đặt bàn, gọi món và thanh toán cho nhà hàng.',
     'CSDL quan hệ, một framework web.', 0),
    ('DT-CNTT-034', 'Hệ thống quản lý ký túc xá sinh viên', HANG, 1, 'Đã duyệt', '',
     'Lĩnh vực: Kỹ thuật phần mềm. Quản lý phòng ở, hợp đồng, điện nước và yêu cầu sửa chữa trong ký túc xá.',
     'Nắm vững một framework web.', 0),
]

# ------------------------------------------------------------------ nguyện vọng (Hình 1.31–1.34)
# id, mã SV, đề tài, NV, lời nhắn, trạng thái, lý do, ngày, CV
REQUESTS = [
    (1001, '24100188', 'DT-CNTT-012', 1, 'Em mong được cô hướng dẫn đề tài phòng khám nha khoa.', 'Từ chối',
     'Đề tài đã đủ sinh viên theo kế hoạch của cô. Em có thể tham khảo đề tài DT-CNTT-013.', '2026-10-06T07:45', None),
    (1002, '24100188', 'DT-CNTT-026', 2,
     'Em đã làm dự án web thư viện với Spring Boot trong môn CNPM và mong được thầy/cô hướng dẫn đề tài này.',
     'Đã hủy', 'Bộ môn đã phân công GVHD', '2026-10-07T10:20', 'CV_NguyenMinhAnh.pdf'),
    (1003, '24100188', 'DT-CNTT-031', 3, '', 'Đã hủy', 'Bộ môn đã phân công GVHD', '2026-10-07T10:35', None),
    (1004, '23010120', 'DT-CNTT-012', 1, 'Em có kinh nghiệm làm web với Node.js.', 'Đã hủy', 'Bộ môn đã phân công GVHD',
     '2026-10-06T14:10', None),
    (1005, '23010079', 'DT-CNTT-013', 2, 'Em quan tâm tới phát triển ứng dụng di động.', 'Chờ xét', '', '2026-10-07T15:30', None),
    (1006, '23010302', 'DT-CNTT-013', 3, '', 'Từ chối',
     'Đề tài đã đủ sinh viên. Em có thể đăng ký đề tài DT-CNTT-031 của thầy Vinh.', '2026-10-08T09:05', None),
]

# ------------------------------------------------------------------ kế hoạch
MA_PLAN = [  # Hình 1.36–1.38: kế hoạch đã tách mốc 4 theo góp ý của GVHD (Hình 1.37)
    ('Đề cương đồ án', '2026-10-12', 'Mục tiêu, phạm vi, kế hoạch · Sản phẩm: Đề cương (PDF)'),
    ('Phân tích yêu cầu', '2026-11-02', 'Khảo sát, đặc tả use-case · Sản phẩm: Tài liệu SRS'),
    ('Thiết kế hệ thống', '2026-11-23', 'Kiến trúc, CSDL, giao diện · Sản phẩm: Tài liệu thiết kế'),
    ('Cài đặt module gợi ý', '2026-12-07', 'Module gợi ý, API · Sản phẩm: Mã nguồn (Git)'),
    ('Cài đặt giao diện web', '2026-12-21', 'Giao diện web · Sản phẩm: Mã nguồn (Git)'),
    ('Kiểm thử', '2027-01-04', 'Kiểm thử chức năng, hiệu năng · Sản phẩm: Báo cáo kiểm thử'),
    ('Hoàn thiện quyển', '2027-01-15', 'Viết quyển, slide bảo vệ · Sản phẩm: Quyển đồ án (bản nháp)'),
]
MA_PLAN_COMMENT = 'Mốc 4 nên tách thành 2 mốc: cài đặt module gợi ý và cài đặt giao diện web để dễ theo dõi.'
TEMPLATE = [('Đề cương chi tiết', '2026-10-26'), ('Đặc tả yêu cầu', '2026-11-09'), ('Phân tích và thiết kế', '2026-11-23'),
            ('Cài đặt chức năng chính', '2026-12-07'), ('Kiểm thử', '2026-12-21'), ('Hoàn thiện sản phẩm', '2027-01-04'),
            ('Bản thảo quyển đồ án', '2027-01-15')]

# Trạng thái báo cáo theo từng mốc (Hình 1.40, 1.41): Đ = Đạt, B = Cần bổ sung, C = Chậm tiến độ
PROGRESS = {
    '23010120': (7, 'ĐĐĐĐĐ'),       # 71 %, đạt
    '23010188': (7, 'ĐĐĐCC'),       # 43 %, chậm tiến độ
    '23010089': (7, 'ĐĐĐĐĐĐ'),      # 86 %
    '23010057': (7, 'ĐĐB'),         # 29 %, cần bổ sung
    '23010166': (7, 'ĐĐĐĐ'),        # 57 %
    '23010233': (6, 'ĐĐCC'),        # 33 %, chậm tiến độ
    '23010301': (6, 'ĐĐCC'),        # 33 %, chậm tiến độ
    '23010099': (7, 'ĐĐĐĐĐĐĐ'),     # 100 %, đã nộp quyển (HĐ05)
    '23010078': (7, 'ĐĐĐĐĐĐĐ'),     # 100 %, đã nộp quyển (HĐ05)
}
STATUS_WORD = {'Đ': 'Đạt', 'B': 'Cần bổ sung', 'C': 'Chậm tiến độ'}
STATUS_CMT = {'Đ': '', 'B': 'Cần bổ sung kết quả thử nghiệm và cập nhật tài liệu theo góp ý.',
              'C': 'Chậm so với kế hoạch, khối lượng công việc của mốc chưa hoàn thành.'}

# ------------------------------------------------------------------ hội đồng (Hình 1.44, 1.45, 1.47, 1.48)
COUNCILS = [  # id, ngày, buổi, phòng, thành viên, đã công bố
    ('HĐ01', '2027-01-20', 'Sáng', 'A2-301', [(VINH, 'Chủ tịch'), (HUNG, 'Thư ký'), (LONG, 'Ủy viên')], 1),
    ('HĐ02', '2027-01-21', 'Sáng', 'A2-302', [(HONG, 'Chủ tịch'), (TRANG, 'Thư ký'), (MAI, 'Ủy viên')], 1),
    ('HĐ03', '2027-01-21', 'Chiều', 'A2-303', [(BINH, 'Chủ tịch'), (HMDUC, 'Thư ký'), (NTTUNG, 'Ủy viên')], 1),
    # Hình 1.44: "Hội đồng KTPM 3" đang được tạo, chưa có sinh viên
    ('HĐ04', '2027-01-21', 'Sáng', 'A2-304', [(HUNG, 'Chủ tịch'), (HANG, 'Thư ký'), (NMDUC, 'Ủy viên')], 0),
    # Hội đồng chưa bảo vệ: TS. Mai Thúy Nga phản biện cả 3 sinh viên (phiếu phản biện đang chờ nhập)
    ('HĐ05', '2027-01-22', 'Sáng', 'A2-305', [(BINH, 'Chủ tịch'), (HMDUC, 'Thư ký'), (LAN, 'Ủy viên')], 0),
]
# mã SV: hội đồng, giờ, GV phản biện, điểm GVHD, điểm PB, điểm 3 thành viên (theo thứ tự thành viên)
DEFENSES = {
    '23010188': ('HĐ01', '07:30', HANG, 7.0, 6.5, [6.8, 7.0, 6.6]),
    '23010057': ('HĐ01', '08:15', LAN, 7.5, 7.0, [7.2, 7.4, 7.0]),
    '24100188': ('HĐ01', '09:00', NMDUC, 8.5, 8.0, [8.4, 8.5, 8.3]),
    '23010120': ('HĐ02', '07:30', BINH, 9.0, 8.5, [8.8, 9.0, 8.6]),
    '23010233': ('HĐ02', '08:15', HUNG, 5.0, 4.5, [4.6, 4.8, 4.4]),  # TS. Mai Thúy Nga phản biện (đã gửi phiếu)
    '23010089': ('HĐ03', '13:30', LAN, 8.0, 8.0, [8.2, 8.4, 8.0]),
}
# Đã xếp lịch vào HĐ05, chưa bảo vệ, chưa có phiếu phản biện: mã SV -> (hội đồng, giờ, GV phản biện)
PENDING_DEFENSES = {
    '23010301': ('HĐ05', '07:30', HUNG),
    '23010099': ('HĐ05', '08:15', HUNG),
    '23010078': ('HĐ05', '09:00', HUNG),
}
# Quyển đồ án đã được GVHD xác nhận đủ điều kiện: mã SV -> (dung lượng, ngày nộp, tỷ lệ trùng, điểm GVHD, nhận xét)
EXTRA_THESES = {
    '23010099': (7.2, '2027-01-16T09:00', 9, 7.0, 'Hoàn thành các chức năng đặt bàn và quản lý thực đơn. Đồng ý cho bảo vệ.'),
    '23010078': (9.4, '2027-01-16T14:30', 7, 7.5, 'Mô hình nhận dạng đạt độ chính xác 91% trên tập kiểm thử. Đồng ý cho bảo vệ.'),
}
MA_HUNG_SCORE = [3.5, 1.3, 1.7, 2.0]  # Hình 1.47

# ------------------------------------------------------------------ kho lưu trữ (Hình 1.29, 1.50)
ARCHIVE = [
    ('LT-2025-087', 'Hệ thống gợi ý khóa học trực tuyến', 'Đỗ Thị Mai', 'TS. Mai Thúy Nga', 'DA2025-2', 8.6,
     'Xây dựng hệ thống gợi ý khóa học trực tuyến cho người học dựa trên lịch sử học tập và lọc cộng tác.'),
    ('LT-2025-031', 'Thư viện điện tử cho THCS', 'Lý Thu Ngân', 'ThS. Phạm Thu Trang', 'DA2025-1', 7.8,
     'Thư viện điện tử phục vụ học sinh và giáo viên THCS: số hóa tài liệu, mượn trả trực tuyến.'),
    ('LT-2024-112', 'Gợi ý sản phẩm thương mại điện tử dùng lọc cộng tác', 'Ngô Văn Tài', 'TS. Ngô Minh Đức', 'DA2024-2', 7.9,
     'Áp dụng lọc cộng tác dựa trên người dùng và sản phẩm để gợi ý sản phẩm cho website thương mại điện tử.'),
    ('LT-2024-045', 'Hệ thống quản lý thư viện trường ĐH', 'Trần Quang Vũ', 'TS. Nguyễn Thị Hồng', 'DA2024-1', 8.0,
     'Quản lý đầu sách, độc giả, mượn trả và thống kê cho thư viện trường đại học.'),
]


def main():
    db = sqlite3.connect(server.DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript(server.SCHEMA)
    with db:
        clear(db)
        users(db)
        periods(db)
        db.execute("INSERT INTO settings(key, value) VALUES('current_period', ?) "
                   "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (P,))
        lecturers_topics_students(db)
        requests(db)
        plans_reports(db)
        theses_defense(db)
        archive(db)
        notifications(db)
    counts = {t: db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in
              ('users', 'periods', 'lecturers', 'topics', 'students', 'requests', 'plans', 'reports', 'theses', 'councils',
               'defenses', 'reviews', 'scores', 'archive', 'notifications')}
    print('[ThesisHub] Đã nạp dữ liệu minh họa vào', server.DB_PATH)
    print('  ' + ', '.join(f'{k}: {v}' for k, v in counts.items()))


def clear(db):
    ph = ','.join('?' * len(PERIOD_IDS))
    for t in ('scores', 'reviews', 'defenses', 'council_members', 'councils', 'theses', 'reports', 'plan_milestones', 'plans',
              'requests', 'students', 'topics', 'lecturers', 'period_phases'):
        db.execute(f'DELETE FROM {t} WHERE period_id IN ({ph})', PERIOD_IDS)
    db.execute(f'DELETE FROM periods WHERE id IN ({ph})', PERIOD_IDS)
    db.execute(f"DELETE FROM archive WHERE period IN ({ph},'DA2024-1','DA2024-2')", PERIOD_IDS)
    db.execute('DELETE FROM notifications WHERE id BETWEEN 9000000 AND 9999999')
    # Tài khoản sinh viên của bản dữ liệu cũ (mã 2201xxxx, lớp K16) được thay bằng mã 2301xxxx, lớp K17
    for code, *_ in STUDENTS:
        old = 's2201' + code[4:]
        for t in ('sessions', 'login_log', 'reset_tokens', 'notifications'):
            db.execute(f'DELETE FROM {t} WHERE user_id=?', (old,))
        db.execute('DELETE FROM users WHERE id=?', (old,))


def put_user(db, uid, code, name, email, roles, dept, pw=PW, must=0, status='Hoạt động'):
    db.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
    db.execute('INSERT INTO users(id, code, name, email, roles, dept, password_hash, status, must_change_pw) VALUES(?,?,?,?,?,?,?,?,?) '
               'ON CONFLICT(id) DO UPDATE SET code=excluded.code, name=excluded.name, email=excluded.email, roles=excluded.roles, '
               'dept=excluded.dept, password_hash=excluded.password_hash, status=excluded.status, must_change_pw=excluded.must_change_pw, '
               'failed=0, locked_until=0', (uid, code, name, email, roles, dept, pw, status, must))


def users(db):
    for uid, code, name, email, roles, dept in STAFF:
        fresh = uid == BINH  # Hình 1.17: tài khoản vừa tạo, mật khẩu mặc định
        put_user(db, uid, code, name, email, roles, dept, PW_DEFAULT if fresh else PW, 1 if fresh else 0)
    for code, name, cls, _, _, email, *_ in STUDENTS:
        uid = 'demo-sv' if code == '24100188' else 's' + code
        put_user(db, uid, code, name, email or f'{code}@st.phenikaa-uni.edu.vn', 'SV', cls,
                 status='Khóa' if code in LOCKED else 'Hoạt động')


def periods(db):
    rows = [  # Hình 1.19, 1.20 (5 giai đoạn theo mô hình của phần mềm; giai đoạn 1 gồm đề xuất – duyệt – đăng ký đề tài)
        ('DA2025-1', 'ĐATN HK1 2025-2026', 'Đã kết thúc', [('2025-09-15', '2025-10-12'), ('2025-10-13', '2026-01-04'),
                                                           ('2026-01-05', '2026-01-16'), ('2026-01-19', '2026-01-23'), ('2026-01-25', '2026-01-25')]),
        ('DA2025-2', 'ĐATN HK2 2025-2026', 'Đã kết thúc', [('2026-02-09', '2026-03-08'), ('2026-03-09', '2026-05-24'),
                                                           ('2026-05-25', '2026-06-07'), ('2026-06-15', '2026-06-19'), ('2026-06-20', '2026-06-20')]),
        (P, 'ĐATN HK1 2026-2027', 'Đang diễn ra', [('2026-09-14', '2026-10-12'), ('2026-10-13', '2027-01-03'),
                                                   ('2027-01-04', '2027-01-17'), ('2027-01-18', '2027-01-22'), ('2027-01-24', '2027-01-24')]),
        ('DA2026-2', 'ĐATN HK2 2026-2027', 'Bản nháp', [('2027-02-08', '2027-03-14'), ('2027-03-15', '2027-05-30'),
                                                       ('2027-05-31', '2027-06-06'), ('2027-06-14', '2027-06-18'), ('2027-06-19', '2027-06-19')]),
    ]
    names = ['Đăng ký đề tài', 'Thực hiện', 'Nộp quyển', 'Bảo vệ', 'Kết quả']
    for pid, name, status, phases in rows:
        db.execute('INSERT INTO periods(id, name, status, w_gv, w_pb, w_hd, assign_locked) VALUES(?,?,?,30,20,50,0)', (pid, name, status))
        for i, (s, e) in enumerate(phases):
            db.execute('INSERT INTO period_phases VALUES(?,?,?,?,?)', (pid, i, names[i], s, e))


def lecturers_topics_students(db):
    for uid, deg, quota in LECTURERS:
        db.execute('INSERT INTO lecturers VALUES(?,?,?,?)', (P, uid, deg, quota))
    for tid, title, gv, slots, status, cmt, desc, req, reserved in TOPICS:
        db.execute('INSERT INTO topics(period_id, id, title, gv, slots, status, comment, descr, req, reserved) VALUES(?,?,?,?,?,?,?,?,?,?)',
                   (P, tid, title, gv, slots, status, cmt, desc, req, reserved))
    for code, name, cls, credits, gpa, _, inside, gvhd, tid in STUDENTS:
        if inside:
            uid = 'demo-sv' if code == '24100188' else 's' + code
            db.execute('INSERT INTO students VALUES(?,?,?,?,?,?,?,?,?)', (P, code, uid, name, cls, gpa, credits, gvhd, tid))


def requests(db):
    for rid, code, tid, nv, msg, status, reason, date, cv in REQUESTS:
        db.execute('INSERT INTO requests VALUES(?,?,?,?,?,?,?,?,?,?)', (rid, P, code, tid, nv, msg, status, reason, date, cv))


def add_plan(db, code, ms, status='Đã duyệt', comment=''):
    db.execute('INSERT INTO plans VALUES(?,?,?,?)', (P, code, status, comment))
    for i, (title, due, desc) in enumerate(ms):
        db.execute('INSERT INTO plan_milestones VALUES(?,?,?,?,?,?)', (P, code, i, title, due, desc))


REPORT_ID = [5000]


def add_report(db, code, m, date, file, size, note, status, comment='', late=0):
    REPORT_ID[0] += 1
    db.execute('INSERT INTO reports VALUES(?,?,?,?,?,?,?,?,?,?,?)',
               (REPORT_ID[0], P, code, m, date, file, size, note, late, status, comment))


def plans_reports(db):
    # Nguyễn Đình Tùng – Hình 1.36–1.40, 1.43 (7/7 mốc đạt ở thời điểm GVHD xác nhận đủ điều kiện)
    add_plan(db, '24100188', MA_PLAN, 'Đã duyệt', MA_PLAN_COMMENT)
    f = lambda m: f'BaoCao_Moc{m}_24100188.pdf'  # noqa: E731
    add_report(db, '24100188', 0, '2026-10-11T20:30', f(1), 1.2, 'Đề cương: mục tiêu, phạm vi, kế hoạch thực hiện.', 'Đạt',
               'Đề cương rõ ràng, phạm vi phù hợp.')
    add_report(db, '24100188', 1, '2026-11-01T21:05', f(2), 2.1, 'Khảo sát nhu cầu sinh viên và doanh nghiệp, đặc tả 18 use-case.', 'Đạt',
               'Tài liệu SRS đầy đủ.')
    add_report(db, '24100188', 2, '2026-11-25T08:40', f(3), 3.4, 'Thiết kế kiến trúc, CSDL và giao diện.', 'Đạt',
               'Thiết kế hợp lý. Lưu ý nộp đúng hạn.', late=1)
    add_report(db, '24100188', 3, '2026-12-06T22:10', f(4), 1.8, 'Cài đặt module gợi ý bằng lọc cộng tác, API gợi ý.', 'Cần bổ sung',
               'Bổ sung đánh giá độ chính xác của module gợi ý và tài liệu API.')
    add_report(db, '24100188', 3, '2026-12-10T19:25', 'BaoCao_Moc4_24100188_v2.pdf', 2.0,
               'Bổ sung đánh giá Precision@10 và tài liệu API theo góp ý.', 'Đạt', 'Đã bổ sung đầy đủ.')
    add_report(db, '24100188', 4, '2026-12-19T22:41', f(5), 2.4,
               'Công việc đã hoàn thành: Hoàn thành trang tìm kiếm việc làm, trang chi tiết tin tuyển dụng, tích hợp API gợi ý top-10. '
               '| Khó khăn: Tốc độ phản hồi API gợi ý còn chậm (~3s) với 5.000 tin. | Kế hoạch tiếp theo: Tối ưu bộ đệm, viết kịch bản kiểm thử. '
               '| Mã nguồn: https://github.com/minhanh-nguyen/job-recommender', 'Đạt',
               'Giao diện hoàn chỉnh, đúng thiết kế. Cần bổ sung xử lý khi không có kết quả gợi ý ở mốc kiểm thử.')
    add_report(db, '24100188', 5, '2027-01-03T21:00', f(6), 1.6, 'Kiểm thử chức năng và hiệu năng; thời gian phản hồi API còn 0,8s.', 'Đạt',
               'Đạt yêu cầu.')
    add_report(db, '24100188', 6, '2027-01-14T18:30', f(7), 6.9, 'Bản thảo quyển đồ án và slide bảo vệ.', 'Đạt', 'Đủ điều kiện nộp quyển.')

    # Các sinh viên khác – Hình 1.40, 1.41
    for code, (n, pattern) in PROGRESS.items():
        add_plan(db, code, [(t, d, '') for t, d in TEMPLATE[:n]])
        for m, ch in enumerate(pattern):
            due = TEMPLATE[m][1]
            add_report(db, code, m, due + 'T20:00', f'BaoCao_Moc{m + 1}_{code}.pdf', 1.5,
                       f'Báo cáo tiến độ mốc {m + 1}: {TEMPLATE[m][0].lower()}.', STATUS_WORD[ch], STATUS_CMT[ch])


def theses_defense(db):
    for cid, date, session, room, members, published in COUNCILS:
        db.execute('INSERT INTO councils VALUES(?,?,?,?,?,?)', (P, cid, date, session, room, published))
        for uid, role in members:
            db.execute('INSERT INTO council_members VALUES(?,?,?,?)', (P, cid, uid, role))
    members_of = {c[0]: c[4] for c in COUNCILS}

    # Quyển đồ án + phiếu GVHD (Hình 1.42, 1.43)
    db.execute('INSERT INTO theses VALUES(?,?,?,?,?,?,?,?,?,?)', (
        P, '24100188', 'DATN_24100188_v2.pdf', 8.7,
        'job-recommender-src.zip (34,1 MB) · Sản phẩm: https://jobhub-demo.vercel.app · Phụ lục: KetQuaKiemTraTrungLap.pdf (0,6 MB)',
        '2027-01-14T20:05', 8, 1, 8.5,
        'Sinh viên có năng lực tốt, sản phẩm có tính ứng dụng. Đề nghị cho bảo vệ. '
        '| Tinh thần, thái độ làm việc (9.0): Chủ động, nộp báo cáo đúng hạn, tiếp thu góp ý tốt. '
        '| Nội dung và kết quả đạt được (8.5): Hoàn thành hệ thống gợi ý, độ chính xác top-10 đạt 78%. '
        '| Hình thức trình bày quyển (8.0): Trình bày đúng mẫu, còn một số lỗi chính tả ở chương 3.'))
    others = {'23010188': 'Hoàn thành các chức năng chính, tiến độ còn chậm ở giai đoạn cài đặt.',
              '23010057': 'Sản phẩm đáp ứng yêu cầu cơ bản. Đồng ý cho bảo vệ.',
              '23010120': 'Kết quả nhận dạng tốt, quyển trình bày chỉn chu. Đồng ý cho bảo vệ.',
              '23010233': 'Sản phẩm còn thiếu một số chức năng, đồng ý cho bảo vệ để hội đồng đánh giá.',
              '23010089': 'Sản phẩm hoàn chỉnh, có tính ứng dụng. Đồng ý cho bảo vệ.'}
    for code, (cid, time, rv, gv, pb, hd) in DEFENSES.items():
        if code != '24100188':
            db.execute('INSERT INTO theses VALUES(?,?,?,?,?,?,?,?,?,?)',
                       (P, code, f'{code}_{P}_v1.pdf', 6.5, f'{code}_src.zip', '2027-01-15T21:00', 10, 1, gv, others[code]))
        db.execute('INSERT INTO defenses VALUES(?,?,?,?,?)', (P, code, cid, rv, time))
        # Phiếu phản biện (Hình 1.46 cho Nguyễn Đình Tùng)
        if code == '24100188':
            comment = ('Tính cấp thiết, mục tiêu đề tài (8.5): Đề tài có ý nghĩa thực tiễn, mục tiêu rõ ràng. '
                       '| Phương pháp và kết quả (7.5): Mô hình lọc cộng tác hợp lý; thiếu so sánh với baseline. '
                       '| Hình thức quyển (8.0): Đúng mẫu, hình vẽ rõ ràng.')
            questions = '1. Em xử lý bài toán "cold-start" với sinh viên mới như thế nào? 2. Vì sao chọn chỉ số Precision@10 để đánh giá?'
        else:
            comment, questions = 'Quyển đồ án đúng mẫu, nội dung đáp ứng mục tiêu đề tài.', '1. Em đánh giá kết quả như thế nào?'
        db.execute('INSERT INTO reviews VALUES(?,?,?,?,?,?,?,?)', (P, code, rv, comment, questions, pb, 1, '2027-01-17T16:00'))
        # Phiếu chấm của 3 thành viên (Hình 1.47 cho phiếu của TS. Mai Thúy Nga)
        for (uid, _), total in zip(members_of[cid], hd):
            c = MA_HUNG_SCORE if (code == '24100188' and uid == HUNG) else split(total)
            cmt = 'Trình bày rõ ràng, trả lời tốt câu hỏi về cold-start.' if (code == '24100188' and uid == HUNG) else ''
            db.execute('INSERT INTO scores VALUES(?,?,?,?,?,?,?,?)', (P, code, uid, *c, cmt))

    # Hình 1.45: sinh viên đủ điều kiện nhưng chưa xếp lịch
    db.execute('INSERT INTO theses VALUES(?,?,?,?,?,?,?,?,?,?)', (P, '23010301', f'23010301_{P}_v1.pdf', 5.9, '23010301_src.zip',
                                                                   '2027-01-16T10:00', 12, 1, 6.5, 'Đồng ý cho bảo vệ.'))
    for code, (size, date, sim, gv, cmt) in EXTRA_THESES.items():
        db.execute('INSERT INTO theses VALUES(?,?,?,?,?,?,?,?,?,?)', (P, code, f'{code}_{P}_v1.pdf', size, f'{code}_src.zip', date, sim, 1, gv, cmt))
    # Lịch bảo vệ HĐ05: đã phân công phản biện, phiếu phản biện chưa nhập
    for i, (code, (cid, time, rv)) in enumerate(PENDING_DEFENSES.items()):
        db.execute('INSERT INTO defenses VALUES(?,?,?,?,?)', (P, code, cid, rv, time))
        name = db.execute('SELECT name FROM students WHERE period_id=? AND code=?', (P, code)).fetchone()[0]
        db.execute('INSERT INTO notifications VALUES(?,?,?,?,?)', (9100001 + i, rv,
                   f'Bạn được phân công phản biện đồ án của {name} (bảo vệ 22/01/2027, {cid}).', '2027-01-17T09:00', 0))


def archive(db):
    for aid, title, student, gv, period, score, abstract in ARCHIVE:
        db.execute('INSERT INTO archive VALUES(?,?,?,?,?,?,?,?)', (aid, title, student, gv, period, score, abstract, None))


def notifications(db):
    rows = [
        # Hình 1.15 – trang chủ sinh viên
        ('demo-sv', 'Đổi mật khẩu thành công.', '2026-10-01T10:05', 1),
        ('demo-sv', 'Bạn đã được thêm vào đợt đồ án DA2026-1 – ĐATN HK1 2026-2027.', '2026-10-04T16:30', 1),
        ('demo-sv', 'Ngân hàng đề tài đợt DA2026-1 đã được công bố: 142 đề tài.', '2026-10-05T08:00', 0),
        ('demo-sv', 'TS. Mai Thúy Nga đã từ chối nguyện vọng của bạn (đề tài DT-CNTT-012).', '2026-10-06T09:12', 0),
        ('demo-sv', 'Bộ môn đã phân công bạn vào đề tài DT-CNTT-015 với GVHD TS. Mai Thúy Nga.', '2026-10-13T08:30', 1),
        ('demo-sv', 'GVHD đã đánh giá báo cáo mốc 5: Đạt.', '2026-12-21T09:15', 1),
        ('demo-sv', 'Nộp quyển thành công – phiên bản v2.', '2027-01-14T20:05', 1),
        ('demo-sv', 'Lịch bảo vệ: HĐ01, 09:00 ngày 20/01/2027, phòng A2-301.', '2027-01-15T09:00', 1),
        ('demo-sv', 'Kết quả bảo vệ đồ án của bạn đã được công bố.', '2027-01-24T08:00', 0),
        ('demo-sv', 'Hội đồng HĐ01 yêu cầu chỉnh sửa sau bảo vệ (hạn nộp bản hoàn thiện 31/01/2027): '
                    '1. Bổ sung so sánh với mô hình baseline (popularity-based) ở chương 4. '
                    '2. Sửa lỗi chính tả chương 3 và cập nhật danh mục tài liệu tham khảo. 3. Bổ sung phụ lục hướng dẫn cài đặt.',
         '2027-01-24T08:05', 0),
        ('s23010189', 'Bạn đã được loại khỏi đợt DA2026-1. Lý do: chuyển đợt sau.', '2026-10-10T10:00', 0),
        # Giảng viên hướng dẫn
        (HUNG, 'Nguyễn Đình Tùng đã gửi kế hoạch thực hiện (6 mốc) chờ duyệt.', '2026-10-05T21:14', 1),
        (HUNG, 'Lê Thị Ngọc Bích gửi nguyện vọng NV2 vào đề tài DT-CNTT-013.', '2026-10-07T15:30', 0),
        (HUNG, 'Bộ môn phân công sinh viên Nguyễn Đình Tùng (24100188) cho bạn hướng dẫn.', '2026-10-13T08:30', 1),
        (HUNG, 'Nguyễn Đình Tùng đã nộp báo cáo mốc 5.', '2026-12-19T22:41', 1),
        (HUNG, 'Nguyễn Đình Tùng đã nộp quyển đồ án (phiên bản 1), chờ xác nhận đủ điều kiện bảo vệ.', '2027-01-10T09:12', 1),
        (HUNG, 'Nguyễn Đình Tùng đã nộp quyển đồ án (phiên bản 2), chờ xác nhận đủ điều kiện bảo vệ.', '2027-01-14T20:05', 1),
        (HUNG, 'Bạn là thư ký hội đồng HĐ01 (20/01/2027, buổi sáng, phòng A2-301).', '2027-01-12T10:00', 1),
        (HUNG, 'Bạn là chủ tịch hội đồng HĐ04 (21/01/2027, buổi sáng, phòng A2-304).', '2027-01-12T10:10', 0),
        (NMDUC, 'Bạn được phân công phản biện đồ án của Nguyễn Đình Tùng (bảo vệ 20/01/2027).', '2027-01-15T09:00', 1),
        # Trưởng khoa
        (VINH, 'TS. Mai Thúy Nga đề xuất đề tài "Kiểm thử tự động API cho hệ thống thương mại điện tử" chờ phê duyệt.', '2026-09-29T10:00', 0),
        (VINH, 'ThS. Phạm Thu Trang đề xuất đề tài "Hệ thống quản lý thư viện số cho trường THPT" chờ phê duyệt.', '2026-09-30T09:00', 1),
        (VINH, 'ThS. Ngô Thanh Tùng đề xuất đề tài "Ứng dụng quản lý chi tiêu cá nhân đa nền tảng" chờ phê duyệt.', '2026-09-30T14:00', 0),
        (VINH, 'TS. Vũ Hoàng Long đề xuất đề tài "Phát hiện mã độc Android bằng học máy" chờ phê duyệt.', '2026-10-01T08:30', 0),
        # Giáo vụ khoa
        (GVU, 'TS. Mai Thúy Nga đã xác nhận phiếu của Nguyễn Đình Tùng: đủ điều kiện.', '2027-01-15T08:00', 1),
        (GVU, 'TS. Ngô Minh Đức đã gửi phiếu phản biện cho Nguyễn Đình Tùng.', '2027-01-17T16:00', 1),
    ]
    for i, (uid, text, t, read) in enumerate(rows):
        db.execute('INSERT INTO notifications VALUES(?,?,?,?,?)', (9000001 + i, uid, text, t, read))


if __name__ == '__main__':
    main()
