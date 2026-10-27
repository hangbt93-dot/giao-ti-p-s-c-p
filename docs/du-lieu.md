# Dữ liệu, tài nguyên và phiên bản

`examples/Unit2-Mau/source/lesson.json` là ví dụ tích hợp rút gọn. Recipe hỗ trợ hợp đồng này; không tự suy ra dữ liệu từ file PowerPoint.

Các trường chính:

- `unit`, `title_zh`, `title_vi`, `revision`, `storage_id`: thông tin bài, phiên bản và vùng lưu riêng của ghi chú/layout.
- `parts`: từng phần, có `words`, `dialogues`, `grammar_pages`.
- Từ: `zh`, `pos`, `vi`, `photo` hoặc `visual`, `example`, `example_vi`, tùy chọn `voice`.
- Hội thoại: `cols` là các lượt `[vai, Hán, Việt]`; `replacement_links` chỉ rõ cột/lượt/cụm gốc và cụm thay; `characters` chọn icon.
- Ngữ pháp: `id`, một phần tử trong `points` với tên, công thức, cách dùng, mục tiêu, ví dụ; `note`; `practice` có Hán đầy đủ, từ cần điền, nghĩa và `audio_key`. `practice_after=false` để nối hai điểm trước một bài luyện chung; `practice_id` giữ ID bài chung.
- `practice`: các dạng bài cuối bài. `reflex_questions` là dữ liệu chuẩn bị, không tự thay file phản xạ giáo viên.

## Audio manifest

```json
[
  {"key":"word-是","file":"assets/audio/word-shi.mp3","voice":"zh-CN-XiaoxiaoNeural","rate":"-35%","kind":"word"},
  {"key":"reflex","file":"assets/audio/reflex-teacher.mp3","kind":"teacher-provided","preserve_speed":true}
]
```

Audio được gán bằng khóa, không dựa vào số thứ tự tệp tình cờ. Công cụ tạo TTS không ghi đè `teacher-provided`. Muốn giữ audio mới giáo viên gửi: chép vào assets/audio và cập nhật đúng khóa/loại trong manifest. TTS mới không có nghĩa đã phát âm chuẩn: vẫn phải nghe lại.

## Ảnh và font

Ảnh trong `assets/photos/<key>.png|jpg|jpeg|svg`; cờ có thể ở `assets/flag-xx.svg`. Mẫu dùng placeholder nếu thiếu và đánh dấu draft. Font nền là fallback hệ thống; muốn font cố định phải thêm font có quyền sử dụng vào nguồn cục bộ và tham chiếu bằng URL tương đối. Không kèm font/ảnh/sách không rõ quyền phân phối vào repo.

## Layout và ghi chú

Runtime xuất JSON bằng nút Tải bố cục; lưu thành `layout.json` cạnh `lesson.json`. Đó là nguồn cần mang sang máy khác; localStorage chỉ giúp chỉnh tại trình duyệt đang dùng. Sao lưu nét vẽ trước khi sửa rồi đổi `storage_id` nếu số/thứ tự trang thay đổi để tránh đặt nét cũ sai trang.

Repo chưa tự đọc chữ viết tay hoặc nhập notes từ một trình duyệt bất kỳ. Trợ lý phải mở đúng tab có nét ghi chú, đọc và biên tập; không hứa đã xử lý nét vẽ chỉ vì đã đọc JSON bài học.
