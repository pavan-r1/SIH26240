"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Crosshair, MapPin, Send } from "lucide-react";

type SpringOption = { id: number; spring_code: string; name: string; data_status?: string };
const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export function FieldValidationForm() {
  const [springs, setSprings] = useState<SpringOption[]>([]);
  const [coords, setCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => { fetch(`${API}/api/springs`).then(r => r.ok ? r.json() : []).then(setSprings).catch(() => setSprings([])); }, []);
  function locate() {
    if (!navigator.geolocation) { setNotice("GPS is not available in this browser."); return; }
    setNotice("Requesting device location…");
    navigator.geolocation.getCurrentPosition(position => { setCoords({ latitude: position.coords.latitude, longitude: position.coords.longitude }); setNotice("Location captured from this device."); }, () => setNotice("Location permission was not granted. Enter coordinates from a trusted GPS device."), { enableHighAccuracy: true, timeout: 15000 });
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setNotice("");
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const payload = { spring_id: Number(form.get("spring_id")), observer: String(form.get("observer")), discharge: Number(form.get("discharge")), water_level: Number(form.get("water_level")), vegetation_condition: String(form.get("vegetation_condition")), nearby_land_use: String(form.get("nearby_land_use")), validation_status: "PENDING", latitude: coords?.latitude ?? Number(form.get("latitude")), longitude: coords?.longitude ?? Number(form.get("longitude")), notes: String(form.get("notes") || ""), data_status: "FIELD" };
    try { const response = await fetch(`${API}/api/field-observations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!response.ok) { const result = await response.json(); throw new Error(result.detail || "The observation could not be saved."); } formElement.reset(); setCoords(null); setNotice("Observation submitted with PENDING validation status."); }
    catch (error) { setNotice(error instanceof Error ? error.message : "Unable to connect to the API."); }
    finally { setSaving(false); }
  }

  return <section className="field-form-panel"><div className="field-form-heading"><span className="field-form-icon"><MapPin size={18}/></span><div><h2>New field observation</h2><p>Submit measurements for review. Submission does not mark a spring or model as validated.</p></div></div><div className="field-data-warning">Records submitted here are marked FIELD and PENDING. A reviewer must validate them.</div>{springs.length === 0 && <div className="field-form-message">No spring records could be loaded. Start the API and add a spring before submitting an observation.</div>}<form onSubmit={submit} className="field-form"><label>Spring<select required name="spring_id" defaultValue=""><option value="" disabled>Select a stored spring</option>{springs.map(s => <option key={s.id} value={s.id}>{s.spring_code} · {s.name} · {s.data_status ?? "UNVERIFIED"}</option>)}</select></label><label>Observer<input required name="observer" maxLength={120} placeholder="Your name or field ID"/></label><div className="field-form-divider">MEASUREMENTS</div><div className="field-form-grid"><label>Discharge (L/s)<input required name="discharge" type="number" min="0" step="any"/></label><label>Water level (m)<input required name="water_level" type="number" step="any"/></label><label>Vegetation condition<input required name="vegetation_condition" maxLength={80}/></label><label>Nearby land use<input required name="nearby_land_use" maxLength={100}/></label></div><div className="field-form-divider">LOCATION</div><button type="button" className="gps-button" onClick={locate}><Crosshair size={15}/> Capture GPS location</button>{coords && <span className="gps-coordinate">{coords.latitude.toFixed(6)}, {coords.longitude.toFixed(6)}</span>}<div className="field-form-grid"><label>Latitude<input name="latitude" type="number" min="-90" max="90" step="any" required={!coords} disabled={!!coords}/></label><label>Longitude<input name="longitude" type="number" min="-180" max="180" step="any" required={!coords} disabled={!!coords}/></label></div><label>Notes<textarea name="notes" rows={3} maxLength={2000} placeholder="Optional field notes"/></label><button className="field-submit" type="submit" disabled={saving || springs.length === 0}><Send size={15}/>{saving ? "Submitting…" : "Submit for validation"}</button>{notice && <p className="field-form-message" role="status">{notice}</p>}</form></section>;
}
