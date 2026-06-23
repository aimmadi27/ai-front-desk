(function () {
  var API_URL = "%%API_URL%%";
  var BUSINESS_ID = "%%BUSINESS_ID%%";
  var PRIMARY = "%%PRIMARY_COLOR%%" || "#6366f1";

  var sessionId = null;
  var open = false;

  var styles = `
    #afd-btn {
      position: fixed; bottom: 24px; right: 24px; z-index: 9998;
      width: 56px; height: 56px; border-radius: 50%;
      background: ${PRIMARY}; border: none; cursor: pointer;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25);
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s;
    }
    #afd-btn:hover { transform: scale(1.08); }
    #afd-btn svg { width: 26px; height: 26px; fill: #fff; }
    #afd-box {
      position: fixed; bottom: 90px; right: 24px; z-index: 9999;
      width: 340px; height: 480px; border-radius: 16px;
      background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.18);
      display: none; flex-direction: column; overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    #afd-box.open { display: flex; }
    #afd-header {
      background: ${PRIMARY}; color: #fff;
      padding: 14px 18px; font-weight: 700; font-size: 15px;
    }
    #afd-header p { margin: 2px 0 0; font-size: 12px; font-weight: 400; opacity: 0.85; }
    #afd-messages {
      flex: 1; overflow-y: auto; padding: 14px;
      display: flex; flex-direction: column; gap: 10px;
    }
    .afd-msg {
      max-width: 82%; padding: 10px 14px; border-radius: 14px;
      font-size: 14px; line-height: 1.45;
    }
    .afd-msg.bot {
      background: #f3f4f6; color: #111; align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .afd-msg.user {
      background: ${PRIMARY}; color: #fff; align-self: flex-end;
      border-bottom-right-radius: 4px;
    }
    #afd-input-row {
      display: flex; padding: 10px; gap: 8px;
      border-top: 1px solid #e5e7eb;
    }
    #afd-input {
      flex: 1; border: 1px solid #d1d5db; border-radius: 8px;
      padding: 9px 12px; font-size: 14px; outline: none;
    }
    #afd-input:focus { border-color: ${PRIMARY}; }
    #afd-send {
      background: ${PRIMARY}; color: #fff; border: none;
      border-radius: 8px; padding: 0 16px; cursor: pointer;
      font-weight: 600; font-size: 14px;
    }
  `;

  var styleEl = document.createElement("style");
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);

  var btn = document.createElement("button");
  btn.id = "afd-btn";
  btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/></svg>';
  document.body.appendChild(btn);

  var box = document.createElement("div");
  box.id = "afd-box";
  box.innerHTML = `
    <div id="afd-header">
      <div>AI Front Desk</div>
      <p>We typically reply instantly</p>
    </div>
    <div id="afd-messages"></div>
    <div id="afd-input-row">
      <input id="afd-input" type="text" placeholder="Type a message..." />
      <button id="afd-send">Send</button>
    </div>
  `;
  document.body.appendChild(box);

  function appendMessage(text, role) {
    var el = document.createElement("div");
    el.className = "afd-msg " + role;
    el.textContent = text;
    document.getElementById("afd-messages").appendChild(el);
    document.getElementById("afd-messages").scrollTop = 9999;
  }

  async function sendMessage(text) {
    appendMessage(text, "user");
    document.getElementById("afd-input").value = "";

    var res = await fetch(API_URL + "/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        business_id: BUSINESS_ID,
        session_id: sessionId,
        message: text,
      }),
    });
    var data = await res.json();
    sessionId = data.session_id;
    appendMessage(data.reply, "bot");
  }

  btn.addEventListener("click", function () {
    open = !open;
    box.classList.toggle("open", open);
    if (open && !document.querySelector(".afd-msg")) {
      appendMessage("Hi! How can I help you today?", "bot");
    }
  });

  document.getElementById("afd-send").addEventListener("click", function () {
    var val = document.getElementById("afd-input").value.trim();
    if (val) sendMessage(val);
  });

  document.getElementById("afd-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      var val = e.target.value.trim();
      if (val) sendMessage(val);
    }
  });
})();
