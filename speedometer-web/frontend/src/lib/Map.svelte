<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	export let points: [number, number][] = [];

	let mapElement: HTMLElement;
	let map: any;

	onMount(async () => {
		const L = (await import('leaflet')).default;
		
		// Fix default icon issues
		delete (L.Icon.Default.prototype as any)._getIconUrl;

		if (points.length > 0 && mapElement) {
			map = L.map(mapElement);
			
			L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
				attribution: '&copy; OpenStreetMap &copy; CARTO',
				maxZoom: 20
			}).addTo(map);

			const polyline = L.polyline(points, { color: '#39ff14', weight: 4 }).addTo(map);
			
			L.circleMarker(points[0], { color: '#39ff14', fillColor: '#39ff14', radius: 6, fillOpacity: 1 }).addTo(map);
			L.circleMarker(points[points.length - 1], { color: '#ff3333', fillColor: '#ff3333', radius: 6, fillOpacity: 1 }).addTo(map);

			map.fitBounds(polyline.getBounds(), { padding: [20, 20] });
		}
	});
	
	onDestroy(() => {
		if (map) {
			map.remove();
		}
	});
</script>

<svelte:head>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div bind:this={mapElement} class="map"></div>

<style>
	.map {
		width: 100%;
		height: 100%;
		z-index: 1;
	}
</style>
