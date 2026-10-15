# Nghiên cứu

Đây là gói nghiên cứu độc lập của dự án: gồm quy trình phân tích R, đầu ra đã chạy hoàn chỉnh, bảng đối chiếu mốc và ghi chú phân tích.

## Trích dẫn bài nghiên cứu

Bài gốc: Zheng, Z., Su, Y., và Liu, J. 2024. "Unlocking the Potential of Construction Governance: Developing Participants' Capability Scale". *Systems*, 12, 497. DOI [https://doi.org/10.3390/systems12110497](https://doi.org/10.3390/systems12110497).

Gói nghiên cứu không kèm tệp PDF của bài. Toàn bộ ghi chú dẫn nguồn bằng DOI và số trang in của bài, tra cứu lại qua DOI.

## Dữ liệu là dữ liệu tổng hợp, không phải dữ liệu gốc

Mọi số liệu trong gói được sinh tổng hợp bằng mã R trong `analysis/`, theo danh mục chỉ báo công bố của bài và tham số giả định được ghi rõ (tương quan nhân tố 0,30, tải 0,75, ngưỡng chia khoảng Likert, seed cố định). Đây không phải dữ liệu khảo sát gốc của bài nghiên cứu và không thể dùng để tái lập số của bài. Bài không công bố dữ liệu từng phiếu; dữ liệu gốc chỉ có thể xin qua tác giả liên hệ theo Data Availability Statement ở trang 15 của bài. Các kết quả số trong gói là minh họa quy trình, không phải bằng chứng thực nghiệm bổ sung cho bài.

## Cấu trúc thư mục

| Thư mục hoặc tệp | Nội dung |
| --- | --- |
| `analysis/` | Mã R và Python của quy trình, `indicators.csv`, `run.sh`, `setup.R`, README riêng của phần phân tích |
| `output-standard/` | Bộ đầu ra đã chạy hoàn chỉnh và được đối chiếu với mốc; đây là nguồn đầu vào mặc định của bảng tính và bộ tạo tài sản báo cáo |
| `baseline/` | Mười bảng mốc dùng để đối chiếu kết quả mỗi lượt chạy (bảng so sánh cố định, không phải toàn bộ đầu ra) |
| `notes/` | Ghi chú phân tích: `evidence.md` (hồ sơ kiểm chứng nguồn) và `indicator-audit.csv` (danh mục mã chỉ báo đã đếm) |
| `spreadsheet/` | Bộ tạo bảng tính XLSX |
| `.gitignore` | Bỏ qua thư viện R cục bộ, thư mục đầu ra mới và bộ đệm |

## Chạy lại phân tích

Cần R và Python 3. Các lệnh dưới đây chạy từ gốc gói nghiên cứu, nơi có README này. Cài các gói CRAN psych, GPArotation, lavaan, plspm và phụ thuộc một lần qua mạng.

```bash
Rscript analysis/setup.R
```

Thư viện được cài vào `analysis/.library`, không sửa thư viện R hệ thống. Các lượt chạy sau không cần mạng.

Chạy toàn bộ quy trình, tạo dữ liệu tổng hợp, CFA, HTMT, PLS bootstrap và tài sản HTML/XLSX:

```bash
bash analysis/run.sh
```

Lượt trên ghi vào `analysis/output/`, thư mục mặc định. Muốn ghi vào thư mục đầu ra mới, truyền tên thư mục:

```bash
bash analysis/run.sh output-rerun
```

Mỗi lượt đầy đủ có 1000 mẫu bootstrap và có thể mất vài phút. `run.sh` giới hạn các luồng BLAS trước khi R khởi động. Không cần mở Excel hoặc LibreOffice để chạy phân tích. Chi tiết tham số, giới hạn diễn giải và kết quả quan sát nằm trong [analysis/README.md](analysis/README.md).

## Tạo bảng tính từ đầu ra chuẩn

```bash
python3 -I spreadsheet/build-workbook.py --source output-standard
```

Cờ `--source` nhận thư mục đầu ra cần dùng; mặc định là `output-standard/`. Tệp XLSX tạo ra ở `spreadsheet/bang-diem-muc-do-quan-trong.xlsx`. Lệnh dùng `python3 -I` và các thư viện chuẩn.

## Đối chiếu với mốc

Mười bảng trong `baseline/` là mốc cố định của lượt chạy đã duyệt: `diagnostics.csv`, `preliminary-diagnostics.csv`, `preliminary-screening.csv`, `preliminary-authored-removals.csv`, `group-summary.csv`, `cfa-fit-measures.csv`, `cfa-cr-ave.csv`, `htmt-pairs.csv`, `pls-inner-summary.csv`, `pls-bootstrap-paths.csv`. So sánh kết quả theo khóa quan sát với sai số tương đối 1e-8 và tuyệt đối 1e-10, không so sánh dấu thời gian hoặc tệp RDS. `output-standard/verification.txt` ghi kiểm tra đầu ra và phép tính độc lập cho lượt bàn giao.

## Kho nghiên cứu

Địa chỉ kho nghiên cứu: [https://github.com/mad-uet/proj-unlockpot](https://github.com/mad-uet/proj-unlockpot).

## Giới hạn cần giữ

- Không tái tạo số liệu gốc của bài và không đặt lại seed để khớp số của bài.
- Điểm nhóm là trung bình các câu trả lời hợp lệ trong nhóm; là phép mô tả của gói, không phải quy tắc do tác giả công bố.
- Các chỉ số phù hợp, HTMT và hệ số PLS tính trên dữ liệu tổng hợp; không suy ra kết luận thực nghiệm cho tổ chức thật.
- Danh mục 49 chỉ báo là danh mục Phụ lục F, Bảng A4 trang 23 của bài, đối chiếu với `notes/indicator-audit.csv` mỗi lượt chạy.
