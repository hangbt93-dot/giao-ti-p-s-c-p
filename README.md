# Quy trình soạn giáo án giao tiếp tiếng Trung

Bộ quy trình và mã dựng HTML rút ra từ dự án đã chỉnh cùng giáo viên: soạn theo bài khoá → kiểm tra vốn từ → tạo tài nguyên → xem trước → sửa theo ghi chú → duyệt → xuất offline.

Đây là bộ công cụ tác giả, không phải bộ giáo trình thương mại hoặc toàn bộ bài giảng đã chốt. Repo chứa hướng dẫn, lịch học, mẫu JSON rút gọn, giao diện và công cụ kiểm tra. Sách, ảnh lớp học, font, audio giáo viên, ghi chú và file xuất giữ cục bộ.

## Chạy thử

Cần Python **3.12 trở lên**. Ví dụ dưới dùng `python3`; có thể thay bằng `python` trên Windows.

```sh
python3 -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/workflow.py init-unit local/Unit2-Mau/source
python scripts/workflow.py build local/Unit2-Mau/source
python scripts/workflow.py check local/Unit2-Mau/source/preview.html
python scripts/workflow.py serve --port 8767
```

Mở `http://127.0.0.1:8767/local/Unit2-Mau/source/preview.html`. Mẫu có ảnh giữ chỗ và loa bị vô hiệu khi chưa có audio. Không dùng mẫu này để dạy ngay.

## Các tệp cần đọc

| Tệp | Mục đích |
|---|---|
| [Quy trình](docs/quy-trinh.md) | Đầu vào, thứ tự công việc, bàn giao |
| [Quy chuẩn hiện hành](docs/quy-chuan-hien-hanh.md) | Form Bài 1 và các thay đổi giáo viên đã yêu cầu |
| [Lịch khóa học](docs/lo-trinh-hien-hanh.md) | 19 unit, 29 buổi học + 1 buổi kiểm tra |
| [Kiểm tra](docs/kiem-tra.md) | Kiểm tra máy và kiểm tra trực quan |
| [Dữ liệu và tài nguyên](docs/du-lieu.md) | Hợp đồng JSON, audio, ảnh, layout |
| [Trạng thái](docs/trang-thai.md) | Bản nào đã chốt, bản nào chỉ để duyệt |
| [AGENTS.md](AGENTS.md) | Hướng dẫn cho trợ lý tiếp tục dự án |

## Tạo audio và xuất

```sh
python scripts/generate_audio.py local/Unit2-Mau/source --dry-run
python scripts/generate_audio.py local/Unit2-Mau/source --kind vocabulary
python scripts/generate_audio.py local/Unit2-Mau/source --kind grammar
python scripts/workflow.py build local/Unit2-Mau/source
```

Audio từ vựng: Edge TTS, mặc định Xiaoxiao, tốc độ 65% (`-35%`); lựa chọn riêng nằm trong trường `voice` của từ. Audio bài khoá và phản xạ do giáo viên cung cấp giữ nguyên. Tạo TTS cần Internet; dựng và xuất HTML không cần mạng.

Sau khi giáo viên duyệt và tài nguyên đủ:

```sh
python scripts/workflow.py snapshot local/Unit2-Mau/source
python scripts/workflow.py export local/Unit2-Mau/source/preview.html output/Unit2-Mau.html --approved
```

Xuất sẽ nhúng tài nguyên, chặn ảnh/audio thiếu và sao lưu nếu đích đã tồn tại. `--allow-draft` chỉ dùng thử kỹ thuật; không dùng để phát hành giáo án còn thiếu tài nguyên.

## Kiểm tra bộ công cụ

```sh
python -m unittest discover -s tests -v
```

Bài test dựng một bản xem trước thật trong thư mục tạm, xác nhận thiếu tài nguyên chặn xuất, thử nhúng ảnh SVG và kiểm tra lịch khóa học. Kiểm tra này không thay việc mở trình duyệt nghe audio, xem nét ghi chú và thử tương tác.

## Phạm vi bản đầu

Recipe hiện bao phủ form giao tiếp: thẻ từ, hội thoại, thay thế có mũi tên chỉnh được, ngữ pháp một điểm/trang, ô từ bay vào chỗ trống, matching và phản xạ có tua. Một số ví dụ kiểm tra bài cũ và nhãn tình huống kế thừa bài mẫu; khi làm unit mới phải biên tập lại, không nhân bản nội dung máy móc. Chưa áp dụng giấy phép nguồn mở; không có quyền phân phối lại giáo trình của bên thứ ba đi kèm repo.

Mẫu CI ở [docs/templates/github-actions-check.yml](docs/templates/github-actions-check.yml). Chưa kích hoạt GitHub Actions: quyền đẩy hiện tại không có scope `workflow`. Có thể bật sau bằng cách đặt mẫu vào `.github/workflows/check.yml` với tài khoản/quyền thích hợp. Các bài test vẫn chạy cục bộ bằng lệnh trên.
