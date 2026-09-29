# Prototype user guide

1. Start the local services using the README or Docker Compose guide.
2. Check the source label at the top of the dashboard. `DEMO DATA` means synthetic records; an API connection does not make those records real.
3. Open a spring marker to inspect its stored coordinates and sample values. Confirm provenance before using measurements.
4. Switch basemaps using the Leaflet layer control. Recharge polygons appear only after geometry is supplied through the recharge-zone API.
5. Use the assistant for read-only spring and zone lookups. It does not run analysis, call an LLM, or change records.
6. The weather endpoint reports when no source is configured. Recharge analysis remains unavailable until sourced GIS data are added.

No intervention should be selected or implemented from demo records or an unvalidated model output.
