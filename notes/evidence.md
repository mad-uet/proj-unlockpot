# Căn cứ kiểm chứng bài báo về năng lực quản trị xây dựng

Tài sản chứng cứ của phiếu Beads "Kiểm chứng bài báo và lập căn cứ cho nội dung báo cáo". Đây là ghi chép đối chiếu nguồn, chưa phải báo cáo giữa kỳ hoặc bản thiết kế demo. Lời giải và các quyết định của map được lưu trong Beads.

Ghi chú này là ghi chú phân tích do người viết báo cáo biên soạn, nằm trong gói nghiên cứu `research/notes/`. Nó tổng hợp kết quả đối chiếu nguồn công bố của bài chính, các nguồn học thuật đối chiếu và sách môn học; không chứa bản chép nguyên văn toàn văn của bất kỳ nguồn nào và không kèm tệp PDF của bài hoặc sách. Mọi phát biểu về nguồn dẫn đến DOI hoặc số trang in của nguồn đó. Tệp [indicator-audit.csv](indicator-audit.csv) cùng thư mục là danh mục mã chỉ báo đã đếm và là đầu vào đối chiếu của quy trình phân tích ở `../analysis`.

## Nguồn và cách kiểm tra

- Nguồn chính là bài báo Zheng, Z., Su, Y., và Liu, J. 2024. "Unlocking the Potential of Construction Governance: Developing Participants' Capability Scale". *Systems*, 12, 497, DOI [10.3390/systems12110497](https://doi.org/10.3390/systems12110497). Gói nghiên cứu không kèm tệp PDF của bài; tra từng phát biểu qua DOI của bài và số trang in đã ghi. Số trang trùng số trang in của bài. Không giả định đã kiểm tra đính chính trên trang nhà xuất bản.
- Thư mục gốc chính xác là Zheng, Z., Su, Y., và Liu, J. 2024. "Unlocking the Potential of Construction Governance: Developing Participants' Capability Scale". *Systems*, 12, 497. DOI [10.3390/systems12110497](https://doi.org/10.3390/systems12110497). Trang 1 ghi ngày công bố 18/11/2024.
- Bản dịch đề xuất là "Khai mở tiềm năng quản trị xây dựng: Phát triển thang đo năng lực của các bên tham gia". Có thể giải thích trong phần mở đầu rằng đối tượng đo cụ thể là năng lực quản trị ở cấp tổ chức. Không đổi "governance" thành "quản lý" trong tên bài.
- Bản trích văn bản PDF (tệp `article-extracted.txt` ở thư mục làm việc gốc, không kèm trong gói nghiên cứu) giữ ngắt trang. PDF có một số lớp chữ chồng ở trang 6, 8 và 12; script đếm mã duy nhất để tránh đếm lặp do lớp chữ. Hình 1, 2 và 3 là ảnh, không có đầy đủ nhãn trong bản trích chữ. Chưa dùng bản trích này để khẳng định từng nhãn hoặc từng hệ số bên trong hình.
- Script kiểm tra (`audit-paper.py` ở thư mục làm việc gốc, không kèm trong gói nghiên cứu) gọi `pdftotext` trực tiếp theo trang; chạy lại từ thư mục gốc của dự án làm việc. [Danh mục mã đã đếm](indicator-audit.csv) nằm cùng thư mục trong gói và cho phép kiểm tra từng mã. Các bản trích phụ lục có sai lệch và các bản trích nguồn khác chỉ kiểm tra danh mục công bố, không phân tích dữ liệu khảo sát.

## Khung khái niệm và đối tượng khảo sát

| Phát biểu có thể dùng | Nguồn | Giới hạn diễn giải |
| --- | --- | --- |
| Bài xây dựng một thang đo năng lực quản trị của bên tham gia dự án xây dựng. | Trang 1-3, mục 1-2. | Không phải mô hình dự báo thành công dự án đã được kiểm định bằng biến kết quả dự án. |
| Năng lực quản trị là khả năng đạt mục tiêu trong quá trình xây dựng thông qua xây dựng và thực hiện chính sách, quy tắc và quyết định. | Trang 2-3, mở đầu mục 2. | Đối tượng là tổ chức. Người quản lý là người trả lời khảo sát. Không đồng nhất năng lực tổ chức với kỹ năng cá nhân. |
| Khung khái niệm tích hợp lý thuyết đại diện, lý thuyết phụ thuộc nguồn lực, kinh tế học chi phí giao dịch và lý thuyết các bên liên quan. | Trang 3-6, mục 2.3-2.4, Bảng 1. | Các lý thuyết là cơ sở xây dựng khái niệm, không phải bốn biến đo trực tiếp bằng đường dẫn thực nghiệm. |
| Lý thuyết đại diện gắn với giám sát và bất cân xứng thông tin; phụ thuộc nguồn lực gắn với liên minh và phối hợp nguồn lực; chi phí giao dịch gắn với giảm chi phí giao dịch; các bên liên quan gắn với cân bằng lợi ích và hợp tác. | Trang 4-5, mục 2.3. | Đây là cách bài chính vận dụng lý thuyết. Phần trình bày lý thuyết nguyên gốc có thể cần thêm nguồn chuyên khảo nếu mở rộng. |
| Có tám nhóm năng lực gồm kinh doanh, tài chính, nguồn nhân lực, học hỏi và đổi mới, tiếp thị, quản lý tổ chức, quản lý dự án, mua sắm. | Trang 1; Bảng 1 trang 6-7; Bảng A4 trang 23. | Không đồng nhất tám nhóm với tám miền hiệu quả thực hiện của PMBOK 7. |
| Khảo sát bao gồm chủ đầu tư hoặc đơn vị phát triển dự án, đơn vị giám sát, tổng thầu, nhà thầu phụ, nhà cung cấp vật liệu, nhà cung cấp thiết bị. | Bảng 2 trang 9; câu 1 Phụ lục B trang 17 và C trang 19. | Đoạn mô tả trang 8 liệt kê khái quát ít nhóm hơn; dùng Bảng 2 và bảng hỏi để nêu đủ sáu nhóm. Developers không tự động có nghĩa là cơ quan nhà nước. Trang 7 giải thích lựa chọn thuật ngữ. |
| Doanh nghiệp và người trả lời phải thỏa các điều kiện tuyển chọn được bài nêu. | Trang 8. | Doanh nghiệp đã làm dự án quy mô lớn, có hoạt động công trình dân dụng và công cộng; người trả lời giữ vị trí quản lý và có hơn 10 năm kinh nghiệm xây dựng. Không coi mẫu này đại diện cho mọi lao động hoặc mọi doanh nghiệp xây dựng. |

Ánh xạ khái niệm theo văn bản mục 2.4 trang 5-6: đại diện gắn với tài chính, nguồn nhân lực, quản lý tổ chức và quản lý dự án; các bên liên quan gắn với tài chính, quản lý tổ chức và tiếp thị; phụ thuộc nguồn lực gắn với kinh doanh, mua sắm, nguồn nhân lực, học hỏi và đổi mới; chi phí giao dịch gắn với tiếp thị, tài chính, kinh doanh và mua sắm. Bảng 1 có thể ghi thêm nguồn lý thuyết cho từng chỉ báo. Không biến ánh xạ này thành quan hệ nhân quả đã được kiểm định.

## Mẫu và ý nghĩa thang trả lời

Bài ghi 600 phiếu phát ra và 438 phiếu hợp lệ ở khảo sát sơ bộ, tỷ lệ 73%; 1.200 phiếu phát ra và 829 phiếu hợp lệ ở khảo sát chính thức, tỷ lệ 69,08%. Nguồn là trang 9, đoạn ngay sau Bảng 2. Các con số đếm theo nhóm cộng đúng về 438 và 829. Không cộng hai mẫu thành một mẫu độc lập, vì Phụ lục C trang 19 có nhắc khả năng người trả lời đã điền bảng hỏi trước đó.

| Vai trò tổ chức | Sơ bộ | Chính thức |
| --- | ---: | ---: |
| Chủ đầu tư hoặc đơn vị phát triển dự án | 19 | 164 |
| Đơn vị giám sát | 38 | 132 |
| Tổng thầu | 103 | 189 |
| Nhà thầu phụ | 133 | 149 |
| Nhà cung cấp vật liệu | 71 | 101 |
| Nhà cung cấp thiết bị | 74 | 94 |
| Tổng | 438 | 829 |

Nguồn của toàn bộ bảng là Bảng 2 trang 9. Tỷ lệ phần trăm ở một số dòng sơ bộ không khớp hoàn toàn với phép chia theo 438, nên ưu tiên số đếm và ghi rõ nếu tự tính lại tỷ lệ.

Trang 8 định nghĩa Likert 1 là cực kỳ không quan trọng, 2 là không quan trọng, 3 là trung lập, 4 là quan trọng, 5 là cực kỳ quan trọng. Phụ lục B trang 17 và C trang 19 dùng chữ "general" cho mức 3. Khác biệt cách gọi mức 3 phải được ghi nhận khi dịch. Cả hai cách diễn đạt đều hỏi về tầm quan trọng, không hỏi mức thành thạo hoặc mức năng lực thực có. Bài đồng thời diễn giải thang như công cụ đo năng lực ở trang 13-15. Khoảng cách giữa nhãn trả lời và kết luận đo lường là điểm cần thảo luận, không được tự bỏ qua.

## Mâu thuẫn về số chỉ báo

| Nhóm | Bảng 1, trang 6-7 | Phụ lục F, Bảng A4, trang 23 | Phụ lục D, Bảng A2, trang 21-22 |
| --- | ---: | ---: | ---: |
| Kinh doanh, Cap-Bus | 8 | 8 | 11 |
| Tài chính, Cap-Fin | 7 | 7 | 7 |
| Nguồn nhân lực, Cap-HR | 7 | 7 | 7 |
| Học hỏi và đổi mới, Cap-LI | 6 | 4 | 4 |
| Tiếp thị, Cap-Mkg | 4 | 3 | 3 |
| Quản lý tổ chức, Cap-OM | 9 | 9 | 9 |
| Quản lý dự án, Cap-PM | 6 | 6 | 6 |
| Mua sắm, Cap-Proc | 5 | 5 | 5 |
| Tổng mã duy nhất | 52 | 49 | 52 |

Tóm tắt của tác giả ở trang 1 tuyên bố tám nhóm với 47 chỉ báo. Danh mục có nội dung ở Bảng A4 lại gồm 49 mã. Bảng A2 có thêm Cap-Bus_9, Cap-Bus_10, Cap-Bus_11 mà Bảng 1, bảng hỏi chính thức và Bảng A4 không cung cấp nội dung. Không có căn cứ để tự đặt tên ba chỉ báo này, tự loại hai chỉ báo từ Bảng A4, hoặc coi độ tin cậy của bộ kinh doanh 11 mã là kết quả kiểm định bộ 8 mã.

Ba mã bỏ từ Bảng 1 sang Bảng A4 đúng là Cap-LI_1, Cap-LI_4 và Cap-Mkg_3. Vì vậy quan hệ đếm được trong PDF là 52 trừ 3 bằng 49. Sai lệch không thể giải thích chỉ bằng việc bỏ ba chỉ báo được văn bản mô tả. Phụ lục C trang 20 có các nội dung tương ứng danh mục cuối, nhưng không gắn mã ở từng dòng.

## Phương pháp và kết quả có thể trích

| Bước | Điều bài chính thực sự công bố | Vị trí nguồn |
| --- | --- | --- |
| Sàng lọc chỉ báo | CITC của Cap-LI_1, Cap-LI_4, Cap-Mkg_3 lần lượt là 0,487; 0,498; 0,491. Tác giả nói alpha của nhóm không thay đổi khi loại, nên đề xuất bỏ ba chỉ báo. | Mục 4.1, trang 10. |
| Phân tích khám phá | Bài gọi là EFA, đồng thời mô tả phép trích thành phần chính PCA với xoay direct oblimin, giữ trị riêng lớn hơn 1. | Mục 3 trang 9 và mục 4.1 trang 10. |
| Kết quả khám phá | KMO 0,965; mức ý nghĩa Bartlett in là 0,00; tám thành phần giải thích 68,592% phương sai; tải được mô tả lớn hơn 0,6. | Trang 10. Không có bảng đầy đủ tải sơ bộ để tính lại từng chỉ báo. |
| Alpha sơ bộ | Theo thứ tự Bus, Fin, HR, LI, Mkg, OM, PM, Proc là 0,931; 0,901; 0,916; 0,849; 0,802; 0,935; 0,893; 0,883. | Trang 10. |
| CFA chính thức | Alpha toàn bảng hỏi 0,973; tải chuẩn hóa từ 0,758 đến 0,829, p nhỏ hơn 0,001; alpha nhóm 0,814-0,949; CR 0,810-0,949; AVE trên 0,5. | Mục 4.2 trang 11; Bảng A2 trang 21-22. Đọc cùng sai lệch mã ở Bảng A2. |
| Giá trị phân biệt | Các ô ngoài đường chéo của HTMT từ 0,540 đến 0,666, thấp hơn ngưỡng 0,85 tác giả chọn. | Bảng 4 trang 11. Đây không phải bảng tương quan có dấu của khảo sát sơ bộ. |
| Mức phù hợp CFA | Dòng Total ghi chi bình phương chia bậc tự do 1,439; RMSEA 0,023; GFI 0,925; CFI 0,982; AGFI 0,917; NFI 0,943. | Bảng 6 trang 12. Không dùng các chỉ số này làm chỉ số phù hợp chung của PLS-SEM. |
| Mô hình đường dẫn | Ba đặc điểm gồm vai trò tổ chức, loại dự án và số năm hoạt động được xét với các nhóm năng lực. Văn bản công bố R bình phương từ 0,282 đến 0,434. Có dùng thuật toán PLS và bootstrap. | Trang 11, Hình 3 trang 12, Bảng A3 trang 22. |
| Vai trò tổ chức | Tám dòng Attributes ở A3 có thống kê t từ 25,186 đến 40,201 và p in là 0. | Bảng A3 trang 22. Không viết p thật sự bằng 0 và không suy ra chiều tác động từ t tuyệt đối. |
| Quy mô ảnh hưởng | Bảng 5 in f bình phương của Attributes từ 0,389 đến 0,763. | Trang 11. Bảng chỉ có bảy cột năng lực, thiếu Cap-Proc. |

Các giá trị p in 0,00 hoặc 0 là số hiển thị làm tròn. Khi trích, ghi rõ tác giả in như vậy; không mô tả xác suất đúng bằng 0. Chỉ chuyển sang bất đẳng thức khi biết độ chính xác hiển thị hoặc có mức ý nghĩa tác giả nêu.

PCA và EFA theo mô hình nhân tố chung khác nhau về toán học. Nguồn đối chiếu là Schreiber, "Issues and recommendations for exploratory factor analysis and principal component analysis", DOI [10.1016/j.sapharm.2020.07.027](https://doi.org/10.1016/j.sapharm.2020.07.027). Phần Introduction (trang bản thảo 3) và phần Abstract (trang bản thảo 2) nêu khuyến nghị với thang Likert. Khi mô tả bài chính, dùng câu "tác giả gọi là EFA và thực hiện trích PCA, xoay direct oblimin". Nếu demo dùng mô hình nhân tố chung hoặc ước lượng phù hợp dữ liệu thứ bậc, ghi đó là lựa chọn bổ sung, không nhận là tham số gốc.

HTMT là tỷ số tương quan giữa chỉ báo của các cấu trúc khác nhau so với tương quan trong cấu trúc, dùng đánh giá giá trị phân biệt. Nguồn đối chiếu là Henseler, Ringle và Sarstedt, "A new criterion for assessing discriminant validity in variance-based structural equation modeling", DOI [10.1007/s11747-014-0403-8](https://doi.org/10.1007/s11747-014-0403-8), trang in 121, công thức 6 và đoạn về ngưỡng 0,85 hoặc 0,90; trang in 122, chú thích 7 nói cần xét trị tuyệt đối. Nguồn này xác nhận không nên dùng các ô dương của HTMT để phủ nhận tương quan âm ở một phân tích khác. Bản PDF của nguồn này ghi số tập 2015 dù công bố online năm 2014; không sao chép năm tài liệu tham khảo của bài chính mà bỏ qua khác biệt này.

## Những mâu thuẫn và giới hạn cần giữ khi viết

- Bảng 3 trang 10 thuộc khảo sát sơ bộ. Bảy tương quan của Cap-OM với Bus, Fin, HR, PM, Proc, LI và Mkg lần lượt là -0,462; -0,429; -0,415; -0,413; -0,334; -0,400; -0,345. Trang 14 giải thích kết quả bằng trọng tâm quản trị nội bộ. Ghi đây là diễn giải của tác giả. Bảng tương quan không chứng minh rằng tăng quản lý tổ chức làm suy giảm bảy năng lực còn lại. Không tự đảo điểm Cap-OM chỉ để khớp dấu tương quan.
- Trang 11 nói số năm hoạt động và loại dự án không có quan hệ có ý nghĩa thống kê với năng lực. Bảng A3 trang 22 lại ghi Years of operation tới Cap-HR có t bằng 2,784 và p bằng 0,006. Dòng này có ý nghĩa ở mức 0,05 khi xét riêng phép kiểm định. Bài không nêu điều chỉnh đa kiểm định cho nhóm đường dẫn này. Không chép nguyên khẳng định tất cả các đường dẫn số năm đều không có ý nghĩa.
- Bảng A3 có độ lệch chuẩn, thống kê t tuyệt đối và p; không có cột ước lượng hệ số đường dẫn gốc. Không gọi độ lệch chuẩn là beta hoặc suy ra dấu của beta từ t. Hình 3 cần được xem trực tiếp nếu muốn dẫn một hệ số cụ thể trong hình.
- Bảng 6 trang 12 ghi CFI của Cap-PM bằng 1,001 và chi bình phương chia bậc tự do bằng 0,612. Cả hai không nằm trong khoảng ngưỡng tác giả in ở đầu cột. Đây là bất nhất cần ghi nguyên, chưa đủ căn cứ kết luận riêng nguyên nhân hoặc toàn mô hình không hợp lệ.
- Bài không mô tả đủ cách mã hóa sáu vai trò tổ chức và các loại dự án trong PLS-SEM. Vai trò tổ chức là biến phân loại, không có căn cứ coi mã 1-6 là mức thứ bậc tăng dần. Phiếu demo cần chốt mã hóa, nhóm tham chiếu hoặc cách phân tích nhóm phù hợp. Không diễn giải một beta đơn như chênh lệch đã biết giữa từng cặp vai trò.
- Trang 2 và 13 phân biệt ordinary capability với năng lực động ở cấp chiến lược, trong khi trang 3 có câu gọi governance capability là dynamic capability. Trình bày định nghĩa ở cấp tổ chức và nêu khác biệt thuật ngữ khi cần, không coi bài có quan điểm hoàn toàn nhất quán ở điểm này.
- Trang 13 tuyên bố áp dụng rộng cho các dự án, nhưng trang 15 thừa nhận cần kiểm tra thêm trong bối cảnh toàn cầu. Đây là giới hạn khái quát hóa do tác giả nêu. Không gọi thang đo là đã được kiểm định cho mọi quốc gia, mọi tổ chức hoặc cho Việt Nam.

## Dữ liệu có sẵn, còn thiếu và hệ quả với demo

Có sẵn danh mục và nội dung chỉ báo, nhãn Likert, bảng đặc điểm mẫu, ma trận tương quan cấp cấu trúc ở khảo sát sơ bộ, bảng HTMT, các số tóm tắt độ tin cậy và tải, bảng chỉ số phù hợp, thống kê kiểm định đường dẫn. Không có câu trả lời từng phiếu, ma trận hiệp phương sai hoặc tương quan đầy đủ giữa các chỉ báo, mã phân tích và cấu hình phần mềm đủ để chạy lại toàn bộ.

Data Availability Statement ở trang 15 ghi dữ liệu tạo hoặc phân tích trong nghiên cứu được cung cấp bởi tác giả liên hệ khi có yêu cầu. Điều này chứng minh PDF không kèm dữ liệu khảo sát và chỉ ra cơ chế xin dữ liệu. Nó không tự chứng minh không tồn tại bản dữ liệu công khai ở mọi nơi. Trang 1 chỉ ra tác giả liên hệ; địa chỉ ở trang 21 là phần liên hệ của bảng hỏi, không tự động cùng một đầu mối. Không gửi thư trong phạm vi map.

Chưa có trong bài quy tắc chấm điểm trung bình theo nhóm, trọng số toàn thang, ngưỡng yếu/trung bình/tốt, xử lý câu thiếu, quy tắc đảo điểm, cách mã hóa biến phân loại, số lần bootstrap, seed, phiên bản phần mềm và ước lượng CFA cụ thể. Mọi quy tắc bổ sung phải được ghi là thiết kế của demo.

Hệ quả để phiếu sau quyết định:

- Không thể tính lại chính xác kết quả gốc chỉ từ các bảng công bố. Tạo dữ liệu tổng hợp là minh họa thuật toán, không bổ sung bằng chứng thực nghiệm cho bài.
- Quy trình của bài có hai giai đoạn với 438 và 829 phiếu. Một tập tổng hợp 829 dòng theo danh mục cuối không tự minh họa được bước sàng lọc ba chỉ báo đã bị loại khỏi danh mục đó. Nếu muốn minh họa sàng lọc, cần đầu vào sơ bộ riêng và nêu đúng nguồn danh mục ban đầu.
- Chưa có bộ 47 chỉ báo nhất quán để sử dụng nguyên trạng. Phải quyết định rõ cách xử lý 47 công bố, 49 ở A4 và 52 ở A2 trước khi xây demo.
- Giữ nhãn tầm quan trọng thì điểm tổng hợp là đánh giá tầm quan trọng. Đổi nhãn sang mức đáp ứng hay mức năng lực là điều chỉnh công cụ và chưa được bài chính kiểm định.
- Có thể lấy trung bình theo nhóm như phép tính mô tả do người làm demo chọn, nhưng chưa được gán nó cho tác giả hoặc dùng nó làm chuẩn chẩn đoán năng lực của tổ chức thật.

## Đối chiếu finding1.md

| Khẳng định trong ghi chú | Kết quả kiểm chứng |
| --- | --- |
| Không thể tái lập đúng số từ PDF đơn lẻ; cần dữ liệu khảo sát. | Có căn cứ, nhưng sửa lời khẳng định tuyệt đối về việc không có repository thành "PDF không cung cấp liên kết bộ dữ liệu công khai". |
| Các giai đoạn CITC, alpha, khám phá, CFA, HTMT, PLS-SEM đều có trong bài. | Có căn cứ ở trang 9-12, nhưng không đủ mọi tham số để nói bài mô tả toàn bộ quy trình chạy lại. |
| PCA và direct oblimin. | Đúng theo mô tả bài chính. Cần phân biệt PCA với EFA theo mô hình nhân tố chung. |
| Phụ lục F có đủ 47 chỉ báo. | Sai theo danh mục thực tế. Bảng A4 liệt kê 49 mã. |
| Dùng thang 1-5 để tính mức mạnh/yếu của nhà thầu hoặc chủ đầu tư. | Vượt bằng chứng. Nhãn trả lời đo tầm quan trọng; không có ngưỡng chẩn đoán hay quy tắc điểm năng lực đã được cung cấp. |
| Tương quan âm Cap-OM ở Bảng 3. | Đúng là số công bố, thuộc khảo sát sơ bộ. Không phải bằng chứng nhân quả hoặc căn cứ đảo điểm. |
| Dùng lavaan hoặc seminr là chạy lại đúng cấu hình tác giả. | Các thư viện chỉ là lựa chọn demo được gợi ý. PDF không xác nhận cấu hình tương đương. |

Nguồn ghi chú được đối chiếu là tệp ghi chú yêu cầu ban đầu (finding1.md) ở thư mục làm việc gốc, không kèm trong gói nghiên cứu. Giữ nguyên ghi chú đầu vào để truy vết; dùng hồ sơ kiểm chứng và resolution comment làm căn cứ cho bước tiếp theo.


## Ứng dụng, ưu điểm và hướng mở rộng có căn cứ trong bài chính

Trang 15 đề xuất dùng thang để tự đánh giá và đánh giá đối tác, hỗ trợ nhận diện cách hợp tác hoặc biện pháp khắc phục. Đây là ứng dụng tác giả đề xuất, chưa phải bằng chứng công cụ đã cải thiện chi phí, thời gian hoặc chất lượng của một dự án thật. Cấu trúc nhiều nhóm và quy trình kiểm tra độ tin cậy, giá trị đo lường là ưu điểm có thể phân tích từ trang 9-12, cùng các giới hạn đã ghi ở trên.

Trang 15 đề xuất đưa biến kết quả thực hiện vào mô hình dự báo, mở rộng sang quản trị khủng hoảng và thảm họa, đối sánh thang trong bối cảnh toàn cầu. Dẫn đây là hướng nghiên cứu do tác giả đề xuất, không gọi là xu hướng toàn ngành đã được chứng minh.

## Nguồn hỗ trợ hai ví dụ thực tế

Đây là các ứng viên có căn cứ để phiếu bố cục chọn cùng người học. Chưa chốt lựa chọn thay người học và chưa đánh giá điểm năng lực của bất kỳ tổ chức thật nào.

### Đầu mối giao thông Nanning

Nguồn là Li, Y., Han, Y., Luo, M., và Zhang, Y. 2019. "Impact of Megaproject Governance on Project Performance: Dynamic Governance of the Nanning Transportation Hub in China". *Journal of Management in Engineering*, 35, 05019002. DOI [10.1061/(ASCE)ME.1943-5479.0000681](https://doi.org/10.1061/(ASCE)ME.1943-5479.0000681). Bản PDF của nguồn này nằm trong thư mục tài liệu tham khảo ở nơi làm việc gốc, không kèm trong gói nghiên cứu. Bản trích chữ của nguồn này (tệp `case-nanning.txt` ở thư mục làm việc gốc, không kèm trong gói nghiên cứu) giữ vị trí nguồn. PDF có 12 trang, trang PDF thứ k tương ứng trang in 05019002-k.

- Mục Case Setting, trang PDF 4, trang in 05019002-4 mô tả đầu mối Nanning với 19 dự án thành phần, 5 chủ đầu tư và 30 nhà thầu. Bảng 3 ở trang PDF 6 cung cấp thêm tên các đơn vị và dự án thành phần. Không suy ra số bên tham gia của toàn dự án chỉ bằng số dòng trong bảng này.
- Trang PDF 9, trang in 05019002-9 mô tả mô hình quản lý điều phối và bộ phận chỉ huy tại hiện trường, với sự thay đổi cấu trúc phối hợp. Trang PDF 10 trình bày sự phối hợp trong giai đoạn chuẩn bị vận hành. Đây là các cơ chế cụ thể để thảo luận quản trị liên tổ chức.
- Có thể phân tích liên hệ với quản lý tổ chức và quản lý dự án, nhưng đây là diễn giải của người làm báo cáo theo khung bài chính. Mô hình chỉ báo và cách chấm điểm của nghiên cứu Nanning khác thang của Zheng và cộng sự. Không chuyển các điểm ở Bảng 7-8 sang điểm của tám nhóm năng lực.
- Nguồn này là nghiên cứu tình huống có tên dự án thật, phù hợp làm ví dụ. Số liệu của nghiên cứu tình huống không phải dữ liệu đầu vào để tái lập bài chính; hồi quy theo các mốc thời gian trong nguồn này có mẫu nhỏ.

### Chuyển giao kinh nghiệm từ Rocky Flats sang London 2012

Nguồn là Denicol, J., và Davies, A. 2022. "The Megaproject-based Firm: Building programme management capability to deliver megaprojects". *International Journal of Project Management*, 40, 505-516. DOI [10.1016/j.ijproman.2022.06.002](https://doi.org/10.1016/j.ijproman.2022.06.002). Bản PDF của nguồn này nằm trong thư mục tài liệu tham khảo ở nơi làm việc gốc, không kèm trong gói nghiên cứu. Bản trích chữ của nguồn này (tệp `case-megafirm.txt` ở thư mục làm việc gốc, không kèm trong gói nghiên cứu) giữ vị trí nguồn. PDF có 12 trang, trang in bằng số trang PDF cộng 504.

- Trang PDF 4, trang in 508 nêu các dự án có tên như Rocky Flats và London 2012 trong danh mục kinh nghiệm của công ty được nghiên cứu. Cũng tại đây, tác giả nói danh tính công ty không được công bố vì bảo mật. Không tự suy đoán tên công ty từ mô tả.
- Mục 4.1.2, trang PDF 5, trang in 509 trình bày chuyển giao kinh nghiệm giữa dự án đầu tiên Rocky Flats và London 2012. Hình 1 trang PDF 8, trang in 512 trình bày mô hình phát triển năng lực quản lý chương trình.
- Phụ lục 3, trang PDF 11-12, trang in 515-516 cung cấp trích dẫn phỏng vấn về thiết kế vai trò và trách nhiệm giữa khách hàng với đối tác thực hiện, cùng cách phân bổ quyền hành động và rủi ro.
- Có thể liên hệ với học hỏi và đổi mới, nguồn nhân lực và quản lý tổ chức. Đây là phần diễn giải của báo cáo, không phải phép áp dụng đã được kiểm định của thang Zheng và cộng sự. Nguồn không cung cấp điểm số tám nhóm năng lực hay dữ liệu hiệu quả dự án đủ để tự tính tác động của từng nhóm.
- Đủ căn cứ cho ví dụ về dự án thật và cơ chế học hỏi. Không đủ căn cứ cho ví dụ về một công ty có tên được xác định. Phiếu bố cục cần chọn rõ trọng tâm là dự án hoặc yêu cầu bổ sung nguồn nếu muốn nêu danh tính tổ chức.

Không có dữ liệu khảo sát theo thang bài chính cho cả hai ví dụ. Không gán điểm Likert, biểu đồ năng lực hoặc thứ hạng tổ chức cho hai trường hợp này. Hai ví dụ chỉ hỗ trợ phân tích ứng dụng và giới hạn của khung khái niệm.


## Căn cứ từ sách và tài liệu môn học

Nguồn sách chính là Project Management Institute, *A Guide to the Project Management Body of Knowledge*, seventh edition, và *The Standard for Project Management*, 2021. Bản PDF của sách nằm ở nơi làm việc gốc, không kèm trong gói nghiên cứu; tra theo số trang PDF và tên phần đã ghi dưới đây. Tệp gộp hai phần có số trang in bắt đầu lại, nên phải ghi cả trang PDF và tên phần. Bản trích đã kiểm tra trực tiếp (tệp `verified-pmbok7.txt` ở thư mục làm việc gốc, không kèm trong gói nghiên cứu) cùng bảng định vị trang (`source-page-locators.json`, cùng nơi) cung cấp vị trí truy vết. Script locate-source-pages.py đếm ngắt trang của bản trích, không đoán vị trí trang từ số dòng.

| Khái niệm cần giải thích | Nội dung có căn cứ | Vị trí trong sách |
| --- | --- | --- |
| Dự án | Nỗ lực tạm thời nhằm tạo một sản phẩm, dịch vụ hoặc kết quả độc đáo. | PDF 31, *The Standard for Project Management*, mục 1.2, trang in 4. |
| Quản lý dự án | Áp dụng kiến thức, kỹ năng, công cụ và kỹ thuật vào hoạt động dự án để đáp ứng yêu cầu, hướng công việc đến kết quả dự kiến. | PDF 31, phần Standard, mục 1.2, trang in 4. |
| Hệ thống quản trị tổ chức và quản trị dự án | Khung chức năng và quá trình định hướng hoạt động, gồm giám sát, kiểm soát, đánh giá giá trị, tích hợp và ra quyết định. Quản trị dự án xác định quyền phê duyệt thay đổi và các quyết định kinh doanh liên quan, phù hợp quản trị chương trình và tổ chức. | PDF 39, phần Standard, mục 2.2, trang in 12. |
| Bên liên quan | Cá nhân, nhóm hoặc tổ chức có thể tác động, chịu tác động hoặc tự nhận chịu tác động bởi quyết định, hoạt động hay kết quả của dự án, chương trình hoặc danh mục. | PDF 103, phần *PMBOK Guide*, mục 2.1, trang in 8. |
| Miền hiệu quả thực hiện dự án | Nhóm hoạt động liên quan cần thiết để chuyển giao kết quả dự án; các miền tương tác và phụ thuộc nhau. | PDF 102, phần Guide, mục 2, trang in 7. |

Từ hai định nghĩa trong sách, có thể giải thích sự khác nhau giữa quyền quyết định và giám sát của governance với việc tổ chức, dẫn dắt công việc của management. Không coi hai từ là đồng nghĩa hoàn toàn hoặc coi quản trị chỉ là công việc nội bộ của nhà quản lý. Sáu vai trò tổ chức mà bài chính khảo sát là phạm vi hẹp hơn khái niệm stakeholder đầy đủ của PMI, vốn còn có thể gồm cộng đồng, người dùng và các bên phản đối.

Tám miền của PMBOK 7 ở trang PDF 102, trang in 7 là các bên liên quan, đội dự án, cách tiếp cận phát triển và vòng đời, lập kế hoạch, công việc dự án, chuyển giao, đo lường và sự không chắc chắn. Đây là các nhóm hoạt động dự án. Tám nhóm trong bài Zheng là các nhóm năng lực của tổ chức được đề xuất và kiểm tra bằng bảng hỏi. Không có căn cứ ánh xạ tương đương từng nhóm hoặc coi thang bài chính là cách đo tám miền PMBOK.

Sách *Information Technology Project Management* (lần xuất bản 9) đã kiểm tra thực tế bắt đầu ở Chương 3, không có phần đầu sách hoặc Chương 1 trong các trang đầu đã kiểm tra. Trang PDF 2 nêu 10 lĩnh vực kiến thức, 5 nhóm quá trình và tính tích hợp của quản lý dự án. Cũng ở trang này, tác giả gọi JWD Consulting là nghiên cứu tình huống mô phỏng. Vì vậy không sử dụng JWD Consulting làm một trong hai ví dụ thực tế. Chỉ dẫn các nội dung thật sự có trong tệp; không gán trang Chương 1 hoặc năm xuất bản dựa riêng vào tên tệp. Các khái niệm nền tảng đã có căn cứ độc lập từ sách PMI, nên thiếu phần đầu tệp này không chặn việc viết phần lý thuyết. Gói nghiên cứu không kèm tệp sách này.
