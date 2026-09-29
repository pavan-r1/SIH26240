"use client";

import { Circle, CircleMarker, MapContainer, Popup, TileLayer, ZoomControl } from "react-leaflet";

type Spring = { id: number; spring_code: string; name: string; spring_type: string; latitude: number; longitude: number; elevation: number; discharge_rate: number; water_quality_ph: number; status: string };
const zones = [
  { center: [30.126, 78.31] as [number, number], radius: 1350, score: 91 },
  { center: [30.145, 78.35] as [number, number], radius: 1100, score: 86 },
  { center: [30.095, 78.365] as [number, number], radius: 950, score: 78 },
  { center: [30.165, 78.285] as [number, number], radius: 1050, score: 73 },
];

export default function MapView({ springs }: { springs: Spring[] }) {
  return <div className="map-shell"><MapContainer center={[30.132, 78.327]} zoom={12} scrollWheelZoom zoomControl={false} className="map-canvas">
    <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    <ZoomControl position="bottomright" />
    {zones.map((zone, index) => <Circle key={index} center={zone.center} radius={zone.radius} pathOptions={{ color: zone.score > 85 ? "#5c8b59" : "#c59848", fillColor: zone.score > 85 ? "#87af70" : "#e1bd70", fillOpacity: 0.15, weight: 1.5, dashArray: "5 5" }}><Popup>Recharge suitability · {zone.score}%</Popup></Circle>)}
    {springs.map(s => <CircleMarker key={s.id} center={[s.latitude, s.longitude]} radius={8} pathOptions={{ color: "#fff", weight: 2, fillColor: s.status.toLowerCase() === "active" ? "#256957" : "#c39348", fillOpacity: 1 }}><Popup><div className="map-popup"><span>{s.spring_code}</span><strong>{s.name}</strong><small>{s.spring_type} · {s.elevation} m</small><small>Discharge {s.discharge_rate.toFixed(2)} L/s · pH {s.water_quality_ph.toFixed(1)}</small><b className="popup-status">{s.status}</b></div></Popup></CircleMarker>)}
  </MapContainer><div className="map-credit">Uttarakhand · Garhwal foothills</div></div>;
}
