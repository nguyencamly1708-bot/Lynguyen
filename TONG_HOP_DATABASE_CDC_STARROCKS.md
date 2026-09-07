# BÁO CÁO TỔNG HỢP CÁC LOẠI DATABASE / BẢNG CDC TRÊN STARROCKS (kfm_scm)

**Máy chủ StarRocks:** `103.147.122.103:9030`  
**Database:** `kfm_scm`  
**Tài khoản:** `kfm_scm_tho_nguyen`  
**Thời gian rà soát:** 04/09/2026  
**Quy mô tổng thể:** 26 bảng CDC thời gian thực, tổng lưu trữ hơn **225+ triệu bản ghi**.

---

## 1. BẢNG TỔNG HỢP CHI TIẾT 26 BẢNG CDC

| STT | Nhóm Nghiệp Vụ | Tên Bảng CDC | Số Lượng Dòng | Ý Nghĩa & Vai Trò Nghiệp Vụ |
| :---: | :--- | :--- | :---: | :--- |
| **I** | **QUẢN LÝ TỒN KHO & THẺ KHO (kf_inventories)** | | | |
| 1 | Thẻ kho & Tổng hợp tồn | `__cdc_kfm_kf_inventories_kf_inventory_transaction_stock_summaries` | 155,820,973 | Tổng hợp số lượng xuất, nhập, tồn kho định kỳ theo từng SKU toàn hệ thống. |
| 2 | Sổ thẻ kho giao dịch | `__cdc_kfm_kf_inventories_kf_inventory_transaction_stockcard` | 50,584,173 | Chi tiết từng giao dịch làm thay đổi thẻ kho (thời gian, mã phiếu, số lượng +/-). |
| 3 | Mặt hàng luân chuyển | `__cdc_kfm_kf_inventories_kf_transfer_items` | 315,096 | Danh mục các mặt hàng được điều chuyển giữa DC và các Cửa hàng/Siêu thị (ST). |
| 4 | Dòng thùng/tote luân chuyển ⭐ | `__cdc_kfm_kf_inventories_kf_transfer_items___container_lines` | 1,259,418 | **Cốt lõi đối soát thùng rổ:** Chi tiết từng mã thùng/rổ/container/tote, thời gian nhận, số lượng xuất/nhận. |
| 5 | Hàng chuyển hoàn | `__cdc_kfm_kf_inventories_kf_transfer_items___return_transfers` | 67,427 | Dữ liệu các đợt hàng hoặc thùng rổ chuyển hoàn ngược từ Siêu thị về DC. |
| 6 | Khiếu nại tồn kho tổng | `__cdc_kfm_kf_inventories_kf_claim_stock_summaries` | 2 | Dữ liệu tổng hợp các phiếu khiếu nại chênh lệch hàng tồn kho. |
| 7 | Chi tiết khiếu nại tồn | `__cdc_kfm_kf_inventories_kf_claim_transaction_details` | 2 | Chi tiết các giao dịch bồi hoàn/xử lý khiếu nại chênh lệch tồn. |
| **II** | **VẬN TẢI, LỘ TRÌNH XE & GIAO NHẬN (Trips & Transport)** | | | |
| 8 | Danh mục chuyến xe | `__cdc_kfm_kf_inventories_kf_trips` | 16,009 | Danh sách các chuyến xe vận tải điều phối hàng ngày từ DC đến các điểm giao. |
| 9 | Điểm giao hàng chuyến xe | `__cdc_kfm_kf_inventories_kf_trip_locations` | 57,215 | Các điểm dừng giao hàng theo chuyến (Cửa hàng, Hub trung chuyển, DC). |
| 10 | Phiếu PT bàn giao thực tế ⭐ | `__cdc_kfm_kf_inventories_kf_trip_locations___tl_received_pts` | 823,305 | **Cốt lõi đối soát SLDT:** Danh sách các Phiếu Điều Chuyển (PT) được bàn giao thực tế tại từng ST. |
| 11 | Chi tiết mặt hàng theo xe | `__cdc_kfm_kf_inventories_kf_trips_locations_items` | 387,203 | Chi tiết số lượng từng mã hàng được giao tại từng điểm dừng của xe. |
| 12 | Phiếu PT tài xế ký nhận | `__cdc_kfm_597a32ea_597a32ea_L1___tl_driver_received_pts` | 95,223 | Xác nhận ký nhận phiếu điều chuyển của tài xế phụ trách chuyến xe. |
| 13 | Giám sát nhiệt độ thùng lạnh | `__cdc_kfm_597a32ea_597a32ea_L1___tl_temperature_images` | 193,221 | Hình ảnh và nhật ký nhiệt độ thùng bảo quản lạnh trên xe vận chuyển. |
| **III** | **CHỨNG TỪ ĐIỀU CHUYỂN (kf_transfer_tickets)** | | | |
| 14 | Phiếu điều chuyển tổng | `__cdc_kfm_kf_transfer_tickets_kf_transfer_tickets` | 51,504 | Phiếu điều chuyển gốc từ hệ thống WMS/ERP (mã PT, mã seal, mã container, trạng thái). |
| 15 | Dòng chi tiết phiếu PT | `__cdc_kfm_kf_transfer_tickets_kf_transfer_ticket_lines` | 162,959 | Chi tiết từng SKU, quy cách đóng gói và số lượng xuất trên phiếu điều chuyển. |
| **IV** | **KIỂM SOÁT CHẤT LƯỢNG & ĐÁNH GIÁ HAO HỤT (HRW & QC)** | | | |
| 16 | Phiếu chất lượng hàng tươi | `__cdc_kfm_kf_inventories_kf_hrw_quality_tickets` | 21,896 | Phiếu thẩm định kiểm tra chất lượng ngành hàng tươi sống/rau củ quả (HRW). |
| 17 | Chi tiết hàng kiểm tra QC | `__cdc_kfm_kf_inventories_kf_hrw_quality_tickets___items` | 101,657 | Chi tiết tình trạng kiểm tra theo từng mã hàng (tươi, dập, hư hỏng). |
| 18 | Tiêu chí kiểm soát lỗi | `__cdc_kfm_bede5be7_de5b9963_L2___criterias` | 1,030,745 | Danh mục bộ tiêu chuẩn kỹ thuật đánh giá quy cách, độ tươi và lỗi hao hụt. |
| 19 | Đánh giá phân loại lỗi | `__cdc_kfm_bede5be7_de5b9963_L2___evaluations` | 41,640 | Ghi nhận số lượng lỗi nặng (heavy defect), lỗi nhẹ (light defect) khi nhập kho. |
| **V** | **DÒNG SẢN PHẨM & LINE ITEMS ĐƠN HÀNG (ec9d24ab_...)** | | | |
| 20 | Dòng sản phẩm đơn hàng | `__cdc_kfm_ec9d24ab_1a050070_L2___product_lines` | 8,283,134 | Phân rã dữ liệu đơn hàng theo từng dòng sản phẩm. |
| 21 | Chi tiết mặt hàng đơn hàng | `__cdc_kfm_ec9d24ab_33bc7bbc_L3___line_items` | 8,281,829 | Dữ liệu mặt hàng chi tiết nhất của các đơn đặt hàng luân chuyển. |
| 22 | Mã điều chuyển gốc | `__cdc_kfm_ec9d24ab_e99d544c_L4___origin_transfer_codes` | 188,040 | Truy vết nguồn gốc đơn hàng từ mã phiếu chuyển kho khởi tạo ban đầu. |
| 23 | Điểm giao theo dòng hàng | `__cdc_kfm_ec9d24ab_c49f2956_L2___trip_locations` | 74,914 | Vị trí giao nhận gắn với từng phân dòng sản phẩm. |
| 24 | Lịch sử số lượng tạo | `__cdc_kfm_c6c82317_c6c82317_L1___created_quantity_histories` | 22,311 | Ghi vết các lần điều chỉnh số lượng tạo đơn ban đầu của người lập phiếu. |
| **VI** | **QUẢN TRỊ THAY ĐỔI CDC (Metadata)** | | | |
| 25 | Nhật ký thay đổi Schema | `__cdc_schema_changes` | 12 | Tự động ghi vết các trường dữ liệu được cập nhật hoặc đổi kiểu từ nguồn CDC. |
| 26 | Chuyến xe - địa điểm - hàng | `__cdc_kfm_kf_inventories_kf_transfer_items___trips` | 74,914 | Bảng liên kết trung gian giữa mặt hàng luân chuyển và mã chuyến xe vận chuyển. |

---

## 2. Ý NGHĨA ỨNG DỤNG TRỰC TIẾP CHO SCM & ĐỐI SOÁT

### 1. Đối Soát Thùng Xanh / Rổ (Tote/Crate Reconciliation)
- **Nguồn dữ liệu gốc:** Bảng `__cdc_kfm_kf_inventories_kf_transfer_items___container_lines`.
- **Dữ liệu có sẵn:**
  - `code`: Mã thùng / Mã rổ (ví dụ: CC00359, CC00360, CC00381 hoặc barcode thùng).
  - `received_at`: Thời gian quét nhận thùng thực tế tại Siêu thị.
  - `total_transfer_quantity` vs `total_store_quantity`: Số lượng thùng DC chuyển đi vs Số lượng ST xác nhận nhận.
- **Ứng dụng:** Đối chiếu tự động với bảng quyết toán bồi hoàn `krc_datapay_records` để tìm ra ngay thùng nào còn đang thất lạc hoặc cửa hàng nào nợ thùng chưa trả về DC.

### 2. Đối Soát Số Lượng Đơn / Phiếu PT (SLDT Reconciliation)
- **Nguồn dữ liệu gốc:** Bảng `__cdc_kfm_kf_inventories_kf_trip_locations___tl_received_pts` kết hợp với `__cdc_kfm_kf_transfer_tickets_kf_transfer_tickets`.
- **Dữ liệu có sẵn:**
  - Mã phiếu điều chuyển `transfer_item_code` (Mã PT).
  - Trạng thái nhận hàng của tài xế và cửa hàng.
- **Ứng dụng:** Xác minh tức thì các khiếu nại thiếu đơn từ phía siêu thị so với dữ liệu quét thực tế của tài xế.
