document.addEventListener("DOMContentLoaded", () => {
  const botStatusBadge = document.getElementById("botStatusBadge");
  const botStatusText = document.getElementById("botStatusText");
  const btnRefresh = document.getElementById("btnRefresh");
  
  const messageText = document.getElementById("messageText");
  const sldtMessageText = document.getElementById("sldtMessageText");
  const selectedGroupCount = document.getElementById("selectedGroupCount");
  const btnToggleSelectAll = document.getElementById("btnToggleSelectAll");
  
  const btnSyncStBroadcast = document.getElementById("btnSyncStBroadcast");
  const btnUploadImages = document.getElementById("btnUploadImages");
  const btnUploadDocs = document.getElementById("btnUploadDocs");
  const imageFileInput = document.getElementById("imageFileInput");
  const documentFileInput = document.getElementById("documentFileInput");
  const attachmentPreviewContainer = document.getElementById("attachmentPreviewContainer");
  
  const btnClearMessage = document.getElementById("btnClearMessage");
  const btnBroadcast = document.getElementById("btnBroadcast");
  
  const searchGroup = document.getElementById("searchGroup");
  const groupsList = document.getElementById("groupsList");
  const groupBadgeCount = document.getElementById("groupBadgeCount");
  
  const searchMentions = document.getElementById("searchMentions");
  const mentionsList = document.getElementById("mentionsList");
  const mentionsBadgeCount = document.getElementById("mentionsBadgeCount");
  const btnClearMentions = document.getElementById("btnClearMentions");
  
  const historyList = document.getElementById("historyList");
  const sldtHistoryList = document.getElementById("sldtHistoryList");
  const toastContainer = document.getElementById("toastContainer");

  let currentGroups = {};
  let selectedGroupIds = new Set();
  let sldtSelectedGroupIds = new Set();
  let sldtSheetGroupIds = new Set();
  let allSelected = true;
  let currentCategory = "all";
  let sldtCurrentCategory = "all";
  let attachedFiles = [];
  let allMentions = [];

  // Tab switching logic for left sidebar menu (3 MỤC CHÍNH)
  const navItems = document.querySelectorAll(".sidebar-menu .nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const activeTabTitle = document.getElementById("activeTabTitle");
  const activeTabSubtitle = document.getElementById("activeTabSubtitle");

  const tabSubtitles = {
    "tab-send-msg": "Soạn tin nhắn thủ công, đính kèm file/ảnh (Ctrl+V) và phát tới các nhóm Telegram cửa hàng ST",
    "tab-doi-soat-sldt": "Tự Động Lọc Sheet SLG (Cột AQ), Nhóm Theo ID ST, Tạo Bảng Ảnh PNG & Tag Tên SM/TC",
    "tab-doi-soat-kho-rau": "Đối Soát Rổ/Tote Tháng 09.2026 - Phân Luồng 5 Bước & Quyết Toán Datapay Nợ Thùng Rổ Bồi Hoàn",
    "tab-mentions": "Theo Dõi & Quản Lý Tất Cả Lượt Tag @teamSCM_bot Hoặc Trả Lời Tin Nhắn Từ Các Nhóm Telegram ST"
  };

  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const targetTabId = item.getAttribute("data-tab");
      const labelText = item.querySelector(".nav-label").innerText.trim();

      navItems.forEach(nav => nav.classList.remove("active"));
      item.classList.add("active");

      tabPanes.forEach(pane => pane.classList.remove("active"));
      const activePane = document.getElementById(targetTabId);
      if (activePane) activePane.classList.add("active");

      if (activeTabTitle) activeTabTitle.textContent = labelText;
      if (activeTabSubtitle) activeTabSubtitle.textContent = tabSubtitles[targetTabId] || "Bảng Điều Khiển KFM LOGISTIC-SCM";
    });
  });

  // 1. Kiểm tra trạng thái máy chủ & bot
  async function checkStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      if (data.status === "online") {
        botStatusBadge.style.borderColor = "rgba(16, 185, 129, 0.25)";
        if (data.userbot_auth) {
          botStatusText.innerHTML = `<span style="color: #38bdf8; font-weight: 700;">@${escapeHtml(data.userbot_username)}</span> Hoạt Động (${data.groups_count} nhóm)`;
        } else {
          botStatusText.textContent = `Bot Hoạt Động (${data.groups_count} nhóm)`;
        }
      } else {
        botStatusText.textContent = "Bot Mất Kết Nối";
      }
    } catch (err) {
      botStatusText.textContent = "Lỗi kết nối Server";
    }
  }

  // 2. Tải danh sách Nhóm & Phân Loại (DC, KRC, ABA, Khác)
  async function loadGroups() {
    try {
      const res = await fetch("/api/groups");
      currentGroups = await res.json();
      selectedGroupIds = new Set(Object.keys(currentGroups));
      sldtSelectedGroupIds = new Set(); // Mặc định không tick chọn sẵn 645 nhóm, để người dùng tự tick

      // Lấy danh sách các nhóm DC có phiếu thực tế trong Google Sheet
      try {
        const sldtRes = await fetch("/api/sldt/stores");
        const sldtData = await sldtRes.json();
        if (sldtData.sheet_group_ids) {
          sldtSheetGroupIds = new Set(sldtData.sheet_group_ids.map(String));
        }
      } catch (e) {
        console.warn("Không tải được danh sách ST từ sheet:", e);
      }

      renderGroupsList(currentGroups);
      renderSldtGroupsList(currentGroups);
      checkStatus();
    } catch (err) {
      showToast("Không thể tải danh sách nhóm", "error");
    }
  }

  function getGroupCategory(title) {
    const t = (title || "").toUpperCase();
    if (t.includes("DC")) return "dc";
    if (t.includes("KRC")) return "krc";
    if (t.includes("ABA")) return "aba";
    return "other";
  }

  function updateCategoryCounts(groups) {
    let countAll = 0, countDc = 0, countKrc = 0, countAba = 0, countOther = 0;
    Object.values(groups).forEach(g => {
      const cat = getGroupCategory(g.title);
      countAll++;
      if (cat === "dc") countDc++;
      else if (cat === "krc") countKrc++;
      else if (cat === "aba") countAba++;
      else countOther++;
    });

    const elAll = document.getElementById("catCountAll");
    const elDc = document.getElementById("catCountDc");
    const elKrc = document.getElementById("catCountKrc");
    const elAba = document.getElementById("catCountAba");
    const elOther = document.getElementById("catCountOther");

    if (elAll) elAll.textContent = countAll;
    if (elDc) elDc.textContent = countDc;
    if (elKrc) elKrc.textContent = countKrc;
    if (elAba) elAba.textContent = countAba;
    if (elOther) elOther.textContent = countOther;
  }

  function renderGroupsList(groups, filterText = "") {
    updateCategoryCounts(groups);

    const entries = Object.entries(groups).filter(([gid, data]) => {
      const matchSearch = data.title.toLowerCase().includes(filterText.toLowerCase());
      const cat = getGroupCategory(data.title);
      const matchCat = (currentCategory === "all") || (cat === currentCategory);
      return matchSearch && matchCat;
    });

    groupBadgeCount.textContent = `${entries.length} Nhóm`;

    if (entries.length === 0) {
      groupsList.innerHTML = `<div class="empty-state">Chưa có nhóm nào hoặc không tìm thấy nhóm phù hợp trong mục này.</div>`;
      updateSelectedCount();
      return;
    }

    groupsList.innerHTML = entries.map(([gid, data]) => {
      const isChecked = selectedGroupIds.has(gid);
      return `
        <div class="group-card-item ${isChecked ? 'selected' : ''}" data-gid="${gid}">
          <div class="group-left-area">
            <input type="checkbox" value="${gid}" class="group-checkbox" ${isChecked ? 'checked' : ''}>
            <div>
              <div class="group-title">👥 ${escapeHtml(data.title)}</div>
              <div class="group-id">ID: ${gid}</div>
            </div>
          </div>
          <button class="btn-send-single" data-gid="${gid}" data-title="${escapeHtml(data.title)}" title="Gửi tin nhắn hiện tại tới nhóm này">
            <i class="fa-paper-plane fa-solid"></i> Gửi riêng
          </button>
        </div>
      `;
    }).join("");

    updateSelectedCount();

    document.querySelectorAll(".group-checkbox").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const gid = e.target.value;
        if (e.target.checked) {
          selectedGroupIds.add(gid);
        } else {
          selectedGroupIds.delete(gid);
        }
        const item = document.querySelector(`.group-card-item[data-gid="${gid}"]`);
        if (item) item.classList.toggle("selected", e.target.checked);
        updateSelectedCount();
      });
    });

    document.querySelectorAll(".btn-send-single").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const gid = btn.getAttribute("data-gid");
        const title = btn.getAttribute("data-title");
        sendBroadcast([gid], `nhóm ${title}`);
      });
    });
  }

  function updateSelectedCount() {
    selectedGroupCount.textContent = selectedGroupIds.size;
  }

  // Sự kiện chuyển Tab Phân Loại ở Mục Gửi Tin ST
  document.querySelectorAll(".group-cat-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".group-cat-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentCategory = tab.getAttribute("data-cat");
      renderGroupsList(currentGroups, searchGroup.value);
    });
  });

  searchGroup.addEventListener("input", (e) => {
    renderGroupsList(currentGroups, e.target.value);
  });

  btnToggleSelectAll.addEventListener("click", () => {
    const currentCategoryEntries = Object.entries(currentGroups).filter(([gid, data]) => {
      const matchSearch = data.title.toLowerCase().includes(searchGroup.value.toLowerCase());
      const cat = getGroupCategory(data.title);
      const matchCat = (currentCategory === "all") || (cat === currentCategory);
      return matchSearch && matchCat;
    });

    const currentCategoryGids = currentCategoryEntries.map(([gid]) => gid);
    const allCurrentlySelected = currentCategoryGids.every(gid => selectedGroupIds.has(gid));

    if (allCurrentlySelected) {
      currentCategoryGids.forEach(gid => selectedGroupIds.delete(gid));
      btnToggleSelectAll.textContent = "Chọn tất cả";
    } else {
      currentCategoryGids.forEach(gid => selectedGroupIds.add(gid));
      btnToggleSelectAll.textContent = "Bỏ chọn tất cả";
    }
    renderGroupsList(currentGroups, searchGroup.value);
  });

  // 2.1 Tải & Chọn Nhóm Riêng Cho Mục ĐỐI SOÁT SLDT
  function updateSldtCategoryCounts(groups) {
    let countAll = 0, countSheet = 0, countDc = 0, countKrc = 0, countAba = 0, countOther = 0;
    Object.entries(groups).forEach(([gid, g]) => {
      const cat = getGroupCategory(g.title);
      countAll++;
      if (sldtSheetGroupIds.has(String(gid))) countSheet++;
      if (cat === "dc") countDc++;
      else if (cat === "krc") countKrc++;
      else if (cat === "aba") countAba++;
      else countOther++;
    });

    const elAll = document.getElementById("sldtCatCountAll");
    const elSheet = document.getElementById("sldtCatCountSheet");
    const elDc = document.getElementById("sldtCatCountDc");
    const elKrc = document.getElementById("sldtCatCountKrc");
    const elAba = document.getElementById("sldtCatCountAba");
    const elOther = document.getElementById("sldtCatCountOther");

    if (elAll) elAll.textContent = countAll;
    if (elSheet) elSheet.textContent = countSheet;
    if (elDc) elDc.textContent = countDc;
    if (elKrc) elKrc.textContent = countKrc;
    if (elAba) elAba.textContent = countAba;
    if (elOther) elOther.textContent = countOther;
  }

  function updateSldtSelectedCount() {
    const countEl = document.getElementById("sldtSelectedGroupCount");
    if (countEl) countEl.textContent = sldtSelectedGroupIds.size;
    if (btnSyncStBroadcast) {
      btnSyncStBroadcast.innerHTML = `<i class="fa-circle-check fa-solid"></i> 🎯 GỬI CHO CÁC ST ĐÃ TICK CHỌN BÊN TRÊN (<span id="sldtSelectedGroupCount">${sldtSelectedGroupIds.size}</span> Nhóm)`;
    }
  }

  function renderSldtGroupsList(groups, filterText = "") {
    const sldtGroupsList = document.getElementById("sldtGroupsList");

    if (!sldtGroupsList) return;

    updateSldtCategoryCounts(groups);

    const entries = Object.entries(groups).filter(([gid, data]) => {
      const matchSearch = data.title.toLowerCase().includes((filterText || "").toLowerCase());
      const cat = getGroupCategory(data.title);
      let matchCat = true;
      if (sldtCurrentCategory === "sheet") {
        matchCat = sldtSheetGroupIds.has(String(gid));
      } else if (sldtCurrentCategory !== "all") {
        matchCat = (cat === sldtCurrentCategory);
      }
      return matchSearch && matchCat;
    });

    updateSldtSelectedCount();

    if (entries.length === 0) {
      sldtGroupsList.innerHTML = `<div class="empty-state">Không tìm thấy nhóm phù hợp trong mục này.</div>`;
      return;
    }

    sldtGroupsList.innerHTML = entries.map(([gid, data]) => {
      const isChecked = sldtSelectedGroupIds.has(gid);
      const inSheet = sldtSheetGroupIds.has(String(gid));
      return `
        <div class="group-card-item ${isChecked ? 'selected' : ''}" data-sgid="${gid}">
          <div class="group-left-area">
            <input type="checkbox" value="${gid}" class="sldt-group-checkbox" ${isChecked ? 'checked' : ''}>
            <div>
              <div class="group-title">
                👥 ${escapeHtml(data.title)}
                ${inSheet ? '<span class="badge badge-cyan" style="font-size: 0.65rem; padding: 1px 5px; margin-left: 5px;">Có trong Sheet</span>' : ''}
              </div>
              <div class="group-id">ID: ${gid}</div>
            </div>
          </div>
          <button type="button" class="btn-send-single-sldt" data-gid="${gid}" data-title="${escapeHtml(data.title)}" title="Gửi riêng Bảng Ảnh cho ST này">
            <i class="fa-paper-plane fa-solid"></i> Gửi ST này
          </button>
        </div>
      `;
    }).join("");

    // Xử lý sự kiện tick checkbox chọn từng ST
    document.querySelectorAll(".sldt-group-checkbox").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const gid = e.target.value;
        if (e.target.checked) {
          sldtSelectedGroupIds.add(gid);
        } else {
          sldtSelectedGroupIds.delete(gid);
        }
        const item = document.querySelector(`.group-card-item[data-sgid="${gid}"]`);
        if (item) item.classList.toggle("selected", e.target.checked);
        updateSldtSelectedCount();
      });
    });

    // Xử lý nút "Gửi ST này" trên từng hàng
    document.querySelectorAll(".btn-send-single-sldt").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const gid = btn.getAttribute("data-gid");
        const title = btn.getAttribute("data-title");
        await sendSldtBroadcast([gid], title);
      });
    });
  }

  // Sự kiện chuyển Tab Phân Loại ở Mục Đối Soát SLDT
  document.querySelectorAll(".sldt-group-cat-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".sldt-group-cat-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      sldtCurrentCategory = tab.getAttribute("data-cat");
      const searchVal = document.getElementById("sldtSearchGroup") ? document.getElementById("sldtSearchGroup").value : "";
      renderSldtGroupsList(currentGroups, searchVal);
    });
  });

  const sldtSearchGroup = document.getElementById("sldtSearchGroup");
  if (sldtSearchGroup) {
    sldtSearchGroup.addEventListener("input", (e) => {
      renderSldtGroupsList(currentGroups, e.target.value);
    });
  }

  const btnSldtToggleSelectAll = document.getElementById("btnSldtToggleSelectAll");
  if (btnSldtToggleSelectAll) {
    btnSldtToggleSelectAll.addEventListener("click", () => {
      const searchVal = sldtSearchGroup ? sldtSearchGroup.value : "";
      const currentCategoryEntries = Object.entries(currentGroups).filter(([gid, data]) => {
        const matchSearch = data.title.toLowerCase().includes(searchVal.toLowerCase());
        const cat = getGroupCategory(data.title);
        let matchCat = true;
        if (sldtCurrentCategory === "sheet") {
          matchCat = sldtSheetGroupIds.has(String(gid));
        } else if (sldtCurrentCategory !== "all") {
          matchCat = (cat === sldtCurrentCategory);
        }
        return matchSearch && matchCat;
      });

      const currentGids = currentCategoryEntries.map(([gid]) => gid);
      const allSelected = currentGids.length > 0 && currentGids.every(gid => sldtSelectedGroupIds.has(gid));

      if (allSelected) {
        currentGids.forEach(gid => sldtSelectedGroupIds.delete(gid));
        btnSldtToggleSelectAll.textContent = "Chọn tất cả";
      } else {
        currentGids.forEach(gid => sldtSelectedGroupIds.add(gid));
        btnSldtToggleSelectAll.textContent = "Bỏ chọn tất cả";
      }
      renderSldtGroupsList(currentGroups, searchVal);
    });
  }

  // 3. Tải Lịch Sử Mentions/Tags (BẢN MỤC RIÊNG BẢN ĐẦY ĐỦ)
  async function loadMentions() {
    try {
      const res = await fetch("/api/mentions");
      allMentions = await res.json();
      renderMentions(allMentions, searchMentions ? searchMentions.value : "");
    } catch (err) {
      console.error(err);
    }
  }

  function renderMentions(mentions, filterText = "") {
    mentionsBadgeCount.textContent = `${mentions.length} Lượt`;

    const filtered = mentions.filter(m => {
      const txt = (filterText || "").toLowerCase();
      return (m.sender_name || "").toLowerCase().includes(txt) ||
             (m.sender_username || "").toLowerCase().includes(txt) ||
             (m.group_title || "").toLowerCase().includes(txt) ||
             (m.text || "").toLowerCase().includes(txt);
    });

    if (filtered.length === 0) {
      mentionsList.innerHTML = `<div class="empty-state">Chưa có ai tag @teamSCM_bot hoặc phản hồi tin nhắn${filterText ? ' phù hợp tìm kiếm' : ''}.</div>`;
      return;
    }

    mentionsList.innerHTML = filtered.slice().reverse().map(m => `
      <div class="mention-item">
        <div class="mention-header">
          <span class="mention-sender"><i class="fa-user fa-solid"></i> ${escapeHtml(m.sender_name)} ${m.sender_username ? `(${m.sender_username})` : ''}</span>
          <span class="mention-time"><i class="fa-clock fa-regular"></i> ${m.timestamp}</span>
        </div>
        <div class="mention-group">📍 Nhóm Telegram: ${escapeHtml(m.group_title)}</div>
        <div class="mention-text">"${escapeHtml(m.text)}"</div>
      </div>
    `).join("");
  }

  if (searchMentions) {
    searchMentions.addEventListener("input", (e) => {
      renderMentions(allMentions, e.target.value);
    });
  }

  btnClearMentions.addEventListener("click", async () => {
    if (confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử Tag/Phản hồi?")) {
      try {
        await fetch("/api/clear_mentions", { method: "POST" });
        loadMentions();
        showToast("Đã xóa lịch sử tag thành công", "success");
      } catch (err) {
        showToast("Không thể xóa lịch sử tag", "error");
      }
    }
  });

  // 4. Tải Lịch Sử Phát Tin & Thu Hồi Chọn Nhóm
  async function loadHistory() {
    try {
      const res = await fetch("/api/history");
      const history = await res.json();

      if (history.length === 0) {
        historyList.innerHTML = `<div class="empty-state">Chưa phát tin nhắn nào.</div>`;
        if (sldtHistoryList) sldtHistoryList.innerHTML = `<div class="empty-state">Chưa phát tin nhắn đối soát nào.</div>`;
        return;
      }

      const renderItemHtml = (h, realIdx) => {
        let successTags = "";
        let failedTags = "";

        if (h.success_groups && h.success_groups.length > 0) {
          successTags = h.success_groups.map(g => `<span class="group-tag-badge group-tag-success">✓ ${escapeHtml(g)}</span>`).join("");
        } else if (h.success_count > 0) {
          successTags = `<span class="group-tag-badge group-tag-success">✓ Thành công ${h.success_count} nhóm</span>`;
        }

        if (h.failed_groups && h.failed_groups.length > 0) {
          failedTags = h.failed_groups.map(g => `<span class="group-tag-badge group-tag-failed">✗ ${escapeHtml(g)}</span>`).join("");
        } else if (h.failed_count > 0) {
          failedTags = `<span class="group-tag-badge group-tag-failed">✗ Thất bại ${h.failed_count} nhóm</span>`;
        }

        const sentRecords = h.sent_records || [];
        const activeRecords = sentRecords.filter(r => !r.revoked);
        const totalRecords = sentRecords.length;

        let revokeSectionHtml = "";

        if (h.revoked || (totalRecords > 0 && activeRecords.length === 0)) {
          revokeSectionHtml = `<span class="badge badge-rose" style="margin-top: 6px;"><i class="fa-ban fa-solid"></i> Đã Thu Hồi Tất Cả Nhóm ${h.revoked_timestamp || ''}</span>`;
        } else if (totalRecords > 0) {
          const rowsHtml = sentRecords.map(rec => {
            const isRev = rec.revoked;
            const gTitle = rec.group_title || `Nhóm (${rec.chat_id})`;
            return `
              <div class="revoke-item-row ${isRev ? 'revoked-row' : ''}">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; flex: 1;">
                  <input type="checkbox" class="chk-revoke-group" data-hidx="${realIdx}" data-cid="${rec.chat_id}" ${isRev ? 'disabled' : 'checked'}>
                  <span>${escapeHtml(gTitle)} ${isRev ? '(Đã thu hồi)' : ''}</span>
                </label>
                ${!isRev ? `
                  <button type="button" class="btn btn-secondary btn-xs btn-revoke-single" data-hidx="${realIdx}" data-cid="${rec.chat_id}" style="color: #fb7185; border-color: rgba(244, 63, 94, 0.4);">
                    <i class="fa-rotate-left fa-solid"></i> Thu hồi
                  </button>
                ` : ''}
              </div>
            `;
          }).join("");

          revokeSectionHtml = `
            <div class="revoke-group-box">
              <div class="revoke-group-header">
                <span>📍 Chọn nhóm cần thu hồi (${activeRecords.length}/${totalRecords} nhóm còn hiển thị):</span>
                <button type="button" class="btn btn-secondary btn-xs btn-toggle-group-list" data-hidx="${realIdx}">
                  <i class="fa-chevron-down fa-solid"></i> Danh sách nhóm (${activeRecords.length})
                </button>
              </div>

              <div class="revoke-group-list hidden" id="revokeGroupList_${realIdx}">
                ${rowsHtml}
                <div class="revoke-action-bar">
                  <button type="button" class="btn btn-secondary btn-xs btn-revoke-selected" data-hidx="${realIdx}" style="color: #fb7185; border-color: rgba(244, 63, 94, 0.4);">
                    <i class="fa-rotate-left fa-solid"></i> Thu hồi nhóm đã chọn
                  </button>
                  <button type="button" class="btn btn-secondary btn-xs btn-revoke-all" data-hidx="${realIdx}" style="color: #f43f5e; background: rgba(244, 63, 94, 0.15);">
                    <i class="fa-trash-can fa-solid"></i> Thu hồi tất cả nhóm
                  </button>
                </div>
              </div>
            </div>
          `;
        }

        return `
          <div class="history-item ${h.revoked ? 'history-item-revoked' : ''}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-weight: 600; color: #f8fafc;">${escapeHtml(h.message)}</span>
              <span class="history-time">${h.timestamp}</span>
            </div>
            <div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">
              ${successTags}
              ${failedTags}
            </div>
            ${revokeSectionHtml}
          </div>
        `;
      };

      const stItems = [];
      const sldtItems = [];

      for (let i = history.length - 1; i >= 0; i--) {
        const h = history[i];
        const html = renderItemHtml(h, i);
        if (h.type === "sldt") {
          sldtItems.push(html);
        } else {
          stItems.push(html);
        }
      }

      historyList.innerHTML = stItems.length > 0 ? stItems.join("") : `<div class="empty-state">Chưa phát tin nhắn ST nào.</div>`;
      if (sldtHistoryList) {
        sldtHistoryList.innerHTML = sldtItems.length > 0 ? sldtItems.join("") : `<div class="empty-state">Chưa phát tin nhắn đối soát nào.</div>`;
      }

      // Event toggle list
      document.querySelectorAll(".btn-toggle-group-list").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const hidx = btn.getAttribute("data-hidx");
          const target = document.getElementById(`revokeGroupList_${hidx}`);
          if (target) target.classList.toggle("hidden");
        });
      });

      // Event single group revoke
      document.querySelectorAll(".btn-revoke-single").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const hidx = parseInt(btn.getAttribute("data-hidx"));
          const cid = parseInt(btn.getAttribute("data-cid"));
          executeSelectiveRevoke(hidx, [cid]);
        });
      });

      // Event selected groups revoke
      document.querySelectorAll(".btn-revoke-selected").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const hidx = parseInt(btn.getAttribute("data-hidx"));
          const checked = Array.from(document.querySelectorAll(`.chk-revoke-group[data-hidx="${hidx}"]:checked`))
                               .map(cb => parseInt(cb.getAttribute("data-cid")));
          if (checked.length === 0) {
            showToast("Vui lòng chọn ít nhất 1 nhóm để thu hồi!", "warning");
            return;
          }
          executeSelectiveRevoke(hidx, checked);
        });
      });

      // Event full revoke
      document.querySelectorAll(".btn-revoke-all").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const hidx = parseInt(btn.getAttribute("data-hidx"));
          executeFullRevoke(hidx);
        });
      });

    } catch (err) {
      console.error(err);
    }
  }

  async function executeSelectiveRevoke(hidx, chatIds) {
    if (confirm(`⚠️ Bạn có chắc chắn muốn THU HỒI tin nhắn/bảng ảnh từ ${chatIds.length} nhóm đã chọn?`)) {
      showToast("Đang thu hồi tin nhắn từ các nhóm...", "info");
      try {
        const res = await fetch("/api/revoke_selective", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ history_index: hidx, chat_ids: chatIds })
        });
        const data = await res.json();
        if (res.ok) {
          showToast(`Đã thu hồi thành công ${data.deleted_count} tin nhắn trên Telegram!`, "success");
          loadHistory();
        } else {
          showToast(data.detail || "Thu hồi thất bại", "error");
        }
      } catch (err) {
        showToast("Lỗi kết nối máy chủ", "error");
      }
    }
  }

  async function executeFullRevoke(hidx) {
    if (confirm("⚠️ Bạn có chắc chắn muốn THU HỒI TẤT CẢ tin nhắn/bảng ảnh đã gửi trong đợt này từ Telegram?")) {
      showToast("Đang thu hồi tất cả tin nhắn...", "info");
      try {
        const res = await fetch("/api/revoke_broadcast", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ history_index: hidx })
        });
        const data = await res.json();
        if (res.ok) {
          showToast(`Đã thu hồi thành công ${data.deleted_count} tin nhắn trên Telegram!`, "success");
          loadHistory();
        } else {
          showToast(data.detail || "Thu hồi thất bại", "error");
        }
      } catch (err) {
        showToast("Lỗi kết nối máy chủ", "error");
      }
    }
  }

  // 5. Xử lý Đính kèm File & Dán Ảnh (Ctrl+V)
  btnUploadImages.addEventListener("click", () => imageFileInput.click());
  btnUploadDocs.addEventListener("click", () => documentFileInput.click());

  imageFileInput.addEventListener("change", (e) => handleFileSelect(e.target.files));
  documentFileInput.addEventListener("change", (e) => handleFileSelect(e.target.files));

  document.addEventListener("paste", (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    let imageFiles = [];
    for (let item of items) {
      if (item.type.indexOf("image") !== -1) {
        const blob = item.getAsFile();
        const file = new File([blob], `pasted_image_${Date.now()}.png`, { type: blob.type });
        imageFiles.push(file);
      }
    }
    if (imageFiles.length > 0) {
      handleFileSelect(imageFiles);
      showToast(`Đã dán ${imageFiles.length} hình ảnh từ Clipboard!`, "success");
    }
  });

  function handleFileSelect(files) {
    for (let file of files) {
      attachedFiles.push(file);
    }
    renderAttachmentPreviews();
  }

  function renderAttachmentPreviews() {
    if (attachedFiles.length === 0) {
      attachmentPreviewContainer.innerHTML = "";
      return;
    }

    attachmentPreviewContainer.innerHTML = attachedFiles.map((file, index) => {
      const isImg = file.type.startsWith("image/");
      const icon = isImg ? "fa-image" : "fa-file";
      const imgPreview = isImg ? `<img src="${URL.createObjectURL(file)}" alt="preview">` : `<i class="fa-solid ${icon}"></i>`;

      return `
        <div class="preview-chip">
          ${imgPreview}
          <span>${escapeHtml(file.name)}</span>
          <button type="button" class="btn-remove-chip" data-index="${index}"><i class="fa-xmark fa-solid"></i></button>
        </div>
      `;
    }).join("");

    document.querySelectorAll(".btn-remove-chip").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const idx = parseInt(btn.getAttribute("data-index"));
        attachedFiles.splice(idx, 1);
        renderAttachmentPreviews();
      });
    });
  }

  btnClearMessage.addEventListener("click", () => {
    messageText.value = "";
    attachedFiles = [];
    renderAttachmentPreviews();
  });

  // 6. Phát Tin Nhắn ST Thủ Công
  btnBroadcast.addEventListener("click", () => {
    if (selectedGroupIds.size === 0) {
      showToast("Vui lòng chọn ít nhất 1 nhóm Telegram ST!", "warning");
      return;
    }
    sendBroadcast(Array.from(selectedGroupIds), `${selectedGroupIds.size} nhóm`);
  });

  async function sendBroadcast(groupArray, label) {
    const text = messageText.value.trim();
    if (!text && attachedFiles.length === 0) {
      showToast("Vui lòng nhập nội dung hoặc đính kèm file!", "warning");
      return;
    }

    btnBroadcast.disabled = true;
    btnBroadcast.innerHTML = `<i class="fa-circle-notch fa-spin fa-solid"></i> Đang gửi tới ${label}...`;

    try {
      let res;
      if (attachedFiles.length === 0) {
        res = await fetch("/api/broadcast", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, target_groups: groupArray })
        });
      } else {
        const formData = new FormData();
        formData.append("message", text);
        formData.append("target_groups", JSON.stringify(groupArray));
        attachedFiles.forEach(file => formData.append("files", file));

        res = await fetch("/api/broadcast_media", {
          method: "POST",
          body: formData
        });
      }

      const data = await res.json();
      if (res.ok) {
        showToast(`Đã gửi xong tới ${data.success_count} nhóm thành công!`, "success");
        messageText.value = "";
        attachedFiles = [];
        renderAttachmentPreviews();
        loadHistory();
      } else {
        showToast(data.detail || "Gửi tin thất bại", "error");
      }
    } catch (err) {
      showToast("Lỗi kết nối máy chủ khi gửi tin", "error");
    } finally {
      btnBroadcast.disabled = false;
      btnBroadcast.innerHTML = `<i class="fa-paper-plane fa-solid"></i> GỬI CÁC NHÓM ĐÃ CHỌN (<span id="selectedGroupCount">${selectedGroupIds.size}</span>)`;
    }
  }

  // 7. Đồng bộ Google Sheet & Tự Động Gửi Bảng Ảnh Đối Soát SLDT
  const btnSyncAutoSheet = document.getElementById("btnSyncAutoSheet");
  if (btnSyncAutoSheet) {
    btnSyncAutoSheet.addEventListener("click", async () => {
      const customMessage = sldtMessageText ? sldtMessageText.value.trim() : "";

      btnSyncAutoSheet.disabled = true;
      btnSyncAutoSheet.innerHTML = `<i class="fa-circle-notch fa-spin fa-solid"></i> Đang Lọc Sheet & Gửi Cho Các ST Có Trong Link...`;
      showToast("Đang đọc Google Sheet và tự động gửi Bảng Ảnh tới các nhóm ST có tên trong link...", "info");

      try {
        const res = await fetch("/api/sync_and_broadcast_st", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ custom_message: customMessage, target_groups: null })
        });
        const data = await res.json();

        if (res.ok) {
          showToast(`Thành công! Đã phát Bảng Ảnh Đối Soát SLDT cho ${data.success_results.length} nhóm ST có trong Sheet!`, "success");
          loadHistory();
        } else {
          showToast(data.detail || "Lỗi đồng bộ Sheet", "error");
        }
      } catch (err) {
        showToast("Lỗi kết nối máy chủ", "error");
      } finally {
        btnSyncAutoSheet.disabled = false;
        btnSyncAutoSheet.innerHTML = `<i class="fa-paper-plane fa-solid"></i> 🚀 GỬI TỰ ĐỘNG CHO ST CÓ TÊN TRONG LINK SHEET`;
      }
    });
  }

  async function sendSldtBroadcast(targetGroupsArray, label = "") {
    const customMessage = sldtMessageText ? sldtMessageText.value.trim() : "";
    if (!targetGroupsArray || targetGroupsArray.length === 0) {
      showToast("Vui lòng tick chọn ít nhất 1 nhóm ST để phát tin!", "warning");
      return;
    }

    if (btnSyncStBroadcast) {
      btnSyncStBroadcast.disabled = true;
      btnSyncStBroadcast.innerHTML = `<i class="fa-circle-notch fa-spin fa-solid"></i> Đang Lọc Sheet & Gửi Cho ${targetGroupsArray.length} Nhóm...`;
    }
    showToast(`Đang lọc Sheet và gửi Bảng Ảnh tới ${label || (targetGroupsArray.length + ' nhóm')} qua tài khoản @JinLi072...`, "info");

    try {
      const res = await fetch("/api/sync_and_broadcast_st", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ custom_message: customMessage, target_groups: targetGroupsArray })
      });
      const data = await res.json();

      if (res.ok) {
        showToast(`Thành công! Đã gửi Bảng Ảnh Đối Soát cho ${data.success_results.length} nhóm ST qua @JinLi072!`, "success");
        loadHistory();
      } else {
        showToast(data.detail || "Lỗi đồng bộ Sheet", "error");
      }
    } catch (err) {
      showToast("Lỗi kết nối máy chủ", "error");
    } finally {
      if (btnSyncStBroadcast) {
        btnSyncStBroadcast.disabled = false;
      }
      updateSldtSelectedCount();
    }
  }

  if (btnSyncStBroadcast) {
    btnSyncStBroadcast.addEventListener("click", async () => {
      const targetGroupsArray = Array.from(sldtSelectedGroupIds);
      if (targetGroupsArray.length === 0) {
        showToast("Vui lòng tick chọn ít nhất 1 nhóm ST ở danh sách bên trên!", "warning");
        return;
      }
      await sendSldtBroadcast(targetGroupsArray, `${targetGroupsArray.length} Nhóm Đã Chọn`);
      await updateLastBroadcastButton();
    });
  }

  // 8. Quản lý Thu Hồi Đợt Tin Nhắn Vừa Phát (An toàn tuyệt đối - CHỈ xóa đúng message_id vừa gửi)
  const btnRevokeLastSldt = document.getElementById("btnRevokeLastSldt");
  const sldtLastSentCount = document.getElementById("sldtLastSentCount");

  async function updateLastBroadcastButton() {
    if (!btnRevokeLastSldt) return;
    try {
      const res = await fetch("/api/last_broadcast");
      const data = await res.json();
      if (data.has_last && !data.revoked && data.total_sent > 0) {
        btnRevokeLastSldt.style.display = "flex";
        if (sldtLastSentCount) sldtLastSentCount.textContent = data.total_sent;
        btnRevokeLastSldt.setAttribute("data-total", data.total_sent);
        btnRevokeLastSldt.setAttribute("data-time", data.timestamp);
        btnRevokeLastSldt.innerHTML = `<i class="fa-trash-can fa-solid"></i> 🗑️ THU HỒI / XÓA TIN NHẮN VỪA PHÁT (${data.total_sent} Tin) (DELETE FOR EVERYONE)`;
      } else {
        btnRevokeLastSldt.style.display = "none";
      }
    } catch (e) {
      console.error(e);
    }
  }

  if (btnRevokeLastSldt) {
    btnRevokeLastSldt.addEventListener("click", async () => {
      const count = btnRevokeLastSldt.getAttribute("data-total") || "0";
      const time = btnRevokeLastSldt.getAttribute("data-time") || "";
      if (!confirm(`⚠️ XÁC NHẬN THU HỒI KHẨN CẤP:\n\nBạn có chắc chắn muốn XÓA TOÀN BỘ ${count} tin nhắn vừa phát lúc ${time} cho tất cả mọi người không?\n\n(Hệ thống chỉ xóa đúng ${count} tin nhắn vừa gửi đi này, tuyệt đối không quét hay xóa bất kỳ tin nhắn nào khác của bạn).`)) {
        return;
      }

      btnRevokeLastSldt.disabled = true;
      btnRevokeLastSldt.innerHTML = `<i class="fa-circle-notch fa-spin fa-solid"></i> Đang Thu Hồi ${count} Tin Nhắn...`;
      showToast(`Đang thu hồi ${count} tin nhắn vừa phát cho tất cả mọi người...`, "info");

      try {
        const res = await fetch("/api/revoke_last_broadcast", { method: "POST" });
        const resData = await res.json();
        if (res.ok) {
          showToast(`✅ Đã thu hồi thành công ${resData.deleted_count}/${resData.total} tin nhắn vừa phát!`, "success");
          btnRevokeLastSldt.style.display = "none";
          loadHistory();
        } else {
          showToast(resData.detail || "Thu hồi thất bại", "error");
        }
      } catch (err) {
        showToast("Lỗi kết nối máy chủ khi thu hồi", "error");
      } finally {
        btnRevokeLastSldt.disabled = false;
        await updateLastBroadcastButton();
      }
    });
  }

  btnRefresh.addEventListener("click", () => {
    loadGroups();
    loadMentions();
    loadHistory();
    updateLastBroadcastButton();
    showToast("Đã làm mới dữ liệu", "info");
  });

  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "fa-circle-check" : type === "error" ? "fa-circle-xmark" : "fa-circle-info";
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  // ==========================================
  // TAB 4: ĐỐI SOÁT KHO RAU & DATAPAY
  // ==========================================
  let allDatapayRows = [];

  async function loadKhoRauSummary() {
    try {
      const res = await fetch("/api/doi-soat/summary");
      const json = await res.json();
      if (json.status === "success" && json.data) {
        const d = json.data;
        const totalCompleted = d.steps ? d.steps.step5_completed : 0;
        const totalRecords = Object.values(d.steps || {}).reduce((a, b) => a + b, 0);
        
        document.getElementById("krTotalRecords").textContent = totalRecords.toLocaleString("vi-VN");
        document.getElementById("krStoreFaults").textContent = (d.responsible_parties?.["Siêu thị"] || 0).toLocaleString("vi-VN");
        document.getElementById("krDcFaults").textContent = (d.responsible_parties?.["DC"] || 0).toLocaleString("vi-VN");
        
        if (d.datapay) {
          document.getElementById("krTotalDatapay").textContent = d.datapay.total_datapay_amount.toLocaleString("vi-VN") + " đ";
          document.getElementById("krTotalStoresOwe").textContent = d.datapay.total_stores_owe.toLocaleString("vi-VN");
          document.getElementById("krTotalBasketsOwe").textContent = d.datapay.total_net_owe_baskets.toLocaleString("vi-VN");
        }
      }
    } catch (e) {
      console.error("Lỗi loadKhoRauSummary:", e);
    }
  }

  async function loadKhoRauDatapay() {
    await loadKhoRauSummary();
    const tbody = document.getElementById("datapayTableBody");
    tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 2rem; color: #94a3b8;">Đang tải danh sách bồi hoàn Datapay...</td></tr>`;

    try {
      const res = await fetch("/api/doi-soat/datapay?period=2026-09");
      const json = await res.json();
      if (json.status === "success" && Array.isArray(json.data)) {
        allDatapayRows = json.data;
        renderDatapayTable(allDatapayRows);
      } else {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 2rem; color: #ef4444;">Không thể lấy dữ liệu đối soát!</td></tr>`;
      }
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 2rem; color: #ef4444;">Lỗi kết nối máy chủ: ${e.message}</td></tr>`;
    }
  }

  function renderDatapayTable(rows) {
    const tbody = document.getElementById("datapayTableBody");
    if (!rows || rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 2rem; color: #94a3b8;">Không có dữ liệu đối soát phù hợp.</td></tr>`;
      return;
    }

    tbody.innerHTML = rows.map((r, i) => `
      <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.03)'" onmouseout="this.style.background='transparent'">
        <td style="padding: 10px; color: #94a3b8;">${i + 1}</td>
        <td style="padding: 10px; font-weight: bold; color: #38bdf8;">${escapeHtml(r.id_st)}</td>
        <td style="padding: 10px; color: #f1f5f9;">${escapeHtml(r.store_name || "")}</td>
        <td style="padding: 10px;"><span style="background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${escapeHtml(r.basket_name || r.basket_code)}</span></td>
        <td style="padding: 10px; text-align: center;">${r.missing_qty || 0}</td>
        <td style="padding: 10px; text-align: center; color: #10b981;">${r.resolved_qty || 0}</td>
        <td style="padding: 10px; text-align: center; font-weight: bold; color: #f87171;">${r.net_owe_qty || 0}</td>
        <td style="padding: 10px; text-align: right; color: #94a3b8;">${(r.unit_price || 0).toLocaleString("vi-VN")} đ</td>
        <td style="padding: 10px; text-align: right; font-weight: bold; color: #f87171;">${(r.total_amount || 0).toLocaleString("vi-VN")} đ</td>
        <td style="padding: 10px; text-align: center;"><span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem;">${escapeHtml(r.pay_status || "Chờ quyết toán")}</span></td>
      </tr>
    `).join("");
  }

  // Tìm kiếm trong bảng Datapay
  const searchDatapay = document.getElementById("searchDatapay");
  if (searchDatapay) {
    searchDatapay.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      if (!q) {
        renderDatapayTable(allDatapayRows);
        return;
      }
      const filtered = allDatapayRows.filter(r => 
        (r.id_st && r.id_st.toLowerCase().includes(q)) ||
        (r.store_name && r.store_name.toLowerCase().includes(q)) ||
        (r.basket_name && r.basket_name.toLowerCase().includes(q)) ||
        (r.basket_code && r.basket_code.toLowerCase().includes(q))
      );
      renderDatapayTable(filtered);
    });
  }

  // Nút đồng bộ Google Sheet
  const btnSyncKhoRauSheet = document.getElementById("btnSyncKhoRauSheet");
  if (btnSyncKhoRauSheet) {
    btnSyncKhoRauSheet.addEventListener("click", async () => {
      btnSyncKhoRauSheet.disabled = true;
      btnSyncKhoRauSheet.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang đồng bộ...`;
      try {
        const res = await fetch("/api/doi-soat/sync", { method: "POST" });
        const json = await res.json();
        if (json.status === "success") {
          showToast(`Đồng bộ thành công ${json.sync_result.total_rows} dòng dữ liệu!`, "success");
          await loadKhoRauDatapay();
        } else {
          showToast("Lỗi đồng bộ: " + (json.detail || "Không rõ"), "error");
        }
      } catch (e) {
        showToast("Lỗi kết nối máy chủ: " + e.message, "error");
      } finally {
        btnSyncKhoRauSheet.disabled = false;
        btnSyncKhoRauSheet.innerHTML = `<i class="fa-solid fa-rotate"></i> Đồng bộ Google Sheet`;
      }
    });
  }

  // Nút Push GitHub
  const btnPushGitHub = document.getElementById("btnPushGitHub");
  if (btnPushGitHub) {
    btnPushGitHub.addEventListener("click", async () => {
      btnPushGitHub.disabled = true;
      btnPushGitHub.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang push GitHub...`;
      try {
        const res = await fetch("/api/git/push", { method: "POST" });
        const json = await res.json();
        if (json.status === "success" || json.status === "warning") {
          showToast(json.message, "success");
        } else {
          showToast("Lỗi khi push: " + (json.detail || "Thất bại"), "error");
        }
      } catch (e) {
        showToast("Lỗi kết nối: " + e.message, "error");
      } finally {
        btnPushGitHub.disabled = false;
        btnPushGitHub.innerHTML = `<i class="fa-brands fa-github"></i> Đẩy lên GitHub`;
      }
    });
  }

  // Bắt sự kiện chuyển tab để load dữ liệu
  navItems.forEach(item => {
    item.addEventListener("click", () => {
      if (item.getAttribute("data-tab") === "tab-doi-soat-kho-rau") {
        loadKhoRauDatapay();
      }
    });
  });

  // Khởi chạy ban đầu
  loadGroups();
  loadMentions();
  loadHistory();
  updateLastBroadcastButton();
  loadKhoRauSummary();
  setInterval(loadMentions, 8000);
});
