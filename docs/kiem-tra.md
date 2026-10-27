# Kiểm tra và điều kiện bàn giao

## Máy kiểm tra được

- JSON đọc được, ID khung không trùng, khóa audio trỏ đúng tệp.
- Ảnh/audio/font tồn tại. Preview đánh dấu thiếu; bản xuất chặn thiếu.
- Không phụ thuộc đường dẫn máy tác giả. HTML xuất không cần tải ảnh/audio từ mạng.
- MP3 giáo viên khớp byte/SHA-256 với file nguồn.
- Lịch đủ 30 buổi, buổi 30 không dạy mới.

## Giáo viên/trợ lý phải mở xem

1. Bìa, thẻ từ ngắn/dài, hội thoại nhiều dòng, mọi dạng ngữ pháp và bài tập.
2. Chữ không đè, không cắt, không vượt khung; chú ý không che ví dụ; ảnh giữ trọn cảnh.
3. Pinyin và nghĩa đúng, tên riêng viết hoa, từ đã học đủ trước ví dụ.
4. Khung thay thế/mũi tên chỉ đúng cụm, ban đầu ẩn; kéo khung thì đường theo.
5. Ngân hàng từ đảo thứ tự nhưng nút tiếp đi câu 1→2→3…; từ vào đúng vị trí; lùi trả từ về; mỗi câu tự phát đúng audio.
6. Luyện phản xạ: phát/dừng, tua, lùi 5 giây, từ đầu; chuyển trang phải dừng.
7. Cuộn sang ít nhất ba trang rồi tắt cuộn, vẫn ở trang vừa xem.
8. Matching đọc đúng audio; bút/tẩy/hoàn tác không chuyển slide; `▧ Khung` lưu/khôi phục JSON được.

Preview hỗ trợ `?qa=1`; sau khi tải, DOM có `#qa-result` chứa danh sách lỗi tràn. Đọc kết quả qua công cụ trình duyệt, không dùng nó thay toàn bộ kiểm tra mắt hoặc gọi thao tác sửa DOM từ công cụ chỉ cho phép đọc.

Kiểm tra lại khi đổi nội dung, cỡ chữ, ảnh hoặc thuật toán ảnh hưởng bố cục; không tự báo “đã kiểm tra” khi chỉ chạy builder.
