import { useState } from "react";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");

  const submit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <form className="chat-input-row" onSubmit={submit}>
      <input
        type="text"
        placeholder="Describe the forest area, e.g. 'A forest area has experienced deforestation. Rainfall has decreased and average temperature has increased.'"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  );
}
