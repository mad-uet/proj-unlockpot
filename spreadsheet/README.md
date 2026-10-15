# Bảng tính bàn giao của gói nghiên cứu

Thư mục này tạo và kiểm tra bảng tính XLSX bàn giao từ đầu ra R của gói `research/`. Mọi lệnh chạy độc lập với thư mục `report/`, tài liệu LaTeX và đường dẫn máy làm việc cụ thể; chỉ cần thư mục `research/` là đủ. Python chỉ dùng thư viện chuẩn.

## Nội dung thư mục

| Tệp | Vai trò |
|---|---|
| `build-workbook.py` | Tạo `bang-diem-muc-do-quan-trong.xlsx` từ bản thử và đầu ra R |
| `check-workbook.py` | Đối chiếu giá trị lưu sẵn trong XLSX với đầu ra R (không chạy công thức) |
| `check-libreoffice.py` | Mở, sửa ô, tính lại, lưu và mở lại XLSX bằng LibreOffice Calc qua UNO |
| `bang-diem-muc-do-quan-trong.xlsx` | Bảng tính bàn giao |
| `tinh-huong-nhap-lieu.csv` | Ba tình huống nhập liệu của nhóm kinh doanh, đối chiếu kết quả R |
| `source-path.txt` | Thư mục đầu ra R dùng cho lượt tạo hiện tại (đường dẫn tương đối) |
| `source-sha256.csv` | SHA-256 của các tệp đầu vào đã dùng (đường dẫn tương đối với gốc `research/`) |

## Yêu cầu và đầu vào

- Python 3 cho `build-workbook.py` và `check-workbook.py`.
- LibreOffice kèm UNO cho `check-libreoffice.py`; nếu dùng Flatpak, script tự nhận đường dẫn UNO trong `/app/libreoffice/program`.
- Đầu vào mặc định là thư mục `../output-standard` (đầu ra chuẩn của quy trình R trong `../analysis`) và `../analysis/indicators.csv`. Một lượt chạy khác ở `../analysis/output/` cũng dùng được qua đối số `--source`.

## Các lệnh

Chạy từ bất kỳ thư mục nào; script tự tính gốc gói từ vị trí của mình. Với đường dẫn tương đối, truyền từ gốc `research/`.

Tạo bảng tính (mặc định dùng `../output-standard`):

```bash
python3 -I spreadsheet/build-workbook.py
python3 -I spreadsheet/build-workbook.py analysis/output          # positional
python3 -I spreadsheet/build-workbook.py --source analysis/output # alias
```

Lệnh tạo chạy sẵn `check-workbook.py` trên bản nháp trước khi ghi bảng tính bàn giao. Tệp hiện tại đã được tạo lại theo cấu trúc gói nghiên cứu và kiểm tra bằng LibreOffice. Cùng đầu vào phải giữ số liệu và công thức tương đương; thời điểm lưu trong ZIP có thể làm SHA-256 khác nhau.

Kiểm tra giá trị lưu sẵn (ZIP/XML, quan hệ, kiểu, 49 mã, 829 phiếu, tám điểm nhóm, bảy tình huống, CFA, CR, AVE, HTMT, PLS, bootstrap, sàng lọc):

```bash
python3 -I spreadsheet/check-workbook.py spreadsheet/bang-diem-muc-do-quan-trong.xlsx
python3 -I spreadsheet/check-workbook.py <tệp khác> --source analysis/output
```

Kiểm tra bằng ứng dụng thật (mở bản có cache bị làm bẩn, sửa ô ở tám nhóm, tính lại, lưu, mở lại; kết quả bỏ ở `verification/` trong thư mục này):

```bash
python3 -I spreadsheet/check-libreoffice.py spreadsheet/bang-diem-muc-do-quan-trong.xlsx
python3 -I spreadsheet/check-libreoffice.py <tệp> --soffice libreoffice --evidence spreadsheet/verification
```

## Sử dụng bảng tính

- Trang `Bang diem`: nhập số nguyên 1 đến 5 ở các ô vàng `D2:D50`; cột E là kiểm tra tính hợp lệ. Giá trị ban đầu là phiếu số 1 của dữ liệu tổng hợp.
- Trang `Diem nhom`: đọc số câu hợp lệ ở C, điểm mức độ quan trọng ở D, trạng thái ở E; cột F là mốc R của phiếu số 1, cố định để đối chiếu. Điểm là mức độ quan trọng, không phải năng lực hiện có.
- Trang `Tinh huong`: bảy trường hợp nhập liệu, điểm ở J, trạng thái ở S; các cột kiểm tra K:R bị ẩn.
- Excel: Formulas > Calculation Options > Automatic, F9 để tính lại. LibreOffice Calc: Data > Calculate > AutoCalculate, Ctrl+Shift+F9 để tính lại toàn bộ. Hướng dẫn đầy đủ nằm trong trang đầu của XLSX.
- Không sửa các ô công thức hoặc cột mã, không chèn hoặc xóa hàng; làm việc trên một bản sao.
