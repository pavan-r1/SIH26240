"use client";

import { useEffect } from "react";
import { CircleMarker, GeoJSON, LayersControl, MapContainer, Popup, ScaleControl, TileLayer, useMap, ZoomControl } from "react-leaflet";
import { latLngBounds } from "leaflet";
import type { Feature, FeatureCollection, Geometry } from "geojson";

type Spring = { id: number; spring_code: string; name: string; spring_type: string; latitude: number; longitude: number; elevation: number; discharge_rate: number; water_quality_ph: number; status: string; data_status?: string };
type ZoneFeature = Feature<Geometry, { zone_code: string; suitability_class: string; data_status: string }>;

function FitSprings({ springs }: { springs: Spring[] }) {
  const map = useMap();
  useEffect(() => {
    if (springs.length) map.fitBounds(latLngBounds(springs.map(s => [s.latitude, s.longitude] as [number, number])), { padding: [28, 28], maxZoom: 13 });
  }, [map, springs]);
  return null;
}

export default function MapView({ springs, zones = [] }: { springs: Spring[]; zones?: ZoneFeature[] }) {
  return <div className="map-shell"><MapContainer center={[15, 0]} zoom={2} scrollWheelZoom zoomControl={false} className="map-canvas">
    <FitSprings springs={springs}/>
    <LayersControl position="topright"><LayersControl.BaseLayer checked name="OpenStreetMap"><TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" /></LayersControl.BaseLayer><LayersControl.BaseLayer name="Satellite imagery"><TileLayer attribution='Tiles &copy; Esri' url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" /></LayersControl.BaseLayer></LayersControl>
    <ZoomControl position="bottomright"/><ScaleControl position="bottomleft"/>
    {zones.length > 0 && <GeoJSON data={{ type: "FeatureCollection", features: zones } as FeatureCollection} style={() => ({ color: "#517c54", fillColor: "#88a978", fillOpacity: .25, weight: 2 })} onEachFeature={(feature, layer) => layer.bindPopup(`${feature.properties?.zone_code ?? "Recharge zone"} · ${feature.properties?.suitability_class ?? "Class unavailable"} · ${feature.properties?.data_status ?? "UNVERIFIED"}`)} />}
    {springs.map(s => <CircleMarker key={s.id} center={[s.latitude, s.longitude]} radius={8} pathOptions={{ color: "#fff", weight: 2, fillColor: s.status.toLowerCase() === "active" ? "#256957" : "#c39348", fillOpacity: 1 }}><Popup><div className="map-popup"><span>{s.spring_code} · {s.data_status ?? "DEMO"}</span><strong>{s.name}</strong><small>{s.spring_type} · {s.elevation} m</small><small>Discharge {s.discharge_rate.toFixed(2)} L/s · pH {s.water_quality_ph.toFixed(1)}</small><b className="popup-status">{s.status}</b></div></Popup></CircleMarker>)}
  </MapContainer><div className="map-credit">Spring locations use stored coordinates · recharge polygons appear only when boundaries are supplied</div></div>;
}
