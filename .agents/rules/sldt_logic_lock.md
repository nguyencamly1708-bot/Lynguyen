# SLDT Sheet Filtering Logic Lock Rule

## IMPORTANT / STRICT RULE
The following logic for parsing and filtering SLDT discrepancy data from Google Sheets in `server.py` is **PERMANENTLY LOCKED** and must NOT be changed or modified:

1. **Filtering Conditions**:
   - **Column AR (Index 43 - Xử lý)**: Must match `"đang xử lý"` (case-insensitive substring check).
   - **Column AQ (Index 42 - Classify)**: Must match `"chờ st"` or `"chờ st phản hồi"`.
   - **Row Acceptance Criterion**: `is_pending = ("đang xử lý" in ar_val) or ("chờ st" in aq_val)`

2. **Discrepancy Check (Bỏ qua phiếu không có lệch)**:
   - If `sl_chuyen == sl_nhan` and `sl_chuyen not in ["", "-1"]`, the row MUST be skipped (no discrepancy, already fully received).
   - `if sl_chuyen == sl_nhan and sl_chuyen not in ["", "-1"]: continue`

3. **Data Structure & Grouping**:
   - Items are grouped by `id_st` (Column 0).
   - Includes keys: `id_st`, `ngay_chuyen`, `cn_chuyen`, `cn_nhan`, `ma_hang`, `ten_hang`, `dvt`, `sl_chuyen`, `sl_nhan`, `sl_nhan_ht`, `ma_chuyen_hang`, `ma_phieu`, `trang_thai`, `tg_tao`.
