import { createClient } from "./api/client.js";

const apiBaseInput = document.querySelector("#apiBase");
const startSessionButton = document.querySelector("#startSessionBtn");
const sessionStatus = document.querySelector("#sessionStatus");
const sessionMeta = document.querySelector("#sessionMeta");
const messageList = document.querySelector("#messageList");
const messageForm = document.querySelector("#messageForm");
const messageInput = document.querySelector("#messageInput");
const sendButton = document.querySelector("#sendBtn");

let client = null;
let session = null;
const messages = [];

const renderMessages = () => {
  messageList.innerHTML = "";

  messages.forEach((message) => {
    const item = document.createElement("li");
    item.className = "message";
    item.dataset.role = message.role;
    if (message.status) {
      item.dataset.status = message.status;
    }

    const meta = message.status ? ` (${message.status})` : "";
    item.textContent = `${message.text}${meta}`;
    messageList.appendChild(item);
  });
};

const setSessionState = ({ statusText, metaText, ready }) => {
  sessionStatus.textContent = statusText;
  sessionMeta.textContent = metaText || "";
  messageInput.disabled = !ready;
  sendButton.disabled = !ready;
};

const startSession = async () => {
  const baseUrl = apiBaseInput.value.trim();
  if (!baseUrl) {
    setSessionState({ statusText: "Session: missing API base URL", ready: false });
    return;
  }

  client = createClient({ baseUrl });
  setSessionState({ statusText: "Session: starting...", ready: false });

  try {
    const payload = await client.createSession();
    session = {
      token: payload.token,
      conversationId: payload.conversation_id,
      expiresIn: payload.expires_in,
    };
    setSessionState({
      statusText: "Session: ready",
      metaText: `Conversation: ${session.conversationId}`,
      ready: true,
    });
  } catch (error) {
    session = null;
    setSessionState({
      statusText: `Session: failed (${error.message})`,
      ready: false,
    });
  }
};

const sendMessage = async (text) => {
  if (!client || !session) {
    setSessionState({ statusText: "Session: not ready", ready: false });
    return;
  }

  const message = {
    id: `local-${Date.now()}`,
    role: "user",
    text,
    status: "sending",
  };
  messages.push(message);
  renderMessages();

  try {
    const payload = await client.createMessage(session.token, text);
    message.id = payload.message_id;
    message.status = "sent";
    renderMessages();
  } catch (error) {
    message.status = "failed";
    renderMessages();
    setSessionState({
      statusText: `Session: ready (last error ${error.message})`,
      metaText: `Conversation: ${session.conversationId}`,
      ready: true,
    });
  }
};

startSessionButton.addEventListener("click", () => {
  startSession();
});

messageForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    return;
  }

  messageInput.value = "";
  sendMessage(text);
});

renderMessages();
