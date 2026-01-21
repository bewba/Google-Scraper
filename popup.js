(() => {
  const fieldsContainer = document.getElementById("fieldsContainer");
  const addFieldBtn = document.getElementById("addField");
  const scrapeBtn = document.getElementById("scrapeBtn");
  const logEl = document.getElementById("log");

  const defaultFields = [
    { name: "name", selector: ".Nv2PK .qBF1Pd" },
    { name: "rating", selector: ".Nv2PK .MW4etd" },
    { name: "reviews", selector: ".Nv2PK .UY7F9" },
    { name: "category", selector: ".Nv2PK .W4Efsd" },
    { name: "address", selector: ".Nv2PK .W4Efsd span:last-child" }
  ];

  const log = (msg) => {
    const ts = new Date().toLocaleTimeString();
    logEl.innerHTML = `<div>[${ts}] ${msg}</div>` + logEl.innerHTML;
  };

  const addFieldRow = ({ name = "", selector = "" } = {}) => {
    const row = document.createElement("div");
    row.className = "field-row";
    row.innerHTML = `
      <input class="fname" placeholder="Field name" value="${name}">
      <input class="fsel" placeholder="CSS selector" value="${selector}">
      <button type="button" class="removeBtn">Remove</button>
    `;
    row.querySelector(".removeBtn").onclick = () => row.remove();
    fieldsContainer.appendChild(row);
  };

  const getFieldConfigs = () =>
    Array.from(fieldsContainer.querySelectorAll(".field-row")).map((row) => ({
      name: row.querySelector(".fname").value.trim(),
      selector: row.querySelector(".fsel").value.trim()
    })).filter(f => f.name && f.selector);

  addFieldBtn.onclick = () => addFieldRow();
  defaultFields.forEach(addFieldRow);

  scrapeBtn.onclick = async () => {
    const fieldConfigs = getFieldConfigs();
    if (!fieldConfigs.length) {
      log("Add at least one field with a selector.");
      return;
    }

    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) {
        log("No active tab found.");
        return;
      }

      log("Starting scrape…");

      const code = `
        (async () => {
          const wait = (ms) => new Promise(r => setTimeout(r, ms));
          const fields = ${JSON.stringify(fieldConfigs)};

          const scroller = document.querySelector('.m6QErb[aria-label*="Results"], .m6QErb.DxyBCb');
          if (scroller) {
            for (let i = 0; i < 8; i++) {
              scroller.scrollTo({ top: scroller.scrollHeight, behavior: "smooth" });
              await wait(600);
            }
          } else {
            window.scrollTo(0, document.body.scrollHeight);
            await wait(1200);
          }

          const results = [];
          const maxLen = Math.max(...fields.map(f => document.querySelectorAll(f.selector).length));
          for (let i = 0; i < maxLen; i++) {
            const row = {};
            fields.forEach(f => {
              const el = document.querySelectorAll(f.selector)[i];
              row[f.name] = el ? el.textContent.trim() : "";
            });
            results.push(row);
          }
          return results;
        })();
      `;

      const injectionResults = await browser.tabs.executeScript(tab.id, { code });
      const places = injectionResults && injectionResults[0] ? injectionResults[0] : [];

      log(`Scrape finished. Items found: ${places.length}`);

      if (!places.length) {
        log("No items found. Check selectors or scroll the list first.");
        return;
      }

      const headers = Object.keys(places[0]);
      const csv = [
        headers,
        ...places.map(p => headers.map(h => `"${(p[h] || "").replace(/"/g, '""')}"`))
      ].map(r => r.join(",")).join("\n");

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "places.csv";
      a.click();
      URL.revokeObjectURL(url);
      log("CSV downloaded!");
    } catch (e) {
      log("Error during scrape: " + e.message);
    }
  };
})();
