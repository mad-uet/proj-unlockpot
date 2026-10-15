# Quy trình phân tích R của gói nghiên cứu

Phần phân tích của gói nghiên cứu `research/`. Toàn bộ mã lệnh, đầu vào và lệnh chạy nằm gọn trong thư mục này; không phụ thuộc thư mục `report/`, tài liệu ở cấp trên hoặc đường dẫn máy làm việc cụ thể. Chỉ cần thư mục `research/` là có thể chạy lại toàn bộ phân tích. Dữ liệu là dữ liệu tổng hợp do chính quy trình tạo ra, không phải dữ liệu gốc của bài nghiên cứu.

Tài sản thử của phiếu Beads "Chốt thiết kế demo R và bảng đánh giá năng lực". Người học đã đồng ý mở rộng để chạy sàng lọc sơ bộ, xoay oblimin, CFA, HTMT và PLS-SEM. Đây là prototype kiểm chứng thiết kế, chưa phải bộ sản phẩm nộp bài. Quyết định chính thức và phản hồi của người học nằm trong resolution comment của phiếu. Không thực hiện Git theo chỉ dẫn của map và phiên.

## Thiết kế được chọn

Giữ quy tắc trung bình không trọng số trong nhóm, chỉ tính khi đủ toàn bộ câu trả lời hợp lệ. Mở rộng quy trình R thành hai đầu vào sơ bộ và chính thức, chạy các phương pháp bằng cấu hình được công bố dưới đây. Không cố tái tạo số liệu bài báo.

Quy ước đã chốt ở phiếu "Chốt cách xử lý sai lệch thang đo và giới hạn diễn giải" vẫn áp dụng. Dùng 49 chỉ báo của Phụ lục F, giữ câu hỏi về mức độ quan trọng, gọi kết quả là điểm mức độ quan trọng theo nhóm năng lực. Không xếp loại năng lực thực có.

## Mở bản thử

Sau một lượt chạy, thư mục đầu ra mặc định là `output/` ngay trong thư mục này. Bộ đầu ra đã chạy hoàn chỉnh và được đối chiếu với mốc nằm ở `../output-standard`; mốc so sánh là `../baseline`. Bản sao `output/` của lượt chạy cũ không được giữ trong gói.

- Mở [bản tương tác HTML](output/demo-prototype.html) bằng trình duyệt. Tệp tự chứa dữ liệu và mã, không cần máy chủ hoặc mạng. Liên kết tải bảng tính và dữ liệu cần các tệp đi kèm trong thư mục output.
- Mở [bảng tính XLSX](output/bang-diem-prototype.xlsx). Trang Bang diem nhận câu trả lời ở D2:D50 và hiển thị tám điểm nhóm ở I2:I9. Trang Tinh huong có bảy trường hợp nhập liệu.
- Xem [trang kết quả mở rộng](output/ket-qua-mo-rong.html) để đọc các bảng CFA, CR, AVE, HTMT và hệ số PLS bằng tiếng Việt. Các bảng này cũng được đưa vào XLSX.
- Xem [kết quả theo nhóm](output/group-summary.csv), [chẩn đoán](output/diagnostics.csv) và [biểu đồ trị riêng PCA](output/pca-scree.svg).

Chạy lại từ thư mục `research/analysis` bằng một lệnh:

```bash
bash run.sh
```

Cài thư viện một lần bằng `Rscript setup.R` từ thư mục `research/analysis`. Cần R, Python 3 và bốn gói R psych, GPArotation, lavaan, plspm. setup.R tải từ CRAN vào thư mục `.library` ngay trong `research/analysis`, không sửa thư viện R hệ thống. Các phiên bản thực tế nằm trong package-versions.csv của thư mục đầu ra. Lần chạy phân tích sau đó không cần mạng. Python chỉ dùng thư viện chuẩn.

Có thể truyền thư mục đầu ra khác làm đối số thứ nhất. run.sh giới hạn các luồng BLAS trước khi R khởi động. prototype.R tạo dữ liệu và kết quả, gọi preliminary.R và extended.R, rồi gọi build-assets.py bằng python -I để tạo HTML và XLSX. Mỗi lượt đầy đủ có 1000 mẫu bootstrap và có thể mất vài phút. Không cần mở Excel để chạy phân tích. Có thể chạy prototype.R trực tiếp bằng Rscript, nhưng nên giới hạn OPENBLAS_NUM_THREADS, OMP_NUM_THREADS và MKL_NUM_THREADS bằng 1 trước khi khởi động R.

## Đầu vào và cách tạo dữ liệu

[indicators.csv](indicators.csv) chứa 49 mã theo Phụ lục F, Bảng A4 trang 23 và nhãn tiếng Việt rút gọn phục vụ bản thử. Đây không phải bản dịch thang đo đã được kiểm định. Script đối chiếu thứ tự và mã với [danh mục đã kiểm đếm](../notes/indicator-audit.csv). Số chỉ báo của tám nhóm lần lượt là 8, 7, 7, 4, 3, 9, 6, 5.

Seed là 20261104. Bộ sinh số ngẫu nhiên là Mersenne-Twister, Inversion, Rejection. Một lần tạo duy nhất, không chọn lại seed để khớp số của bài báo.

Với mỗi phiếu i, tạo biến chuẩn chung C và tám nhiễu chuẩn độc lập U. Nhân tố giả định của nhóm g là F_g = sqrt(0,30) C + sqrt(0,70) U_g. Vì thế tương quan nhân tố trong mô hình sinh dữ liệu là 0,30. Với chỉ báo j thuộc nhóm g, tạo Z_j = 0,75 F_g + sqrt(1 - 0,75^2) E_j, trong đó E là nhiễu chuẩn độc lập. Các ngưỡng -1,2; -0,4; 0,4; 1,2 chia Z thành năm giá trị Likert 1 đến 5. R dùng khoảng đóng bên phải của hàm cut.

Tám nhóm và mức liên hệ giữa các biến là giả định của demo. Việc thấy tám thành phần trong PCA không chứng minh cấu trúc tám nhóm của nghiên cứu gốc.

Tạo 829 phiếu tổng hợp hoàn chỉnh, không thêm ô thiếu vào mẫu phân tích. Sáu vai trò có số đếm 164, 132, 189, 149, 101, 94 theo Bảng 2 trang 9, rồi được gán ngẫu nhiên độc lập với điểm. Chỉ số đếm vai trò được lấy từ bài, câu trả lời từng phiếu do demo tạo. Không giả định tác động vai trò và không thêm loại dự án hoặc số năm hoạt động khi bản thử chưa dùng các biến đó.

Vai trò là biến danh nghĩa. role-design.csv có một hệ số chặn và năm biến giả với chủ đầu tư làm nhóm tham chiếu. Các cột role_2 đến role_6 lần lượt là giám sát, tổng thầu, thầu phụ, vật liệu, thiết bị. PLS dùng năm biến giả này làm năm khối một chỉ báo; không thêm cột hệ số chặn vào khối đo lường. Không dùng mã 1 đến 6 như thang thứ bậc. Các biến và điểm khối PLS được chuẩn hóa, nên hệ số không phải chênh lệch trung bình Likert thô.

## Quy tắc tính điểm

Trong từng nhóm, lấy tổng câu trả lời chia cho số chỉ báo của nhóm. Các chỉ báo trong nhóm có trọng số bằng nhau. Chỉ tính khi tất cả câu trả lời là số nguyên từ 1 đến 5. Một câu trống, chữ, 0, 6 hoặc 4,5 khiến nhóm chưa có điểm. Không điền bù, không đảo điểm. Không tính điểm tổng toàn thang và không đặt ngưỡng yếu, trung bình, tốt.

Quy tắc này do demo đề xuất. Bài báo không công bố quy tắc trung bình, trọng số hoặc xử lý thiếu. Trung bình Likert là phép mô tả dùng trong demo, không phải bằng chứng các khoảng giữa nhãn trả lời cách đều về tâm lý.

R và HTML có hàm tính riêng để người học xem hành vi. XLSX có cột E kiểm tra từng câu bằng ISNUMBER, INT và giới hạn 1 đến 5. Cột H đếm câu hợp lệ của nhóm. Cột I dùng IF và AVERAGE khi số hợp lệ bằng số chỉ báo. Cột J phân biệt chưa nhập với thiếu hoặc sai. Công thức trả chuỗi rỗng khi nhóm không đủ dữ liệu.

Bảy tình huống gồm đủ tám câu ở mức 4, thiếu một câu, trống cả nhóm, nhập 0, nhập 6, nhập 4,5 và nhập chữ. Chúng tách khỏi 829 phiếu phân tích. Trường hợp đủ câu có điểm 4, các trường hợp còn lại không có điểm.

## Phân tích thực sự đã chạy

| Bước | Đầu vào và tham số | Đầu ra |
| --- | --- | --- |
| Kiểm tra danh mục và miền giá trị | 49 mã duy nhất đúng thứ tự A4, 829 phiếu, số nguyên 1 đến 5 | Script dừng nếu điều kiện sai |
| Mô tả và điểm nhóm | Trung bình đủ câu, độ lệch chuẩn mẫu, trung vị | group-scores.csv và group-summary.csv |
| Alpha thô | k chia k trừ 1, nhân với 1 trừ tổng phương sai chỉ báo chia phương sai tổng điểm nhóm | group-summary.csv |
| CITC | Tương quan Pearson giữa chỉ báo và tổng các chỉ báo còn lại trong cùng nhóm | citc.csv, kèm alpha nếu bỏ chỉ báo |
| KMO | Ma trận Pearson của 49 chỉ báo và ma trận tương quan riêng phần | diagnostics.csv |
| Bartlett | Xấp xỉ chi bình phương với 1176 bậc tự do, lưu log xác suất đuôi trên | diagnostics.csv |
| PCA | prcomp, chuẩn hóa biến, Pearson, chưa xoay, xuất đủ 49 thành phần | pca-variance.csv, pca-vectors.csv, pca-loadings.csv, pca-scree.svg |

CITC ở đây minh họa phép tính trên danh mục cuối. Không tự loại thêm chỉ báo theo CITC tổng hợp. Phân tích Pearson trên Likert là xấp xỉ của demo, chưa so sánh độ nhạy với tương quan polychoric.

pca-vectors.csv là vector riêng. pca-loadings.csv là tương quan biến với thành phần, tính bằng vector riêng nhân căn trị riêng. Không gọi vector riêng là tải tương quan. Quy tắc trị riêng lớn hơn 1 được hiển thị để minh họa cách mô tả của bài, không phải bằng chứng duy nhất quyết định số nhân tố.

Bartlett dùng xấp xỉ phân phối cho dữ liệu và chỉ có vai trò minh họa ở đây. Lưu log p để tránh diễn giải số làm tròn hoặc tràn dưới thành xác suất thật sự bằng 0. Chỉ số alpha cao không chứng minh đơn hướng hoặc giá trị đo lường.

## Quy trình mở rộng

### Sàng lọc sơ bộ riêng

preliminary.R tạo 438 phiếu tổng hợp với seed 20261105, theo 52 mã ở Bảng 1 trang 6-7. Danh mục này khác bộ 52 mã ở A2. Không thêm Cap-Bus_9 đến Cap-Bus_11. Cách sinh giữ tương quan nhân tố 0,30, tải 0,75 và cùng ngưỡng Likert với tập chính thức. Hai tập độc lập theo thiết kế mô phỏng, không suy ra rằng hai mẫu khảo sát thật độc lập.

Tính CITC, alpha và alpha nếu bỏ chỉ báo. Quy tắc thử tạo cờ xem xét khi CITC nhỏ hơn 0,50 và alpha khi bỏ cao hơn alpha trước hơn 0,000001. Đây là quy tắc vận hành của demo, không gán cho tác giả. Không lặp loại chỉ báo theo kết quả mô phỏng. Riêng ba mã tác giả loại được đối chiếu và tính độ nhạy trước/sau loại theo danh sách công bố. Phép tính theo danh sách không phải quyết định loại từ mẫu tổng hợp. Đầu vào phân tích chính thức luôn giữ 49 mã A4 đã chốt.

### PCA và direct oblimin

Chạy psych::principal riêng cho tập sơ bộ và tập cuối. Dùng tương quan Pearson, số thành phần theo trị riêng lớn hơn 1, xoay direct oblimin với gamma bằng 0 qua GPArotation. Đây là một phép minh họa tiêu chí tác giả mô tả, không phải đầy đủ cấu hình gốc. Xuất riêng pattern, structure và Phi. Pattern là tải trong phương trình tái tạo biến; structure là tương quan biến với thành phần. Chúng khác nhau khi các thành phần tương quan. Không cộng phần phương sai từng thành phần xoay như thể các thành phần độc lập.

### CFA, CR và AVE

Mô hình được định trước gồm tám nhân tố tương quan, 49 chỉ báo thứ bậc, mỗi chỉ báo tải lên một nhân tố. Dùng lavaan::cfa với WLSMV, parameterization delta, std.lv TRUE. Không thêm tải chéo, tương quan phần dư hoặc sửa mô hình sau khi xem chỉ số phù hợp. Kiểm tra hội tụ và tính chấp nhận của nghiệm. cfa-model.lav và cfa-name-map.csv lưu mô hình cùng ánh xạ mã chỉ báo. cfa-fit.rds giữ đối tượng đã ước lượng để kiểm tra tiếp mà không cần chạy lại.

cfa-fit-measures.csv xuất đầy đủ chỉ số. Trang HTML dùng các chỉ số scaled cho chi bình phương, CFI, TLI và RMSEA; ghi rõ tên hiệu chỉnh. CR bằng bình phương tổng tải chuẩn hóa chia cho bình phương tổng tải cộng tổng phương sai phần dư chuẩn hóa. AVE bằng tổng bình phương tải chia cho tổng bình phương tải cộng tổng phương sai phần dư. Với CFA ordinal, các phép này áp dụng trên biến đáp ứng tiềm ẩn, không đồng nhất với độ tin cậy của trung bình điểm Likert quan sát.

### HTMT

Tính HTMT theo trung bình tương quan Pearson tuyệt đối giữa các chỉ báo khác nhóm, chia cho căn tích hai trung bình tương quan tuyệt đối trong nhóm. Xuất 28 cặp và ma trận tám nhóm. Đây là phép mô tả riêng trên điểm Likert, không sử dụng tương quan nhân tố từ CFA hoặc coi là kiểm định chung với WLSMV. Chỉ xuất ước lượng điểm, chưa bootstrap HTMT. Mốc 0,85 minh họa tiêu chí trong bài, không chứng minh giá trị đo lường ngoài dữ liệu tổng hợp.

### PLS-PM và bootstrap

Dùng plspm cho PLS truyền thống với Mode A, path weighting, scaled TRUE, ngưỡng hội tụ 1e-7, tối đa 300 vòng. Năm khối một chỉ báo cho biến giả vai trò liên hệ với tám khối chỉ báo của tám nhóm. Không thêm đường dẫn giữa các nhóm năng lực, loại dự án hoặc số năm hoạt động. Đây là mô hình minh họa riêng, không phải toàn bộ Hình 3 hoặc cấu hình gốc của tác giả.

Bootstrap 1000 mẫu theo phiếu, seed 20261106. Tạo trước danh sách mẫu bằng một luồng ngẫu nhiên, sau đó phân tích bằng tối đa hai tiến trình và một luồng BLAS mỗi tiến trình. Ước lượng lại trọng số và đường dẫn trong mỗi mẫu. Mỗi mẫu chỉ được thử một lần, không thay bằng mẫu mới khi không hội tụ. Ghi trạng thái từng mẫu và tổng số thành công/thất bại. Các khoảng dùng mẫu hội tụ và công khai số lượng thực tế. Xuất hệ số gốc, trung bình bootstrap, sai số chuẩn và phân vị 2,5%/97,5%. Các khoảng chưa được hiệu chỉnh cho so sánh nhiều đường dẫn. Nếu khoảng chứa 0 thì chưa có căn cứ từ khoảng đó để nói hệ số khác 0. Không suy ra quan hệ nhân quả.

PLS Mode A tạo điểm khối tổng hợp; không phải PLSc và không dùng cùng mô hình ước lượng với CFA ordinal. Vai trò được gán ngẫu nhiên độc lập với câu trả lời nên không kỳ vọng tái hiện các tác động hoặc R bình phương cao trong bài. Xuất mô hình, khối đo, tải, hệ số, R bình phương, kết quả bootstrap và đối tượng pls-fit.rds để kiểm tra tiếp.

### Phần chưa chạy và giới hạn

EFA khám phá theo mô hình nhân tố chung chưa chạy. PCA phân rã phương sai tổng; mô hình nhân tố chung tách phương sai chung với phần riêng. CFA đã chạy là phân tích khẳng định theo mô hình định trước. Chưa bootstrap HTMT, chưa kiểm tra độ nhạy PCA với tương quan polychoric, chưa thêm loại dự án và số năm hoạt động vào PLS. Các giới hạn này không được che bằng số từ bài báo.

## Kết quả quan sát và kiểm tra

Lần chạy bằng R 4.6.1 cho KMO 0,9298628. PCA có tám trị riêng lớn hơn 1; tám thành phần đầu giải thích 59,77194% phương sai. Đây là kết quả tổng hợp, không phải 68,592% tác giả công bố ở trang 10. Alpha thô theo nhóm nằm trong khoảng 0,7368345 đến 0,9063936. Trung bình nhóm trên mẫu nằm trong khoảng 2,950026 đến 3,002815, phù hợp với cách sinh đối xứng quanh mức 3 đã chọn. Không hiệu chỉnh dữ liệu để các số giống bài báo.

Ở bản tối thiểu, đã chạy lại vào một thư mục tạm độc lập và dùng cmp xác nhận synthetic-829.csv, group-summary.csv và pca-variance.csv giống từng byte giữa hai lần chạy trong cùng môi trường. Bản mở rộng sau đó đã chạy đầy đủ từ thư mục đầu ra rỗng. Các chỉ số CFA và HTMT khớp giữa lượt thử riêng và lượt toàn quy trình. [sessionInfo.txt](output/sessionInfo.txt) ghi phiên bản và môi trường R. Không cam kết kết quả số thực giống từng byte giữa mọi phiên bản R hoặc thư viện đại số tuyến tính.

Kết quả sơ bộ có 0 cờ xem xét theo quy tắc thử. CITC của ba mã tác giả loại là 0,6892455; 0,6977111; 0,6973425 trong dữ liệu tổng hợp, khác các giá trị tác giả công bố. Khi bỏ LI_1 và LI_4 theo danh sách, alpha nhóm học hỏi và đổi mới giảm từ 0,8780259 xuống 0,8204106. Bỏ Mkg_3 làm alpha nhóm tiếp thị giảm từ 0,8488364 xuống 0,8037816. Giữ nguyên kết quả này, không làm yếu các mã khi sinh dữ liệu để ép quyết định loại. PCA sơ bộ giữ tám thành phần, giải thích 60,64131% phương sai.

CFA hội tụ và nghiệm hợp lệ. CFI scaled là 0,9991179 và RMSEA scaled là 0,004803079. HTMT của 28 cặp nằm từ 0,2100276 đến 0,3922849. PLS có R bình phương từ 0,003226749 đến 0,008029863, phù hợp với việc gán vai trò độc lập với điểm. Cả 1000 mẫu bootstrap đã hội tụ, 0 mẫu thất bại, không thay mẫu. [verification.txt](output/verification.txt) xác nhận Python đã tính lại độc lập trung bình bootstrap, sai số chuẩn mẫu và các phân vị cho đủ 40 đường dẫn từ các hệ số từng mẫu. Không có cảnh báo trong extended-warnings.txt của lượt hoàn tất.

Bộ tạo XLSX đã kiểm tra cấu trúc XML và checksum của ZIP. Tám điểm nhóm lưu sẵn và bảy tình huống đã đối chiếu với R. Chưa chạy máy tính công thức Excel hoặc LibreOffice. Vì thế giá trị lưu sẵn khớp R không tự chứng minh ứng dụng bảng tính tính lại đúng sau khi sửa ô.

Đã mở HTML bằng Chrome. Đã kiểm tra xóa một câu, xóa cả nhóm, nhập 6, nhập 4,5, nhập chữ và khôi phục mức 4. Các trường hợp sai hoặc thiếu đều làm nhóm chưa có điểm; khôi phục đủ câu cho điểm 4. Đã nạp phiếu tổng hợp đầu tiên, chuyển sang nhóm tiếp thị và kiểm tra thứ tự nút trong tình huống có hướng dẫn. Các thao tác chạy cục bộ và không lưu dữ liệu.

## Nguồn

- Zheng, Su và Liu, 2024, Systems 12, 497. Bảng 2 trang 9, mô tả phương pháp trang 9-12, nhãn Likert trang 8 và phụ lục trang 17, 19, Bảng A4 trang 23.
- [Hồ sơ kiểm chứng](../notes/evidence.md), đặc biệt mục dữ liệu có sẵn và giới hạn demo.
- Trợ giúp các hàm R gồm prcomp, cor, var, model.matrix, cut, RNGkind, psych::principal, GPArotation::oblimin, lavaan::cfa và plspm::plspm. Phiên bản thực thi nằm trong sessionInfo.txt và package-versions.csv.
- Tài liệu phần mềm chính thức: [psych trên CRAN](https://cran.r-project.org/package=psych), [GPArotation trên CRAN](https://cran.r-project.org/package=GPArotation), [hướng dẫn CFA ordinal của lavaan](https://lavaan.ugent.be/tutorial/cat.html), [plspm trên CRAN](https://cran.r-project.org/package=plspm). Công thức và hành vi thực thi có thể đối chiếu với trợ giúp của các phiên bản đã cài.
