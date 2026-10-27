# Quy trình làm một unit

1. **Nhận đầu vào.** Xác định bài, 90 phút/buổi, mục tiêu giao tiếp; đọc lịch hiện hành và yêu cầu mới nhất. Nguồn sách ở thư mục riêng. Xác định file chính đã duyệt và bản xem trước đang chỉnh.
2. **Biên tập nội dung.** Đối chiếu bài khoá, chọn vốn từ chủ động/nhận biết, sắp từ theo phụ thuộc. Một ví dụ đặt ở thẻ từ cuối cùng cần biết để hiểu câu. Dùng lại từ đã học; không đưa cả danh sách nhiều bài sách vào một buổi.
3. **Lập JSON.** Một nguồn dữ liệu cho thẻ từ, hội thoại, ngữ pháp, đáp án, thứ tự và khóa audio. Không chỉnh HTML sinh ra rồi chạy builder cũ ghi đè.
4. **Làm tài nguyên.** Ảnh đúng người, quốc tịch và tình huống; không cắt người. Từ trừu tượng dùng biểu tượng phù hợp. Audio từ vựng đúng giọng đã chọn; giữ nguyên audio giáo viên. Nghe lại từng từ, đặc biệt thanh 3 và biến điệu 不.
5. **Dựng preview.** Tài nguyên dạng tệp để dễ sửa. Kiểm tra ảnh/audio thiếu, rồi kiểm tra trên trình duyệt. Không mặc định xuất file chính thức.
6. **Sửa theo ghi chú.** Sao lưu SVG/ảnh ghi chú, dữ liệu và layout. Phân biệt nét chú thích với nội dung cần đưa lên slide. Dấu ngoặc trên khung nghĩa là thu khung theo chữ. Sửa mẫu giáo viên đã ghi, áp dụng nhất quán các trang cùng loại; không tự diễn giải dấu chưa đọc được.
7. **Duyệt và bàn giao.** Kiểm tra lại sau từng đổi nội dung có ảnh hưởng bố cục. Chỉ khi giáo viên yêu cầu xuất mới tạo HTML tự chứa; sao lưu file cũ và ghi SHA-256/tài nguyên. Sau duyệt mới cập nhật sổ tay của unit đang làm.

## Cấu trúc cục bộ

```text
local/
  UnitN-Tenbai/
    source/
      lesson.json
      audio-manifest.json
      layout.json
      assets/
        photos/
        audio/
      preview.html             # sinh ra
      preview-model.json       # sinh ra
    teacher-notes/             # ghi chú gốc, không đưa Git
output/
  UnitN-Tenbai.html            # chỉ sau duyệt
```

Bản chính được coi là bất biến trong lúc sửa preview. Mỗi thay đổi mới phải ghi vào quy chuẩn hiện hành hoặc dữ liệu, không chỉ nằm trong lịch sử trò chuyện.
