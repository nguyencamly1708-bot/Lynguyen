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
        botStatusText.textContent = `Bot Hoạt Động (${data.groups_count} nhóm)`;
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
      sldtSelectedGroupIds = new Set(Object.keys(currentGroups));

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
    let countAll = 0, countDc = 0, countKrc = 0, countAba = 0, countOther = 0;
    Object.values(groups).forEach(g => {
      const cat = getGroupCategory(g.title);
      countAll++;
      if (cat === "dc") countDc++;
      else if (cat === "krc") countKrc++;
      else if (cat === "aba") countAba++;
      else countOther++;
    });

    const elAll = document.getElementById("sldtCatCountAll");
    const elDc = document.getElementById("sldtCatCountDc");
    const elKrc = document.getElementById("sldtCatCountKrc");
    const elAba = document.getElementById("sldtCatCountAba");
    const elOther = document.getElementById("sldtCatCountOther");

    if (elAll) elAll.textContent = countAll;
    if (elDc) elDc.textContent = countDc;
    if (elKrc) elKrc.textContent = countKrc;
    if (elAba) elAba.textContent = countAba;
    if (elOther) elOther.textContent = countOther;
  }

  function renderSldtGroupsList(groups, filterText = "") {
    const sldtGroupsList = document.getElementById("sldtGroupsList");
    const sldtSelectedGroupCount = document.getElementById("sldtSelectedGroupCount");

    if (!sldtGroupsList) return;

    updateSldtCategoryCounts(groups);

    const entries = Object.entries(groups).filter(([gid, data]) => {
      const matchSearch = data.title.toLowerCase().includes((filterText || "").toLowerCase());
      const cat = getGroupCategory(data.title);
      const matchCat = (sldtCurrentCategory === "all") || (cat === sldtCurrentCategory);
      return matchSearch && matchCat;
    });

    if (sldtSelectedGroupCount) sldtSelectedGroupCount.textContent = sldtSelectedGroupIds.size;

    if (entries.length === 0) {
      sldtGroupsList.innerHTML = `<div class="empty-state">Không tìm thấy nhóm phù hợp trong mục này.</div>`;
      return;
    }

    sldtGroupsList.innerHTML = entries.map(([gid, data]) => {
      const isChecked = sldtSelectedGroupIds.has(gid);
      return `
        <div class="group-card-item ${isChecked ? 'selected' : ''}" data-sgid="${gid}">
          <div class="group-left-area">
            <input type="checkbox" value="${gid}" class="sldt-group-checkbox" ${isChecked ? 'checked' : ''}>
            <div>
              <div class="group-title">👥 ${escapeHtml(data.title)}</div>
              <div class="group-id">ID: ${gid}</div>
            </div>
          </div>
        </div>
      `;
    }).join("");

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
        if (sldtSelectedGroupCount) sldtSelectedGroupCount.textContent = sldtSelectedGroupIds.size;
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
        const matchCat = (sldtCurrentCategory === "all") || (cat === sldtCurrentCategory);
        return matchSearch && matchCat;
      });

      const currentGids = currentCategoryEntries.map(([gid]) => gid);
      const allSelected = currentGids.every(gid => sldtSelectedGroupIds.has(gid));

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

  btnSyncStBroadcast.addEventListener("click", async () => {
    const customMessage = sldtMessageText ? sldtMessageText.value.trim() : "";
    const targetGroupsArray = Array.from(sldtSelectedGroupIds);

    if (targetGroupsArray.length === 0) {
      showToast("Vui lòng chọn ít nhất 1 nhóm Telegram ST để phát tin đối soát!", "warning");
      return;
    }

    btnSyncStBroadcast.disabled = true;
    btnSyncStBroadcast.innerHTML = `<i class="fa-circle-notch fa-spin fa-solid"></i> Đang Lọc Sheet & Gửi Bảng Ảnh Cho ${targetGroupsArray.length} Nhóm...`;
    showToast(`Đang đồng bộ dữ liệu Google Sheet và gửi Bảng Ảnh tới ${targetGroupsArray.length} nhóm được chọn...`, "info");

    try {
      const res = await fetch("/api/sync_and_broadcast_st", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ custom_message: customMessage, target_groups: targetGroupsArray })
      });
      const data = await res.json();

      if (res.ok) {
        showToast(`Thành công! Đã phát Bảng Ảnh Đối Soát SLDT cho ${data.success_results.length} nhóm ST!`, "success");
        loadHistory();
      } else {
        showToast(data.detail || "Lỗi đồng bộ Sheet", "error");
      }
    } catch (err) {
      showToast("Lỗi kết nối máy chủ", "error");
    } finally {
      btnSyncStBroadcast.disabled = false;
      btnSyncStBroadcast.innerHTML = `<i class="fa-file-image fa-solid"></i> 🚀 GỬI TIN NHẮN VÀ BẢNG ẢNH ĐỐI SOÁT SLDT (<span id="sldtSelectedGroupCount">${sldtSelectedGroupIds.size}</span> Nhóm)`;
    }
  });

  btnRefresh.addEventListener("click", () => {
    loadGroups();
    loadMentions();
    loadHistory();
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

  // Khởi chạy ban đầu
  loadGroups();
  loadMentions();
  loadHistory();
  setInterval(loadMentions, 8000);
});
