> Tài liệu đối chiếu form đã chốt. Các đường dẫn trong tài liệu này thuộc dự án giáo viên, không phải tệp có trong repo. Các yêu cầu mới hơn xem docs/quy-chuan-hien-hanh.md.

# Form Bài 1 đã chốt — 23/10/2026

Đây là quy chuẩn mới nhất, thay thế các ghi chú thử nghiệm trước ngày chốt. Áp dụng cho các bài tiếp theo của khoá giao tiếp cấp tốc. Không tự đổi bố cục bài khoá giáo viên đã chỉnh.

## Mẫu chuẩn và nguồn

- File dùng để dạy và đối chiếu: `Unit1-Chaohoi.html` (74 slide, tự chứa ảnh/font/audio, offline).
- Nguồn và công cụ sửa Bài 1: `nguon-chinh-sua/`.
- PPTX giáo viên chỉnh tay: `powerpoint/Unit-01_Chao-hoi_mau-chinh-sua.pptx`. Bản HTML đã có các thay đổi duyệt sau PPTX; HTML là chuẩn cuối cùng.
- Ảnh/audio gốc, giáo trình, tài liệu Bài 2 vẫn được giữ. Các nội dung Bài 1 là mẫu cấu trúc, không sao chép máy móc từ vựng sang bài khác.

## Khung, màu và chữ

- Slide ngang 16:9, khung 1920 × 1080 (1080p); không cần render 4K, không dùng ảnh slide 1248 × 702 để xuất bản.
- Giữ nền, logo và vị trí đầu mục của mẫu. Không hiện số trang cuối slide.
- Màu cam cho chữ/nghĩa Việt/nhấn cam: `#f15922`. Chữ Hán và pinyin xanh dương đậm theo mẫu (`#275389`, `#002060`); tiêu đề tiếng Trung ở bìa `#1300aa`, in đậm; nghĩa Việt đặt bên dưới.
- Cỡ mặc định: Hán tự và pinyin 52px, nghĩa Việt câu 42px, loại từ 32px, nghĩa Việt từ mới 36px. Giữ các cỡ đã được duyệt riêng trong mẫu (bài khoá 64px, câu thay thế, bài tập…) khi cần vừa bố cục; đề và đáp án cùng cỡ.
- Mọi Hán tự đều có pinyin phía trên, pinyin in đậm. Các text box ví dụ cách dòng 1,25. Không chồng chữ, cắt chữ hoặc làm sai thanh điệu; 不 có biến điệu đúng ngữ cảnh.

## Từ vựng và bài khoá

- Một từ mới mỗi slide: thẻ xanh một bên, ảnh một bên. Thẻ gồm loa, pinyin, Hán tự, loại từ, nghĩa Việt. Loa và pinyin đặt cao, khoảng hở với Hán tự khoảng 0,5cm (19px).
- Ảnh đúng tình huống; resize toàn ảnh, dùng `object-fit:contain`, không cắt mất người/đồ vật. Ghi chú giáo viên mô tả ảnh không được hiện trên slide.
- Danh sách từ mới bám bài khoá; không tự thêm từ ngoài bài. Sắp xếp theo nhóm nghĩa, chẳng hạn 哥哥 → 弟弟 → 姐姐 → 妹妹.
- Bài khoá giữ form gốc, pinyin trên Hán tự, nghĩa Việt dưới câu. Các khung xanh trích từ/thay thế và mũi tên đúng vị trí đã duyệt; bấm mới hiện. Mỗi text box thay thế cũng có pinyin.
- Mở rộng giữ đường nhánh; lần lượt từng nhánh: ảnh + từ trước, câu ví dụ sau.
- Tổng kết từ sau mỗi phần thành nối cặp Hán tự+pinyin với nghĩa Việt, nghĩa đảo thứ tự, tối đa hai slide mỗi phần, đúng danh sách từ đã dạy. Nối đúng thì phát audio từ vừa nối.

## Audio và tương tác

- Từ vựng dùng **Microsoft Edge TTS, giọng theo lựa chọn giáo viên cho từng từ, tốc độ 65% (`rate=-35%`)**. Đây là lựa chọn mới nhất, thay cấu hình Xiaoxiao 70% trước đó. Yunyang cho 你、好、渴、请、你好; Yunxi cho 我、很; các từ còn lại dùng Xiaoxiao. Các lựa chọn cho cụm/câu được lưu trong `nguon-chinh-sua/voice-choices-65.json`. Chỉ giảm tốc độ audio từ vựng; không đổi audio bài khoá và luyện phản xạ. Tạo audio thật và nhúng vào HTML; không gắn nhãn Xiaoxiao cho audio cũ.
- Loa từ vựng tự phát một lần khi vào slide; có thể bấm loa nghe lại. Matching dùng cùng audio từ vựng tương ứng, chỉ phát khi nối đúng.
- Audio bài khoá dùng file giáo viên cung cấp, gán theo phần/trang, giữ nguyên nội dung. Bài luyện phản xạ dùng file giáo viên cung cấp với phát/dừng, tua, lùi 5 giây, nghe lại từ đầu; chuyển slide phải dừng audio.
- Bấm nửa phải: hiện bước kế rồi sang slide; nửa trái: thu lại bước cuối rồi về trước. Phím mũi tên tương tự. Bấm phải hiện tiếp.
- Đáp án điền vào chỗ trống, không thêm dòng đáp án trùng bên dưới. Dấu hỏi/chấm đặt ngoài phần ẩn và luôn hiện sau dòng trống. Lựa chọn đáp lại đúng chuyển đỏ ngay tại lựa chọn.
- Thanh công cụ: trước/sau, ẩn nghĩa Việt, cuộn, trình chiếu toàn màn hình, bút. Bấm bút mới mở các icon tẩy, hoàn tác, xoá tất cả ghi chú trên slide và năm màu bút. Khi viết/tẩy không kích hoạt điều hướng slide.

## Phần luyện tập

Bài 1 đã chốt bảy slide luyện tập sau trang phân phần; các bài sau giữ trình tự, điều chỉnh nội dung theo bài:

1. Hai bảng từ vựng riêng: nói tiếng Trung hoặc nghĩa Việt vào ô trống; Hán tự+pinyin xanh, nghĩa Việt cam kể cả khi hiện đáp án.
2. Hoàn thành câu: sáu câu, nghĩa Việt trên câu tiếng Trung cần điền.
3. Trên: bốn câu sắp xếp, đáp án theo chiều ngang ngay cạnh đề; dưới: bốn câu dịch Việt → Trung. Không thêm tiêu đề chung “Sắp xếp câu và dịch”, không kẻ vạch ngăn hai phần. Câu dịch thứ hai của Bài 1 là “Tôi không đói.” → 我不饿。
4. Hoàn thành hội thoại theo bốn tranh; chỉ ghi đề bài chung một lần ở trên.
5. Hội thoại dài theo hai tranh: chia trái/phải, mỗi bên ảnh phía trên và hội thoại phía dưới, đáp án bấm hiện tại chỗ trống; dấu câu luôn hiện. Bài 1 dùng hai bạn làm việc nhiều tài liệu và hai bạn cầm số sách khác nhau.
6. Luyện phản xạ nghe câu hỏi, trả lời trong khoảng nghỉ, có trình phát audio tua được.
7. Tự luyện thực tế: các tình huống bằng tiếng Việt dạng đầu dòng, từ gợi ý có pinyin bên dưới; không viết “đi quanh lớp”.

## Cách thực hiện bài tiếp theo

Đọc file HTML chuẩn và quy chuẩn này trước khi soạn. Lấy nội dung bài tiếp theo từ giáo trình và yêu cầu giáo viên; giữ hệ thống bố cục, màu, audio và tương tác đã chốt. Kiểm tra trực quan, tràn khung, chữ đè, ảnh bị cắt, pinyin, đáp án, audio và matching. Mặc định đưa bản xem trước để giáo viên duyệt; chỉ xuất HTML cuối khi giáo viên yêu cầu. HTML xuất phải tự chứa đầy đủ và mở offline.
