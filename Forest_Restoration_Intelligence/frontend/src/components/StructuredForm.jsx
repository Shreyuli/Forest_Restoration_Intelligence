import { useState } from "react";

const TREND_OPTIONS = ["", "increasing", "decreasing", "stable"];

export default function StructuredForm({ onSubmit, disabled }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    deforestation: false,
    fragmentation: false,
    temperature_trend: "",
    rainfall_trend: "",
    region: "",
    lat: "",
    lon: "",
  });

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const submit = (e) => {
    e.preventDefault();
    const payload = {
      deforestation: form.deforestation || null,
      fragmentation: form.fragmentation || null,
      temperature_trend: form.temperature_trend || null,
      rainfall_trend: form.rainfall_trend || null,
      region: form.region || null,
      geo:
        form.lat !== "" && form.lon !== ""
          ? { lat: parseFloat(form.lat), lon: parseFloat(form.lon) }
          : null,
    };
    onSubmit(payload);
  };

  if (!open) {
    return (
      <button className="structured-toggle" onClick={() => setOpen(true)}>
        + Structured JSON input (deforestation / trends / geo)
      </button>
    );
  }

  return (
    <form className="structured-form" onSubmit={submit}>
      <div className="structured-form-header">
        Structured input
        <button type="button" className="link-btn" onClick={() => setOpen(false)}>
          collapse
        </button>
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.deforestation}
          onChange={(e) => update("deforestation", e.target.checked)}
        />
        Deforestation present
      </label>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.fragmentation}
          onChange={(e) => update("fragmentation", e.target.checked)}
        />
        Fragmentation / agricultural expansion present
      </label>

      <div className="field-row">
        <label>
          Temperature trend
          <select
            value={form.temperature_trend}
            onChange={(e) => update("temperature_trend", e.target.value)}
          >
            {TREND_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o || "(unspecified)"}
              </option>
            ))}
          </select>
        </label>
        <label>
          Rainfall trend
          <select
            value={form.rainfall_trend}
            onChange={(e) => update("rainfall_trend", e.target.value)}
          >
            {TREND_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o || "(unspecified)"}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="field-row">
        <label>
          Region
          <input
            type="text"
            placeholder="e.g. Amazon Basin"
            value={form.region}
            onChange={(e) => update("region", e.target.value)}
          />
        </label>
      </div>

      <div className="field-row">
        <label>
          Lat
          <input type="number" step="any" value={form.lat} onChange={(e) => update("lat", e.target.value)} />
        </label>
        <label>
          Lon
          <input type="number" step="any" value={form.lon} onChange={(e) => update("lon", e.target.value)} />
        </label>
      </div>

      <button type="submit" disabled={disabled}>
        Analyze
      </button>
    </form>
  );
}
